# trading-dashboard Workstream Decisions

_Last updated: 2026-04-05_

## 1. Module boundary decisions

### 1.1 Welcome
1. the site should not drop directly into Trading Performance
2. a top-level Welcome page exists so module choice comes first

### 1.2 Historical Backtest
1. Historical Backtest is the control-center module homepage for the first major workflow
2. it should handle:
   - instrument selection
   - strategy/family selection
   - artifact readiness/checklist
   - download access
   - load execution and progress
3. Trading Performance should not force a modal instrument choice on entry anymore

### 1.3 Trading Performance
1. this module is strictly about trading behavior, returns, routing outcomes, and trade-level results
2. it should avoid drifting into state-interpretation or parameter-research semantics
3. cluster-related content is allowed here only when it answers a trading question such as:
   - what trades best in this cluster?
   - what family/variant is best in this cluster?

### 1.4 Market State Analysis
1. this module is about state/cluster structure, state separation, state transitions, and explanation
2. it should stay largely instrument-anonymized
3. `State Explanation` is the one intentional exception where a controlled sample instrument can be used as a real-market projection layer

## 2. Loading / scope decisions

1. Historical Backtest should let the user choose either all strategies or a subset before loading Trading Performance
2. strategy selection should be a multi-select table, not a single dropdown
3. instrument selection should be a single-select table, not a blind dropdown
4. instrument table columns should prioritize selection-help fields such as start date, end date, granularity, and row count rather than implementation-only fields like raw derived filenames
5. large payload loading should be explicitly user-triggered via the load card at the bottom of Historical Backtest
6. the page should show progress only after load starts
7. current progress UI should appear below the load button, not above it
8. current selection summary should live in the same final execution card instead of floating as a separate top card

## 3. Table behavior decisions

1. all tables must support sorting
2. large tables should also support search/filtering
3. this rule applies even if the current dataset is small or only one row is visible today

## 4. Dictionary / explanation decisions

1. avoid one-dictionary-key-per-variant sprawl
2. prefer mother-key explanations, for example:
   - `moving_average_variant_code`
   - `donchian_breakout_variant_code`
   - `bollinger_reversion_variant_code`
   - `parameter_region_code`
3. concrete labels should point to the right mother key instead of reusing a semantically wrong generic key

## 5. Current implementation caveats

1. hot-reload/server stability has intermittently caused the browser to show stale UI until the local server process is restarted
2. Historical Backtest controls, progress, and selective loading are mid-refactor and should be revalidated against the running local server after significant edits
3. large trading payloads are still heavy enough that progress/status communication remains important even after scope narrowing
4. the current incremental cache strategy is intentionally conservative: still-selected families may be reused, but deselected families should be cleared instead of retained indefinitely
