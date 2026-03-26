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

# --- Realistic product catalog ---

PRODUCT_CATALOG = [
    # (title, base_sku, variants: [(variant_title, variant_sku_suffix, price)])
    ("Classic Leather Wallet", "WLT", [
        ("Brown / Small", "BRN-S", 35.00),
        ("Brown / Large", "BRN-L", 45.00),
        ("Black / Small", "BLK-S", 35.00),
        ("Black / Large", "BLK-L", 45.00),
        ("Tan / Small", "TAN-S", 35.00),
        ("Tan / Large", "TAN-L", 45.00),
    ]),
    ("Canvas Tote Bag", "BAG", [
        ("Navy / Medium", "NVY-M", 32.00),
        ("Navy / Large", "NVY-L", 38.00),
        ("Cream / Medium", "CRM-M", 32.00),
        ("Cream / Large", "CRM-L", 38.00),
        ("Olive / Medium", "OLV-M", 32.00),
        ("Olive / Large", "OLV-L", 38.00),
    ]),
    ("Wireless Charging Pad", "CHG", [
        ("Black", "BLK", 29.90),
        ("White", "WHT", 29.90),
    ]),
    ("Organic Cotton T-Shirt", "TSH", [
        ("White / S", "WHT-S", 29.00),
        ("White / M", "WHT-M", 29.00),
        ("White / L", "WHT-L", 29.00),
        ("White / XL", "WHT-XL", 29.00),
        ("Black / S", "BLK-S", 29.00),
        ("Black / M", "BLK-M", 29.00),
        ("Black / L", "BLK-L", 29.00),
        ("Gray / M", "GRY-M", 29.00),
        ("Gray / L", "GRY-L", 29.00),
    ]),
    ("Stainless Steel Water Bottle", "BTL", [
        ("Silver / 500ml", "SLV-500", 28.00),
        ("Silver / 750ml", "SLV-750", 34.00),
        ("Silver / 1000ml", "SLV-1000", 42.00),
        ("Matte Black / 500ml", "BLK-500", 28.00),
        ("Matte Black / 750ml", "BLK-750", 34.00),
    ]),
    ("Phone Case", "CSE", [
        ("Clear / iPhone 15", "CLR-IP15", 18.50),
        ("Clear / iPhone 14", "CLR-IP14", 16.50),
        ("Clear / Samsung S24", "CLR-S24", 18.50),
        ("Matte Black / iPhone 15", "BLK-IP15", 22.00),
        ("Matte Black / iPhone 14", "BLK-IP14", 20.00),
    ]),
    ("Bamboo Sunglasses", "SUN", [
        ("Classic / Brown Lens", "CLS-BRN", 48.00),
        ("Classic / Gray Lens", "CLS-GRY", 48.00),
        ("Aviator / Brown Lens", "AVT-BRN", 55.00),
        ("Aviator / Gray Lens", "AVT-GRY", 55.00),
    ]),
    ("Merino Wool Beanie", "BNE", [
        ("Charcoal", "CHR", 36.00),
        ("Navy", "NVY", 36.00),
        ("Burgundy", "BRG", 36.00),
        ("Forest Green", "GRN", 36.00),
    ]),
    ("Leather Keychain Set", "KEY", [
        ("Brown / 3-pack", "BRN-3", 24.00),
        ("Black / 3-pack", "BLK-3", 24.00),
        ("Mixed / 3-pack", "MIX-3", 26.00),
    ]),
    ("Aromatherapy Candle", "CND", [
        ("Lavender / 8oz", "LAV-8", 22.00),
        ("Lavender / 16oz", "LAV-16", 38.00),
        ("Eucalyptus / 8oz", "EUC-8", 22.00),
        ("Vanilla / 8oz", "VAN-8", 22.00),
        ("Vanilla / 16oz", "VAN-16", 38.00),
    ]),
    ("Minimalist Watch", "WCH", [
        ("Silver / Leather", "SLV-LTH", 89.00),
        ("Silver / Mesh", "SLV-MSH", 95.00),
        ("Gold / Leather", "GLD-LTH", 99.00),
        ("Rose Gold / Leather", "RSG-LTH", 99.00),
    ]),
    ("Yoga Mat", "YGA", [
        ("Purple / 4mm", "PRP-4", 45.00),
        ("Blue / 4mm", "BLU-4", 45.00),
        ("Black / 6mm", "BLK-6", 55.00),
        ("Sage / 4mm", "SGE-4", 45.00),
    ]),
    ("Linen Throw Pillow", "PLW", [
        ("Ivory / 18x18", "IVR-18", 42.00),
        ("Sage / 18x18", "SGE-18", 42.00),
        ("Dusty Rose / 18x18", "RSE-18", 42.00),
        ("Charcoal / 20x20", "CHR-20", 48.00),
    ]),
    ("Ceramic Mug Set", "MUG", [
        ("White / 2-pack", "WHT-2", 28.00),
        ("Earth Tones / 4-pack", "ERT-4", 52.00),
        ("Speckled / 2-pack", "SPK-2", 32.00),
    ]),
    ("Cork Notebook", "NTB", [
        ("A5 / Lined", "A5-LND", 18.00),
        ("A5 / Dot Grid", "A5-DOT", 18.00),
        ("A4 / Lined", "A4-LND", 24.00),
    ]),
    ("Essential Oil Diffuser", "DIF", [
        ("Wood Grain / 300ml", "WGR-300", 42.00),
        ("White / 300ml", "WHT-300", 38.00),
        ("Wood Grain / 500ml", "WGR-500", 56.00),
    ]),
    ("Copper Desk Lamp", "LMP", [
        ("Brushed Copper", "BCP", 78.00),
        ("Matte Black", "MBK", 72.00),
        ("Polished Brass", "PBR", 85.00),
    ]),
    ("Handwoven Basket", "BSK", [
        ("Natural / Small", "NAT-S", 34.00),
        ("Natural / Large", "NAT-L", 52.00),
        ("Black / Small", "BLK-S", 36.00),
    ]),
    ("Recycled Glass Vase", "VSE", [
        ("Clear / 8 inch", "CLR-8", 28.00),
        ("Amber / 8 inch", "AMB-8", 32.00),
        ("Smoke / 12 inch", "SMK-12", 44.00),
    ]),
    ("Macrame Plant Hanger", "PLH", [
        ("Natural / Small", "NAT-S", 22.00),
        ("Natural / Large", "NAT-L", 32.00),
        ("Black / Small", "BLK-S", 24.00),
    ]),
    ("Wooden Cutting Board", "CUT", [
        ("Walnut / Medium", "WLN-M", 48.00),
        ("Walnut / Large", "WLN-L", 68.00),
        ("Maple / Medium", "MPL-M", 44.00),
    ]),
    ("Linen Apron", "APR", [
        ("Natural", "NAT", 38.00),
        ("Charcoal", "CHR", 38.00),
        ("Terracotta", "TRC", 38.00),
    ]),
    ("Beeswax Wrap Set", "BWX", [
        ("Floral / 3-pack", "FLR-3", 18.00),
        ("Solid / 3-pack", "SLD-3", 16.00),
        ("Mixed / 5-pack", "MIX-5", 28.00),
    ]),
    ("Turkish Cotton Towel", "TWL", [
        ("White / Bath", "WHT-BTH", 34.00),
        ("Gray / Bath", "GRY-BTH", 34.00),
        ("Striped / Bath", "STR-BTH", 38.00),
        ("White / Hand", "WHT-HND", 18.00),
    ]),
    ("Soy Wax Melts", "MLT", [
        ("Cinnamon / 6-pack", "CIN-6", 14.00),
        ("Fresh Linen / 6-pack", "LIN-6", 14.00),
        ("Citrus / 6-pack", "CIT-6", 14.00),
    ]),
    ("Reusable Produce Bags", "RPB", [
        ("Mesh / 5-pack", "MSH-5", 16.00),
        ("Cotton / 5-pack", "CTN-5", 18.00),
        ("Mixed / 8-pack", "MIX-8", 24.00),
    ]),
    ("Leather Journal", "JRN", [
        ("Brown / A5", "BRN-A5", 42.00),
        ("Black / A5", "BLK-A5", 42.00),
        ("Cognac / A5", "CGN-A5", 46.00),
    ]),
    ("Himalayan Salt Lamp", "SLT", [
        ("Small (5-7 lbs)", "SM", 24.00),
        ("Medium (8-11 lbs)", "MD", 36.00),
        ("Large (12-15 lbs)", "LG", 52.00),
    ]),
    ("Stoneware Dinner Set", "DNR", [
        ("White / 4-piece", "WHT-4", 68.00),
        ("Speckled / 4-piece", "SPK-4", 74.00),
        ("Blue / 4-piece", "BLU-4", 74.00),
    ]),
    ("Cotton Rope Coasters", "CST", [
        ("Natural / 4-pack", "NAT-4", 14.00),
        ("Mixed / 6-pack", "MIX-6", 18.00),
    ]),
    ("Wall Art Print", "ART", [
        ("Abstract / 8x10", "ABS-810", 28.00),
        ("Abstract / 16x20", "ABS-1620", 48.00),
        ("Botanical / 8x10", "BOT-810", 28.00),
        ("Botanical / 16x20", "BOT-1620", 48.00),
        ("Landscape / 16x20", "LND-1620", 52.00),
    ]),
    ("Copper Measuring Cups", "MSR", [
        ("4-piece Set", "4PC", 38.00),
        ("7-piece Set", "7PC", 56.00),
    ]),
    ("French Press Coffee Maker", "FPC", [
        ("Glass / 34oz", "GLS-34", 34.00),
        ("Stainless / 34oz", "STL-34", 48.00),
    ]),
    ("Wool Throw Blanket", "BLN", [
        ("Ivory / 50x60", "IVR-5060", 78.00),
        ("Gray / 50x60", "GRY-5060", 78.00),
        ("Plaid / 50x60", "PLD-5060", 85.00),
    ]),
    ("Brass Picture Frame", "FRM", [
        ("Gold / 4x6", "GLD-46", 22.00),
        ("Gold / 5x7", "GLD-57", 28.00),
        ("Gold / 8x10", "GLD-810", 36.00),
        ("Antique / 5x7", "ANT-57", 32.00),
    ]),
    ("Ceramic Soap Dispenser", "SPD", [
        ("White / 12oz", "WHT-12", 24.00),
        ("Black / 12oz", "BLK-12", 24.00),
        ("Terracotta / 12oz", "TRC-12", 26.00),
    ]),
    ("Bamboo Utensil Set", "UTN", [
        ("5-piece", "5PC", 22.00),
        ("8-piece", "8PC", 32.00),
    ]),
    ("Scented Room Spray", "SPR", [
        ("Sea Breeze / 4oz", "SEA-4", 16.00),
        ("Cedar / 4oz", "CDR-4", 16.00),
        ("Rose / 4oz", "RSE-4", 16.00),
    ]),
    ("Woven Storage Bin", "BIN", [
        ("Natural / Small", "NAT-S", 26.00),
        ("Natural / Medium", "NAT-M", 34.00),
        ("Natural / Large", "NAT-L", 44.00),
        ("Gray / Medium", "GRY-M", 36.00),
    ]),
    ("Cocktail Shaker Set", "CKT", [
        ("Stainless / 5-piece", "STL-5", 42.00),
        ("Copper / 5-piece", "CPR-5", 52.00),
    ]),
    ("Linen Table Runner", "TBR", [
        ("Natural / 72 inch", "NAT-72", 34.00),
        ("Charcoal / 72 inch", "CHR-72", 34.00),
        ("Sage / 90 inch", "SGE-90", 42.00),
    ]),
    ("Porcelain Ring Dish", "RNG", [
        ("White / Gold Trim", "WHT-GLD", 16.00),
        ("Marble Pattern", "MRB", 18.00),
    ]),
    ("Electric Kettle", "KTL", [
        ("Stainless / 1.0L", "STL-10", 52.00),
        ("Stainless / 1.7L", "STL-17", 62.00),
        ("Matte Black / 1.0L", "BLK-10", 58.00),
    ]),
    ("Desk Organizer", "DSK", [
        ("Bamboo / 3-tier", "BMB-3", 38.00),
        ("Walnut / 2-tier", "WLN-2", 44.00),
    ]),
    ("Natural Lip Balm Set", "LIP", [
        ("Variety / 4-pack", "VAR-4", 12.00),
        ("Vanilla / 3-pack", "VAN-3", 10.00),
    ]),
    ("Cast Iron Skillet", "SKL", [
        ("10 inch", "10IN", 38.00),
        ("12 inch", "12IN", 48.00),
    ]),
    ("Hanging Planter", "HNG", [
        ("Ceramic / White", "CRM-WHT", 28.00),
        ("Ceramic / Black", "CRM-BLK", 28.00),
        ("Terracotta / Natural", "TRC-NAT", 24.00),
    ]),
    ("Cocktail Napkins", "NAP", [
        ("Linen / White / 12-pack", "LIN-WHT-12", 22.00),
        ("Linen / Mixed / 12-pack", "LIN-MIX-12", 26.00),
    ]),
    ("Pour Over Coffee Dripper", "POC", [
        ("Ceramic / White", "CRM-WHT", 26.00),
        ("Copper", "CPR", 34.00),
    ]),
]

