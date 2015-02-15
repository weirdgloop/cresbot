# ----------------------------------------------------------------------
# Copyright (c) 2015 Matthew Dowdell <cqm.fwd@gmail.com>.
#
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

import requests
from copy import copy
from time import time, sleep
from urllib.parse import urlparse
from platform import python_version as pyv

# move these into a separate file, info.py
repo = 'https://github.com/onei/cresbot'
USER_AGENT = 'Cresbot/%s (Python %s; %s; mailto:cqm.fwd@gmail.com)'
USER_AGENT %= '0.1', pyv(), repo

class RuneScapeRequest():

    def __init__(self, config:dict):
        """<doc>"""
        # check URL is a runescape.com subdomain
        o = urlparse(url)
            
        if not o.netloc.endswith('runescape.com'):
            raise ValueError('URL is not a valid runescape domain')
            
        self._url = url

        # default throttle to 0
        if 'throttle' not in config:
            config.update({'throttle': 0})

        self._throttle = config['throttle']

        # add user agent for jagex
        self._request = requests.Session()
        self._request.headers.update({'User-Agent': USER_AGENT})

    def get(self, params):
        """<doc>"""
        if self._last is not None:
            diff = time() - self._last
            print(diff)
            
            if diff < throttle:
                sleep(diff)

        # @todo errors?
        ret = self._request.get(self._url, params=params)
        return ret

# simple hiscores test
conf = {
    throttle: 0,
    url: 'http://services.runescape.com/m=hiscore/ranking'
}
r = RuneScapeRequest(conf)
params = {'category_type': 0, 'table': 0, 'page': 1}
r.get(params)
print(res.text)
