-- account.005.create-account-privileges-table migration
CREATE TABLE account_privileges (
    account_id INTEGER,
    privilege TEXT,
    PRIMARY KEY (account_id, privilege)
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);
