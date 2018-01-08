import logging
import time

logger = logging.getLogger(__name__)

class TimedCache:
    """
    Timed cache to reduce upvote/downvote spam. [user] cannot vote
    [target] before VOTE_DELAY seconds

    This functionality is easily provided by Gemfire and may be moved to that
    service at some point...
    """


    VOTE_DELAY = 300

    def __init__(self):
        self.cache = {}
        self.max_cache_size = 500  # ideally, this should never be reached
        logger.debug('Cache created')

    def __contains__(self, key):
        """
        True or false depending on if key is in cache
        """
        self.clean()
        return key in self.cache

    def update(self, key):
        """
        Updates the cache with key after cleaning it of old values
        """
        self.clean()
        if key not in self.cache and len(self.cache) < self.max_cache_size:
            self.cache[key] = {'time_added': time.time()}
            logger.debug('added to cache {} at time {}'.format(key, time.time()))

        elif key not in self.cache and len(self.cache) >= self.max_cache_size:
            logger.warning('cache is full - dropping oldest entry')
            self.remove_old()
            self.cache[key] = {'time_added': time.time()}

    def clean(self):
        """
        Removes any item older than VOTE_DELAY from the cache
        """
        logger.debug("cleaning cache")
        drop_keys = []
        for key in self.cache:
            if time.time() - self.cache[key]['time_added'] > self.VOTE_DELAY:
                drop_keys.append(key)
                logger.debug('Marked {} ready to be dropped'.format(key))
        for key in drop_keys:
            self.cache.pop(key)
            logger.debug('Dropped {} from cache'.format(key))


    def remove_old(self):
        """
        This should not generally be used - only occurs if we're actually
        reaching the cache size AFTER clearing old values. Ideally, cache
        and clean should be large/often enough that this function is never used
        """
        oldest = None
        for key in self.cache:
            if oldest is None:
                oldest = key
            elif (self.cache[key]['time_added'] <
                self.cache[oldest]['time_added']):
                oldest = key
        self.cache.pop(oldest)

    @property
    def timeout(self):
        return self.VOTE_DELAY
