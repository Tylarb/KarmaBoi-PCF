import re
import dbopts
import logging
import time
import textwrap as tw


logger = logging.getLogger(__name__)


def triage(sc, BOT_ID):
    """
        Here, we read and triage all messages. Messages directed to the bot will
        be triaged to the command handler. Otherwise, the output is parsed for
        special events
    """
    # special events - Karma up or down, or @bot; add
    AT_BOT = '<@' + BOT_ID + '>'
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
        # logger.debug('Channel: {} user: {} message: {}'.format(channel, user, text))
        if text_list[0] == AT_BOT and len(text_list) > 1:
            logger.debug('Message directed at bot: {}'.format(text))
            handle_command(sc, text_list, channel)
            continue

        elif question.search(text_list[0]):
            word = text_list[0].strip('?')
            if dbopts.also_ask(word):
                also = dbopts.also_ask(word)
                sc.rtm_send_message(channel,
                    'I remember hearing that {} is also {}'.format(word,also))
            continue

        else:   ## karma and shame here
            for word in list(set(text_list)):
                if karmaup.search(word):
                    name = word.strip('+')      # can use "get UID" at this point if desired later
                    if name == '<@' + user + '>':
                        logger.debug('user {} attempted to give personal karma'.format(user))
                        shame = dbopts.shame_add(name)
                        sc.rtm_send_message(channel, tw.dedent('''\
                            Self promotion will get you nowhere.
                            {} now has {} points of shame forever.
                            ''').format(name, shame))
                    else:
                        karma = dbopts.karma_add(name)
                        sc.rtm_send_message(channel,
                            '{} now has {} points of karma'.format(name,karma))
                if karmadown.search(word):
                    name = word.strip('-')
                    if name == '<@' + user + '>':
                        sc.rtm_send_message(channel, tw.dedent('''
                        I still love you, even if you don\'t always love yourself
                        '''))
                    karma = dbopts.karma_sub(name)
                    sc.rtm_send_message(channel,
                        '{} now has {} points of karma'.format(name,karma))
                if shameup.search(word):
                    logger.debug('shame was added for {}'.format(word))
                    name = word.strip('~')
                    shame = dbopts.shame_add(name)
                    if shame == 1:
                        sc.rtm_send_message(channel,tw.dedent('''
                         What is done cannot be undone.
                         {} now has shame until the end of time
                         ''').format(name))
                    else:
                        sc.rtm_send_message(channel,
                        '{} now has {} points of shame'.format(name,shame))


def handle_command(sc, text_list, channel):

    # person rankings - karma and shame
    if len(text_list) > 2 and text_list[1] == 'rank':
        name = text_list[2]
        new_name = get_uid(sc, name.strip('@')) #WIP
        karma = dbopts.karma_ask(name)
        if karma:
            sc.rtm_send_message(channel,
                '{} has {} points of karma'.format(name,karma))
        else:
            sc.rtm_send_message(channel,
                '{} hasn\'t been given karma yet'.format(name))

    if len(text_list) > 2 and text_list[1] == '~rank':
        name = text_list[2]
        shame = dbopts.shame_ask(name)
        if shame:
            sc.rtm_send_message(channel, tw.dedent('''
                I will forever remember that {} has {} points of shame.
                ''').format(name,shame))
        else:
            sc.rtm_send_message(channel,
                '{} is in some ways a shameless creature'.format(name))

    # leaderboards
    if len(text_list) == 2 and text_list[1] == 'rank':
        leaderboard = dbopts.karma_top()
        sc.rtm_send_message(channel,tw.dedent(
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
        sc.rtm_send_message(channel,tw.dedent(
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
        sc.rtm_send_message(channel,tw.dedent(
        ''':darth: :darth: :darth: SHAME LEADERBOARD \
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
            elif ('display_name' in user.get('profile')
                    and user.get('profile').get('display_name') == name):
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


class VoteCache:
    """
    Timed cache to reduce upvote/downvote spam. [user] cannot vote
    [target] before VOTE_DELAY seconds
    """

    VOTE_DELAY = 120

    def __init__(self):
        self.cache = {}
        self.max_cache_size = 500  # size of cache

    def __contains__(self, key):
        """
        True or false depending on if key is in cache
        """
        return key in self.cache

    def update(self, key):
        """
        Updates the cache with key after cleaning it of old values
        """
        self.clean()
        if key not in self.cache and len(self.cache) < max_cache_size:
            self.cache[key] = {'time_added': time.time()}

        elif key not in self.cache and len(self.cache) >= max_cache_size:
            self.remove_old()
            self.cache[key] = {'time_added': time.time()}

    def clean(self):
        """
        Removes any item older than VOTE_DELAY from the cache
        """
        for key in self.cache:
            if self.cache[key]['time_added'] > time.time() - VOTE_DELAY:
                self.cache.pop(key)


    def remove_old(self):
        """
        This should not generally be used - only occurs if we're actually
        reaching the cache size AFTER clearing old values. Ideally, cache
        and clearn should be large enough that this function is never used
        """
        oldest = None
        for key in self.cache:
            if oldest is None:
                oldest = key
            elif (self.cache[key]['time_added'] <
                self.cache[oldest]['time_added'])
                oldest = key
        self.cache.pop(oldest)
