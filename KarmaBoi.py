import sqlite3
import os

DB_PATH = os.path.expanduser("~/.KarmaBoi/databases/")

def db_connect():
    db_karma = sqlite3.connect(DB_PATH + 'karmadb')
    return db_karma

def db_close():
    db_karma.close()

def karma_ask(name):
    karma = 10
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
