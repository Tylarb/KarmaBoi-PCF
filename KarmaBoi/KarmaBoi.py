#!/usr/bin/env python

import dbopts
import os, sys, traceback
import time
import slack_parse
import logging
import errno
import textwrap as tw
from slackclient import SlackClient


# These values are set in ~/.KarmaBoi and exported to environment by sourcing
# init.sh
BOT_NAME = os.environ.get('SLACK_BOT_NAME')
BOT_HOME = os.environ.get('BOT_HOME')
READ_WEBSOCKET_DELAY = .1  # delay in seconds between reading from firehose


# logger basic configuration
logging.basicConfig(filename=BOT_HOME+'/log',level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)


def bot_id(BOT_NAME,sc):
    user_obj = sc.api_call("users.list")
    if user_obj.get('ok'):
        # retrieve all users so we can find our bot
        users = user_obj.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                BOT_ID = user.get('id')
                return BOT_ID
    else:
        logger.critical(
            "API call failed - please ensure your token and bot name are valid")
        return NULL

def main():
    # create database if it doesn't exist
    if not os.path.exists(dbopts.DB_PATH + 'karmadb'):
        logger.info("No database exists. Creating databases for the first time")
        dbopts.create_karma_table()
        dbopts.create_also_table()

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
    while attempt < MAX_ATTEMPTS:
        sc = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

        if sc.rtm_connect():
            logger.info('KarmaBoi connected')
            BOT_ID = bot_id(BOT_NAME,sc)

            try:
                logger.info('now doing ~important~ things')
                while True:
                    slack_parse.triage(sc,BOT_ID)
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
    main()
