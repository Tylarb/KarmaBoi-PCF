'''
Main language parsing operations. Handles all interaction with slack after
valid slack client has been passed.

Released under MIT license, copyright 2018 Tyler Ramer
'''

import re
import dbopts
import logging
import time
import textwrap as tw

logger = logging.getLogger(__name__)
BASE_URL = "http://example.com/"


def triage(sc, BOT_ID, kcache):
    """
        We read and triage all messages. Messages directed to the bot will
        be triaged to the command handler. Otherwise, the output is parsed for
        special events
    """

    # special events - Karma up or down, or @bot; add
    AT_BOT = '<@' + BOT_ID + '>'
    question = re.compile('.+\?{1,1}$')
    weblink = re.compile('^<http.+>$')  # slack doesn't handle <link>

    for slack_message in sc.rtm_read():
        text = slack_message.get('text')
        user = slack_message.get('user')
        channel = slack_message.get('channel')
        if not text or not user:
            continue
        if user == 'USLACKBOT':
            logger.debug(
                'USLACKBOT sent message {} which is ignored'.format(text))
            continue
        # Need to add users to ignore here - if user in "ignore list"....
        text_list = text.split()
        if text_list[0] == AT_BOT and len(text_list) > 1:
            logger.debug('Message directed at bot: {}'.format(text))
            handle_command(sc, text_list, channel)
            continue

        elif question.search(text_list[0]) and len(text_list) == 1:
            word = text_list[0].strip('?')
            if dbopts.also_ask(word):
                also = dbopts.also_ask(word)
                if weblink.search(also):
                    logger.debug('trimming web link {}'.format(also))
                    also = also.strip('<>').split('|')[0]
                sc.rtm_send_message(
                    channel, 'I remember hearing that {} is also {}'.format(
                        word, also))
            continue

        else:  # karma and shame here
            for word in list(set(text_list)):
                if handle_word(sc, word, kcache, user, channel):
                    continue


def handle_word(sc, word, kcache, user, channel):

    karmaup = re.compile('.+\+{2,2}$')
    karmadown = re.compile('.+-{2,2}$')
    shameup = re.compile('.+~{2,2}$')
    nonkarma = re.compile('^\W+$')
    caseid = re.compile('^[0-9]{5,5}$')  # URL expander for cases

    if karmaup.search(word):
        name = word.rstrip(
            '+')  # can use "get UID" at this point if desired later
        if name == '' or nonkarma.search(name):
            logger.debug('Ignored word {}'.format(name))
            return True
        if name == '<@' + user + '>':
            logger.debug(
                'user {} attempted to give personal karma'.format(user))
            shame = dbopts.shame_add(name)
            sc.rtm_send_message(channel,
                                tw.dedent('''\
               Self promotion will get you nowhere.
               {} now has {} points of shame forever.
               ''').format(name, shame))
        else:
            key = user + '-' + name
            if key not in kcache:
                kcache.update(key)
                karma = dbopts.karma_add(name)
                sc.rtm_send_message(channel,
                                    '{} now has {} points of karma'.format(
                                        name, karma))
                if get_prize(karma) is not None:
                    sc.rtm_send_message(channel, get_prize(karma))
            else:
                t_remain = kcache.timeout - (
                    time.time() - kcache.cache[key]['time_added'])
                t_warn = tw.dedent('''\
                    Please wait {} seconds before adjusting karma of {}
                    '''.format(int(t_remain), name))
                sc.api_call(
                    'chat.postEphemeral',
                    channel=channel,
                    text=t_warn,
                    user=user,
                    as_user=True)
                logger.debug(
                    '{} seconds remaining to adjust karma for {}'.format(
                        t_remain, key))

    if karmadown.search(word):
        name = word.rstrip('-')
        if name == '' or nonkarma.search(name):
            logger.debug('Ignored word {}'.format(name))
            return True
        if name == '<@' + user + '>':
            sc.rtm_send_message(channel,
                                tw.dedent('''
           I still love you, even if you don\'t always love yourself
           '''))
        key = user + '-' + name
        if key not in kcache:
            kcache.update(key)
            karma = dbopts.karma_sub(name)
            sc.rtm_send_message(channel,
                                '{} now has {} points of karma'.format(
                                    name, karma))
            if get_prize(karma) is not None:
                sc.rtm_send_message(channel, get_prize(karma))

        else:
            t_remain = kcache.timeout - (
                time.time() - kcache.cache[key]['time_added'])
            t_warn = tw.dedent('''\
                Please wait {} seconds before adjusting karma of {}
               '''.format(int(t_remain), name))
            sc.api_call(
                'chat.postEphemeral',
                channel=channel,
                text=t_warn,
                user=user,
                as_user=True)
            logger.debug('{} seconds remaining to adjust karma for {}'.format(
                t_remain, key))

    if shameup.search(word):
        name = word.rstrip('~')
        if name == '' or nonkarma.search(name):
            logger.debug('Ignored word {}'.format(name))
            return True
        key = user + '~' + name
        if key not in kcache:
            kcache.update(key)
            shame = dbopts.shame_add(name)
            if shame == 1:
                sc.rtm_send_message(channel,
                                    tw.dedent('''
               What is done cannot be undone.
               {} now has shame until the end of time
              ''').format(name))
            else:
                sc.rtm_send_message(channel,
                                    '{} now has {} points of shame'.format(
                                        name, shame))
        else:
            t_remain = kcache.timeout - (
                time.time() - kcache.cache[key]['time_added'])
            t_warn = tw.dedent('''\
                Please wait {} seconds before adjusting karma of {}
               '''.format(int(t_remain), name))
            sc.api_call(
                'chat.postEphemeral',
                channel=channel,
                text=t_warn,
                user=user,
                as_user=True)

            logger.debug('{} seconds remaining to add shame for {}'.format(
                t_remain, key))
    if caseid.search(word):
        urlExpanded = BASE_URL + word
        sc.rtm_send_message(channel, urlExpanded)


