import sqlite3
from datetime import datetime
import shutil,os
import click
import tome.utils.config as config

DATABASE_DIR = str(config.get("TOME.toml", "database_dir"))
if DATABASE_DIR == None: exit(1)
if DATABASE_DIR.endswith("/"): DATABASE_DIR = DATABASE_DIR.rstrip('/')

def resolve_schema_path(schema_name: str, base_path: str = "schemas", ext: str = ".sql") -> None | str:
    '''
    Convert schema name like 'test.001' into a path like 'schemas/test/001-*.sql'.

    Parameters
    ----------
    schema_name : str
        Name of the schema
    base_path : str, optional
        Base path to schema folder (default is 'schemas')
    ext : str, optional
        Extension to search for (default is '.sql')

    Raises
    ------
    ValueError:
        Raised if an invalid schema format is used
    FileNotFoundError:
        Raised if the schema directory does not exist
    FileNotFoundError:
        Raised if no schema file found

    Returns
    -------
    None | str
        The schema file path or None
    '''
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

def backup_db() -> None:
    '''
    Create a backup of the database
    '''
    if os.path.exists(DATABASE_DIR+"/database.db"):
        dt_string = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        shutil.copy("{DATABASE_DIR}/database.db", f"{DATABASE_DIR}/backups/{dt_string}.db")

def get() -> sqlite3.Connection:
    '''
    Get a database connection

    Returns
    -------
    sqlite3.Connection
        The connection
    '''
    return sqlite3.connect(DATABASE_DIR+'/database.db', timeout=100.0)

def get_latest_backup() -> None | str:
    '''
    Gets the latest backup

    Returns
    -------
    None | str
        The backup file path or None
    '''
    datetime_format = "%d-%m-%Y_%H-%M-%S"
    backups = []

    for filename in os.listdir(DATABASE_DIR+"/backups"):
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

def init_db(dobackup: bool = True, clickecho: bool = False) -> None:
    '''
    Initialize the database

    Parameters
    ----------
    dobackup : bool
        If the existing database should be backed up
    clickecho : bool
        If click.echo should be used instead of print
    '''
    
    if clickecho:
        click.echo("Initializing database...")
    else:
        print("Initializing database...")

    if not os.path.exists(DATABASE_DIR+"/backups"):
        os.mkdir(DATABASE_DIR+"/backups")

    if dobackup:
        backup_db()

    fail = False

    conn = get()
    cursor = conn.execute("SELECT name FROM migrations")
    applied = {row[0] for row in cursor.fetchall()}
    conn.close()

    for root, _, files in os.walk(DATABASE_DIR+"/schemas"):
        dirname = os.path.basename(root)

        files.sort()

        for schema in files:
            if not schema.endswith(".sql"):
                continue
            schema_name = schema.replace(".sql", "")
            schema_path = DATABASE_DIR+"/schemas/"+dirname+"/"+schema_name+".sql"
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
