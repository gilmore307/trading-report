from collections import deque
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import json
import os

ROOT = Path('/root/.openclaw/workspace/projects/ops-dashboard')
TRADING = Path('/root/.openclaw/workspace/projects/crypto-trading')
DICT = Path('/root/.openclaw/workspace/projects/ops-dashboard/data/metric-dictionary')

FAMILY_BACKTEST_SUMMARY = TRADING / 'data' / 'derived' / 'family_backtest_summary_v1.json'
FAMILY_EQUITY_CURVES = TRADING / 'data' / 'intermediate' / 'dashboard_payloads' / 'family_equity_curves_v1.jsonl'
FAMILY_TRADE_LEDGER = TRADING / 'data' / 'derived' / 'family_trade_ledger_v1.jsonl'
COMPOSITE_BACKTEST_SUMMARY = TRADING / 'data' / 'derived' / 'composite_backtest_summary_v1.json'
FAMILY_VARIANT_DASHBOARD_DIR = TRADING / 'data' / 'intermediate' / 'dashboard_payloads' / 'family_variant_dashboard'
UNSUP_LABELS = TRADING / 'data' / 'intermediate' / 'market_state' / 'unsupervised_market_state_labels_v1.jsonl'
UNSUP_LABELS_SUMMARY = TRADING / 'data' / 'derived' / 'unsupervised_market_state_labels_summary_v1.json'
UNSUP_EVAL = TRADING / 'data' / 'derived' / 'unsupervised_market_state_evaluation_v1.json'
MARKET_STATE_DATASET = TRADING / 'data' / 'derived' / 'crypto_market_state_dataset_v1.jsonl'


def load_json(path: Path, fallback=None):
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return fallback


