-- account.004.drop-builder-and-admin-rows migration
ALTER TABLE accounts DROP COLUMN admin;
ALTER TABLE accounts DROP COLUMN builder;
