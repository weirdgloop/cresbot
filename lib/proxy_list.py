#

"""An iterator for spreading requests over multiple proxies to get around Jagex's rate limiting."""

import logging
import time
from typing import List


__all__ = ["ProxyList"]

LOGGER = logging.getLogger(__name__)


class ProxyList:
    """An iterator for spreading requests across a number of proxies.

    When iterated over, each proxy is returned in order and all proxies have been returned then the
    iteration is restarted from the beginning again. If a proxy is re-used, there is a minimum
    amount of time to wait before it can be re-used in which case the iterator will block until the
    delay period has elapsed.

    Example::

        >>> proxy_list = ProxyList(["a", "b", "c", "d"], 5)
        >>> for proxy in proxy_list:
        ...     print(proxy)
    """

    def __init__(self, proxies: List[str], delay: int, iter_delay: int = 1):
        """Create a new instance of ``ProxyList``

        :param List[str] proxies: The proxies to iterator over.
        :param int delay: The minimum amount of time to wait between re-using a proxy in seconds.
            Used to avoid sending too many requests from a single IP address within a given time
            period.
        :param int iter_delay: The minimum amount of time to wait between outputting the next
            element in the iteration in seconds. Defaults to 1. Used to avoid sending too many
            requests overall and overloading the target site.
        """
        self.proxies = proxies if proxies else [None]
        self.delay = delay
        self.iter_delay = iter_delay

        self.index = 0
        self.used = {}
        self.last = None

    def __len__(self):
        return len(self.proxies)

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        now = time.perf_counter()
        ret = self.proxies[self.index]

        # implement delay between using a given proxy
        # to avoid them getting blacklisted
        if self.index not in self.used:
            self.used[self.index] = time.perf_counter()
        else:
            diff = now - self.used[self.index]

            if diff < self.delay:
                sleep = self.delay - diff
                LOGGER.debug("Sleeping %.2f seconds before yielding %s (delay)", sleep, ret)
                time.sleep(sleep)

            self.used[self.index] = time.perf_counter()

        # set the index to the next value
        # or wrap back to the start if we've reached the end
        if self.index + 1 == len(self.proxies):
            self.index = 0
        else:
            self.index += 1

        # implement delay between requests
        # so we're not excessively hammering someone else's site
        if self.last is not None:
            diff = now - self.last

            if diff < self.iter_delay:
                sleep = self.iter_delay - diff
                LOGGER.debug("Sleeping %.2f seconds before yielding %s (iter delay)", diff, ret)
                time.sleep(sleep)

        self.last = time.perf_counter()

        return ret
