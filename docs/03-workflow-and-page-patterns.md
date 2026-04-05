# 03 Workflow and Page Patterns

This document defines the user workflow, page patterns, and key current implementation state of `trading-dashboard`.

## Core page pattern

Historical/research pages should converge on a repeatable structure, but module homepages are allowed to act as control centers rather than chart pages.

Two main patterns now exist.

### Control-center page pattern
Used by `Historical Backtest`.

1. selection tables (instrument / strategy)
2. artifact checklist and file visibility
3. execution/load card with progress

### Analysis page pattern
Used by Trading Performance / Composite / Routing / state analysis subpages.

1. summary table or summary cards
2. chart
3. chart-scoped large table

This analysis-page pattern remains the reference model for composite / routing views and family-variant detail pages.

## Historical Backtest control center

Historical Backtest should be the user-facing load control center for Trading Performance.

Current rules:
- do not force instrument selection by opening a modal when the user enters Trading Performance
- the user should select instrument and strategy scope on the Historical Backtest homepage first
- instrument selection should use a single-select table, not a blind dropdown
- strategy selection should use a multi-select table with checkbox first column
- artifact checklist should expose file status, size, line counts when meaningful, and download actions
- the final execution card should contain the current selection summary, the load button, and any progress UI
- progress UI should stay hidden until the user actually starts loading

## Current implementation state

### Navigation / module structure
- Welcome page exists
- Historical Backtest module homepage exists
- Trading Performance exists under Historical Backtest
- Market State Analysis exists as a separate module area with child pages:
  - State Separation
  - State Transitions
  - State Explanation

### Trading Performance work
- Strategy Variants workspace exists as a unified cross-family page
- Composite / Routing supports selector-driven views
- Trading Performance now has a dedicated `Best Trading Choice by Cluster` block fed from formal cluster evaluation payloads
- cluster-family and cluster-variant best-choice data are now expected to come from formal backend evaluation payloads rather than front-end approximations
- MA variant-id mismatch handling was added in the front end so MA variant curves can render despite summary/curve naming differences
- hover popovers were removed; dictionary access is click-to-open only

### Historical Backtest work
- Historical Backtest now acts as the control center before entering Trading Performance
- instrument selection has been converted from dropdown intent toward a single-select table
- instrument rows now target meaningful selection-help data such as start date, end date, granularity, and row count instead of raw implementation-path fields
- strategy selection has been converted from dropdown intent toward a multi-select sortable/searchable table
- strategy selection is intended to help the user narrow scope before loading the heavy trading-performance payloads
- artifact checklist exists and includes download buttons/links
- the final execution card is now the place where Trading Performance is loaded and where progress should appear only after load starts
- strategy selection now constrains which family dashboards get loaded for Trading Performance
- loading logic has begun moving toward incremental reuse for still-selected families while clearing caches for families that were explicitly deselected

### Market State Analysis work
- overview/separation/explanation page skeletons exist
- state module can load independently of Trading Performance
- State Explanation has a dedicated controlled sample instrument selector because explanation is allowed to project anonymized states onto a real market sample
- second-module design rule is now clearer: Market State Analysis stays anonymized at the module level, but State Explanation is allowed to use a controlled real-market projection instrument

## Family detail pages

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

## Immediate next priorities

1. finish Historical Backtest as the true control center for instrument + strategy selection + artifact visibility + progress
2. continue refining instrument/strategy selection tables so they help the user choose scope rather than merely exposing controls
3. improve incremental loading/reuse for Trading Performance while keeping memory usage bounded and clearing deselected-family caches
4. continue filling Market State Analysis with real content, especially State Explanation
