-- Fifth migration step. Adds shipping + tax to the valuation calculator so
-- Max Bid can be computed as a true all-in budget ceiling (item + shipping
-- + CA sales tax), not just a raw fraction of TMV.

alter table valuation_entries
  add column shipping numeric(10,2) default 0,
  add column tax numeric(10,2) default 0;