def dictionary_payload():
    index = load_json(DICT / 'index.json', {}) or {}
    groups = index.get('entryGroups') or {}
    entries = {}
    folder_map = {'metrics': 'metrics', 'terms': 'terms', 'parameters': 'parameters', 'enums': 'enums'}
    for group, folder in folder_map.items():
        for key in groups.get(group, []) or []:
            row = load_json(DICT / folder / f'{key}.json', None)
            if row is not None:
                entries[key] = row
    synthetic = {
        'trading_performance': {'key':'trading_performance','label':'Trading Performance','entryType':'term','definition':'The trading-and-return layer of the dashboard focused on realized or backtested equity behavior, routing outcomes, and trade-level results.','interpretation':'Use this section to judge strategy profitability and switching effect; parameter research belongs in later sections.'},
        'moving_average': {'key':'moving_average','label':'Moving Average','entryType':'term','definition':'Trend-following strategy family using fast/slow moving-average relationships and entry/exit thresholds.','interpretation':'Used as one of the baseline strategy families in trading comparison pages.'},
        'donchian_breakout': {'key':'donchian_breakout','label':'Donchian Breakout','entryType':'term','definition':'Breakout strategy family based on Donchian channel highs/lows and breakout confirmation logic.','interpretation':'Captures expansion and breakout-style moves; compared against other families by cluster.'},
        'bollinger_reversion': {'key':'bollinger_reversion','label':'Bollinger Reversion','entryType':'term','definition':'Mean-reversion strategy family based on Bollinger bands, z-score band breaches, and reversion exits.','interpretation':'Used to test whether band-based reversion dominates in some unsupervised clusters.'},
        'cluster': {'key':'cluster','label':'Unsupervised Cluster','entryType':'term','definition':'A market regime discovered by unsupervised learning rather than assigned by manual pre-grouping.','interpretation':'This dashboard uses cluster as the primary grouping axis for trading and routing analysis.'},
        'cluster_id': {'key':'cluster_id','label':'Cluster ID','entryType':'metric','definition':'Identifier of an unsupervised market cluster assigned to a timestamp.','interpretation':'Use when the UI needs the exact cluster label itself, not a higher-level summary about cluster quality.'},
        'cluster_count': {'key':'cluster_count','label':'Cluster Count','entryType':'metric','definition':'Number of unsupervised clusters currently present in the loaded trading dataset.','interpretation':'Higher count means the market was partitioned into more distinct learned regimes.'},
        'persisted_label_rows': {'key':'persisted_label_rows','label':'Persisted Label Rows','entryType':'metric','definition':'Number of timestamps for which a cluster label was persisted into the trading dataset.','interpretation':'Acts as effective coverage for cluster-based trading analysis.'},
        'most_distinct_cluster': {'key':'most_distinct_cluster','label':'Most Distinct Cluster','entryType':'metric','definition':'The cluster with the largest separation between its best and worst region-level utility outcome.','interpretation':'This is a cluster-quality summary, not the definition of cluster_id itself. Use it to identify where routing or parameter choice matters most.'},
        'parameter_region': {'key':'parameter_region','label':'Parameter Region','entryType':'term','definition':'A coarse bucket of strategy parameters used to compare families and variants at a more stable level than single variants.','interpretation':'Useful when exact variant-level rankings are too noisy.'},
        'best_region': {'key':'best_region','label':'Best Region','entryType':'metric','definition':'The parameter region with the highest average utility inside a given cluster or comparison slice.','interpretation':'Shows which parameter regime currently looks most suitable within that cluster.'},
        'best_avg_utility_1h': {'key':'best_avg_utility_1h','label':'Best Avg Utility 1h','entryType':'metric','definition':'Highest average one-hour utility achieved by the best parameter region in the current slice.','interpretation':'Used to compare relative attractiveness of parameter regions.'},
        'spread_best_minus_worst': {'key':'spread_best_minus_worst','label':'Best-Worst Spread','entryType':'metric','definition':'Difference between the best and worst average utility across parameter regions in the same cluster.','interpretation':'Higher spread implies stronger parameter sensitivity or more informative clustering.'},
        'sample_count': {'key':'sample_count','label':'Sample Count','entryType':'metric','definition':'Number of observations supporting the displayed statistic.','interpretation':'Use to judge confidence and avoid over-reading small groups.'},
        'trade_count': {'key':'trade_count','label':'Trade Count','entryType':'metric','definition':'Number of completed trades contributing to the displayed performance row.','interpretation':'Use alongside return and drawdown to judge how much evidence sits behind the result.'},
        'signal_count': {'key':'signal_count','label':'Signal Count','entryType':'metric','definition':'Number of strategy entry or action signals generated in the evaluated window.','interpretation':'Higher signal count usually means a more active decision process, but not necessarily better profitability.'},
        'turnover_count': {'key':'turnover_count','label':'Turnover','entryType':'metric','definition':'Count of allocation changes, position turnovers, or routing re-allocations during the evaluated window.','interpretation':'Higher turnover usually means the strategy or router changes exposure more frequently, which may raise trading friction or instability.'},
        'total_return': {'key':'total_return','label':'Total Return','entryType':'metric','definition':'Net percentage return over the evaluated window, usually measured as final_equity minus 1.','interpretation':'Primary headline profitability metric for comparing variants, family composites, and overall composite routing.'},
        'max_drawdown': {'key':'max_drawdown','label':'Max Drawdown','entryType':'metric','definition':'Largest peak-to-trough equity decline observed during the evaluated window.','interpretation':'Use as the main downside-risk metric when comparing strategies with similar return.'},
        'win_rate': {'key':'win_rate','label':'Win Rate','entryType':'metric','definition':'Fraction of closed trades that ended profitable within the evaluated window.','interpretation':'Helpful context, but should not be read in isolation from drawdown, turnover, and total return.'},
        'utility_1h': {'key':'utility_1h','label':'1h Utility','entryType':'metric','definition':'One-hour-forward utility measure used in strategy comparison datasets.','interpretation':'Acts as the core payoff score for ranking families, parameter regions, and variants in research layers.'},
        'composite_strategy': {'key':'composite_strategy','label':'Composite Strategy','entryType':'term','definition':'A stitched strategy that switches family or variant according to a routing rule instead of remaining fixed on one baseline.','interpretation':'Use this key when the UI is discussing the combined routed strategy rather than a single standalone variant.'},
        'routing': {'key':'routing','label':'Routing','entryType':'term','definition':'Selection rule that maps each market situation to a chosen trading family or chosen variant.','interpretation':'In the trading-performance layer, routing is evaluated by return, drawdown, switch count, and lift over the best static baseline.'},
        'composite_routing': {'key':'composite_routing','label':'Composite / Routing','entryType':'term','definition':'Trading-performance view focused on how a composite strategy switches between families or variants over time and whether that switching improves results over static baselines.','interpretation':'Use this when the UI is discussing the combined selector, routing comparison, routed curve, and visible switch table as one coherent layer.'},
        'strategy_variants': {'key':'strategy_variants','label':'Strategy Variants','entryType':'term','definition':'Unified cross-family table and curve workspace for comparing overall composite, family composites, and individual strategy variants.','interpretation':'This is the trading-side comparison surface; it helps choose what to plot and compare, but it is not the parameter-research section.'},
        'moving_average_variant_code': {'key':'moving_average_variant_code','label':'Moving Average Variant Code','entryType':'term','definition':'Naming grammar for Moving Average family variant ids. Pattern seen in current payloads: `sma_<source>_<fast>_<slow>_te<entry-threshold>_tx<exit-threshold>`. `sma` = simple moving average. `<source>` is the input price (`close`, `hl2` = (high+low)/2, `hlc3` = (high+low+close)/3). `<fast>_<slow>` gives the fast and slow MA windows, such as `5_20`. `te005` means entry threshold 0.05 and `tx000` means exit threshold 0.00 under the current compact decimal convention.','interpretation':'Use this key to decode concrete MA variant labels such as `sma_close_5_20_te005_tx000`. The important thing is the family-wide code grammar: source + MA windows + entry threshold + exit threshold.'},
        'donchian_breakout_variant_code': {'key':'donchian_breakout_variant_code','label':'Donchian Breakout Variant Code','entryType':'term','definition':'Naming grammar for Donchian Breakout family variant ids. Pattern seen in current payloads: `donchian_<side-mode>_<source>_bw<breakout-window>_ew<exit-window>_cb<confirm/buffer-flag>`. `both` means the variant is configured for both long and short breakout directions. `<source>` is the input price (`close`, `hl2`, `hlc3`). `bw020` means breakout window 20. `ew010` means exit window 10. `cb01` is a compact boolean-like confirmation/buffer control currently set to 1 in the active variants.','interpretation':'Use this key to decode specific Donchian labels such as `donchian_both_close_bw020_ew010_cb01`. The code primarily expresses direction mode, price source, breakout lookback, exit lookback, and confirmation/buffer control.'},
        'bollinger_reversion_variant_code': {'key':'bollinger_reversion_variant_code','label':'Bollinger Reversion Variant Code','entryType':'term','definition':'Naming grammar for Bollinger Reversion family variant ids. Pattern seen in current payloads: `bollinger_<side-mode>_<source>_w<window>_m<band-multiplier>_e<exit-control>`. `<side-mode>` may be `both` or `long`. `<source>` is the input price (`close` or `hlc3` in current payloads). `w020` means Bollinger window 20. `m20` is the compact multiplier code currently used for band width. `e00` is the compact exit-control code in the current variants.','interpretation':'Use this key to decode concrete Bollinger labels such as `bollinger_both_close_w020_m20_e00`. The code primarily expresses direction mode, price source, Bollinger window, multiplier setting, and exit control.'},
        'parameter_region_code': {'key':'parameter_region_code','label':'Parameter Region Code','entryType':'term','definition':'Shared naming grammar for concrete parameter-region labels such as `fast_windows__tight_threshold`, `fast_windows__mid_threshold`, and `fast_windows__wide_threshold`. These names sit underneath the broader `parameter_region` concept. The prefix before `__` describes the window-speed regime (for example `fast_windows`), while the suffix after `__` describes the threshold regime (for example `tight_threshold`, `mid_threshold`, or `wide_threshold`).','interpretation':'When the UI shows a concrete region name, point to this mother key so the dictionary explains how to read the region label and how it decomposes into a window regime plus a threshold regime. The concrete region is a child label; `parameter_region` is the parent concept.'},
    }
    entries.update(synthetic)
    return {'entries': entries}


