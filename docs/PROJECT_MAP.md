# trading-dashboard Project Map

## 1. Core files

1. `index.html` — main front-end UI, layout, charts, state management, and interactions
2. `server.py` — local HTTP server and payload adapters for dashboard endpoints
3. `vendor/lightweight-charts.standalone.production.js` — charting library bundle
4. `run_daemon.sh` — local helper for running the server/daemon flow

## 2. Docs

1. `docs/PROJECT_STATUS.md` — current status and active refactor notes
2. `docs/PROJECT_MAP.md` — this file
3. `docs/DASHBOARD_DESIGN.md` — layout and table/chart interaction rules
4. `docs/DATA_CONTRACTS.md` — important endpoint and payload notes
5. `docs/WORKSTREAM_DECISIONS.md` — durable module/product decisions

## 3. Main UI module structure

1. `welcome-home`
2. `historical-backtest-home`
3. `current-trading-overview` → Trading Performance
4. `trading-strategy-families` → Strategy Variants
5. `trading-composite-routing` → Composite / Routing
6. `trading-trade-ledger` → Trade Ledger
7. `market-overview` → Market State Analysis overview
8. `market-state-separation`
9. `market-state-transitions`
10. `market-state-explanation`

## 4. Data source direction

The dashboard reads visualization inputs from trading-system artifacts produced outside this repo.
This repo should stay dashboard-only.

Current important payload families:
1. family backtest summary
2. family equity curves
3. family trade ledger
4. composite backtest summary
5. cluster overview
6. family variant dashboard payloads
7. dictionary payload
8. historical backtest catalog payload

### 4.1 Control-page specific payloads
1. instruments catalog
2. historical backtest catalog
3. family variant catalog

### 4.2 Trading Performance specific payloads
1. family backtest summary
2. family equity curves
3. family trade ledger
4. composite backtest summary
5. selected family variant dashboard payloads

### 4.3 Market State Analysis specific payloads
1. cluster overview
2. dictionary
3. later: state explanation series payload(s)

## 5. Key current caches / stateful front-end layers

1. selected instrument
2. selected strategies
3. family variant dashboard cache keyed by instrument + family
4. state sample instrument for State Explanation
5. workspace variant selection/sort state
6. composite selector / switch filter state

## 6. Structural rule

Keep dashboard meta-work in `docs/` continuously during active development.
