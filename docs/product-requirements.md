# Stock App Product Requirements

## 1. Overview
- **Goal**: Consolidate all of a user's investment portfolios across multiple brokers in a single application.
- **Objectives**: Deliver accurate performance tracking (fees, dividends), automated dividend management, benchmarking, allocation analysis, return metrics (IRR/TTWRR/XIRR), and tax reporting.

## 2. Functional Scope

### 2.1 Portfolios and Accounts
- Support multiple portfolios per user with nested broker and cash sub-accounts.
- Allow quick switching between individual accounts and aggregated portfolio views.

### 2.2 Holdings and Transactions
- Persist buys, sells, fees, taxes, FX conversions, and corporate actions (splits, dividends, spin-offs).
- Store transaction and portfolio base currencies, including FX rates.
- Track cash events alongside asset trades.

### 2.3 Dividend Automation and Analytics
- Automatically ingest dividend payments and maintain a dividend calendar for upcoming distributions.
- Calculate Dividend Yield, Yield on Cost, and track withholding tax per ISIN/broker.
- Provide dividend ratings and "top dividend stocks" insights.

### 2.4 Performance and Metrics
- Compute IRR, XIRR, TTWRR, volatility, Sharpe ratio, beta, and P/E (when available).
- Offer multi-period analytics (YTD, 1/3/5 year, custom), including cash performance.

### 2.5 Benchmarking
- Compare portfolio performance against indices or custom baskets with "what-if" simulations using identical cash flows.

### 2.6 Allocation and Diversification
- Break down allocation by asset class, region, sector, and currency using heatmaps and charts.

### 2.7 Tax Reporting
- Present realized gains/losses (short vs. long term), dividends by country of origin, and unrealized gains for tax-loss harvesting.
- Export reports to CSV/PDF.

### 2.8 Data Imports
- Universal CSV import with configurable field mapping.
- Provide default mapping profiles for Interactive Brokers, Revolut, Freetrade, TradeStation Global, and Degiro.
- Allow manual transaction entry.

### 2.9 Events and Notifications
- Display upcoming corporate events (earnings, dividends, splits) via a customizable dashboard.
- Support email and PWA push notifications for dividend reminders, earnings, and threshold alerts.

## 3. Non-Functional Requirements
- **Performance**: Filtering data for portfolios with 50k+ transactions must respond within 200 ms.
- **Security**: Implement OAuth2 with WebAuthn, encrypt sensitive columns (AES-256-GCM), provide audit logging, RBAC (Owner, Member, Read-only), and IP allowlisting for admin.
- **Privacy**: No account scraping without explicit consent; disclose FX rates and pricing data sources.
- **Reliability**: Background jobs must be idempotent with exponential backoff retries and import checksums.

## 4. Data Model (Minimum)
- **User**: `id`, `email`, `auth_provider`, `2fa_enabled`, `created_at`
- **Portfolio**: `id`, `user_id`, `name`, `base_currency`, `benchmark_id?`
- **Account**: `id`, `portfolio_id`, `broker`, `account_name`, `type {broker|cash}`, `currency`
- **Asset**: `id`, `symbol`, `isin?`, `name`, `type {stock|etf|bond|crypto|fund|cash}`, `sector?`, `region?`, `currency`
- **Transaction**: `id`, `account_id`, `asset_id`, `type {BUY|SELL|DIVIDEND|FEE|TAX|SPLIT|FX}`, `qty`, `price`, `fee`, `tax`, `gross_amount`, `trade_currency`, `trade_time`, `fx_rate_to_portfolio_ccy`
- **Dividend**: `id`, `account_id`, `asset_id`, `ex_date`, `pay_date`, `gross`, `withholding_tax`, `net`, `currency`
- **Price**: `asset_id`, `date`, `close`, `currency`, `source`
- **Benchmark**: `id`, `symbol|custom_series_ref`, `name`, `currency`
- **ReportCache**: `portfolio_id`, `key`, `payload_json`, `computed_at`
- **AuditLog**: `id`, `user_id`, `entity`, `entity_id`, `action`, `before`, `after`, `ts`

> Transactions must model FX rates and fees at both transaction and account levels.

## 5. CSV Import and Mapping
- Universal CSV columns: `Account`, `Date`, `Type`, `Ticker/ISIN`, `Name`, `Qty`, `Price`, `Fee`, `Tax`, `Currency`, `GrossAmount`, `Notes`.
- Drag-and-drop field mapper with preset profiles for common brokers.
- Validation includes 100-row preview, checksum (`Σ qty*price + fees + taxes`), and duplicate detection using hash `{Account, Date, Ticker, Qty, Price}`.

## 6. Analytics and Calculations
- **Performance**: TTWRR, MWRR (IRR/XIRR), absolute and annualized net returns, multi-period insights with fees and dividends.
- **Benchmarking**: Cash-flow normalized comparisons, "what-if" projections, tracking error, beta.
- **Allocation**: Breakdown by class/region/sector/currency, top-N concentration, overweight warnings.
- **Dividends**: Cashflow calendar, yield on cost, rolling 12-month income, stability/growth scoring.
- **Risk**: Volatility, Sharpe ratio, max drawdown per portfolio and holding.
- **Tax**: Realized P/L (short/long), dividends by country, unrealized P/L for harvesting, CSV/PDF export.

## 7. User Interface
- Customizable dashboard widgets (performance, dividend/earnings calendar, allocation heatmaps, cashflow).
- Portfolio and account management with aggregation and filtering.
- Holdings view with detailed metrics, history, dividends, and cost basis.
- Transaction timeline with CRUD and bulk edits.
- Dividend views (received, planned, calendar).
- Reports for performance, taxes, and exports.
- Import screens with broker profiles and validation.
- Settings for currencies, benchmarks, roles, and integrations.

## 8. Integrations and Data Providers
- Modular market data providers for equities, ETFs, crypto; daily close fallback; FX rates from authoritative sources (e.g., ECB).
- Notifications via email and PWA push.
- REST/GraphQL APIs for CRUD and reporting with per-user API keys.

## 9. Technology Recommendations
- **Frontend**: React/Next.js with TypeScript, Zustand/Redux, React Query, PWA, Recharts for charts.
- **Backend**: Node.js (NestJS) or Python (FastAPI) with BullMQ or Celery for job queues.
- **Database**: PostgreSQL with partitioning (TimescaleDB for time series).
- **Compute**: Stateless worker services, Redis caching.
- **Infrastructure**: Docker, CI/CD, OpenAPI, and OpenTelemetry instrumentation.

## 10. Acceptance Criteria (Selected)
- CSV imports from supported brokers create transactions and compute TTWRR/IRR with <0.1% variance from checksum.
- Dividend calendar updates net cashflow and Yield on Cost after withholding tax changes.
- S&P 500 benchmark renders "what-if" curve with beta and tracking error.
- Tax reports output short/long gains and dividend origins with CSV/PDF export.
- Multi-currency dashboards respect portfolio base currency with dated FX transparency.
- Dashboard widgets can be toggled and reordered by users.

## 11. Test Data
- Seed script populates 2 portfolios, 3 accounts, 20 tickers (stocks/ETF/crypto), 2 years of price history, 1,000 transactions, and 150 dividends.
