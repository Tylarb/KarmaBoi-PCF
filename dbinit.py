import sqlite3
import os


DB_PATH = os.path.expanduser("~/.KarmaBoi/databases/")



def create_users_table():
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH)
    db_karma = sqlite3.connect(DB_PATH + 'karmadb')
    cursor = db_karma.cursor()
    cursor.execute('''
        CREATE TABLE people(name TEXT PRIMARY KEY, karma INTEGER)
    ''')
    db_karma.commit()
    db_karma.close()
