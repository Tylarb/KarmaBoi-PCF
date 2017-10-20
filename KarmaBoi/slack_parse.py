import re
import dbopts

def triage(sc, BOT_ID):
    """
        Here, we read and triage all messages. Messages directed to the bot will
        be triaged to the command handler. Otherwise, the output is parsed for
        special events
    """
    AT_BOT = "<@" + BOT_ID + ">"
    karmaup = re.compile('.+\+{2,2}$')
    karmadown = re.compile('.+-{2,2}$')
    question = re.compile('.+\?{1,1}$')

    for slack_message in sc.rtm_read():
        text = slack_message.get('text')
        user = slack_message.get('user')
        channel = slack_message.get('channel')
        if not text or not user:
            continue
        # Need to add users to ignore here - if user in "ignore list"....
        text_list = text.split()

        if text_list[0] == AT_BOT and len(text_list) > 2:
            handle_command(sc, text_list, channel)
            continue

        elif question.search(text_list[0]):
            word = text_list[0].strip('?')
            if dbopts.also_ask(word):
                also = dbopts.also_ask(word)
                sc.rtm_send_message(channel,
                    "I remember hearing that {} is also {}".format(word,also))
            else:
                sc.rtm_send_message(channel,
                    "To be honest, I've never heard of {} before".format(word))
            continue

        else:
            for word in list(set(text_list)):
                if karmaup.search(word):
                    name = word.strip('+')      # can use "get UID" at this point if desired later
                    karma = dbopts.karma_add(name)
                    sc.rtm_send_message(channel,
                        "{} now has {} points of karma".format(name,karma))
                if karmadown.search(word):
                    name = word.strip('-')
                    karma = dbopts.karma_sub(name)
                    sc.rtm_send_message(channel,
                        "{} now has {} points of karma".format(name,karma))


def handle_command(sc, text_list, channel):
    if text_list[1] == 'rank':
        name = text_list[2]
        karma = dbopts.karma_ask(name)
        if karma:
            sc.rtm_send_message(channel,
                "{} has {} points of karma".format(name,karma))
        else:
            sc.rtm_send_message(channel,
                "{} hasn't been given karma yet".format(name))
    if text_list[2] == 'is' and text_list[3] == 'also':
        if len(text_list) < 5:
            sc.rtm_send_message(channel,
                "Surely {} isn't nothing!".format(name))
        else:
            also = ' '.join(text_list[4:len(text_list)])
            dbopts.also_add(text_list[1], also)
            sc.rtm_send_message(channel,
                "I'll keep that in mind")

def get_uid(sc, name):
    api_call = sc.api_call("users.list")
    if api_call.get('ok'):
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == name:
                uid = user.get('id')
                return "<@"+uid+">"
            elif 'display_name' in user.get('profile') and user.get('profile').get('display_name') == name:
                uid = user.get('id')
                return "<@"+uid+">"
            else:
                return name
