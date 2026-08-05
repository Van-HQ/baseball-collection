-- Baseball Collection — Supabase schema
--
-- Design notes:
--   * Every table gets a real `id` primary key. The old system identified
--     records by `_row` (their literal xlsx row number), which broke the
--     moment a row was deleted and everything below it shifted. Nothing
--     here depends on row position ever again.
--   * `cost` / `pl` / `pl_dollars` on `cards` are generated columns, not
--     stored values — they can't drift out of sync the way `total_pl` did
--     in the old xlsx (it silently ignored wax spend for months).
--   * `summary` is a view, not a table, for the same reason.
--   * RLS: reads are public, writes require an authenticated session.
--     "Enable automatic RLS" on the project already turns RLS on for new
--     tables by default; the policies below are the explicit versions of
--     that so the schema is self-documenting and portable.

-- ── cards ────────────────────────────────────────────────────────────────
create table cards (
  id          uuid primary key default gen_random_uuid(),
  binder      text,                    -- slot, e.g. "1.1" — display/sort only, not an identifier
  player      text not null,
  year        integer,
  parallel    text,
  card_no     text,
  type        text,                    -- 'Ripped' | 'Auction'
  card_price  numeric(10,2) default 0,
  shipping    numeric(10,2) default 0,
  taxes       numeric(10,2) default 0,
  cost        numeric(10,2) generated always as (card_price + shipping + taxes) stored,
  scp_value   numeric(10,2),
  tmv         numeric(10,2),
  pl          numeric(10,2) generated always as (
                case when (card_price + shipping + taxes) > 0
                  then ((coalesce(tmv,0) - (card_price + shipping + taxes)) / (card_price + shipping + taxes)) * 100
                  else 0
                end
              ) stored,
  pl_dollars  numeric(10,2) generated always as (coalesce(tmv,0) - (card_price + shipping + taxes)) stored,
  comps       jsonb default '[]'::jsonb,   -- array of up to 5 recent comp prices
  status      text,                    -- 'sell' | 'hold' | 'flip' | null
  scp_url     text,
  created_at  timestamptz default now(),
  updated_at  timestamptz default now()
);

create index cards_player_idx on cards (player);
create index cards_status_idx on cards (status);

-- ── rookies ──────────────────────────────────────────────────────────────
create table rookies (
  id          uuid primary key default gen_random_uuid(),
  player      text not null,
  team        text,
  year        integer,
  card_title  text,
  set_name    text,                    -- "set" is a reserved word in some contexts, avoid it
  card_no     text,
  value       numeric(10,2),
  collected   boolean default false,
  wishlist    boolean default false,
  created_at  timestamptz default now()
);

-- ── watchlist ────────────────────────────────────────────────────────────
-- Replaces both the xlsx Watchlist sheet AND the browser-localStorage copy
-- (WL_KEY) that used to exist alongside it as a second, divergeable source.
create table watchlist (
  id          uuid primary key default gen_random_uuid(),
  player      text not null unique,
  price_tier  text,                    -- 'Low' | 'Medium' | 'High'
  created_at  timestamptz default now()
);

-- ── fav_players ──────────────────────────────────────────────────────────
create table fav_players (
  id           uuid primary key default gen_random_uuid(),
  player       text not null,
  team         text,
  rank         numeric(10,2),
  level        text,
  favorite     boolean default false,
  rookie_year  text,
  created_at   timestamptz default now()
);

-- ── wax_transactions ─────────────────────────────────────────────────────
create table wax_transactions (
  id          uuid primary key default gen_random_uuid(),
  product     text,
  price       numeric(10,2),
  txn_date    date,
  created_at  timestamptz default now()
);

-- ── singles_transactions ─────────────────────────────────────────────────
create table singles_transactions (
  id          uuid primary key default gen_random_uuid(),
  player      text,
  product     text,
  price       numeric(10,2),
  txn_date    date,
  created_at  timestamptz default now()
);