def load_cluster_map() -> dict[int, int]:
    out = {}
    if not UNSUP_LABELS.exists():
        return out
    with UNSUP_LABELS.open('r', encoding='utf-8') as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = row.get('ts')
            cluster_id = row.get('cluster_id')
            if ts is None or cluster_id is None:
                continue
            out[int(ts)] = int(cluster_id)
    return out


def trade_ledger_payload() -> bytes:
    cluster_by_ts = load_cluster_map()
    lines = []
    if FAMILY_TRADE_LEDGER.exists():
        with FAMILY_TRADE_LEDGER.open('r', encoding='utf-8') as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                entry_ts = row.get('entry_ts')
                exit_ts = row.get('exit_ts')
                row['entry_cluster'] = None if entry_ts is None else cluster_by_ts.get(int(entry_ts))
                row['exit_cluster'] = None if exit_ts is None else cluster_by_ts.get(int(exit_ts))
                lines.append(json.dumps(row, ensure_ascii=False))
    return ('\n'.join(lines) + ('\n' if lines else '')).encode('utf-8')


def family_equity_curves_payload(selected_families: list[str] | None = None) -> bytes:
    wanted = set(selected_families or [])
    lines = []
    if FAMILY_EQUITY_CURVES.exists():
        with FAMILY_EQUITY_CURVES.open('r', encoding='utf-8') as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                if not wanted:
                    lines.append(line)
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if row.get('family') in wanted:
                    lines.append(json.dumps(row, ensure_ascii=False))
    return ('\n'.join(lines) + ('\n' if lines else '')).encode('utf-8')


