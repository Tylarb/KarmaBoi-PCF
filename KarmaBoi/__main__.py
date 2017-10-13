#!/usr/bin/env python

import KarmaBoi
import os
import dbinit
import time
from slackclient import SlackClient


# these need to be set as environmental variables: export SLACK_BOT_NAME='watts-bot1'
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
BOT_NAME = os.environ.get('SLACK_BOT_NAME')
READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose

print('This is a Karma Boi')

if not os.path.exists(dbinit.DB_PATH + 'karmadb'):
    print("No database exists \n  Creating databases for the first time")
    dbinit.create_users_table()
#
#name = input('please provide a name:\n')
#print('You\'ve chosen ' + name)
#karmaInput = input('please add or subtract karma\n')
#
#
#if karmaInput == '++':
#    karma = KarmaBoi.karma_add(name)
#elif karmaInput == '--':
#    karma = KarmaBoi.karma_sub(name)
#else:
#    karma = KarmaBoi.karma_ask(name)
#
#if karma is None:
#    print(name + ' has no karma')
#else:
#    print(name + ' now has ' + str(karma) + ' points of karma' )

# getting our bot ID:
def bot_id(BOT_NAME):
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                BOT_ID = user.get('id')
    else:
        print("API call failed - please ensure your token and bot name are valid")
    return BOT_ID

BOT_ID = bot_id(BOT_NAME)

AT_BOT = "<@" + BOT_ID + ">"


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "HELLLOOO"
    if command.startswith('hello'):
        response = "Sure...write some more code then I can do that!"
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None



def main():
    # create database if it doesn't exist
    if not os.path.exists(dbinit.DB_PATH + 'karmadb'):
        print("No database exists \n  Creating databases for the first time")
        dbinit.create_users_table()

    # connect to channel and do things
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")



if __name__ == "__main__":
    main()
