#!/usr/bin/env python

import dbopts
import os, sys, traceback
import time
import slack_parse
import logging
import errno
import textwrap as tw
import threading
from slackclient import SlackClient
from cache import TimedCache
import argparse
from flask import Flask
from cfenv import AppEnv






'''
These values are set in ~/.KarmaBoi and exported to environment by sourcing
init.sh if on a local host. If on PCF, be sure to set the environment variables
'SLACK_BOT_NAME' and 'SLACK_BOT_TOKEN'
'''
BOT_NAME = os.environ.get('SLACK_BOT_NAME')
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
READ_WEBSOCKET_DELAY = .1  # delay in seconds between reading from firehose

env = AppEnv()



parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose',
    help='add debug messages to log output', action='store_true')
args = parser.parse_args()

# set up log setting
if args.verbose:
    logLevel = logging.DEBUG
else:
    logLevel = logging.INFO


'''
Setting environment specific logger settings - log to file if not using CF
'''
if env.name == None:
    BOT_HOME = os.environ.get('BOT_HOME')
    envHandler = logging.FileHandler("{}/{}.log".format(BOT_HOME,'KarmaBoi'))
else:
    envHandler = logging.StreamHandler()


logging.basicConfig(level=logLevel, handlers=[envHandler],
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')


logger = logging.getLogger(__name__)



'''
Using flask as a simple server - provides a quick status check, and, more
importantly, allows it to work on Cloud Foundry by providing socket listening
'''
app = Flask(__name__)

port = int(os.getenv("PORT",8080))



def bot_id(BOT_NAME,sc):
    user_obj = sc.api_call('users.list')
    if user_obj.get('ok'):
        # retrieve all users so we can find our bot
        users = user_obj.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                BOT_ID = user.get('id')
                logger.debug('Returned Bot ID {}'.format(BOT_ID))
                return BOT_ID
    else:
        logger.critical(
            "API call failed - please ensure your token and bot name are valid")
        return NULL

@app.route('/')
def status():
    return 'I\'m alive!'


def webMain():
    app.run(host='0.0.0.0', port=port)
    logger.info('Listening on port {}'.format(port))

def botMain():

    if dbopts.db_connect():
        logger.info('DB connection successful, continuing')
    else:
        logger.error('DB connection not successful, exiting')
        exit(1)
    # connect to channel and do things
    attempt = 0
    MAX_ATTEMPTS = 500
    '''
    we'll try to connect/recover after a failure for MAX_ATTEMPTS times - this
    should probably be changed into separate connection vs. failure/recovery
    attempts later.
    Probably should always attempt to recover after broken pipe (or, recover
    so many times wthin some time period), but stop general errors after a
    number of attempts. Need to collect logs on what is causing failures first
    '''
    while True:
        sc = SlackClient(SLACK_BOT_TOKEN)
        kcache = TimedCache()

        if sc.rtm_connect():
            logger.info('KarmaBoi connected')
            BOT_ID = bot_id(BOT_NAME,sc)

            try:
                logger.info('now doing ~important~ things')
                while True:
                    slack_parse.triage(sc,BOT_ID, kcache)
                    time.sleep(READ_WEBSOCKET_DELAY)

            except BrokenPipeError as e:
                logger.error('connection failed with Broken Pipe')
                logger.error(e)
                logger.error('retrying connection in a few seconds...')
                time.sleep(5)

            except Exception as e:
                logger.error('Connection failed with some other error')
                logger.exception(e)
                logger.error('trying to restore bot in a few seconds')
                time.sleep(5)

            else:
                logger.critical('general bot error: now ending this short life')
                logger.exception("Error found:")
                break
        attempt += 1
        logger.warning('Attempt number {} of {}'.format(attempt, MAX_ATTEMPTS))

    logger.critical('too many failed attempts - shutting down')

if __name__ == "__main__":
    s = threading.Thread(name='slack_bot', target=botMain)
    f = threading.Thread(name='flask_server', target=webMain)
    s.start()
    f.start()
