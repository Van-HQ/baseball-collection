-- Third migration step. The "mark as sold" flow on the Valuation page
-- needed three more columns that weren't visible until the mutation
-- functions were inspected in detail.

alter table valuation_entries
  add column status text,               -- 'sold' | null
  add column sold_price numeric(10,2),
  add column sold_date date;
