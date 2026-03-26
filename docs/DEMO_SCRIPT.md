# Demo Video Script

**Format**: Loom or screen recording, 2:30–3:00 minutes
**Resolution**: 1920x1080, browser in full screen
**Preparation**: App running in Demo Mode with seeded data, dark theme if available

---

## [0:00–0:10] Dashboard Overview

> "This is Shopify Order Manager — a dashboard that gives Shopify sellers the financial visibility they actually need."

**On screen**: Dashboard page with all summary cards and charts visible. Mouse moves slowly across the summary cards.

---

## [0:10–0:25] Summary Cards and Charts

> "At a glance: 1,247 orders, $89K in revenue, 3.2% refund rate. The revenue chart shows the last 30 days with a clear upward trend. The pie chart breaks down order statuses — 68% fulfilled, 22% still unfulfilled."

**On screen**: Hover over summary cards briefly to show tooltips. Point cursor at the revenue line chart's peak. Point at the pie chart segments.

---

## [0:25–0:45] Orders Table

> "Here's the full orders table. I can filter by status — let's look at partially fulfilled orders. And search works by order number, customer name, or SKU."

**On screen**:
1. Click "Orders" in sidebar
2. Table loads with 1,247 orders
3. Click status filter → select "Partial"
4. Table filters to ~87 results
5. Type "leather" in search bar to show product search
6. Clear filters

---

## [0:45–1:05] Order Detail

> "Clicking into an order shows every line item with variant details, pricing, discounts, and fulfillment status. Here we see three items — Classic Leather Wallet in Brown Large, Canvas Tote Bag, and a Phone Case. Notice the discount code SAVE10 applied to this order and the per-item tax calculation."

**On screen**:
1. Click on order #1089
2. Detail view opens showing line items table
3. Hover over the discount line to highlight it
4. Scroll to show order summary with subtotal, discount, tax, shipping, total

---

## [1:05–1:30] SKU Cleaning

> "This is one of the most unique features. See these red badges? They mean the original SKU contained hidden Unicode characters — zero-width spaces, soft hyphens — invisible to the eye but they break Excel VLOOKUPs and inventory matching. The system automatically strips them."

**On screen**:
1. Navigate to Line Items view (or toggle SKU cleaning display)
2. Show table with Raw SKU and Cleaned SKU columns
3. Hover over a red "Unicode chars detected" badge to show tooltip
4. Point to the summary: "12 of 147 SKUs contained hidden characters — all cleaned automatically"

> "12 out of 147 SKUs had this problem, all fixed automatically. The tooltip shows exactly which Unicode code points were found."

---

## [1:30–1:55] Payout Breakdown

> "Here's the per-item payout breakdown — something Shopify doesn't show you. For each product: gross revenue, minus Shopify's 2.9% plus 30 cents fee, minus discounts, minus refunds, equals net payout. This is critical for understanding actual profitability per product."

**On screen**:
1. Click "Payouts" in sidebar
2. Select "December 2024" from period dropdown
3. Show the payout table with columns: Product, SKU, Qty, Gross, Fees, Discounts, Refunds, Net
4. Scroll to the summary row showing total net payout
5. Point to the callout box explaining the fee calculation

---

## [1:55–2:15] Google Sheets Export

> "One click exports everything to Google Sheets — three tabs: Orders, Line Items, Payouts. Batch update, no duplicates. It synced 1,247 orders and 3,891 line items in one call."

**On screen**:
1. Click export button or navigate to Export panel
2. Click "Sync to Google Sheets"
3. Show loading state → success toast notification
4. (Optional: switch to a browser tab showing the actual Google Sheet with data, three tabs visible)

---

## [2:15–2:35] Demo/Live Toggle and Store Connection

> "The system supports multiple Shopify stores. Right now we're looking at Demo Mode with sample data. In production, the seller connects their store via OAuth — authorizes once, and sync runs automatically in the background via Celery workers."

**On screen**:
1. Point to Demo Mode banner
2. Navigate to Settings page
3. Show store connection section with OAuth and Custom App Token options
4. Show the mode toggle: Demo / Live
5. Brief hover over API scopes list

---

## [2:35–2:50] Closing

> "Built with FastAPI, React, and the official Shopify API. Full Docker Compose deployment — one command to start everything. Handles 10,000+ orders, with incremental sync so it stays fast even as the store grows."

**On screen**: Quick flash of the terminal showing `docker-compose up` with services starting. Return to dashboard for final shot.

---

## Recording Tips

- **Pace**: Speak slowly and clearly. Pause briefly between sections.
- **Mouse movement**: Move the cursor deliberately to guide the viewer's eye. Don't click rapidly.
- **Browser**: Use Chrome/Firefox in full screen. Close all other tabs. Hide bookmarks bar.
- **Data**: Make sure Demo Mode is freshly seeded so numbers are consistent.
- **No audio dead space**: If waiting for a page to load, narrate what's happening.
- **End frame**: Pause on the dashboard for 2-3 seconds at the end so the viewer sees the full interface.
