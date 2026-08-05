#!/usr/bin/env python3
"""
import_to_supabase.py — one-time load of collection_data.json into Supabase.

Usage:
  python3 scripts/import_to_supabase.py            # import everything
  python3 scripts/import_to_supabase.py --dry-run   # print counts, write nothing

Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env (project root).
The service_role key bypasses RLS, which is required here since this script
runs unauthenticated — never use it anywhere except this local script.

Safe to re-run: pass --wipe first to clear the target tables, otherwise
re-running duplicates rows (no unique constraint on cards/rookies/etc,
since none of their real-world fields are guaranteed unique).
"""
import json
import sys
from pathlib import Path

import requests

HERE = Path(__file__).parent.parent
ENV_PATH = HERE / '.env'
DATA_PATH = HERE / 'collection_data.json'

TABLE_ORDER = [
    'cards', 'rookies', 'watchlist', 'fav_players',
    'wax_transactions', 'singles_transactions', 'checklist_cards',
]


def load_env(require_service_key):
    env = {}
    if not ENV_PATH.exists():
        sys.exit(f"Missing {ENV_PATH}")
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip()
    required = ['SUPABASE_URL'] + (['SUPABASE_SERVICE_ROLE_KEY'] if require_service_key else [])
    missing = [k for k in required if not env.get(k)]
    if missing:
        sys.exit(f"Missing from .env: {', '.join(missing)}\n"
                  f"Add SUPABASE_SERVICE_ROLE_KEY from Project Settings -> API (never commit it).")
    return env


def post_rows(base_url, key, table, rows, dry_run):
    if not rows:
        print(f"  {table}: 0 rows, skipping")
        return
    if dry_run:
        print(f"  {table}: {len(rows)} rows (dry run, not written)")
        return
    resp = requests.post(
        f"{base_url}/rest/v1/{table}",
        headers={
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal',
        },
        data=json.dumps(rows),
    )
    if resp.status_code >= 300:
        sys.exit(f"  {table}: FAILED ({resp.status_code}) {resp.text[:500]}")
    print(f"  {table}: {len(rows)} rows imported")


def wipe_table(base_url, key, table):
    resp = requests.delete(
        f"{base_url}/rest/v1/{table}?id=not.is.null",
        headers={'apikey': key, 'Authorization': f'Bearer {key}'},
    )
    if resp.status_code >= 300:
        sys.exit(f"  {table}: wipe FAILED ({resp.status_code}) {resp.text[:500]}")
    print(f"  {table}: wiped")


# ── per-table transforms: collection_data.json shape -> schema.sql columns ──

def xf_cards(cards):
    return [{
        'binder':     c.get('binder'),
        'player':     c['player'],
        'year':       c.get('year'),
        'parallel':   c.get('parallel'),
        'card_no':    c.get('card_no'),
        'type':       c.get('type'),
        'card_price': c.get('card_price') or 0,
        'shipping':   c.get('shipping') or 0,
        'taxes':      c.get('taxes') or 0,
        'scp_value':  c.get('scp_value'),
        'tmv':        c.get('tmv'),
        'comps':      c.get('comps') or [],
        'status':     c.get('status') or None,
        'scp_url':    c.get('scp_url'),
    } for c in cards]


def xf_rookies(rookies):
    return [{
        'player':     r['player'],
        'team':       r.get('team'),
        'year':       r.get('year'),
        'card_title': r.get('card_title'),
        'set_name':   r.get('set'),
        'card_no':    r.get('card_no'),
        'value':      r.get('value'),
        'collected':  bool(r.get('collected')),
        'wishlist':   bool(r.get('wishlist')),
    } for r in rookies]


def xf_watchlist(watchlist):
    return [{
        'player':     w['player'],
        'price_tier': w.get('price_tier'),
    } for w in watchlist]


def xf_fav_players(favs):
    return [{
        'player':      f['player'],
        'team':        f.get('team'),
        'rank':        f.get('rank'),
        'level':       f.get('level'),
        'favorite':    bool(f.get('favorite')),
        'rookie_year': f.get('rookie_year'),
    } for f in favs]


def xf_wax(txns):
    return [{
        'product':  t.get('product'),
        'price':    t.get('price'),
        'txn_date': t.get('date'),
    } for t in txns]


def xf_singles(txns):
    return [{
        'player':   t.get('player'),
        'product':  t.get('product'),
        'price':    t.get('price'),
        'txn_date': t.get('date'),
    } for t in txns]


def xf_checklist(checklist):
    rows = []
    for year_key, year_label in (('bowman_2026', '2026'), ('bowman_2025', '2025')):
        cl = checklist.get(year_key)
        if not cl:
            continue
        for s in cl.get('sets', []):
            for card in s.get('cards', []):
                rows.append({
                    'set_year':   year_label,
                    'set_key':    s.get('key'),
                    'set_prefix': s.get('prefix'),
                    'set_name':   s.get('name'),
                    'card_no':    card.get('no'),
                    'player':     card.get('player'),
                    'team':       card.get('team'),
                    'owned':      bool(card.get('owned')),
                })
    return rows


def main():
    dry_run = '--dry-run' in sys.argv
    wipe = '--wipe' in sys.argv

    env = load_env(require_service_key=not dry_run)
    base_url = env['SUPABASE_URL'].rstrip('/')
    key = env.get('SUPABASE_SERVICE_ROLE_KEY', '')

    if not DATA_PATH.exists():
        sys.exit(f"Missing {DATA_PATH} — run build_collection.py first")
    data = json.loads(DATA_PATH.read_text())

    payload = {
        'cards':                 xf_cards(data.get('cards', [])),
        'rookies':               xf_rookies(data.get('rookies', [])),
        'watchlist':             xf_watchlist(data.get('watchlist', [])),
        'fav_players':          xf_fav_players(data.get('fav_players', [])),
        'wax_transactions':      xf_wax(data.get('wax_transactions', [])),
        'singles_transactions':  xf_singles(data.get('singles_transactions', [])),
        'checklist_cards':       xf_checklist(data.get('checklist', {})),
    }

    print(f"{'DRY RUN — ' if dry_run else ''}Importing into {base_url}")

    if wipe and not dry_run:
        print("Wiping target tables...")
        for t in reversed(TABLE_ORDER):
            wipe_table(base_url, key, t)

    for table in TABLE_ORDER:
        post_rows(base_url, key, table, payload[table], dry_run)

    print()
    print("NOTE: valuation_history was not imported — that data only ever lived in")
    print("browser localStorage / npoint.io, not in collection_data.json. If you want")
    print("the old value-history sparklines preserved, export it from the dashboard's")
    print("Cloud Sync panel (or localStorage key 'baseball_val_history') before cutover.")


if __name__ == '__main__':
    main()