def instruments_catalog_payload():
    instruments = []
    recent = sorted((TRADING / 'data' / 'derived').glob('*_recent120k.jsonl'))
    if recent:
        for path in recent:
            name = path.name.replace('_recent120k.jsonl', '')
            start_ts = None
            end_ts = None
            row_count = 0
            granularity = None
            try:
                with path.open('r', encoding='utf-8') as handle:
                    first_row = None
                    last_row = None
                    for line in handle:
                        line = line.strip()
                        if not line:
                            continue
                        row = json.loads(line)
                        if first_row is None:
                            first_row = row
                            granularity = row.get('bar')
                        last_row = row
                        row_count += 1
                    if first_row is not None:
                        start_ts = first_row.get('ts') or first_row.get('timestamp')
                    if last_row is not None:
                        end_ts = last_row.get('ts') or last_row.get('timestamp')
            except Exception:
                pass
            instruments.append({'instrument': name, 'label': name, 'startTs': start_ts, 'endTs': end_ts, 'granularity': granularity, 'rowCount': row_count})
    else:
        instruments.append({'instrument': 'BTC-USDT-SWAP', 'label': 'BTC-USDT-SWAP', 'startTs': None, 'endTs': None, 'granularity': None, 'rowCount': None})
    return {'instruments': instruments, 'defaultInstrument': instruments[0]['instrument'] if instruments else None}


def load_family_variant_family_payload(family: str) -> dict:
    safe_family = ''.join(ch for ch in family if ch.isalnum() or ch in {'_', '-'})
    family_dir = FAMILY_VARIANT_DASHBOARD_DIR / safe_family
    if family_dir.exists() and family_dir.is_dir():
        summary = load_json(family_dir / 'summary.json', {}) or {}
        composite = load_json(family_dir / 'composite.json', {}) or {}
        variants_dir = family_dir / 'variants'
        variant_payloads = []
        if variants_dir.exists():
            for path in sorted(variants_dir.glob('*.json')):
                row = load_json(path, None)
                if row is not None:
                    variant_payloads.append(row)
        return {
            'family': safe_family,
            'summary': summary.get('summary') or [],
            'curves': [curve_row for payload in variant_payloads for curve_row in (payload.get('curve') or [])],
            'ledger': [ledger_row for payload in variant_payloads for ledger_row in (payload.get('ledger') or [])],
            'composite': {
                'summary': composite.get('summary') or {},
                'curve': composite.get('curve') or [],
            },
            'parts': {
                'summary': str(family_dir / 'summary.json'),
                'composite': str(family_dir / 'composite.json'),
                'variants_dir': str(variants_dir),
            },
        }
    compat_path = FAMILY_VARIANT_DASHBOARD_DIR / f'{safe_family}.json'
    return load_json(compat_path, {'family': safe_family, 'summary': [], 'curves': [], 'ledger': [], 'composite': {'summary': {}, 'curve': []}}) or {'family': safe_family, 'summary': [], 'curves': [], 'ledger': [], 'composite': {'summary': {}, 'curve': []}}


