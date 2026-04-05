# ops-dashboard

Web dashboard surface for operational and research views.

## Current scope

- historical trading dashboard for `projects/crypto-trading`
- reusable dictionary-backed metric labels/tooltips
- family / composite / ledger / routing views
- includes shared field/metric definitions under `data/metric-dictionary`

## Run

```bash
python3 server.py
```

Default server:
- <http://localhost:8787>

## Current implementation notes

The dashboard is currently a static HTML app served by `server.py`, with live local data endpoints sourced from `projects/crypto-trading` and local dictionary files.

Key endpoints include:

- `/data/family-backtest-summary.json`
- `/data/family-equity-curves.jsonl`
- `/data/family-trade-ledger.jsonl`
- `/data/composite-backtest-summary.json`
- `/data/family-variant-dashboard/<family>.json`
- `/data/cluster-overview.json`
- `/data/dictionary.json`

## Documentation

- Design notes: `docs/DASHBOARD_DESIGN.md`

## Near-term next steps

- add richer tooltip/popover UI instead of plain `title` attributes
- add a real parameter change-log source instead of the current empty/placeholder path from market-discovery payloads
- continue hardening the family-variant dashboard pattern until all three family pages behave identically
