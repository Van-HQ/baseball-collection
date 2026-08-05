#!/usr/bin/env python3
"""
import_valuation_entries.py — one-time load of the Valuation page's analysis
log (BUY/PASS decisions, hold/flip state, purchase tracking) from npoint.io
into Supabase's valuation_entries table.

Usage:
  python3 scripts/import_valuation_entries.py            # import
  python3 scripts/import_valuation_entries.py --dry-run   # print count, write nothing

Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env (project root).
Run supabase/valuation_entries.sql in the SQL Editor before this.
"""
import json
import sys
from pathlib import Path

import requests

HERE = Path(__file__).parent.parent
ENV_PATH = HERE / '.env'

# The npoint.io bin the dashboard's Cloud Sync panel has been writing to.
# npoint bins are public-read by design (no auth needed to GET them).
NPOINT_ENDPOINT = 'https://api.npoint.io/c1250e70cd19951c451a'


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
        sys.exit(f"Missing from .env: {', '.join(missing)}")
    return env


def xf_entry(e):
    return {
        'legacy_id':     e.get('id'),
        'entry_date':    e.get('date'),
        'player':        e.get('player'),
        'year':          str(e.get('year')) if e.get('year') is not None else None,
        'parallel':      e.get('parallel'),
        'card_no':       e.get('cardno'),
        'scp_url':       e.get('scpUrl'),
        'type':          e.get('type'),
        'listing':       e.get('listing'),
        'tmv':           e.get('tmv'),
        'discount':      e.get('discount'),
        'max_bid':       e.get('maxBid'),
        'decision':      e.get('decision'),
        'comps':         e.get('comps') or [],
        'price_goal':    e.get('priceGoal'),
        'notes':         e.get('notes') or None,
        'hold_flip':     e.get('holdFlip'),
        'purchased':     bool(e.get('purchased')),
        'purchase_date': e.get('purchaseDate'),
    }


def main():
    dry_run = '--dry-run' in sys.argv
    env = load_env(require_service_key=not dry_run)
    base_url = env['SUPABASE_URL'].rstrip('/')

    print(f"Fetching {NPOINT_ENDPOINT} ...")
    resp = requests.get(NPOINT_ENDPOINT)
    resp.raise_for_status()
    entries = resp.json()
    if not isinstance(entries, list):
        sys.exit(f"Expected a JSON array from npoint, got {type(entries)}")

    rows = [xf_entry(e) for e in entries]
    print(f"{len(rows)} entries fetched")

    if dry_run:
        print(json.dumps(rows[0], indent=2) if rows else "(empty)")
        print(f"DRY RUN — would import {len(rows)} rows, wrote nothing")
        return

    key = env['SUPABASE_SERVICE_ROLE_KEY']
    r = requests.post(
        f"{base_url}/rest/v1/valuation_entries",
        headers={
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal',
        },
        data=json.dumps(rows),
    )
    if r.status_code >= 300:
        sys.exit(f"FAILED ({r.status_code}) {r.text[:500]}")
    print(f"Imported {len(rows)} rows into valuation_entries")


if __name__ == '__main__':
    main()