def family_variant_catalog_payload(instrument: str | None = None):
    families = []
    seen = set()
    evaluation = load_json(UNSUP_EVAL, {}) or {}
    cluster_family_cube = evaluation.get('cluster_family_cube') or []
    family_rankings_by_cluster = {}
    for row in cluster_family_cube:
        cid = row.get('cluster_id')
        family = row.get('family')
        if cid is None or not family:
            continue
        family_rankings_by_cluster.setdefault(str(cid), []).append(row)
    for cid, rows in family_rankings_by_cluster.items():
        rows.sort(key=lambda r: float(r.get('avg_utility_1h', float('-inf'))), reverse=True)

    family_cluster_rank_map = {}
    family_cluster_tier_map = {}
    for cid, rows in family_rankings_by_cluster.items():
        for idx, row in enumerate(rows, start=1):
            family = row.get('family')
            if not family:
                continue
            family_cluster_rank_map.setdefault(family, {})[str(cid)] = idx
            if idx <= 1:
                tier = 'active'
            elif idx <= 5:
                tier = 'reserve'
            else:
                tier = 'archived'
            family_cluster_tier_map.setdefault(family, {})[str(cid)] = tier

    if FAMILY_VARIANT_DASHBOARD_DIR.exists():
        for path in sorted(FAMILY_VARIANT_DASHBOARD_DIR.iterdir()):
            if path.is_dir():
                family = path.name
                summary_obj = load_json(path / 'summary.json', {}) or {}
                composite_obj = load_json(path / 'composite.json', {}) or {}
                summaries = summary_obj.get('summary') or []
                composite_summary = composite_obj.get('summary') or {}
                variants_dir = path / 'variants'
                variant_file_count = 0
                if variants_dir.exists():
                    try:
                        variant_file_count = sum(1 for _ in variants_dir.glob('*.json'))
                    except Exception:
                        variant_file_count = 0
                families.append({
                    'instrument': instrument or 'BTC-USDT-SWAP',
                    'family': family,
                    'path': str(path),
                    'variant_count': len(summaries),
                    'variant_file_count': variant_file_count,
                    'splitReady': bool((path / 'summary.json').exists() and (path / 'composite.json').exists()),
                    'family_cluster_ranks': family_cluster_rank_map.get(family, {}),
                    'family_cluster_tiers': family_cluster_tier_map.get(family, {}),
                    'sizeBytes': sum(p.stat().st_size for p in path.rglob('*.json') if p.exists()),
                    'compositeFinalEquity': composite_summary.get('final_equity'),
                    'compositeMaxDrawdown': composite_summary.get('max_drawdown'),
                    'compositeCurvePoints': composite_summary.get('curve_points'),
                })
                seen.add(family)
        for path in sorted(FAMILY_VARIANT_DASHBOARD_DIR.glob('*.json')):
            if path.stem in seen:
                continue
            row = load_json(path, {}) or {}
            summaries = row.get('summary') or []
            composite_summary = (row.get('composite') or {}).get('summary') or {}
            families.append({
                'instrument': instrument or 'BTC-USDT-SWAP',
                'family': row.get('family') or path.stem,
                'variant_count': len(summaries),
                'path': path.name,
                'family_cluster_ranks': family_cluster_rank_map.get(row.get('family') or path.stem, {}),
                'family_cluster_tiers': family_cluster_tier_map.get(row.get('family') or path.stem, {}),
                'sizeBytes': path.stat().st_size if path.exists() else None,
                'compositeFinalEquity': composite_summary.get('final_equity'),
                'compositeMaxDrawdown': composite_summary.get('max_drawdown'),
                'compositeCurvePoints': composite_summary.get('curve_points'),
            })
    return {'families': families}


def historical_backtest_catalog_payload(instrument: str | None = None):
    files = []

    def dir_size_bytes(path: Path) -> int:
        total = 0
        for child in path.rglob('*'):
            if child.is_file():
                try:
                    total += child.stat().st_size
                except Exception:
                    pass
        return total

    def add_file(label: str, key: str, path: Path, kind: str, download_path: str | None = None):
        exists = path.exists()
        line_count = None
        if exists and kind == 'jsonl' and path.is_file():
            try:
                with path.open('r', encoding='utf-8') as handle:
                    line_count = sum(1 for _ in handle)
            except Exception:
                line_count = None
        size_bytes = None
        if exists:
            if path.is_dir():
                size_bytes = dir_size_bytes(path)
            else:
                size_bytes = path.stat().st_size
        files.append({
            'key': key,
            'label': label,
            'path': str(path),
            'filename': path.name,
            'exists': exists,
            'kind': kind,
            'sizeBytes': size_bytes,
            'lineCount': line_count,
            'downloadPath': download_path or f'/download/{key}',
        })

    add_file('Family Backtest Summary', 'family-backtest-summary', FAMILY_BACKTEST_SUMMARY, 'json')
    add_file('Family Equity Curves', 'family-equity-curves', FAMILY_EQUITY_CURVES, 'jsonl')
    add_file('Family Trade Ledger', 'family-trade-ledger', FAMILY_TRADE_LEDGER, 'jsonl')
    add_file('Composite Backtest Summary', 'composite-backtest-summary', COMPOSITE_BACKTEST_SUMMARY, 'json')
    add_file('Cluster Overview', 'cluster-overview', UNSUP_EVAL, 'json')

    seen = set()
    if FAMILY_VARIANT_DASHBOARD_DIR.exists():
        for path in sorted(FAMILY_VARIANT_DASHBOARD_DIR.iterdir()):
            if path.is_dir():
                family = path.name
                seen.add(family)
                add_file(
                    f'Family Variant Dashboard · {family}',
                    f'family-variant-dashboard-{family}',
                    path,
                    'family-variant-dashboard-dir',
                    f'/data/family-variant-dashboard/{family}.json',
                )
                add_file(
                    f'Family Variant Summary · {family}',
                    f'family-variant-summary-{family}',
                    path / 'summary.json',
                    'json',
                    f'/download/family-variant-summary-{family}',
                )
                add_file(
                    f'Family Variant Composite · {family}',
                    f'family-variant-composite-{family}',
                    path / 'composite.json',
                    'json',
                    f'/download/family-variant-composite-{family}',
                )
                variants_dir = path / 'variants'
                add_file(
                    f'Family Variant Variants Dir · {family}',
                    f'family-variant-variants-dir-{family}',
                    variants_dir,
                    'family-variant-variants-dir',
                )
        for path in sorted(FAMILY_VARIANT_DASHBOARD_DIR.glob('*.json')):
            if path.stem in seen:
                continue
            add_file(f'Family Variant Dashboard · {path.stem}', f'family-variant-dashboard-{path.stem}', path, 'json')

    return {'instrument': instrument, 'files': files, 'families': family_variant_catalog_payload(instrument).get('families', [])}


