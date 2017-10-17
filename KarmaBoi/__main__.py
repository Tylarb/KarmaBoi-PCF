#!/usr/bin/env python

import KarmaBoi
import os
import dbinit
import time
import slack_parse
from slackclient import SlackClient


# These values are set in ~/.KarmaBoi and exported to environment by sourcing init.sh
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
BOT_NAME = os.environ.get('SLACK_BOT_NAME')
READ_WEBSOCKET_DELAY = .5 #  delay in seconds between reading from firehose

def bot_id(BOT_NAME):
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                BOT_ID = user.get('id')
                return BOT_ID
    else:
        print("API call failed - please ensure your token and bot name are valid")
        return NULL

BOT_ID = bot_id(BOT_NAME)


def main():
    # create database if it doesn't exist
    if not os.path.exists(dbinit.DB_PATH + 'karmadb'):
        print("No database exists \n  Creating databases for the first time")
        dbinit.create_users_table()

    # connect to channel and do things
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            slack_parse.triage(slack_client,BOT_ID)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")



if __name__ == "__main__":
    main()
