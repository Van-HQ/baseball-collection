#!/usr/bin/env python3
"""
build_collection.py — Rebuild the baseball collection dashboard from the xlsx.

Usage:
    python3 build_collection.py

Reads:  ~/Downloads/Baseball Collection.xlsx
Writes: collection_data.json  (same folder as this script)
        baseball_collection.html  (updates const DATA = {...} in-place)
"""

import json, re, sys
from pathlib import Path
import openpyxl

XLSX    = Path.home() / 'Downloads' / 'Baseball Collection.xlsx'
HERE    = Path(__file__).parent
HTML    = HERE / 'baseball_collection.html'
JSON_OUT = HERE / 'collection_data.json'


def _float(v, default=0.0):
    try:   return float(v) if v is not None else default
    except: return default

def _str(v):
    return str(v).strip() if v is not None else ''

def _date(v):
    if v is None: return ''
    if hasattr(v, 'strftime'): return v.strftime('%Y-%m-%d')
    return str(v)


# ── Sheets ────────────────────────────────────────────────────────────────────

def parse_bowman(ws):
    """Row 1 = merged title, Row 2 = headers, Row 3+ = card data."""
    cards = []
    for row in ws.iter_rows(min_row=3, values_only=True):
        player = _str(row[1])
        if not player:
            continue
        cards.append({
            'binder':    _str(row[0]),
            'player':    player,
            'year':      int(row[2]) if row[2] else None,
            'parallel':  _str(row[3]),
            'card_no':   _str(row[4]),
            'type':      _str(row[8]),
            'cost':      round(_float(row[12]), 2),   # Total col
            'scp_value': round(_float(row[13]), 2),
            'tmv':       round(_float(row[14]), 2),
            'pl':        round(_float(row[15]), 2),
        })
    return cards


def parse_fav_players(ws):
    """Row 1 = headers, Row 2+ = data."""
    favs = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0]: continue
        favs.append({
            'player':      _str(row[0]),
            'team':        _str(row[1]),
            'rank':        _float(row[2]) if row[2] else None,
            'level':       _str(row[3]),
            'favorite':    bool(row[4]),
            'rookie_year': _str(row[5]),
        })
    return favs


def parse_watchlist(ws):
    """Row 1 = headers, Row 2+ = data."""
    wl = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0]: continue
        wl.append({
            'player':     _str(row[0]),
            'price_tier': _str(row[1]),
        })
    return wl


def parse_transactions(ws):
    """
    Row 1: section labels  (Ripping Wax | Slinging Singles)
    Row 2: column headers  (Product, Price, Date | Player, Product, Price, Date)
    Row 3: totals row      (Total, <sum>, ... | Total, None, <sum>, ...)
    Row 4+: individual transactions
    """
    wax, singles = [], []
    for row in ws.iter_rows(min_row=3, values_only=True):
        if _str(row[0]).lower() == 'total':
            continue  # skip totals row; we sum dynamically below
        if row[0] and row[1] is not None:
            wax.append({
                'product': _str(row[0]),
                'price':   round(_float(row[1]), 2),
                'date':    _date(row[2]),
            })
        if row[3] and row[5] is not None:
            singles.append({
                'player':  _str(row[3]),
                'product': _str(row[4]),
                'price':   round(_float(row[5]), 2),
                'date':    _date(row[6]),
            })
    return wax, singles


def parse_rookies(ws):
    """Row 1 = 'Favorite Rookie' label, Row 2 = headers, Row 3+ = data."""
    rookies = []
    for row in ws.iter_rows(min_row=3, values_only=True):
        if not row[0]: continue
        rookies.append({
            'player':     _str(row[0]),
            'team':       _str(row[1]),
            'year':       int(row[2]) if row[2] else None,
            'card_title': _str(row[3]),
            'set':        _str(row[4]),
            'card_no':    _str(row[5]),
            'value':      round(_float(row[6]), 2),
            'collected':  bool(row[7]),
            'wishlist':   bool(row[8]),
        })
    return rookies


