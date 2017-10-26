#!/usr/bin/env python

import dbopts
import os
import time
import slack_parse
import logging
from slackclient import SlackClient



# These values are set in ~/.KarmaBoi and exported to environment by sourcing
# init.sh
BOT_NAME = os.environ.get('SLACK_BOT_NAME')
BOT_HOME = os.environ.get('BOT_HOME')
READ_WEBSOCKET_DELAY = .5 #  delay in seconds between reading from firehose


# logging basic configuration
logging.basicConfig(filename=BOT_HOME+'/log',level=logging.DEBUG,
    format='%(asctime)s %(message)s')


def bot_id(BOT_NAME,sc):
    api_call = sc.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                BOT_ID = user.get('id')
                return BOT_ID
    else:
        logging.critical(
            "API call failed - please ensure your token and bot name are valid")
        return NULL

def main():
    # create database if it doesn't exist
    if not os.path.exists(dbopts.DB_PATH + 'karmadb'):
        logging.info("No database exists \n  Creating databases for the first time")
        dbopts.create_karma_table()
        dbopts.create_also_table()

    # connect to channel and do things
    attempt = 0
    MAX_ATTEMPTS = 30
    while  attempt < MAX_ATTEMPTS:
        sc = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
        if sc.rtm_connect():
            logging.info('KarmaBoi connected')
            BOT_ID = bot_id(BOT_NAME,sc)
            try:
                logging.info('now doing ~important~ things')
                while True:
                    slack_parse.triage(sc,BOT_ID)
                    time.sleep(READ_WEBSOCKET_DELAY)
            except BrokenPipeError as e:
                logging.error('connection failed with Broken Pipe')
                logging.error(e)
                logging,error('retrying connection in a few seconds...')
                time.sleep(5)
                continue
            else:
                logging.critical('general bot error: now ending this short life')

        else:
            attempt += 1

    logging.critical('too many failed attempts - shutting down')

if __name__ == "__main__":
    main()
