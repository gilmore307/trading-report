# trading-dashboard Data Contracts

## 1. Important endpoints

### 1.1 General / module control
1. `/data/instruments/catalog.json`
2. `/data/historical-backtest/catalog.json`
3. `/data/dictionary.json`

### 1.2 Trading Performance
1. `/data/family-backtest-summary.json`
2. `/data/family-equity-curves.jsonl?family=<family>&family=<family>...`
3. `/data/family-trade-ledger.jsonl`
4. `/data/composite-backtest-summary.json`
5. `/data/family-variant-dashboard/<family>.json`
6. `/data/family-variant-dashboard/catalog.json`

`/data/family-variant-dashboard/<family>.json` is the stable dashboard-read endpoint.

Server rule:
1. if split outputs exist under `<family>/summary.json`, `<family>/composite.json`, and `<family>/variants/*.json`, the server should aggregate from those files directly
2. the front end should not require a compatibility monolith in order to load a family dashboard
3. compatibility monoliths may still be served if a family has not yet been migrated

## 2. Family variant artifact workflow rule

Family variant dashboard artifacts should no longer be treated as one growing monolithic family blob by default.

Target on-disk structure for each family:
1. `data/intermediate/dashboard_payloads/family_variant_dashboard/<family>/summary.json`
2. `data/intermediate/dashboard_payloads/family_variant_dashboard/<family>/composite.json`
3. `data/intermediate/dashboard_payloads/family_variant_dashboard/<family>/variants/<variant_id>.json`

Workflow rule going forward:
1. new or regenerated family-variant artifacts should be emitted in this split directory structure
2. compatibility monoliths may exist temporarily during migration, but they are transitional outputs, not the target format
3. when artifacts get larger, prefer splitting one level deeper rather than growing a single JSON blob
4. dashboard loading should keep the Load button as the loading boundary, but payload organization should stay small-file / scope-bounded underneath that boundary

## 3. Preferred retained-data policy for family variants

The dashboard does not need full heavy artifacts for every tested variant forever.

Preferred retention model:
1. keep lightweight summary/evaluation records for all tested variants
2. keep full heavy artifacts locally only for the most useful subset, currently:
   - top 1 variant per cluster within each family
3. keep reserve/history records for top 10 variants per cluster in summary/history layers
4. treat the rest as archived summary/history-only variants

Family layer uses the same idea with smaller counts:
1. top 1 family per cluster = active
2. top 5 families per cluster = reserve
3. the rest = archived

### 3.1 `summary.json` should retain
1. `family`
2. `variant_count_total`
3. `variant_count_evaluated`
4. `variant_count_retained_full`
5. `retained_full_variant_ids`
6. `reserve_variant_ids`
7. `composite_summary`
8. `cluster_rankings`
9. `variant_summaries`

### 3.2 Each lightweight `variant_summaries` record should retain
1. `variant_id`
2. `family`
3. `tested`
4. `retained_full`
5. `active`
6. `deprecated`
7. `deprecated_reason`
8. overall metrics such as:
   - `total_return`
   - `max_drawdown`
   - `trade_count`
   - `win_rate`
9. per-cluster metrics such as:
   - `cluster_id`
   - `rank_in_cluster`
   - `avg_utility_1h`
   - `sample_count`
   - `trade_count`
   - `avg_trade_return`
   - `positive_rate`
   - `turnover_count`

### 3.3 `variants/<variant_id>.json` should exist only for retained full variants
These files may keep the heavy data required for deep inspection:
1. `summary`
2. `curve`
3. `ledger`

### 3.4 Heavy data that may be dropped for non-retained variants
1. full equity curve points
2. full trade ledger
3. signal-level records
4. trade-point / switching-point detail
5. other large chart-ready arrays not needed for catalog/ranking decisions

## 4. Market State Analysis
1. `/data/cluster-overview.json`
2. `/data/state-explanation.json?cluster_id=<id>&instrument=<instrument>&window=<recent|representative>`

## 5. Current front-end expectations

### 5.1 instruments catalog
Expected fields per instrument row:
1. `instrument`
2. `label`
3. `startTs`
4. `endTs`
5. `granularity`
6. `rowCount`

Current UI meaning:
1. `startTs` / `endTs` feed the Start Date / End Date columns in the Historical Backtest instrument-selection table
2. `granularity` feeds the time-scale selection-help column
3. `rowCount` gives the rough payload/data coverage scale for selection decisions

### 5.2 historical backtest catalog
Expected top-level fields:
1. `instrument`
2. `files`
3. `families`

File rows currently expose:
1. `key`
2. `label`
3. `path`
4. `filename`
5. `exists`
6. `kind`
7. `sizeBytes`
8. `lineCount`
9. `downloadPath`

Family rows currently expose:
1. `instrument`
2. `family`
3. `variant_count`
4. `path`
5. `sizeBytes`
6. `compositeFinalEquity`
7. `compositeMaxDrawdown`
8. `compositeCurvePoints`

Current UI use:
1. Historical Backtest instrument selection table uses the instruments catalog
2. Historical Backtest strategy selection table uses the family rows in the catalog
3. Artifact Checklist uses the file rows and download paths
4. the final load card uses the current selections plus stage-based load progress

### 5.3 cluster overview
The dashboard currently expects cluster rows to carry at least:
1. `cluster_id`
2. `row_count`
3. `best_region`
4. `best_avg_utility_1h`
5. `spread_best_minus_worst`
6. `best_family`
7. `best_family_avg_utility_1h`
8. `best_variant`
9. `best_variant_family`
10. `best_variant_avg_utility_1h`

## 6. Loading behavior note
1. Historical Backtest should be the user-controlled entry point for heavy Trading Performance loads
2. the front end now supports family-selection-constrained loads for Trading Performance
3. the current implementation has first-pass family dashboard reuse behavior for still-selected families, while deselected families are cleared from cache
4. instrument changes should be treated as a stronger boundary than family selection changes

## 7. Design note
1. Trading Performance is instrument-scoped
2. Market State Analysis is generally anonymized/state-centric, except State Explanation which is allowed to use a controlled sample instrument as a real-market projection layer
