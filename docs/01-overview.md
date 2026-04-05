# 01 Overview

`trading-dashboard` is the website dashboard repository for the trading system.

Its job is to:
- provide the website/dashboard surface for trading-system outputs
- define the dashboard module/page structure
- define dashboard-side interaction patterns
- expose local server/adaptation paths for dashboard payloads
- maintain shared dictionary/display metadata used by the UI

It should not be the canonical home for:
- upstream market-data acquisition
- strategy replay computation
- model-training or ranking internals
- live execution internals
- centralized cross-repo report generation

## Main interpretation

This repo is downstream of the trading producer repos.
It does not replace their output/report generation responsibilities.
Instead, it visualizes the outputs already produced by those repos.

## Current module interpretation

The dashboard should stay modular.
Current major product surfaces are:
- Welcome
- Historical Backtest
- Trading Performance
- Market State Analysis

Boundary rule:
- Historical Backtest = control center / pre-load workspace
- Trading Performance = trading-and-return analysis
- Market State Analysis = state/cluster interpretation

## Current status summary

The repo is now established as the dashboard-only downstream repository for the trading system.
Its current codebase comes from the earlier dashboard implementation lineage, but this repo should now be treated simply as `trading-dashboard`.