def cluster_overview_payload():
    labels = load_json(UNSUP_LABELS_SUMMARY, {}) or {}
    evaluation = load_json(UNSUP_EVAL, {}) or {}
    counts = labels.get('cluster_counts') or []
    count_map = {int(row.get('cluster_id')): int(row.get('row_count', 0)) for row in counts if row.get('cluster_id') is not None}
    separation = {int(row.get('cluster_id')): row for row in (evaluation.get('cluster_separation_summary') or []) if row.get('cluster_id') is not None}
    cube_rows = evaluation.get('cluster_parameter_region_cube') or []
    by_cluster = {}
    for row in cube_rows:
        cid = row.get('cluster_id')
        if cid is None:
            continue
        by_cluster.setdefault(int(cid), []).append(row)
    clusters = []
    for cid in sorted(set(count_map) | set(separation) | set(by_cluster)):
        sep = separation.get(cid, {})
        clusters.append({
            'cluster_id': cid,
            'row_count': count_map.get(cid, 0),
            'best_region': sep.get('best_region'),
            'best_avg_utility_1h': sep.get('best_avg_utility_1h'),
            'worst_region': sep.get('worst_region'),
            'worst_avg_utility_1h': sep.get('worst_avg_utility_1h'),
            'spread_best_minus_worst': sep.get('spread_best_minus_worst'),
            'best_family': sep.get('best_family'),
            'best_family_avg_utility_1h': sep.get('best_family_avg_utility_1h'),
            'best_variant': sep.get('best_variant'),
            'best_variant_family': sep.get('best_variant_family'),
            'best_variant_avg_utility_1h': sep.get('best_variant_avg_utility_1h'),
            'parameter_rows': sorted(by_cluster.get(cid, []), key=lambda r: float(r.get('avg_utility_1h', 0)), reverse=True),
        })
    return {
        'summary': {
            'cluster_count': labels.get('clusters') or evaluation.get('summary', {}).get('cluster_count'),
            'persisted_label_rows': labels.get('persisted_label_rows'),
            'weighted_avg_cluster_spread': evaluation.get('summary', {}).get('weighted_avg_cluster_spread'),
            'matched_utility_rows': evaluation.get('summary', {}).get('matched_utility_rows'),
        },
        'clusters': clusters,
    }


