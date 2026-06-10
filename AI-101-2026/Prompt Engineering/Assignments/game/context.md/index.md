# The Allocator: Game System Configuration & Mapping Data

This file acts as the explicit state, logic mapping, and evaluation framework for the core game loop.

---

## 1. Investor Types Detailing

### I. The Income Seeker

- **Investment Thesis:** Requires consistent, predictable, maximized annualized cash flows to fulfill structural personal obligations or beat immediate inflation. This investor type wants cash actively distributed _out_ of the business into their pocket.
- **Focus Point:** Sustained operational payout velocity.
- **Clear Trap:** **The Yield Trap**. Chasing an astronomical static Dividend Yield that is caused by a crashing stock price or a non-recurring, one-off capital gain from an asset sale rather than recurring core operations.

### II. The Value Compounding Purist

- **Investment Thesis:** Inspired by traditional economic moats (Buffett/Munger style). Seeks to acquire businesses that demonstrate unparalleled operational efficiency by deploying capital into highly lucrative returns year after year.
- **Focus Point:** Capital utilization efficiency.
- **Clear Trap:** **The Equity Bloat**. Accepting a massive company with impressive absolute profit figures but a crashing internal rate of return, signaling that retained earnings are being wasted on low-yielding expansions.

### III. The Deep Value Hunter

- **Investment Thesis:** Searches for unloved, ignored, or temporarily distressed businesses selling significantly below their intrinsic, liquidable book value where minor structural operational adjustments unlock massive upside.
- **Focus Point:** Deep discount on tangible asset value coupled with baseline survival capacity.
- **Clear Trap:** **The Value Trap / Impending Insolvency**. Buying a cheap Price-to-Book stock that is running completely dry of operational liquidity, causing it to default or go bankrupt before the turnaround story can unfold.

### IV. The High-Growth Aggressive Allocator

- **Investment Thesis:** Dislikes dividends due to tax inefficiencies. Demands that corporate management retain 100% of profits and continuously plow them back into expanding factory capacities, technological scale, or industrial market acquisitions.
- **Focus Point:** Capacity scale converting cleanly into explosive top-line and bottom-line output.
- **Clear Trap:** **The Cash Burn (Fake Scale)**. Spectacular top-line revenue and market share gains masking negative operating cash flows and catastrophic drop-offs in asset utilization velocity.

### V. The Defensive / Conservative Guardian

- **Investment Thesis:** A strict capital preservation profile built to operate safely during intense macroeconomic volatility, inflation, or geopolitical uncertainty. They want bulletproof financial shields over expansion.
- **Focus Point:** Uncompromised short-term solvency and non-existent debt weight.
- **Clear Trap:** **The Cash Drag Inefficiency**. Exceptional survival metrics that hide completely stagnant growth, where excess unutilized cash sitting idle on the balance sheet is silently eroded by inflation.

---

## 2. Core Ratios Framework

| Financial Ratio                       | Core Signification / Analytical Meaning                                                                                       | Primary Target Investor  |
| :------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------- | :----------------------- |
| **Dividend Yield (DY)**               | Immediate annualized cash-on-cash return generated directly by holding the business assets.                                   | **Income Seeker**        |
| **Dividend Payout Ratio (DPR)**       | The exact percentage of net earnings returned to shareholders versus what is retained for internal business reinvestment.     | **Income Seeker**        |
| **Free Cash Flow (FCF) Yield**        | Validates whether distributions are sustained by genuine operational surplus cash or engineered through debt.                 | **Income Seeker**        |
| **Return on Equity (ROE)**            | Measures how efficiently management utilizes the owners' capital to generate bottom-line corporate profits.                   | **Compounding Purist**   |
| **Return on Capital Employed (ROCE)** | Examines efficiency across the entire capital base (including debt), highlighting asset productivity independent of leverage. | **Compounding Purist**   |
| **Price to Earnings (P/E)**           | Measures market valuation relative to earnings; gauges if the core compounding engine is fairly priced.                       | **Compounding Purist**   |
| **Price to Book (P/B)**               | Signals that the company is trading at a direct discount to its tangible liquidation asset value.                             | **Deep Value Hunter**    |
| **Interest Coverage Ratio (ICR)**     | Identifies how many times over a company can comfortably pay its debt interest burden from current operating profits.         | **Deep Value Hunter**    |
| **EPS Growth CAGR**                   | Quantifies bottom-line growth acceleration over time, proving the capacity expansions are working.                            | **Aggressive Allocator** |
| **Retention Ratio**                   | Reflects the percentage of earnings kept in the business to fund aggressive capacity scale.                                   | **Aggressive Allocator** |
| **Quick Ratio**                       | Validates the immediate capacity to clear operational liabilities using highly liquid assets (minus inventory).               | **Defensive Guardian**   |
| **Debt-to-Equity (D/E)**              | Quantifies capital structure leverage; ensures the business structure is virtually unburdened by debt.                        | **Defensive Guardian**   |

---

## 3. Master Investor to Sector & Ratio Mapping Matrix

| Investor Archetype          | Primary Target PSX Sectors                     | Primary Metrics                              | Secondary Validation | Focus Point / Goal   | Clear Trap Heading   |
| :-------------------------- | :--------------------------------------------- | :------------------------------------------- | :------------------- | :------------------- | :------------------- |
| **1. Income Seeker**        | Fertilizer, Commercial Banks                   | Dividend Yield, Dividend Payout Ratio        | Free Cash Flow Yield | Cash Payout Velocity | **The Yield Trap**   |
| **2. Compounding Purist**   | Fertilizer, Consumer Discretionary             | Return on Equity, Return on Capital Employed | Price to Earnings    | Capital Efficiency   | **The Equity Bloat** |
| **3. Deep Value Hunter**    | Battered Cyclicals, Distressed Cement          | Price to Book, Interest Coverage Ratio       | Debt-to-Equity       | Asset Discount       | **The Value Trap**   |
| **4. Aggressive Allocator** | Technology, Expanding Cement                   | EPS Growth CAGR, Retention Ratio             | Asset Turnover       | Capacity Scale       | **The Cash Burn**    |
| **5. Defensive Guardian**   | Oil & Gas Exploration, Multinational Bluechips | Quick Ratio, Debt-to-Equity                  | Current Ratio        | Solvency Shield      | **The Cash Drag**    |
