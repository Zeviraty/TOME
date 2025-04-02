import sqlite3
from datetime import datetime
import shutil,os
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
    click.echo("Creating database...")
    init_db()
    click.echo("Created database!")

def init_db(dobackup=True):
    if dobackup:
        backup_db()

    schemas = os.listdir("db/schemas")
    for schema in schemas:
        conn = get()
        conn.execute(open(f"db/schemas/{schema}",'r').read())

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
