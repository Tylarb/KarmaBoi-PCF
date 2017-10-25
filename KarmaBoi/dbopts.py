import sqlite3
import os

DB_PATH = os.path.expanduser("~/.KarmaBoi/databases/")
DB_NAME = 'karmadb'

def db_connect():
    db = sqlite3.connect(DB_PATH + DB_NAME)
    return db

def create_karma_table():
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH)
    db = db_connect()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS people(name TEXT PRIMARY KEY, karma INTEGER)
    ''')
    db.commit()
    db.close()

def create_also_table():
    db = db_connect()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS isalso(id INTEGER PRIMARY KEY, name TEXT,
        also TEXT)
    ''')
    db.commit()
    db.close()


def karma_ask(name):
    db = db_connect()
    cursor = db.cursor()
    cursor.execute(''' SELECT karma FROM people WHERE name=? ''',(name,))
    karma = cursor.fetchone()
    db.close()
    if karma is None:
        return karma
    else:
        karma = karma[0]
        return karma


def karma_add(name):
    karma = karma_ask(name)
    db = db_connect()
    cursor = db.cursor()
    if karma is None:
        cursor.execute(
            ''' INSERT INTO people(name,karma) VALUES(?,?) ''',(name,1))
        db.commit()
        db.close()
        return 1
    else:
        karma = karma + 1
        cursor.execute(
            ''' UPDATE people SET karma = ? WHERE name = ? ''', (karma,name))
        db.commit()
        db.close()
        return karma

def karma_sub(name):
    karma = karma_ask(name)
    db = db_connect()
    cursor = db.cursor()
    if karma is None:
        cursor.execute(
            ''' INSERT INTO people(name,karma) VALUES(?,?) ''',(name,-1))
        db.commit()
        db.close()
        return -1
    else:
        karma = karma - 1
        cursor.execute(
            ''' UPDATE people SET karma = ? WHERE name = ? ''', (karma,name))
        db.commit()
        db.close()
        return karma



# add quotes
def user_add(name):
    db = db_connect()
    cursor = db.cursor()
    cursor.execute(
        ''' INSERT INTO people(name,karma) VALUES(?,?) ''',(name,0))
    return name

# add "is also"


def also_add(name, also):
    db = db_connect()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO isalso(name,also) VALUES(?,?)
        ''',(name,also))
    db.commit()
    db.close()



def also_ask(name):
    db = db_connect()
    cursor = db.cursor()
    cursor.execute('''
        SELECT also FROM isalso WHERE name=? ORDER BY RANDOM() LIMIT 1
        ''',(name,))
    also = cursor.fetchone()
    db.close()
    if also is None:
        return also
    else:
        also = also[0]
        return also
