import sqlite3
from datetime import datetime
import shutil,os
import click

@click.command()
def full_init() -> None:
    click.echo("Creating directories...")
    os.makedirs("db")
    os.makedirs("db/backups")
    os.makedirs("db/schemas")
    click.echo("Done creating directories!")

    click.echo("Creating database...")
    init(False,True)
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
def init(dobackup=True,noecho=False):
    if dobackup:
        backup_db()

    if not noecho:
        click.echo('Initialized the database')


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