def parse_checklist(ws):
    """
    Multi-column layout with repeating groups of (#, Player, Team, [Year,] Own, spacer).
    Returns total/owned counts and individual card list.
    """
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return {'total': 0, 'owned': 0, 'cards': []}

    headers = rows[0]
    groups  = []  # (no_col, player_col, team_col, own_col)

    i = 0
    while i < len(headers):
        if headers[i] == '#' and i + 1 < len(headers) and headers[i + 1] == 'Player':
            team_col = i + 2 if i + 2 < len(headers) and headers[i + 2] == 'Team' else None
            for j in range(i + 2, min(i + 7, len(headers))):
                if headers[j] == 'Own':
                    groups.append((i, i + 1, team_col, j))
                    i = j + 2
                    break
            else:
                i += 1
        else:
            i += 1

    total = owned = 0
    cards = []
    for row in rows[1:]:
        for no_col, player_col, team_col, own_col in groups:
            if player_col >= len(row) or not row[player_col]:
                continue
            card_no  = _str(row[no_col])
            player   = _str(row[player_col])
            team     = _str(row[team_col]) if team_col and team_col < len(row) else ''
            is_owned = bool(row[own_col]) if own_col < len(row) and row[own_col] is not None else False
            total += 1
            if is_owned: owned += 1
            cards.append({'no': card_no, 'player': player, 'team': team, 'owned': is_owned})

    return {'total': total, 'owned': owned, 'cards': cards}


# ── Main ──────────────────────────────────────────────────────────────────────

def build():
    if not XLSX.exists():
        print(f'✗  Not found: {XLSX}')
        sys.exit(1)

    print(f'Reading {XLSX.name} ...')
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)

    cards       = parse_bowman(wb['Bowman'])
    fav_players = parse_fav_players(wb['Favorite Players']) if 'Favorite Players' in wb.sheetnames else []
    watchlist   = parse_watchlist(wb['Watchlist'])
    wax, singles = parse_transactions(wb['Transactions'])
    rookies     = parse_rookies(wb['Rookies'])
    cl_2026     = parse_checklist(wb['Bowman 2026'])
    cl_2025     = parse_checklist(wb['Bowman 2025'])
    wb.close()

    wax_spent     = round(sum(t['price'] for t in wax), 2)
    singles_spent = round(sum(t['price'] for t in singles), 2)
    total_cost    = round(sum(c['cost'] for c in cards), 2)
    total_tmv     = round(sum(c['tmv']  for c in cards), 2)
    total_pl      = round(sum(c['pl']   for c in cards), 2)

    data = {
        'summary': {
            'total_cards':   len(cards),
            'total_cost':    total_cost,
            'total_tmv':     total_tmv,
            'total_pl':      total_pl,
            'wax_spent':     wax_spent,
            'singles_spent': singles_spent,
        },
        'cards':                cards,
        'fav_players':          fav_players,
        'watchlist':            watchlist,
        'wax_transactions':     wax,
        'singles_transactions': singles,
        'rookies':              rookies,
        'checklist': {
            'bowman_2026': cl_2026,
            'bowman_2025': cl_2025,
        },
    }

    # Write JSON sidecar
    JSON_OUT.write_text(json.dumps(data, indent=2))
    print(f'✓  {JSON_OUT.name}  ({len(cards)} cards)')

    # Patch the HTML — replace const DATA = {...};
    if not HTML.exists():
        print(f'✗  HTML not found: {HTML}')
        sys.exit(1)

    html = HTML.read_text()
    new_block = f'const DATA = {json.dumps(data, separators=(",", ":"))};'
    patched, n = re.subn(r'const DATA = \{.*?\};', lambda _: new_block, html, flags=re.DOTALL)
    if n == 0:
        print('✗  Could not locate "const DATA = {...}" in HTML — file not updated')
        sys.exit(1)

    HTML.write_text(patched)
    print(f'✓  {HTML.name}  (DATA block replaced)')

    print(f'\n{"─"*46}')
    print(f'  Cards        {len(cards):>6}')
    print(f'  Total Cost   ${total_cost:>9.2f}')
    print(f'  Total TMV    ${total_tmv:>9.2f}')
    print(f'  P/L          ${total_pl:>+9.2f}')
    print(f'  Wax spent    ${wax_spent:>9.2f}')
    print(f'  Singles      ${singles_spent:>9.2f}')
    print(f'  CL 2026      {cl_2026["owned"]:>3}/{cl_2026["total"]}')
    print(f'  CL 2025      {cl_2025["owned"]:>3}/{cl_2025["total"]}')
    print(f'{"─"*46}')
    print('  Done. Reload baseball_collection.html in your browser.')


if __name__ == '__main__':
    build()
