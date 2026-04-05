# ops-dashboard TODO

_Last updated: 2026-03-30_

## Immediate next work
- finish Historical Backtest homepage as the true load control center
  - validate that instrument selection table shows start/end date, granularity, and row count correctly in the running UI
  - continue polishing strategy selection table with stronger aggregated metrics
  - keep the final load card as the single execution entry point
- keep refining Trading Performance loading around the Load-button boundary
  - validate the new selected-family equity-curve load path and confirm page navigation does not re-fetch curves within one Load
  - continue migrating family variant dashboard artifacts toward split outputs (`summary.json`, `composite.json`, `variants/<variant>.json`) and remove dependence on compatibility monoliths once the new flow is proven
  - change family variant retention policy to `all tested summary + top 3 per cluster full artifact` so large non-winning variants do not keep full curve/ledger payloads forever
  - consider splitting family equity curves into physically separate on-disk payload files later if selected-family filtering over the monolithic source remains too slow
  - continue validating which caches should be retained vs trimmed when scope changes
- continue filling Market State Analysis with real content
  - validate the first real State Explanation path now that dedicated payload + K-line main chart + parameter subcharts are wired
  - improve State Explanation window selection / representative-window logic once the first real charts are verified
  - add real transition content to State Transitions
- keep dashboard docs/meta-work continuously updated as implementation changes

## Known issues to revisit
- local dashboard server process/hot-reload stability can leave the browser on stale UI until the process is restarted
- Historical Backtest UI has been changing quickly and should be revalidated against the running local server after major edits
- some intended aggregated selection-help metrics still require better backend support or clearer definitions
