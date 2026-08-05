# Supabase + Vercel Migration Plan

**Goal:** edits and additions save without `collection_server.py` running, and the dashboard
is hosted on Vercel with `git push` to deploy.

**Decisions made:**
- Supabase is the source of truth; the xlsx becomes a historical artifact
- The SCP/eBay scraper stays local, run on demand
- Supabase email login gates writes; reads stay public
- Built alongside the current dashboard, cut over only once verified

---

## 1. Why `_row` is the thing that has to go

Every record today is identified by `_row` — its literal row number in the xlsx. The server
finds a card by scanning `ws.iter_rows()` for a matching row number, with player+card_no as a
fallback. Delete a row and every `_row` beneath it shifts by one, so any stale reference in an
open browser tab now points at the wrong card.

Each table gets a real `id` primary key. `_row` is used once during import to match records up,
then dropped. This is the single most valuable part of the migration.

## 2. Schema

Eight tables, ~1,900 rows. `summary` is deliberately **not** a table — it becomes a Postgres
view, so the totals can't drift from the cards the way `total_pl` did.

| Table | Rows | Key columns |
|---|---|---|
| `cards` | 79 | binder, player, year, parallel, card_no, type, card_price, shipping, taxes, scp_value, tmv, comps (jsonb), status, scp_url |
| `checklist_cards` | 1,170 | set_year, set_key, card_no, player, team, owned |
| `rookies` | 63 | player, team, year, card_title, set, card_no, value, collected, wishlist |
| `singles_transactions` | 55 | player, product, price, date |
| `watchlist` | 13 | player, price_tier |
| `wax_transactions` | 4 | product, price, date |
| `fav_players` | 0 | player, tier |
| `valuation_history` | — | replaces npoint.io + localStorage |

Derived columns (`cost`, `pl`, `pl_dollars`) become generated columns or view fields rather than
stored values, so they cannot go stale.

Note: `watchlist` currently exists in **two** places — the xlsx and browser localStorage
(`WL_KEY`). The migration collapses these into one table.

## 3. Files

**New**
- `supabase/schema.sql` — tables, the summary view, RLS policies
- `scripts/import_to_supabase.py` — one-time load from `collection_data.json`
- `index.html` — the Supabase-backed dashboard (built alongside the current file)
- `vercel.json`, `.env.example`

**Changed**
- `collection_server.py` — shrinks to `/api/scp` + `/health`. The eight write endpoints and the
  auto-commit-and-push block are deleted.

**Unchanged / retired**
- `baseball_collection.html` — left working until cutover, then retired
- `build_collection.py` — retired; nothing to rebuild once data lives in Postgres

## 4. Frontend changes

- Data loads via a Supabase query on page load instead of the baked-in `const DATA = {...}`
- ~20 `fetch('localhost:5055/api/...')` mutation calls become Supabase client calls
- All 6 `/api/rebuild` calls are removed outright
- CSP `connect-src` gains the Supabase project URL; `http://localhost:5055` stays for the scraper
- The page probes `/health` and greys out only the SCP buttons when the scraper is offline —
  every other feature works with it stopped

## 5. Auth

Reads are public; writes require a signed-in session, enforced by RLS server-side (not merely
hidden in the UI). A small email login appears in the corner; signed out, the dashboard is
read-only.

**Security note:** the anon key is public by design and safe to commit — RLS is what actually
protects the data. The `service_role` key must never go in the repo; it is only used locally by
the import script, via `.env`.

## 6. Sequence

1. You create the Supabase project and send me the project URL + anon key
2. I apply `schema.sql` and run the import; we verify all ~1,900 rows landed correctly
3. I build `index.html` against Supabase
4. Verify side by side against the current dashboard — same totals, same counts
5. You connect the repo to Vercel and add the env vars
6. Cut over: `index.html` becomes the live dashboard, `baseball_collection.html` is retired

Steps 1 and 5 need your account credentials, so you'll do those — I'll give you the exact values
to paste. I won't ask you for passwords, and no key beyond the public anon key goes in the repo.

## 7. Rollback

Until step 6, the current dashboard is untouched and keeps working. The xlsx stays in the repo as
a snapshot, so a bad import is recoverable by re-running the import script.
