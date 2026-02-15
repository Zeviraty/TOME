CREATE TABLE characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    class TEXT,
    account_id INTEGER,
    FOREIGN KEY(account_id) REFERENCES accounts(id)
);

CREATE TABLE character_attributes (
    character_id INTEGER,
    attr_name TEXT,
    attr_value VARCHAR,
    FOREIGN KEY(character_id) REFERENCES characters(id)
);
