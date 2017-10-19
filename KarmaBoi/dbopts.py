import sqlite3
import os

DB_PATH = os.path.expanduser("~/.KarmaBoi/databases/")

def db_karma_connect():
    db = sqlite3.connect(DB_PATH + 'karmadb')
    return db


def karma_ask(name):
    db = db_karma_connect()
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
    db = db_karma_connect()
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
    db = db_karma_connect()
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
    db = db_karma_connect()
    cursor = db.cursor()
    cursor.execute(
        ''' INSERT INTO people(name,karma) VALUES(?,?) ''',(name,0))
    return name

# add "is also"