-- ── checklist_cards ──────────────────────────────────────────────────────
-- Both Bowman 2026 and 2025 checklists (~1,170 rows) live in one table,
-- distinguished by set_year. `set_key`/`set_prefix`/`set_name` describe
-- which of the 8 insert sets per year a card belongs to (Base, BCP, ES...).
create table checklist_cards (
  id          uuid primary key default gen_random_uuid(),
  set_year    text not null,           -- '2026' | '2025'
  set_key     text not null,           -- e.g. 'base', 'bcp'
  set_prefix  text,                    -- e.g. 'BCP'
  set_name    text,                    -- e.g. 'Chrome Prospect Autographs'
  card_no     text,
  player      text,
  team        text,
  owned       boolean default false
);

create index checklist_year_set_idx on checklist_cards (set_year, set_key);

-- ── valuation_history ────────────────────────────────────────────────────
-- Replaces the npoint.io + localStorage valuation-history sync.
create table valuation_history (
  id          uuid primary key default gen_random_uuid(),
  player      text not null,
  value       numeric(10,2) not null,
  recorded_at timestamptz default now()
);

create index valhist_player_idx on valuation_history (player, recorded_at);

-- ── summary (view, not a table — cannot go stale) ───────────────────────
create view summary as
select
  (select count(*) from cards)                                as total_cards,
  (select coalesce(sum(cost), 0) from cards)                  as total_cost,
  (select coalesce(sum(tmv), 0) from cards)                   as total_tmv,
  (select coalesce(sum(pl_dollars), 0) from cards)            as total_pl_dollars,
  (select coalesce(sum(price), 0) from wax_transactions)      as wax_spent,
  (select coalesce(sum(price), 0) from singles_transactions)  as singles_spent,
  (
    (select coalesce(sum(cost), 0) from cards) +
    (select coalesce(sum(price), 0) from wax_transactions)
  )                                                            as total_cost_basis,
  (
    (select coalesce(sum(tmv), 0) from cards) -
    (
      (select coalesce(sum(cost), 0) from cards) +
      (select coalesce(sum(price), 0) from wax_transactions)
    )
  )                                                            as total_pl,
  case when (
    (select coalesce(sum(cost), 0) from cards) +
    (select coalesce(sum(price), 0) from wax_transactions)
  ) > 0 then (
    (
      (select coalesce(sum(tmv), 0) from cards) -
      (
        (select coalesce(sum(cost), 0) from cards) +
        (select coalesce(sum(price), 0) from wax_transactions)
      )
    ) / (
      (select coalesce(sum(cost), 0) from cards) +
      (select coalesce(sum(price), 0) from wax_transactions)
    )
  ) * 100 else 0 end                                            as total_pl_pct;

-- ── updated_at trigger (cards only — the table that gets edited live) ──
create or replace function set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger cards_set_updated_at
  before update on cards
  for each row
  execute function set_updated_at();

-- ── Row Level Security ──────────────────────────────────────────────────
-- Public read, authenticated write. This mirrors what "Enable automatic
-- RLS" already turns on by default; written out explicitly here so the
-- policy is visible and portable rather than implicit project config.

alter table cards                 enable row level security;
alter table rookies               enable row level security;
alter table watchlist             enable row level security;
alter table fav_players           enable row level security;
alter table wax_transactions      enable row level security;
alter table singles_transactions  enable row level security;
alter table checklist_cards       enable row level security;
alter table valuation_history     enable row level security;

do $$
declare
  t text;
begin
  foreach t in array array[
    'cards','rookies','watchlist','fav_players',
    'wax_transactions','singles_transactions','checklist_cards','valuation_history'
  ]
  loop
    execute format('create policy "%s public read" on %I for select using (true);', t, t);
    execute format('create policy "%s auth write" on %I for insert with check (auth.role() = ''authenticated'');', t, t);
    execute format('create policy "%s auth update" on %I for update using (auth.role() = ''authenticated'');', t, t);
    execute format('create policy "%s auth delete" on %I for delete using (auth.role() = ''authenticated'');', t, t);
  end loop;
end $$;

-- `summary` is a view over already-RLS-protected tables, so it inherits
-- their read policy automatically — no separate grant needed.
