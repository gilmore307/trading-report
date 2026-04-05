# 02 Structure and Runtime

This document defines the core file layout, runtime entrypoints, and structural direction of `trading-dashboard`.

## Core files

- `index.html` — main front-end UI, layout, charts, state management, and interactions
- `server.py` — local HTTP server and payload adapters for dashboard endpoints
- `vendor/lightweight-charts.standalone.production.js` — charting library bundle
- `run_daemon.sh` — local helper for running the server/daemon flow

## Docs

- `docs/01-overview.md` — repo role and top-level interpretation
- `docs/02-structure-and-runtime.md` — this file
- `docs/03-workflow-and-page-patterns.md` — dashboard workflow and page interaction design
- `docs/04-data-contracts.md` — important endpoint and payload notes
- `docs/05-module-boundaries-and-decisions.md` — durable module/product decisions
- `docs/06-metawork-checklist.md` — dashboard doc-maintenance checklist

## Main UI module structure

- `welcome-home`
- `historical-backtest-home`
- `current-trading-overview` → Trading Performance
- `trading-strategy-families` → Strategy Variants
- `trading-composite-routing` → Composite / Routing
- `trading-trade-ledger` → Trade Ledger
- `market-overview` → Market State Analysis overview
- `market-state-separation`
- `market-state-transitions`
- `market-state-explanation`

## Runtime entrypoint

Run locally with:

```bash
python3 server.py
```

Default local server:
- <http://localhost:8787>

Interpreter rule:
- use `python3` for direct CLI invocation in this environment
- do not assume a bare `python` command exists

## Structural rule

This repo should stay dashboard-only.
Keep UI meta-work in `docs/` continuously during active development.
