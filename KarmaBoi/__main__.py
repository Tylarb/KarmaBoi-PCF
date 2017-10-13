#!/usr/bin/env python

import KarmaBoi
import os
import dbinit
from slackclient import SlackClient


print('This is a Karma Boi')

if not os.path.exists(dbinit.DB_PATH + 'karmadb'):
    print("No database exists \n  Creating databases for the first time")
    dbinit.create_users_table()

name = input('please provide a name:\n')
print('You\'ve chosen ' + name)
karmaInput = input('please add or subtract karma\n')


if karmaInput == '++':
    karma = KarmaBoi.karma_add(name)
elif karmaInput == '--':
    karma = KarmaBoi.karma_sub(name)
else:
    karma = KarmaBoi.karma_ask(name)

if karma is None:
    print(name + ' has no karma')
else:
    print(name + ' now has ' + str(karma) + ' points of karma' )



# these need to be set as environmental variables: export SLACK_BOT_NAME='watts-bot1'
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
BOT_NAME = os.environ.get('SLACK_BOT_NAME')

if __name__ == "__main__":
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
    else:
        print("could not find bot user with the name " + BOT_NAME)
    slack_client.rtm_connect()
    slack_client.rtm_send_message("general","HELLOOOOO")
