

def triage(sc, BOT_ID):
    """
        Here, we read and triage all messages. Messages directed to the bot will
        be triaged to the command handler. Otherwise, the output is parsed for
        special events
    """
    AT_BOT = "<@" + BOT_ID + ">"
    for slack_message in sc.rtm_read():
        message = slack_message.get('text')
        user = slack_message.get('user')
        channel = slack_message.get('channel')
        if not message or not user:
            continue
        # Need to add users to ignore here - if user in "ignore list"....



        sc.rtm_send_message(channel, "<@{} wrote \n \"{}\"".format(user,message))



def slack_karma(slack_client, text):
    food = text
