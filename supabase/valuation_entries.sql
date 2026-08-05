-- Second migration step, run after schema.sql + grants.sql.
--
-- This is the Valuation page's real data model: every analyzed listing with
-- its BUY/PASS decision, discount %, max bid, and hold/flip/purchased state.
-- It previously lived in npoint.io + localStorage, discovered mid-migration
-- to be much richer than simple price history — see chat for context.
--
-- No separate grants needed: the "alter default privileges" statements in
-- grants.sql already apply to any table created afterward in this schema.

create table valuation_entries (
  id            uuid primary key default gen_random_uuid(),
  legacy_id     bigint,                  -- the old JS Date.now() id, kept for reference only
  entry_date    date,
  player        text,
  year          text,
  parallel      text,
  card_no       text,
  scp_url       text,
  type          text,                    -- 'S/N' | 'AUTO' | ...
  listing       numeric(10,2),
  tmv           numeric(10,2),
  discount      numeric(6,4),
  max_bid       numeric(10,2),
  decision      text,                    -- 'BUY' | 'PASS'
  comps         jsonb default '[]'::jsonb,
  price_goal    numeric(10,2),
  notes         text,
  hold_flip     text,                    -- 'hold' | 'flip' | 'watching'
  purchased     boolean default false,
  purchase_date date,
  created_at    timestamptz default now()
);

create index valentries_player_idx on valuation_entries (player);

alter table valuation_entries enable row level security;

create policy "valuation_entries public read" on valuation_entries for select using (true);
create policy "valuation_entries auth write" on valuation_entries for insert with check (auth.role() = 'authenticated');
create policy "valuation_entries auth update" on valuation_entries for update using (auth.role() = 'authenticated');
create policy "valuation_entries auth delete" on valuation_entries for delete using (auth.role() = 'authenticated');
