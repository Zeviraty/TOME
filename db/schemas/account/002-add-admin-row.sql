-- account.002.add-admin-row migration
ALTER TABLE accounts ADD COLUMN admin BOOLEAN DEFAULT 0;
