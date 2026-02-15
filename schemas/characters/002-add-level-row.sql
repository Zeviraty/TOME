-- characters.002.add-level-row migration
ALTER TABLE characters ADD COLUMN lvl INTEGER DEFAULT 0;
