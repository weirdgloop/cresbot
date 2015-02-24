# ----------------------------------------------------------------------
# Copyright (c) 2015 Matthew Dowdell <mdowdell244@gmail.com>.
# This file is part of Cresbot.
#
# Cresbot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cresbot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cresbot.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------

from copy import copy
from time import time, sleep
from urllib.parse import urlparse
import requests
from cresbot import USER_AGENT

class RuneScapeRequest():

    _last = None

    def __init__(self, url:str, throttle:int=0):
        """Create a RuneScapeRequest instance.

        Args:
            url: A string representing a URL pointing to runescape.com for
                HTTP requests to be sent to.
            throttle: A positive integer representing the minimum time in
                seconds between HTTP requests to `url`.

        Raises:
            ValueError: "url" is not a valid runescape domain.
        """
        # check URL is a runescape.com subdomain
        o = urlparse(url)
            
        if not o.netloc.endswith('runescape.com'):
            raise ValueError('"url" is not a valid runescape domain.')
            
        self._url = url
        self._throttle = throttle

        # setup request session
        self._request = requests.Session()
        self._request.headers.update({'User-Agent': USER_AGENT})

    def get(self, params:dict):
        """Make a request with the GET method.

        Args:
            params: A dict representing key-value pairs of a query string
                to be appended to the request URL

        Returns:
            An instance of requests.models.Response containing the response
            to the GET request.
        """
        if self._last is not None:
            diff = time() - self._last
            
            if diff < self._throttle:
                sleep(self._throttle - diff)

        ret = self._request.get(self._url, params=params)
        self._last = time()
        return ret
