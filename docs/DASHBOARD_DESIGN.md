# Dashboard Design

## 1. Core page pattern

Historical/research pages should converge on a repeatable structure, but module homepages are allowed to act as control centers rather than chart pages.

Two main patterns now exist.

### 1.1 Control-center page pattern
Used by `Historical Backtest`.

1. selection tables (instrument / strategy)
2. artifact checklist and file visibility
3. execution/load card with progress

### 1.2 Analysis page pattern
Used by Trading Performance / Composite / Routing / state analysis subpages.

1. summary table or summary cards
2. chart
3. chart-scoped large table

This analysis-page pattern remains the reference model for composite / routing views and family-variant detail pages.

## 2. Table rules

Global rule:
1. all tables must support sorting
2. even tables that currently render only one or a few rows should still have sorting configured from the start
3. small tables may omit search if compact enough
4. large tables should support:
   - sorting
   - search
   - filters
   - reset filters
   - export current view as CSV

For chart-mounted large tables, the effective result set should be:

`visible chart range ∩ table filters ∩ search ∩ current sort view`

Export must export exactly that current result.

## 3. Historical Backtest control center

Historical Backtest should be the user-facing load control center for Trading Performance.

Current rules:
1. do not force instrument selection by opening a modal when the user enters Trading Performance
2. the user should select instrument and strategy scope on the Historical Backtest homepage first
3. instrument selection should use a single-select table, not a blind dropdown
4. strategy selection should use a multi-select table with checkbox first column
5. artifact checklist should expose file status, size, line counts when meaningful, and download actions
6. the final execution card should contain the current selection summary, the load button, and any progress UI
7. progress UI should stay hidden until the user actually starts loading

## 4. Composite / Routing

Composite pages should use:
1. a clean main equity chart
2. a routing strip synced to current visible range
3. a chart-scoped switch table underneath

Routing/switch explanations should be cluster-first rather than based on manual market-state labels.

Preferred switch-table fields:
1. switch time
2. from
3. to
4. cluster
5. equity
6. step delta

## 5. Market State Analysis boundary

1. Trading Performance is instrument-scoped and focused on returns, routing results, and what to trade.
2. Market State Analysis is state/cluster-scoped and focused on what the state is and how it should be interpreted.
3. State Explanation is the only place in the second module where a controlled sample instrument is intentionally allowed as a real-market projection layer.

## 6. Family detail pages

Each strategy family detail page should be generated from per-family artifacts rather than hard-coded variant lists in the front end.

Target layout:
1. **Variant Summary**
   - placed above the chart
   - every row has a checkbox
   - default state: Composite ON, all individual variants OFF
   - purpose: reduce initial chart load while allowing opt-in comparison
2. **Variant Curves chart**
   - `n + 1` lines
   - all variants from artifact
   - plus one composite line
3. **Composite Variant Switching**
   - chart-scoped large table using the same interaction model as Composite / Routing

## 7. Artifact-driven extension model

The front end should not require code changes whenever new variants are added.

Desired contract:
1. back-end runners emit structured family artifacts
2. front end reads whatever variants appear in those artifacts
3. adding new variants or new strategies should primarily be a data-pipeline task, not a UI rewrite

## 8. Current implementation note

Family-variant dashboard artifacts are currently generated outside this repo.
Current sample artifact families include:
1. `moving_average`
2. `donchian_breakout`
3. `bollinger_reversion`

These are still sample-size variant sets for faster iteration.

## 9. Data sync policy

For dashboard-facing work:
1. raw downloaded market data should stay outside this repo
2. oversized intermediate derived datasets should stay outside this repo
3. lightweight summaries, docs, and reviewable dashboard artifacts may be synced here when appropriate
4. large JSON payloads should be split into lighter endpoints/artifacts before syncing
