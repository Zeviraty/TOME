import shutil,os
import click
from trogon import tui
from utils import *

@tui()
@click.group()
def cli():
    """Database management"""
    pass

@cli.command()
@click.option("--force", is_flag=True, help="Force destructive action.")
def full_init(force) -> None:
    if os.path.exists("db/database.db") and not force:
        yn = input("This is destructive do you want to do this? (y/N): ")
        if yn.lower() != "y":
            return
    click.echo("Creating directories...")
    if not force:
        backup_db()
    if os.path.exists("db/database.db"):
        os.remove("db/database.db")
    for i in ["db","db/schemas","db/backups"]:
        if not os.path.exists(i):
            click.echo(f"Creating {i}...")
            os.makedirs(i)
            click.echo(f"Created {i}")
    click.echo("Created directories.")

    click.echo("Creating migrations table.")
    conn = get()
    conn.executescript('''
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY,
    name TEXT,
    applied_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS migration_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    error TEXT NOT NULL,
    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);''')
    conn.commit()
    conn.close()
    click.echo("Created migrations table.")

    click.echo("Creating database...")
    init_db(False)
    click.echo("Created database.")

    click.echo("Fully initialized the database.")

@cli.command()
def backup():
    click.echo("Starting backup...")
    backup_db()
    click.echo("Created backup!")

@cli.command()
@click.argument('date')
def revert(date):
    dobackup = input("Do you want to backup now? Y/n: ")

    last = get_latest_backup()

    if dobackup.lower() != "n":
        backup_db()

    if date == "last":
        if last == None:
            print("No last backup")
            return
        shutil.copy(f"db/backups/{last}","db/database.db")
        print(f"reverted to: {last}")
    else:
        if os.path.exists(f"db/backups/{date}"):
            shutil.copy(f"db/backups/{date}","db/database.db")
            print(f"reverted to: {date}")
        else:
            print("No backup from that date")

@cli.command()
def init():
    init_db(True,True)

@cli.group()
def schema():
    """Schema management"""

@schema.command()
@click.argument("schema")
@click.option("--force", is_flag=True, help="Force apply even if already applied.")
def apply(schema,force):
    try:
        path = resolve_schema_path(schema)
    except Exception as e:
        click.echo(f"Schema resolution error: {e}")
        return

    if not os.path.exists(path):
        print(f"Schema: {path} does not exist.")
        return

    conn = get()
    cursor = conn.execute("SELECT name FROM migrations")
    applied = {row[0] for row in cursor.fetchall()}
    conn.close()

    if schema in applied and not force:
        yn = input("That schema is already applied. Do you want to apply it again (may be destructive)? y/N: ")
        if yn.lower() != "y":
            return

    conn = get()
    message = f"Executing {schema}... "
    click.echo(message, nl=False)

    try:
        with open(path, 'r') as file:
            conn.executescript(file.read())
    except Exception as e:
        status = "\033[0;31mFailed\033[0m\n" + str(e)

        # Log to migration_errors
        conn.execute(
            "INSERT INTO migration_errors (name, error) VALUES (?, ?)",
            (path, str(e))
        )
        conn.commit()
        conn.close()
    else:
        status = "\033[0;32mOk\033[0m"
        conn.execute("INSERT INTO migrations (name) VALUES (?)", (schema,))
        conn.commit()
        conn.close()

    click.echo(status)

@schema.command()
@click.argument("schema")
@click.argument("name")
def new(schema, name):
    folder, number = schema.split(".")
    filename = f"{number}-{name}.sql"
    down_filename = f"{number}-{name}.down.sql"
    dir_path = os.path.join("db/schemas", folder)
    os.makedirs(dir_path, exist_ok=True)
    up_path = os.path.join(dir_path, filename)
    down_path = os.path.join(dir_path, down_filename)

    for path in [up_path, down_path]:
        if not os.path.exists(path):
            with open(path, "w") as f:
                if path.endswith(".down.sql"):
                    f.write(f"-- {schema}.{name}.down migration\n")
                else:
                    f.write(f"-- {schema}.{name} migration\n")
            click.echo(f"Created {path}")
        else:
            click.echo(f"File {path} already exists.")

