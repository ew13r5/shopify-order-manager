import logging
import random
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from faker import Faker
from sqlalchemy.orm import Session

from models import Adjustment, LineItem, Order, Payout, PayoutItem, Product, Store
from models.enums import (
    AdjustmentType,
    DataMode,
    FinancialStatus,
    FulfillmentStatus,
    PayoutStatus,
)
from seed.dirty_sku_generator import maybe_contaminate

logger = logging.getLogger(__name__)
fake = Faker()


def seed_demo_data(
    session: Session,
    num_orders: int = 500,
    num_products: int = 50,
) -> dict:
    """Seed the database with realistic demo e-commerce data."""

    # 1. Create demo store
    store = Store(
        id=uuid.uuid4(),
        name="Demo Store",
        is_demo=True,
        data_mode=DataMode.demo,
    )
    session.add(store)
    session.flush()

    # 2. Generate products
    products = []
    for _ in range(num_products):
        clean_sku = fake.bothify(text="???-####").upper()
        raw_sku = maybe_contaminate(clean_sku, rate=0.2)
        product = Product(
            id=uuid.uuid4(),
            store_id=store.id,
            shopify_id=str(uuid.uuid4()),
            title=fake.catch_phrase(),
            sku=raw_sku,
            sku_cleaned=clean_sku,
            variant_title=random.choice(["Default", "Small", "Medium", "Large", None]),
            variant_sku=fake.bothify(text="??-##") if random.random() > 0.5 else None,
            price=Decimal(str(round(random.uniform(5.0, 500.0), 2))),
        )
        products.append(product)
    session.add_all(products)
    session.flush()

    # 3. Generate orders distributed across 6 months
    orders = []
    line_items_all = []
    now = datetime.now(timezone.utc)
    six_months_ago = now - timedelta(days=180)

    financial_statuses = (
        [FinancialStatus.paid] * 80
        + [FinancialStatus.partially_refunded] * 10
        + [FinancialStatus.refunded] * 5
        + [FinancialStatus.pending] * 5
    )
    fulfillment_statuses = (
        [FulfillmentStatus.fulfilled] * 70
        + [FulfillmentStatus.unfulfilled] * 20
        + [FulfillmentStatus.partial] * 10
    )

    for i in range(num_orders):
        # Weighted date: more orders in Nov-Dec
        day_offset = random.randint(0, 180)
        order_date = six_months_ago + timedelta(days=day_offset)
        if order_date.month in (11, 12):
            # 50% more likely to keep holiday orders
            pass
        elif random.random() < 0.3:
            # Shift some orders to Nov-Dec for holiday bump
            order_date = order_date.replace(month=random.choice([11, 12]))

        fin_status = random.choice(financial_statuses)
        ful_status = random.choice(fulfillment_statuses)

        order = Order(
            id=uuid.uuid4(),
            store_id=store.id,
            shopify_id=str(uuid.uuid4()),
            order_number=f"#{1000 + i}",
            customer_name=fake.name(),
            customer_email=fake.email(),
            status="open",
            financial_status=fin_status,
            fulfillment_status=ful_status,
            total_price=Decimal("0"),
            order_created_at=order_date,
            order_updated_at=order_date + timedelta(hours=random.randint(0, 48)),
        )
        orders.append(order)

    session.add_all(orders)
    session.flush()

    # 4. Generate line items
    for order in orders:
        num_items = random.randint(1, 5)
        order_total = Decimal("0")

        for _ in range(num_items):
            product = random.choice(products)
            qty = random.randint(1, 4)
            unit_price = product.price or Decimal("10.00")
            total = unit_price * qty
            discount = Decimal(str(round(float(total) * random.uniform(0, 0.2), 2))) if random.random() < 0.3 else Decimal("0")
            tax = Decimal(str(round(float(total - discount) * 0.08, 2)))

            li = LineItem(
                id=uuid.uuid4(),
                order_id=order.id,
                product_id=product.id,
                shopify_id=str(uuid.uuid4()),
                title=product.title,
                sku=product.sku,
                sku_cleaned=product.sku_cleaned,
                variant_title=product.variant_title,
                variant_sku=product.variant_sku,
                quantity=qty,
                unit_price=unit_price,
                total_price=total,
                discount_amount=discount,
                tax_amount=tax,
                fulfillment_status=order.fulfillment_status.value if order.fulfillment_status else None,
                refund_amount=Decimal("0"),
            )
            line_items_all.append(li)
            order_total += total - discount + tax

        order.total_price = order_total

    session.add_all(line_items_all)
    session.flush()

    # 5. Generate payouts (monthly batches)
    payouts = []
    payout_items = []
    months_covered = set()
    for li in line_items_all:
        order = next(o for o in orders if o.id == li.order_id)
        if order.order_created_at:
            month_key = order.order_created_at.strftime("%Y-%m")
            months_covered.add(month_key)

    for month_str in sorted(months_covered):
        year, month = int(month_str[:4]), int(month_str[5:])
        payout = Payout(
            id=uuid.uuid4(),
            store_id=store.id,
            shopify_payout_id=str(uuid.uuid4()),
            date=date(year, month, 28),
            amount=Decimal("0"),
            status=PayoutStatus.paid,
        )
        payouts.append(payout)

    session.add_all(payouts)
    session.flush()

    # Create payout items per line item
    payout_map = {}
    for p in payouts:
        payout_map[p.date.strftime("%Y-%m")] = p

    for li in line_items_all:
        order = next(o for o in orders if o.id == li.order_id)
        if not order.order_created_at:
            continue
        month_key = order.order_created_at.strftime("%Y-%m")
        payout = payout_map.get(month_key)
        if not payout:
            continue

        gross = (li.unit_price or Decimal("0")) * li.quantity - (li.discount_amount or Decimal("0")) + (li.tax_amount or Decimal("0"))
        fee_rate = Decimal(str(round(random.uniform(0.024, 0.029), 4)))
        fee = round(gross * fee_rate, 2)
        net = gross - fee

        pi = PayoutItem(
            id=uuid.uuid4(),
            payout_id=payout.id,
            line_item_id=li.id,
            gross_amount=gross,
            fee_amount=fee,
            net_amount=net,
        )
        payout_items.append(pi)
        payout.amount = (payout.amount or Decimal("0")) + net

    session.add_all(payout_items)

    # 6. Generate adjustments
    adjustments = []
    refund_orders = random.sample(orders, min(len(orders), int(num_orders * 0.10)))
    for order in refund_orders:
        adj = Adjustment(
            id=uuid.uuid4(),
            store_id=store.id,
            order_id=order.id,
            type=AdjustmentType.refund,
            amount=Decimal(str(round(float(order.total_price or 0) * random.uniform(0.1, 1.0), 2))),
            reason=random.choice(["Customer request", "Defective item", "Wrong size", "Not as described"]),
        )
        adjustments.append(adj)

    chargeback_orders = random.sample(orders, min(len(orders), int(num_orders * 0.02)))
    for order in chargeback_orders:
        adj = Adjustment(
            id=uuid.uuid4(),
            store_id=store.id,
            order_id=order.id,
            type=AdjustmentType.chargeback,
            amount=order.total_price or Decimal("0"),
            reason="Disputed transaction",
        )
        adjustments.append(adj)

    session.add_all(adjustments)
    session.commit()

    result = {
        "store_id": str(store.id),
        "products": len(products),
        "orders": len(orders),
        "line_items": len(line_items_all),
        "payouts": len(payouts),
        "payout_items": len(payout_items),
        "adjustments": len(adjustments),
    }
    logger.info("Demo data seeded: %s", result)
    return result
