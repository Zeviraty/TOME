import sqlite3
from datetime import datetime
import shutil,os

def get():
    return sqlite3.connect('db/database.db')

def backup():
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    shutil.copy("db/database.db",f"db/backups/{dt_string}")

def revert(date):


def init():
    backup()
