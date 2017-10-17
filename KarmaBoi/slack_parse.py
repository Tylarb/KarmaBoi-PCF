

def triage(slack_client, BOT_ID):
    """
        Here, we read and triage all messages. Messages directed to the bot will be triaged to the
        command handler. Otherwise, the output is parsed for special events
    """
    AT_BOT = "<@" + BOT_ID + ">"
    
