-- account.003.add-builder-row migration
ALTER TABLE accounts ADD COLUMN builder BOOLEAN DEFAULT 0;
