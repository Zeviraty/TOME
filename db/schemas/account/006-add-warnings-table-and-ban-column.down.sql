-- account.006.add-warnings-table-and-ban-column.down migration
DROP TABLE warnings;
ALTER TABLE accounts DROP COLUMN banned;
