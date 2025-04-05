import sqlite3
from datetime import datetime
import shutil,os
from typing import final
import click

@click.command()
def full_init() -> None:
    click.echo("Creating directories...")
    for i in ["db","db/schemas","db/backups"]:
        if not os.path.exists(i):
            click.echo(f"Creating {i}...")
            os.makedirs(i)
            click.echo(f"Created {i}")
    click.echo("Done creating directories!")

    click.echo("Creating database...")
    init_db(False)
    click.echo("Created database!")

    click.echo("Fully initialized the database!")

def backup_db():
    dt_string = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    shutil.copy("db/database.db", f"db/backups/{dt_string}.db")

def get() -> sqlite3.Connection:
    return sqlite3.connect('db/database.db')

@click.command()
def backup():
    click.echo("Starting backup...")
    backup_db()
    click.echo("Created backup!")

@click.command()
@click.argument('date')
def revert(date):
    shutil.copy(f"db/backups/{date}","db/database.db")

@click.command()
def init():
    click.echo("Initializing database...")
    init_db(True,True)
    click.echo("Initialized database!")

def init_db(dobackup=True, clickecho=False):
    if dobackup:
        backup_db()

    for root, _, files in os.walk("db/schemas"):
        dirname = os.path.basename(root)

        for schema in files:
            schema_name = schema.replace(".sql", "")
            schema_path = os.path.join(root, schema)
            display_name = f"{dirname}.{schema_name}" if dirname != "schemas" else schema_name

            conn = get()
            message = f"Executing {display_name}... "

            if clickecho:
                click.echo(message, nl=False)
            else:
                print(message, end="")

            try:
                with open(schema_path, 'r') as file:
                    conn.execute(file.read())
            except Exception:
                status = "\033[0;31mFailed\033[0m"
            else:
                status = "\033[0;32mOk\033[0m"

            if clickecho:
                click.echo(status)
            else:
                print(status)

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
