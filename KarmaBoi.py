import sqlite3
import os

DB_PATH = os.path.expanduser("~/.KarmaBoi/databases/")

def db_karma_connect():
    db_karma = sqlite3.connect(DB_PATH + 'karmadb')
    return db_karma

def db_close(db):
    db.close()

def karma_ask(name):
    db_karma = db_karma_connect()
    cursor = db_karma.cursor()
    cursor.execute(''' SELECT name, karma FROM people WHERE name=? ''',(name,))
    karma = cursor.fetchone()
    if karma is None:
        return 0
    else:
        return karma

def karma_add(name):
    karma = karma_ask(name) + 1
    return karma

def karma_sub(name):
    karma = karma_ask(name) - 1
    return karma

def user_add(name):
    return name

# db_karma.close()
