# trading-dashboard TODO

_Last updated: 2026-04-05_

## Repository direction

- [x] establish this repo as the dashboard-only downstream repository for the trading system
- [ ] keep repo docs aligned with the dashboard-only boundary as implementation evolves

## Structure and runtime

- [ ] keep `index.html`, `server.py`, `vendor/`, `data/metric-dictionary/`, and `docs/` aligned with the current dashboard module structure
- [ ] revalidate local dashboard server behavior after major UI/server edits
- [ ] keep runtime invocation/documentation accurate for this server environment

## Workflow and page patterns

### Historical Backtest
- [ ] finish Historical Backtest as the true load-control center
- [ ] validate that the instrument selection table shows start/end date, granularity, and row count correctly in the running UI
- [ ] continue polishing the strategy selection table with stronger aggregated metrics
- [ ] keep the final load card as the single execution entry point
- [ ] keep artifact checklist visibility and pre-load workflow aligned with the documented page pattern

### Trading Performance
- [ ] keep refining Trading Performance loading around the Load-button boundary
- [ ] validate the selected-family equity-curve load path and confirm page navigation does not re-fetch curves within one Load
- [ ] continue validating which caches should be retained vs trimmed when scope changes
- [ ] preserve the module boundary so Trading Performance stays focused on trading behavior, returns, routing, and trade-level results

### Market State Analysis
- [ ] continue filling Market State Analysis with real content
- [ ] validate the first real State Explanation path now that dedicated payload + K-line main chart + parameter subcharts are wired
- [ ] improve State Explanation window selection / representative-window logic once the first real charts are verified
- [ ] add real transition content to State Transitions

## Data contracts and payload shaping

- [ ] continue migrating family variant dashboard artifacts toward split outputs (`summary.json`, `composite.json`, `variants/<variant>.json`) and remove dependence on compatibility monoliths once the new flow is proven
- [ ] change family-variant retention policy to `all tested summary + top 3 per cluster full artifact` so large non-winning variants do not keep full curve/ledger payloads forever
- [ ] consider splitting family equity curves into physically separate on-disk payload files later if selected-family filtering over the monolithic source remains too slow
- [ ] keep dashboard endpoint expectations aligned with the documented data contracts
- [ ] keep dictionary/display metadata aligned with the UI fields that depend on them

## Durable decisions to preserve

- [ ] keep Welcome as the top-level module entry instead of dropping directly into Trading Performance
- [ ] keep Historical Backtest as the control-center module homepage
- [ ] keep instrument selection as a single-select table
- [ ] keep strategy selection as a multi-select table
- [ ] keep progress hidden until load actually starts
- [ ] keep Market State Analysis separate from Trading Performance except where explicitly allowed
- [ ] keep mother-key dictionary explanations preferred over one-key-per-variant sprawl

## Meta-work and doc maintenance

- [ ] keep dashboard docs/meta-work continuously updated as implementation changes
- [ ] update docs whenever module structure, workflow, data contracts, loading behavior, or dictionary rules change
- [ ] use `docs/06-metawork-checklist.md` during active dashboard changes instead of deferring doc updates until later

## Known issues to revisit

- [ ] local dashboard server process/hot-reload stability can leave the browser on stale UI until the process is restarted
- [ ] Historical Backtest UI has been changing quickly and should be revalidated against the running local server after major edits
- [ ] some intended aggregated selection-help metrics still require better backend support or clearer definitions