DISCOUNT_CODES = [
    ("SAVE10", 0.10),
    ("WELCOME15", 0.15),
    ("HOLIDAY20", 0.20),
    ("VIP25", 0.25),
    ("FLASH30", 0.30),
]

REFUND_REASONS = [
    "Customer request",
    "Defective item",
    "Wrong size",
    "Not as described",
    "Arrived damaged",
    "Changed mind",
    "Duplicate order",
    "Late delivery",
]


def _weighted_date(start: datetime, end: datetime) -> datetime:
    """Generate a date weighted towards recent months (upward revenue trend).
    More recent dates are more likely to be selected."""
    total_days = (end - start).days
    while True:
        # Triangular distribution: heavily weighted towards recent dates
        # This creates a natural upward trend in the revenue chart
        day_offset = int(random.triangular(0, total_days, total_days * 0.85))
        dt = start + timedelta(days=day_offset)
        # Weekends get slight boost
        if dt.weekday() >= 5 and random.random() < 0.6:
            return dt
        # Regular days: always accept (triangular already shapes the distribution)
        if random.random() < 0.8:
            return dt


def seed_demo_data(
    session: Session,
    num_orders: int = 1247,
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

    # 2. Generate products from catalog
    products = []
    catalog_entries = PRODUCT_CATALOG[:num_products] if len(PRODUCT_CATALOG) >= num_products else PRODUCT_CATALOG

    for title, base_sku, variants in catalog_entries:
        for variant_title, variant_suffix, price in variants:
            clean_sku = f"{base_sku}-{variant_suffix}"
            raw_sku = maybe_contaminate(clean_sku, rate=0.2)
            product = Product(
                id=uuid.uuid4(),
                store_id=store.id,
                shopify_id=str(uuid.uuid4()),
                title=title,
                sku=raw_sku,
                sku_cleaned=clean_sku,
                variant_title=variant_title,
                variant_sku=variant_suffix,
                price=Decimal(str(price)),
            )
            products.append(product)
    session.add_all(products)
    session.flush()

    # 3. Generate orders distributed across 6 months
    orders = []
    line_items_all = []
    now = datetime.now(timezone.utc)
    six_months_ago = now - timedelta(days=180)

    # Status distributions for impressive portfolio numbers:
    # ~95% fulfilled, ~3% unfulfilled, ~1% partial, ~1% refunded
    fulfillment_weights = (
        [FulfillmentStatus.fulfilled] * 95
        + [FulfillmentStatus.unfulfilled] * 3
        + [FulfillmentStatus.partial] * 1
        + [None] * 1  # refunded orders → ~3% refund rate
    )
    # ~97% paid, ~2% partially_refunded, ~1% refunded (via None above)
    financial_for_fulfilled = (
        [FinancialStatus.paid] * 97
        + [FinancialStatus.partially_refunded] * 3
    )

    # Generate 150 realistic customers
    customers = []
    for _ in range(150):
        customers.append({
            "name": fake.name(),
            "email": fake.email(),
        })

    for i in range(num_orders):
        order_date = _weighted_date(six_months_ago, now)

        ful_status = random.choice(fulfillment_weights)
        if ful_status is None:
            # Refunded order
            fin_status = FinancialStatus.refunded
            ful_status = FulfillmentStatus.fulfilled
        else:
            fin_status = random.choice(financial_for_fulfilled)

        customer = random.choice(customers)

        order = Order(
            id=uuid.uuid4(),
            store_id=store.id,
            shopify_id=str(uuid.uuid4()),
            order_number=f"{1000 + i + 1}",
            customer_name=customer["name"],
            customer_email=customer["email"],
            status="open",
            financial_status=fin_status,
            fulfillment_status=ful_status,
            total_price=Decimal("0"),
            order_created_at=order_date,
            order_updated_at=order_date + timedelta(hours=random.randint(1, 72)),
        )
        orders.append(order)

    session.add_all(orders)
    session.flush()

    # 4. Generate line items (avg ~3.1 items per order)
    for order in orders:
        # Weighted: more likely to have 2-3 items than 5
        num_items = random.choices([1, 2, 3, 4, 5], weights=[15, 30, 30, 15, 10])[0]
        order_total = Decimal("0")
        used_products = set()

        # Decide if this order gets a discount (25% chance)
        has_discount = random.random() < 0.25
        discount_code, discount_rate = random.choice(DISCOUNT_CODES) if has_discount else (None, 0)

        for _ in range(num_items):
            # Avoid duplicate products in same order
            product = random.choice(products)
            attempts = 0
            while product.id in used_products and attempts < 10:
                product = random.choice(products)
                attempts += 1
            used_products.add(product.id)

            qty = random.choices([1, 2, 3, 4], weights=[50, 30, 15, 5])[0]
            unit_price = product.price or Decimal("10.00")
            total = unit_price * qty
            discount = Decimal(str(round(float(total) * discount_rate, 2))) if has_discount else Decimal("0")
            tax = Decimal(str(round(float(total - discount) * 0.08, 2)))

            # Refund amount for refunded orders
            refund = Decimal("0")
            if order.financial_status == FinancialStatus.refunded:
                refund = total - discount
            elif order.financial_status == FinancialStatus.partially_refunded and random.random() < 0.4:
                refund = Decimal(str(round(float(total - discount) * random.uniform(0.3, 0.8), 2)))

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
                refund_amount=refund,
            )
            line_items_all.append(li)
            order_total += total - discount + tax

        order.total_price = order_total

    session.add_all(line_items_all)
    session.flush()

    # 5. Generate payouts (bi-weekly schedule)
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
        # Bi-weekly payouts: 15th and last day of month
        for payout_day in [15, 28]:
            payout = Payout(
                id=uuid.uuid4(),
                store_id=store.id,
                shopify_payout_id=str(uuid.uuid4()),
                date=date(year, month, payout_day),
                amount=Decimal("0"),
                status=PayoutStatus.paid,
            )
            payouts.append(payout)

    session.add_all(payouts)
    session.flush()

    # Map line items to payouts (by order date → closest payout date)
    payout_map = {}
    for p in payouts:
        key = f"{p.date.year}-{p.date.month:02d}-{'A' if p.date.day <= 15 else 'B'}"
        payout_map[key] = p

    for li in line_items_all:
        order = next(o for o in orders if o.id == li.order_id)
        if not order.order_created_at:
            continue
        dt = order.order_created_at
        half = "A" if dt.day <= 15 else "B"
        key = f"{dt.year}-{dt.month:02d}-{half}"
        payout = payout_map.get(key)
        if not payout:
            # Fallback to any payout in same month
            alt_key = f"{dt.year}-{dt.month:02d}-{'B' if half == 'A' else 'A'}"
            payout = payout_map.get(alt_key)
        if not payout:
            continue

        gross = (li.unit_price or Decimal("0")) * li.quantity - (li.discount_amount or Decimal("0")) + (li.tax_amount or Decimal("0"))
        # Realistic Shopify fee: 2.9% + $0.30 per transaction
        fee_percent = gross * Decimal("0.029")
        fee_flat = Decimal("0.30")
        fee = round(fee_percent + fee_flat, 2)
        net = gross - fee - (li.refund_amount or Decimal("0"))

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

    # 6. Generate adjustments (~10% refunds, ~2% chargebacks)
    adjustments = []
    refund_orders = random.sample(orders, min(len(orders), int(num_orders * 0.10)))
    for order in refund_orders:
        adj = Adjustment(
            id=uuid.uuid4(),
            store_id=store.id,
            order_id=order.id,
            type=AdjustmentType.refund,
            amount=Decimal(str(round(float(order.total_price or 0) * random.uniform(0.1, 1.0), 2))),
            reason=random.choice(REFUND_REASONS),
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