def handle_command(sc, text_list, channel):

    # person rankings - karma and shame
    if len(text_list) > 2 and text_list[1] == 'rank':
        name = text_list[2]
        new_name = get_uid(sc, name.strip('@'))  # WIP
        karma = dbopts.karma_ask(name)
        if karma:
            rank = dbopts.karma_rank(name)
            sc.rtm_send_message(channel,
                                '{} is rank {} with {} points of karma'.format(
                                    name, rank, karma))
            if get_prize(karma) is not None:
                sc.rtm_send_message(channel, get_prize(karma))

        else:
            sc.rtm_send_message(channel,
                                '{} hasn\'t been given karma yet'.format(name))

    if len(text_list) > 2 and text_list[1] == '~rank':
        name = text_list[2]
        shame = dbopts.shame_ask(name)
        if shame:
            sc.rtm_send_message(channel,
                                tw.dedent('''
                I will forever remember that {} has {} points of shame.
               ''').format(name, shame))
        else:
            sc.rtm_send_message(
                channel,
                '{} is in some ways a shameless creature'.format(name))

    # leaderboards
    if len(text_list) == 2 and text_list[1] == 'rank':
        leaderboard = dbopts.karma_top()
        if len(leaderboard) < 5:
            logger.info(
                'less than 5 entries in the leaderboard - ignoring rank')
        else:
            sc.rtm_send_message(
                channel,
                tw.dedent(
                    ''':fiestaparrot: :fiestaparrot: :fiestaparrot: TOP KARMA LEADERBOARD \
            :fiestaparrot: :fiestaparrot: :fiestaparrot:
            1. :dealwithitparrot: {l[0][0]} with {l[0][1]}
            2. :aussieparrot: {l[1][0]} with {l[1][1]}
            3. :derpparrot: {l[2][0]} with {l[2][1]}
            4. :explodyparrot: {l[3][0]} with {l[3][1]}
            5. :sadparrot: {l[4][0]} with {l[4][1]}
            '''.format(l=leaderboard)))

    if len(text_list) == 2 and text_list[1] == '!rank':
        leaderboard = dbopts.karma_bottom()
        if len(leaderboard) < 5:
            logger.info(
                'less than 5 entries in the leaderboard - ignoring rank')
        else:
            sc.rtm_send_message(
                channel,
                tw.dedent(
                    ''':sadparrot: :sadparrot: :sadparrot: BOTTOM KARMA LEADERBOARD \
            :sadparrot: :sadparrot: :sadparrot:
            1. :sad_unikitty: {l[0][0]} with {l[0][1]}
            2. :sadpanda: {l[1][0]} with {l[1][1]}
            3. :tippy-sad: {l[2][0]} with {l[2][1]}
            4. :sadcloud: {l[3][0]} with {l[3][1]}
            5. :sadrabbit: {l[4][0]} with {l[4][1]}
            '''.format(l=leaderboard)))

    if len(text_list) == 2 and text_list[1] == '~rank':
        leaderboard = dbopts.shame_top()
        if len(leaderboard) < 5:
            logger.info(
                'less than 5 entries in the leaderboard - ignoring rank')
        else:
            sc.rtm_send_message(
                channel,
                tw.dedent(''':darth: :darth: :darth: SHAME LEADERBOARD \
            :darth: :darth: :darth:
            1. {l[0][0]} with {l[0][1]}
            2. {l[1][0]} with {l[1][1]}
            3. {l[2][0]} with {l[2][1]}
            4. {l[3][0]} with {l[3][1]}
            5. {l[4][0]} with {l[4][1]}
            '''.format(l=leaderboard)))

    # is also
    if len(text_list) > 3 and text_list[2] == 'is' and text_list[3] == 'also':
        if len(text_list) < 5:
            sc.rtm_send_message(channel, "Surely {} isn't nothing!".format(
                text_list[1]))
        else:
            also = ' '.join(text_list[4:len(text_list)])
            dbopts.also_add(text_list[1], also)
            sc.rtm_send_message(channel, "I'll keep that in mind")


# currently unused
def get_prize(karma):
    prize = None
    if karma > 0:
        if karma % 5000 is 0:
            prize = dbopts.also_ask("superprize")
        elif karma % 1000 is 0:
            prize = dbopts.also_ask("grandprize")
        elif karma % 100 is 0:
            prize = dbopts.also_ask("prize")
    return prize


def get_uid(sc, name):

    api_call = sc.api_call("users.list")
    if api_call.get('ok'):
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == name:
                uid = user.get('id')
                logger.debug('found UID {} with provided name'.format(uid))
                return "<@" + uid + ">"
            elif ('display_name' in user.get('profile')
                  and user.get('profile').get('display_name') == name):
                uid = user.get('id')
                logger.debug(
                    'found UID {} with provided display name'.format(uid))
                return "<@" + uid + ">"
            else:
                logger.debug('No UID found for name {}'.format(name))
                return name
    else:
        logger.warning('API call failed in get_uid')
        return name
