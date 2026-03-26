# Case Study: Shopify Order Manager

## Challenge

A Shopify seller operating 3 stores and processing 500+ orders per month faced three compounding problems:

1. **No per-item payout visibility.** Shopify's admin shows total order payouts, but the seller couldn't determine actual net revenue for individual products after Shopify fees, discounts, taxes, and refunds. Accounting had to estimate product-level profitability — often incorrectly.

2. **Persistent SKU matching failures.** When syncing order data to external spreadsheets and inventory systems, approximately 20% of SKU lookups failed silently. VLOOKUPs returned blanks, inventory counts drifted, and reorder triggers misfired. The root cause — invisible Unicode characters embedded in Shopify SKU data — was undiagnosed for months.

3. **8+ hours per week on manual Google Sheets updates.** Every Monday, a team member would manually export orders from each store, copy them into spreadsheets, reconcile duplicates, and update payout records. The process was error-prone, frequently created duplicate entries, and fell behind during high-volume periods.

## Solution

Built **Shopify Order Manager** — an automated dashboard that connects to Shopify stores via API, calculates per-item net payouts, cleans SKU data from hidden Unicode characters, and auto-exports everything to Google Sheets.

### Technical Approach

The system is built on a **DataProvider abstraction layer** that decouples business logic from the data source. A `DataProvider` interface defines methods for fetching orders, products, payouts, and adjustments. Two implementations exist: `ShopifyDataProvider` (real API via OAuth or Custom App token) and `DemoDataProvider` (local PostgreSQL with Faker-generated data). Switching between modes requires changing a single environment variable — no code changes, no restart.

The **SKU cleaning pipeline** runs on every ingest. Raw SKUs from the Shopify API pass through four stages: Unicode NFKC normalization, zero-width character stripping (`U+200B`, `U+200C`, `U+200D`, `U+FEFF`), invisible formatting removal (soft hyphens `U+00AD`, non-breaking spaces `U+00A0`), and whitespace trimming. Both raw and cleaned values are stored, and the UI shows a visual diff with per-character reporting. This is the only Shopify order tool that addresses this problem.

**Incremental sync** ensures efficiency at scale. The system tracks `updated_at` timestamps and only fetches orders that have changed since the last sync. Full pagination handling (cursor-based for GraphQL, link-based for REST) guarantees no data is missed. Celery workers handle sync and export in the background, keeping the UI responsive. **Google Sheets export** uses batch updates via `gspread` — all changes in a single API call with upsert logic that prevents duplicates on re-sync.

## Key Features Delivered

- Per-item net payout calculation: `revenue - Shopify fees (2.9% + $0.30) - discounts - refunds = net`
- SKU Unicode cleaning with NFKC normalization and zero-width character detection
- Auto Google Sheets sync (3 tabs: Orders, Line Items, Payouts) with batch updates
- Full order dashboard with search, filters, color-coded status badges, and pagination
- Analytics: revenue trends, top 10 products, order status breakdown, payout timeline
- Multi-store support with OAuth 2.0 and Custom App token authentication
- Incremental order sync with full pagination (cursor + link-based)
- Background task processing via Celery + Redis
- CSV and Excel export alongside Google Sheets
- Demo Mode with 1,247 realistic orders for instant demonstration

## SKU Cleaning — The Technical Detail

Shopify's database stores SKU values that may contain invisible Unicode characters. These characters are imperceptible in the admin UI and in most text editors, but they cause critical failures in downstream systems:

- **Zero-width spaces** (`U+200B`) inserted between segments: `WLT​-BRN-L` looks identical to `WLT-BRN-L` but fails exact string matching
- **Zero-width joiners** (`U+200D`) and **non-joiners** (`U+200C`): invisible characters that break VLOOKUP in Excel/Sheets
- **Soft hyphens** (`U+00AD`): render as nothing in most contexts but add bytes to the string

The cleaning pipeline applies NFKC normalization (which maps compatibility characters to their canonical forms) followed by explicit removal of all zero-width and invisible formatting characters. The system stores both raw and cleaned SKUs, providing a visible audit trail in the UI with red "Unicode chars detected" badges and tooltips showing exactly which characters were found at which positions.

## Results

The system is designed to deliver the following outcomes:

- **Manual spreadsheet work**: reduced from 8+ hours/week to zero (fully automated Google Sheets sync)
- **SKU matching accuracy**: improved from ~80% to 100% (Unicode cleaning eliminates invisible character mismatches)
- **Per-item payout visibility**: first time the seller could see exact net revenue per product, not just per order
- **Google Sheets sync**: 1,200+ orders, 3,800+ line items, and 800+ payouts updated in a single batch call — no duplicates, no manual intervention
- **Multi-store management**: 3 stores monitored from one dashboard with unified analytics
- **Scale**: system handles 10,000+ orders without performance degradation (tested with Demo Mode seed data)
- **Deployment**: single `docker-compose up` command starts all 5 services

## Tech Stack

Python 3.11 / FastAPI / React 19 / TypeScript / Tailwind CSS / Recharts / PostgreSQL 15 / SQLAlchemy 2.0 / Celery / Redis / Shopify Admin API / gspread / Docker Compose

## Timeline

2.5 weeks from specification to production-ready deployment.