@schema.command()
def list():
    """List applied migrations"""
    conn = get()
    cursor = conn.execute("SELECT name, applied_at FROM migrations ORDER BY applied_at")
    migrations = cursor.fetchall()
    conn.close()

    if migrations:
        click.echo("Applied migrations:")
        for name, applied_at in migrations:
            click.echo(f" - {name} @ {applied_at}")
    else:
        click.echo("No migrations have been applied yet.")

    unapplied = []
    for root, _, files in os.walk("db/schemas"):
        dirname = os.path.basename(root)

        for schema in files:
            schema_name = schema.replace(".sql", "")
            display_name = f"{dirname}.{schema_name}" if dirname != "schemas" else schema_name

            if len([item for item in migrations if item[0] == display_name]) != 0:
                continue
            if schema.endswith(".down.sql"):
                continue

            unapplied.append(display_name)

    if len(unapplied) != 0:
        click.echo("Pending migrations:")
        for name in unapplied:
            click.echo(f" - {name}")
    else:
        click.echo("No migrations are pending.")


@schema.command()
@click.argument("Schema")
def rollback(schema):
    """Rollback a migration, if a .down.sql file exists."""
    try:
        down_path = resolve_schema_path(schema,ext="down.sql")
    except Exception as e:
        click.echo(f"Schema resolution error: {e}")
        return

    if not os.path.exists(down_path):
        click.echo(f"No rollback file found for {schema}")
        return

    conn = get()
    try:
        with open(down_path, 'r') as file:
            conn.executescript(file.read())
        conn.execute("DELETE FROM migrations WHERE name LIKE ?", (schema + '%',))
        conn.commit()
        status = "\033[0;32mRolled back\033[0m"
    except Exception as e:
        status = "\033[0;31mFailed\033[0m\n" + str(e)
    finally:
        conn.close()

    click.echo(status)

@schema.command()
def apply_all():
    """Apply all pending migrations"""
    conn = get()
    cursor = conn.execute("SELECT name FROM migrations")
    applied = {row[0] for row in cursor.fetchall()}
    conn.close()

    all_files = []
    for root, _, files in os.walk("db/schemas"):
        files.sort()
        for file in files:
            if file.endswith(".sql") and not file.endswith(".down.sql"):
                rel = os.path.relpath(os.path.join(root, file), "db/schemas")
                schema = rel.replace("/", ".").replace("\\", ".").replace(".sql", "")
                all_files.append((schema, os.path.join(root, file)))

    all_files.sort()  # Optional: ensure consistent order

    for schema, _ in all_files:
        if schema not in applied:
            #click.echo(f"Applying {schema}...")
            ctx = click.get_current_context()
            ctx.invoke(apply, schema=schema)

@schema.command()
def errors():
    """Show logged migration errors"""
    conn = get()
    cursor = conn.execute(
        "SELECT id, name, error, occurred_at FROM migration_errors ORDER BY occurred_at DESC LIMIT 10"
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        click.echo("No migration errors logged.")
        return

    click.echo("Recent migration errors:")
    for row in rows:
        click.echo(f"\n#{row[0]} | {row[1]} @ {row[3]}\n → {row[2]}")

@schema.command()
def clear_errors():
    """Clear all logged migration errors"""
    conn = get()
    conn.execute("DELETE FROM migration_errors")
    conn.commit()
    conn.close()
    click.echo("Cleared all migration errors.")

@cli.command()
@click.argument("table")
def table(table):
    conn = get()
    data = conn.execute(f"PRAGMA table_info({table});").fetchall()
    if len(data) == 0:
        print("Table doesnt exist.")
        return

    maxlen_id = max([len(str(item[0])) for item in data])
    maxlen_name = max([len(str(item[1])) for item in data])
    maxlen_type = max([len(str(item[2])) for item in data])
    maxlen_nn = max([len(str(item[3])) for item in data])

    print(f"id{' '*(maxlen_id-2)}|name{' '*(maxlen_name-4)}|type{' '*(maxlen_type-4)}|nn{' '*(maxlen_nn-2)}|")
    print(f"--{'-'*(maxlen_id-2)}|----{'-'*(maxlen_name-4)}|----{'-'*(maxlen_type-4)}|--{'-'*(maxlen_nn-2)}|")
    for item in data:
        print(f"id{' ' * (maxlen_id - 2)}|name{' ' * (maxlen_name - 4)}|type{' ' * (maxlen_type - 4)}|nn{' ' * (maxlen_nn - 2)}|")

if __name__ == '__main__':
    cli()
