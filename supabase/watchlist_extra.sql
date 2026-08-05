-- Fourth migration step. The watchlist add/edit modal also uses `notes`
-- and an `added` date that weren't in the original watchlist table.

alter table watchlist
  add column notes text,
  add column added date default current_date;
