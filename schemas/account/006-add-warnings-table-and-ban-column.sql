-- account.006.add-warnings-table-and-ban-column migration
ALTER TABLE accounts ADD COLUMN banned BOOLEAN DEFAULT 0;

CREATE TABLE warnings (
    id INTEGER,
    account_id INTEGER,
    reason TEXT,
    PRIMARY KEY (account_id, id),
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);