def state_explanation_payload(cluster_id: int | None, instrument: str | None = None, window_mode: str | None = None):
    overview = cluster_overview_payload()
    cluster_row = next((row for row in (overview.get('clusters') or []) if int(row.get('cluster_id')) == int(cluster_id)), None) if cluster_id is not None else None
    if cluster_id is None or cluster_row is None:
        return {
            'cluster_id': cluster_id,
            'instrument': instrument,
            'window_mode': window_mode,
            'window': {},
            'candles': [],
            'parameterSeries': [],
            'clusterSummary': cluster_row,
        }

    instrument = instrument or 'BTC-USDT-SWAP'
    window_mode = window_mode or 'recent'
    labels_by_ts = {}
    cluster_rows = []
    if UNSUP_LABELS.exists():
        with UNSUP_LABELS.open('r', encoding='utf-8') as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if row.get('symbol') != instrument:
                    continue
                ts = row.get('ts')
                cid = row.get('cluster_id')
                if ts is None or cid is None:
                    continue
                labels_by_ts[int(ts)] = row
                if int(cid) == int(cluster_id):
                    cluster_rows.append(row)

    if not cluster_rows:
        return {
            'cluster_id': cluster_id,
            'instrument': instrument,
            'window_mode': window_mode,
            'window': {},
            'candles': [],
            'parameterSeries': [],
            'clusterSummary': cluster_row,
        }

    cluster_rows = sorted(cluster_rows, key=lambda r: int(r.get('ts') or 0))
    target_label = cluster_rows[-1] if window_mode == 'recent' else cluster_rows[len(cluster_rows)//2]
    target_ts = int(target_label.get('ts') or 0)
    half_window = 120
    window_rows = []

    if window_mode == 'recent':
        history = deque(maxlen=half_window)
        tail = []
        found_target = False
        if MARKET_STATE_DATASET.exists():
            with MARKET_STATE_DATASET.open('r', encoding='utf-8') as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if row.get('symbol') != instrument:
                        continue
                    ts = row.get('ts')
                    if ts is None:
                        continue
                    ts = int(ts)
                    label_row = labels_by_ts.get(ts)
                    row['cluster_id'] = label_row.get('cluster_id') if label_row else None
                    row['market_state'] = (label_row.get('market_state') if label_row else row.get('market_state'))
                    row['feature_columns'] = (label_row.get('feature_columns') if label_row else row.get('feature_columns'))
                    if not found_target:
                        history.append(row)
                        if ts >= target_ts:
                            found_target = True
                            tail.append(row)
                    else:
                        tail.append(row)
                        if len(tail) >= half_window + 1:
                            break
        window_rows = list(history)[:-1] + tail if tail else list(history)
    else:
        all_rows = []
        if MARKET_STATE_DATASET.exists():
            with MARKET_STATE_DATASET.open('r', encoding='utf-8') as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if row.get('symbol') != instrument:
                        continue
                    ts = row.get('ts')
                    if ts is None:
                        continue
                    ts = int(ts)
                    label_row = labels_by_ts.get(ts)
                    row['cluster_id'] = label_row.get('cluster_id') if label_row else None
                    row['market_state'] = (label_row.get('market_state') if label_row else row.get('market_state'))
                    row['feature_columns'] = (label_row.get('feature_columns') if label_row else row.get('feature_columns'))
                    all_rows.append(row)
        all_rows = sorted(all_rows, key=lambda r: int(r.get('ts') or 0))
        idx = next((i for i, row in enumerate(all_rows) if int(row.get('ts') or 0) >= target_ts), len(all_rows)-1)
        start = max(0, idx-half_window)
        end = min(len(all_rows), idx+half_window+1)
        window_rows = all_rows[start:end]

    numeric_fields = ['return_5m', 'return_15m', 'return_1h', 'trend_return_60', 'range_width_30', 'realized_vol_30', 'volume_burst_z_30', 'funding_rate', 'basis_pct']
    feature_columns = [c for c in (target_label.get('feature_columns') or []) if c in numeric_fields]
    if not feature_columns:
        feature_columns = [c for c in numeric_fields if any(r.get(c) is not None for r in window_rows)][:4]
    else:
        feature_columns = feature_columns[:4]

    parameter_series = []
    for field in feature_columns:
        points = []
        for row in window_rows:
            value = row.get(field)
            if value is None:
                continue
            points.append({'time': int(int(row.get('ts'))/1000), 'value': value})
        parameter_series.append({'key': field, 'label': field, 'points': points})

    candles = [{
        'time': int(int(row.get('ts'))/1000),
        'open': row.get('open'),
        'high': row.get('high'),
        'low': row.get('low'),
        'close': row.get('close'),
        'cluster_id': row.get('cluster_id'),
        'market_state': row.get('market_state'),
    } for row in window_rows if row.get('open') is not None and row.get('high') is not None and row.get('low') is not None and row.get('close') is not None]

    target_region = cluster_row.get('best_region')
    ranked_regions = (cluster_row.get('parameter_rows') or [])[:5]
    return {
        'cluster_id': int(cluster_id),
        'instrument': instrument,
        'window_mode': window_mode,
        'window': {
            'targetTs': target_ts,
            'startTs': int(window_rows[0].get('ts')) if window_rows else None,
            'endTs': int(window_rows[-1].get('ts')) if window_rows else None,
            'rowCount': len(window_rows),
        },
        'candles': candles,
        'parameterSeries': parameter_series,
        'clusterSummary': cluster_row,
        'narrativeInputs': {
            'best_region': target_region,
            'ranked_regions': ranked_regions,
            'target_market_state': target_label.get('market_state'),
            'feature_columns': feature_columns,
        },
    }


class Handler(SimpleHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def serve_bytes(self, body: bytes, content_type='application/json; charset=utf-8'):
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store, max-age=0')
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()
        self.close_connection = True

    def serve_file(self, path: Path, fallback=None, content_type='application/json; charset=utf-8'):
        if path.exists():
            body = path.read_bytes()
        else:
            body = json.dumps(fallback or {}).encode('utf-8')
        self.serve_bytes(body, content_type)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query or '')
        instrument = (query.get('instrument') or [None])[0]
        if path.startswith('/data/family-backtest-summary.json'):
            return self.serve_file(FAMILY_BACKTEST_SUMMARY, {'families': [], 'instrument': instrument})
        if path.startswith('/data/family-equity-curves.jsonl'):
            selected_families = [str(v) for v in (query.get('family') or []) if str(v).strip()]
            return self.serve_bytes(family_equity_curves_payload(selected_families), 'application/x-ndjson; charset=utf-8')
        if path.startswith('/data/family-trade-ledger.jsonl'):
            return self.serve_bytes(trade_ledger_payload(), 'application/x-ndjson; charset=utf-8')
        if path.startswith('/data/composite-backtest-summary.json'):
            return self.serve_file(COMPOSITE_BACKTEST_SUMMARY, {'summary': {}, 'curve': [], 'instrument': instrument})
        if path.startswith('/data/instruments/catalog.json'):
            return self.serve_bytes(json.dumps(instruments_catalog_payload()).encode('utf-8'))
        if path.startswith('/data/family-variant-dashboard/catalog.json'):
            return self.serve_bytes(json.dumps(family_variant_catalog_payload(instrument)).encode('utf-8'))
        if path.startswith('/data/historical-backtest/catalog.json'):
            return self.serve_bytes(json.dumps(historical_backtest_catalog_payload(instrument)).encode('utf-8'))
        if path.startswith('/data/family-variant-dashboard/'):
            family = path.split('/data/family-variant-dashboard/', 1)[1].strip('/').replace('.json', '')
            safe_family = ''.join(ch for ch in family if ch.isalnum() or ch in {'_', '-'})
            return self.serve_bytes(json.dumps(load_family_variant_family_payload(safe_family)).encode('utf-8'))
        if path.startswith('/data/cluster-overview.json'):
            return self.serve_bytes(json.dumps(cluster_overview_payload()).encode('utf-8'))
        if path.startswith('/data/state-explanation.json'):
            cluster_id = (query.get('cluster_id') or [None])[0]
            window_mode = (query.get('window') or ['recent'])[0]
            cid = int(cluster_id) if cluster_id is not None and str(cluster_id).strip() != '' else None
            return self.serve_bytes(json.dumps(state_explanation_payload(cid, instrument, window_mode)).encode('utf-8'))
        if path.startswith('/data/dictionary.json'):
            return self.serve_bytes(json.dumps(dictionary_payload()).encode('utf-8'))
        if path.startswith('/download/'):
            key = path.split('/download/', 1)[1].strip('/')
            if key.startswith('family-variant-summary-'):
                family = key.replace('family-variant-summary-', '', 1)
                return self.serve_file(FAMILY_VARIANT_DASHBOARD_DIR / family / 'summary.json', {}, 'application/json; charset=utf-8')
            if key.startswith('family-variant-composite-'):
                family = key.replace('family-variant-composite-', '', 1)
                return self.serve_file(FAMILY_VARIANT_DASHBOARD_DIR / family / 'composite.json', {}, 'application/json; charset=utf-8')
            catalog = historical_backtest_catalog_payload(instrument)
            match = next((row for row in catalog['files'] if row['key'] == key), None)
            if match and match['exists'] and Path(match['path']).is_file():
                content_type = 'application/x-ndjson; charset=utf-8' if match['kind'] == 'jsonl' else 'application/json; charset=utf-8'
                return self.serve_file(Path(match['path']), {}, content_type)
            return self.serve_bytes(json.dumps({'error': 'not found', 'key': key}).encode('utf-8'))
        return super().do_GET()


if __name__ == '__main__':
    os.chdir(ROOT)
    port = int(os.getenv('PORT', '8787'))
    server = ThreadingHTTPServer(('0.0.0.0', port), Handler)
    print(f'Serving ops-dashboard on http://0.0.0.0:{port}')
    server.serve_forever()
