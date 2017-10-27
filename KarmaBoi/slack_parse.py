import re
import dbopts
import logging


logger = logging.getLogger(__name__)


def triage(sc, BOT_ID):
    """
        Here, we read and triage all messages. Messages directed to the bot will
        be triaged to the command handler. Otherwise, the output is parsed for
        special events
    """
    # special events - Karma up or down, or @bot; add
    AT_BOT = "<@" + BOT_ID + ">"
    karmaup = re.compile('.+\+{2,2}$')
    karmadown = re.compile('.+-{2,2}$')
    shameup = re.compile('.+~{2,2}$')
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
            logger.debug('Message directed at bot: {}'.format(text))
            handle_command(sc, text_list, channel)
            continue

        elif question.search(text_list[0]):
            word = text_list[0].strip('?')
            if dbopts.also_ask(word):
                also = dbopts.also_ask(word)
                sc.rtm_send_message(channel,
                    "I remember hearing that {} is also {}".format(word,also))
            continue

        else:   ## karma and shame here
            for word in list(set(text_list)):
                if karmaup.search(word):
                    name = word.strip('+')      # can use "get UID" at this point if desired later
                    new_name = get_uid(sc, name.strip('@')) # WIP - this for debug currently
                    karma = dbopts.karma_add(name)
                    sc.rtm_send_message(channel,
                        "{} now has {} points of karma".format(name,karma))
                if karmadown.search(word):
                    name = word.strip('-')
                    new_name = get_uid(sc, name.strip('@')) #WIP
                    karma = dbopts.karma_sub(name)
                    sc.rtm_send_message(channel,
                        "{} now has {} points of karma".format(name,karma))
                if shameup.search(word):
                    logger.debug('shame was added for {}'.format(word))
                    name = word.strip('~')
                    shame = dbopts.shame_add(name)
                    if shame == 1:
                        sc.rtm_send_message(channel,
                         'What is done cannot be undone.\n{} now has shame until the end of time'.format(name))
                    else:
                        sc.rtm_send_message(channel,'{} now has {} points of shame'.format(name,shame))


def handle_command(sc, text_list, channel):
    if text_list[1] == 'rank':
        name = text_list[2]
        new_name = get_uid(sc, name.strip('@')) #WIP
        karma = dbopts.karma_ask(name)
        if karma:
            sc.rtm_send_message(channel,
                "{} has {} points of karma".format(name,karma))
        else:
            sc.rtm_send_message(channel,
                "{} hasn't been given karma yet".format(name))

    if text_list[1] == '~rank':
        name = text_list[2]
        shame = dbopts.shame_ask(name)
        if shame:
            sc.rtm_send_message(channel,
                'I will forever remember that {} has {} points of shame.'.format(name,shame))
        else:
            sc.rtm_send_message(channel,
                '{} is a shameless creature'.format(name))

    if text_list[2] == 'is' and text_list[3] == 'also':
        if len(text_list) < 5:
            sc.rtm_send_message(channel,
                "Surely {} isn't nothing!".format(text_list[1]))
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
                logger.debug('found UID {} with provided name'.format(uid))
                return "<@"+uid+">"
            elif 'display_name' in user.get('profile') and user.get('profile').get('display_name') == name:
                uid = user.get('id')
                logger.debug(
                    'found UID {} with provided display name'.format(uid))
                return "<@"+uid+">"
            else:
                logger.debug('No UID found for name {}'.format(name))
                return name
    else:
        logger.warning('API call failed in get_uid')
        return name
