-- Table-level grants — run once after schema.sql.
--
-- RLS policies control *which rows* a role can see/touch; these GRANTs
-- control whether the role can touch the table at all. Both layers are
-- required. This step only exists because "Automatically expose new
-- tables" was unchecked at project creation (the safer default) — that
-- setting is what normally runs these grants for you.

grant usage on schema public to anon, authenticated, service_role;

grant select on all tables in schema public to anon, authenticated;
grant insert, update, delete on all tables in schema public to authenticated;

-- service_role bypasses RLS entirely, but still needs base grants
grant all on all tables in schema public to service_role;

-- Applies to future tables created the same way, so this doesn't need
-- re-running every time the schema grows.
alter default privileges in schema public grant select on tables to anon, authenticated;
alter default privileges in schema public grant insert, update, delete on tables to authenticated;
alter default privileges in schema public grant all on tables to service_role;
