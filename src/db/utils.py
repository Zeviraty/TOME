import sqlite3
from datetime import datetime
import shutil,os

def resolve_schema_path(schema_name, base_path="db/schemas", ext=".sql"):
    """Convert schema name like 'test.001' into a path like 'db/schemas/test/001-*.sql'."""
    parts = schema_name.split(".")
    if len(parts) != 2:
        raise ValueError(f"Invalid schema name format: '{schema_name}'. Use format 'folder.number'.")

    folder, number = parts
    schema_dir = os.path.join(base_path, folder)

    if not os.path.isdir(schema_dir):
        raise FileNotFoundError(f"Schema directory '{schema_dir}' does not exist.")

    # Look for a file like 001-*.sql
    for file in os.listdir(schema_dir):
        if ext != "down.sql":
            if file.endswith("down.sql"):
                continue
        if (file.startswith(f"{number}-") or file.startswith(f"{number}")) and file.endswith(ext):
            return os.path.join(schema_dir, file)

    raise FileNotFoundError(f"No matching schema file found for '{schema_name}' in '{schema_dir}'")

def backup_db():
    if os.path.exists("db/database.db"):
        dt_string = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        shutil.copy("db/database.db", f"db/backups/{dt_string}.db")

def get() -> sqlite3.Connection:
    return sqlite3.connect('db/database.db', timeout=100.0)

def get_latest_backup():
    datetime_format = "%d-%m-%Y_%H-%M-%S"
    backups = []

    for filename in os.listdir("db/backups"):
        if filename.endswith(".db"):
            dt_str = filename[:-3]
            try:
                dt = datetime.strptime(dt_str, datetime_format)
                backups.append((dt, filename))
            except ValueError:
                continue

    if not backups:
        return None

    return max(backups)[1]

def init_db(dobackup=True, clickecho=False):
    if clickecho:
        click.echo("Initializing database...")
    else:
        print("Initializing database...")

    if not os.path.exists("db/backups"):
        os.mkdir("db/backups")

    if dobackup:
        backup_db()

    fail = False

    conn = get()
    cursor = conn.execute("SELECT name FROM migrations")
    applied = {row[0] for row in cursor.fetchall()}
    conn.close()

    for root, _, files in os.walk("db/schemas"):
        dirname = os.path.basename(root)

        files.sort()

        for schema in files:
            if not schema.endswith(".sql"):
                continue
            schema_name = schema.replace(".sql", "")
            schema_path = "db/schemas/"+dirname+"/"+schema_name+".sql"
            display_name = f"{dirname}.{schema_name}" if dirname != "schemas" else schema_name

            if display_name in applied:
                continue
            if schema.endswith(".down.sql"):
                continue

            conn = get()
            message = f"Executing {display_name}... "

            if clickecho:
                click.echo(message, nl=False)
            else:
                print(message, end="")

            try:
                with open(schema_path, 'r') as file:
                    conn.executescript(file.read())
            except Exception as e:
                status = "\033[0;31mFailed\033[0m\n" + str(e)
                fail = True
                conn.execute(
                    "INSERT INTO migration_errors (name, error) VALUES (?, ?)",
                    (schema_path, str(e))
                )
                conn.commit()
                conn.close()
            else:
                status = "\033[0;32mOk\033[0m"
                conn.execute("INSERT INTO migrations (name) VALUES (?)", (display_name,))
                conn.commit()
                conn.close()

            if clickecho:
                click.echo(status)
            else:
                print(status)
    if clickecho:
        click.echo("Database initialized." if fail == False else "Errors during initializing database.")
    else:
        print("Database initialized." if fail == False else "Errors during initializing database.")
