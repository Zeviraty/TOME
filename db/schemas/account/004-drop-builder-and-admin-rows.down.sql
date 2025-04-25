-- account.004.drop-builder-and-admin-rows.down migration
ALTER TABLE accounts ADD COLUMN admin BOOLEAN DEFAULT 0;
ALTER TABLE accounts ADD COLUMN builder BOOLEAN DEFAULT 0;
