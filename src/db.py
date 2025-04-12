import sqlite3
from datetime import datetime
import shutil,os
import click

@click.command()
def full_init() -> None:
    click.echo("Creating directories...")
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
    name TEXT PRIMARY KEY,
    applied_at TEXT DEFAULT CURRENT_TIMESTAMP
);
    ''')
    conn.commit()
    conn.close()
    click.echo("Created migrations table.")

    click.echo("Creating database...")
    init_db(False)
    click.echo("Created database.")

    click.echo("Fully initialized the database.")

def backup_db():
    dt_string = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    shutil.copy("db/database.db", f"db/backups/{dt_string}.db")

def get() -> sqlite3.Connection:
    return sqlite3.connect('db/database.db')

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

@click.command()
def backup():
    click.echo("Starting backup...")
    backup_db()
    click.echo("Created backup!")

@click.command()
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

@click.command()
def init():
    init_db(True,True)

def init_db(dobackup=True, clickecho=False):
    if clickecho:
        click.echo("Initializing database...")
    else:
        print("Initializing database...")

    if dobackup:
        backup_db()

    fail = False

    conn = get()
    cursor = conn.execute("SELECT name FROM migrations")
    applied = {row[0] for row in cursor.fetchall()}
    conn.close()

    for root, _, files in os.walk("db/schemas"):
        dirname = os.path.basename(root)

        for schema in files:
            schema_name = schema.replace(".sql", "")
            schema_path = os.path.join(root, schema)
            display_name = f"{dirname}.{schema_name}" if dirname != "schemas" else schema_name

            if display_name in applied:
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

@click.group()
def cli():
    """Database management"""
    pass

cli.add_command(full_init)
cli.add_command(backup)
cli.add_command(revert)
cli.add_command(init)

if __name__ == '__main__':
    cli()
