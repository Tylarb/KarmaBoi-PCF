#!/bin/bash 

DIR=`pwd`
export BOT_HOME=~/.KarmaBoi

token=$BOT_HOME/bot_token

if [ ! -d $DIR/KarmaBoi/env_KarmaBoi ]; then
	echo 'setting up for the first time'
	python3 -m venv $DIR/KarmaBoi/env_KarmaBoi
	source $DIR/KarmaBoi/env_KarmaBoi/bin/activate
	pip install -r $DIR/requirements.txt
fi

echo $token
if [ -f $token ]; then
	echo "found bot token"
	export SLACK_BOT_NAME=$(grep name $token| cut -d : -f 2)
	export SLACK_BOT_TOKEN=$(grep token $token| cut -d : -f 2)
	source $DIR/KarmaBoi/env_KarmaBoi/bin/activate
else
	echo "Please add your bot name and token at ~/.KarmaBoi/bot_token\nhttps://api.slack.com/bot-users\n\nFORMAT: \nname:[bot-name]\ntoken:[bot-token]"
fi

