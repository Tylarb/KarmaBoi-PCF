import sqlite3
import os
import logging

DB_PATH = os.path.expanduser("~/.KarmaBoi/databases/")
DB_NAME = 'karmadb'
logger = logging.getLogger(__name__)

def db_connect():
    try:
        db = sqlite3.connect(DB_PATH + DB_NAME)
        return db
    except:
        logger.error('db connection was not successful')
        return NULL

def create_karma_table():
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH)
    db = db_connect()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS people(
        name TEXT PRIMARY KEY, karma INTEGER, shame INTEGER)
    ''')
    db.commit()
    logger.info('successfully created karma db for the first time')
    db.close()

def create_also_table():
    db = db_connect()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS isalso(id INTEGER PRIMARY KEY, name TEXT,
        also TEXT)
    ''')
    db.commit()
    logger.info('successfully created also table for the first time')
    db.close()

## Karma function
def karma_ask(name):
    db = db_connect()
    cursor = db.cursor()
    cursor.execute(''' SELECT karma FROM people WHERE name=? ''',(name,))
    karma = cursor.fetchone()
    db.close()
    if karma is None:
        logger.debug('No karma found for name {}'.format(name))
        return karma
    else:
        karma = karma[0]
        logger.debug('karma of {} found for name {}'.format(karma, name))
        return karma

def karma_rank(name):
    db = db_connect()
    cursor = db.cursor()
    cursor.execute('''
        SELECT (SELECT COUNT(*) FROM people AS t2 WHERE t2.karma > t1.karma)
        AS row_Num FROM people AS t1 WHERE name=?
    ''', (name,))
    rank = cursor.fetchone()[0] + 1
    db.close
    logger.debug('Rank of {} found for name {}'.format(rank, name))
    return rank

def karma_add(name):
    karma = karma_ask(name)
    db = db_connect()
    cursor = db.cursor()
    if karma is None:
        cursor.execute(
            ''' INSERT INTO people(name,karma,shame) VALUES(?,?,0) ''',(name,1))
        db.commit()
        logger.debug('Inserted into karmadb 1 karma for {}'.format(name))
        db.close()
        return 1
    else:
        karma = karma + 1
        cursor.execute(
            ''' UPDATE people SET karma = ? WHERE name = ? ''', (karma,name))
        db.commit()
        logger.debug('Inserted into karmadb {} karma for {}'.format(karma, name))
        db.close()
        return karma

def karma_sub(name):
    karma = karma_ask(name)
    db = db_connect()
    cursor = db.cursor()
    if karma is None:
        cursor.execute(
            ''' INSERT INTO people(name,karma,shame) VALUES(?,?,0) ''',(name,-1))
        db.commit()
        logger.debug('Inserted into karmadb -1 karma for {}'.format(name))
        db.close()
        return -1
    else:
        karma = karma - 1
        cursor.execute(
            ''' UPDATE people SET karma = ? WHERE name = ? ''', (karma,name))
        db.commit()
        logger.debug('Inserted into karmadb {} karma for {}'.format(karma, name))
        db.close()
        return karma

def karma_top():
    db = db_connect()
    cursor = db.cursor()
    cursor.execute(
    ''' SELECT name, karma FROM people ORDER BY karma DESC LIMIT 5 '''
    )
    leaders = cursor.fetchall()
    logger.debug('fetched top karma values')
    return leaders

def karma_bottom():
    db = db_connect()
    cursor = db.cursor()
    cursor.execute(
    ''' SELECT name, karma FROM people ORDER BY karma ASC LIMIT 5 '''
    )
    leaders = cursor.fetchall()
    logger.debug('fetched bottom karma values')
    return leaders

## Shame functions

def shame_ask(name):
    db = db_connect()
    cursor = db.cursor()
    cursor.execute(''' SELECT shame FROM people WHERE name=? ''',(name,))
    shame = cursor.fetchone()
    db.close()
    if shame is None:
        logger.debug('No shame found for name {}'.format(name))
        return shame
    else:
        shame = shame[0]
        logger.debug('shame of {} found for name {}'.format(shame, name))
        return shame

def shame_add(name):
    shame = shame_ask(name)
    db = db_connect()
    cursor = db.cursor()
    if shame is None:
        cursor.execute(
            ''' INSERT INTO people(name,karma,shame) VALUES(?,0,?) ''',(name,1))
        db.commit()
        logger.debug('Inserted into karmadb 1 shame for {}'.format(name))
        db.close()
        return 1
    else:
        shame = shame + 1
        cursor.execute(
            ''' UPDATE people SET shame = ? WHERE name = ? ''', (shame,name))
        db.commit()
        logger.debug('Inserted into karmadb {} shame for {}'.format(shame, name))
        db.close()
        return shame


def shame_top():
    db = db_connect()
    cursor = db.cursor()
    cursor.execute(
    ''' SELECT name, shame FROM people ORDER BY shame DESC LIMIT 5 '''
    )
    leaders = cursor.fetchall()
    logger.debug('fetched top shame values')
    return leaders

# WIP add quotes here
def user_add(name):
    db = db_connect()
    cursor = db.cursor()
    cursor.execute(
        ''' INSERT INTO people(name,karma) VALUES(?,?) ''',(name,0))
    db.commit()
    logger.debug('added into people name {} with 0 karma'.format(name))
    return name



# "is also" table functions
def also_add(name, also):
    db = db_connect()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO isalso(name,also) VALUES(?,?)
        ''',(name,also))
    db.commit()
    logger.debug('added to isalso name {} with value {}'.format(name,also))
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
        logger.debug('could not find is_also for name {}'.format(name))
        return also
    else:
        also = also[0]
        logger.debug('found is_also {} for name {}'.format(also, name))
        return also
