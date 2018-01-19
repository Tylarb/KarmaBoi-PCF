import sqlite3
import os
import logging
from cfenv import AppEnv
import mysql.connector
from mysql.connector import errorcode


DB_NAME = 'karmadb'
env = AppEnv()
logger = logging.getLogger(__name__)



'''
Check what env we have - if on PCF, use mysql connector. Otherwise, we can
use sqlite to build our database. Fortunately, command execution libraries
are identical once we have a cursor.
'''

if env.name == None:
    DB_PATH = os.path.expanduser("~/.KarmaBoi/databases/")
else:
    mysql_env = env.get_service(label='p-mysql')
    mysql_creds = mysql_env.credentials
    mysql_config = {
        'user': mysql_creds.get('username'),
        'password': mysql_creds.get('password'),
        'host': mysql_creds.get('hostname'),
        'port': mysql_creds.get('port'),
        'raise_on_warnings': True,
    }







def db_connect():
    if env.name == None:
        if not os.path.exists(DB_PATH + 'karmadb'):
            logger.info("No database exists. Creating databases for the first time")
            if not os.path.exists(DB_PATH):
                os.makedirs(DB_PATH)
            db = sqlite3.connect(DB_PATH + DB_NAME)
            create_karma_table(db)
            create_also_table(db)
            return db
        else:
            try:
                db = sqlite3.connect(DB_PATH + DB_NAME)
                return db
            except:
                logger.error('db connection to sqlite was not successful')
                exit(1)
    else:
        try:
            db = mysql.connector.connect(**mysql_config, database=DB_NAME)
            return db
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logger.error('Username or password is incorrect')
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logger.warning('''
                    Database does not exist, attempting to create it now
                    ''')
                cnx = mysql.connector.connect(**mysql_config)
                create_db(cnx)
                try:
                    create_karma_table(cnx)
                    create_also_table(cnx)
                    return cnx
                except mysql.connector.Error as err:
                    logger.error('failed creating tables with error {}'.err)
            else:
                logger.error(err)


def create_db(cnx):
    cursor = cnx.cursor()
    try:
        cursor.execute('''
            CREATE DATABASE '{}' DEFAULT CHARACTER SET 'utf8'
            '''.format(DB_NAME))
    except mysql.connector.Error as err:
        logger.error("Failed creating database: {}".format(err))
        exit(1)


def create_karma_table(db):
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS people(
        name TEXT PRIMARY KEY, karma INTEGER, shame INTEGER)
    ''')
    db.commit()
    logger.info('successfully created karma db for the first time')

def create_also_table(db):
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS isalso(id INTEGER PRIMARY KEY, name TEXT,
        also TEXT)
    ''')
    db.commit()
    logger.info('successfully created also table for the first time')

## Karma function
def karma_ask(name):
    db = db_connect()
    cursor = db.cursor()
    cursor.execute(''' SELECT karma FROM people WHERE name='{}' '''.format(name))
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
        AS row_Num FROM people AS t1 WHERE name='{}'
    '''.format(name))
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
            '''
            INSERT INTO people(name,karma,shame) VALUES('{}',1,0)
            '''.format(name))
        db.commit()
        logger.debug('Inserted into karmadb 1 karma for {}'.format(name))
        db.close()
        return 1
    else:
        karma = karma + 1
        cursor.execute(
            '''
            UPDATE people SET karma = {0} WHERE name = '{1}'
            '''.format(karma,name))
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
            '''
            INSERT INTO people(name,karma,shame) VALUES('{}',-1,0)
            '''.format(name))
        db.commit()
        logger.debug('Inserted into karmadb -1 karma for {}'.format(name))
        db.close()
        return -1
    else:
        karma = karma - 1
        cursor.execute(
            '''
            UPDATE people SET karma = {0} WHERE name = '{1}'
            '''.format(karma,name))
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
    cursor.execute('''
        SELECT shame FROM people WHERE name='{}'
        '''.format(name))
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
            '''
            INSERT INTO people(name,karma,shame) VALUES('{}',0,1)
            '''.format(name))
        db.commit()
        logger.debug('Inserted into karmadb 1 shame for {}'.format(name))
        db.close()
        return 1
    else:
        shame = shame + 1
        cursor.execute(
            '''
            UPDATE people SET shame = {0} WHERE name = '{1}'
            '''.format(shame,name))
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


# WIP add quotes somewhere in here

# "is also" table functions
def also_add(name, also):
    db = db_connect()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO isalso(name,also) VALUES('{}','{}')
        '''.format(name, also))
    db.commit()
    logger.debug('added to isalso name {} with value {}'.format(name,also))
    db.close()



def also_ask(name):
    db = db_connect()
    cursor = db.cursor()
    cursor.execute('''
        SELECT also FROM isalso WHERE name='{}' ORDER BY RANDOM() LIMIT 1
        '''.format(name))
    also = cursor.fetchone()
    db.close()
    if also is None:
        logger.debug('could not find is_also for name {}'.format(name))
        return also
    else:
        also = also[0]
        logger.debug('found is_also {} for name {}'.format(also, name))
        return also
