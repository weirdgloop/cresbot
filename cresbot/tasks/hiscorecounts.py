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

import re
import sys
import math
from copy import copy
from time import time, sleep
from datetime import datetime

import requests
from ceterach.api import MediaWiki
from ceterach import exceptions as cetexc
from bs4 import BeautifulSoup, NavigableString as nstr

from .task import Task
from .. import exceptions as crexc

__all__ = ['HiscoreCounts']

# minimum xp required for certain lvels
XP_99 = 13034431
XP_120 = 104273167
XP_MAX = 200000000

# current list of skills
SKILLS = ['overall', 'attack', 'defence', 'strength', 'constitution',
          'ranged', 'prayer', 'magic', 'cooking', 'woodcutting',
          'fletching', 'fishing', 'firemaking', 'crafting', 'smithing',
          'mining', 'herblore', 'agility', 'thieving', 'slayer',
          'farming', 'runecrafting', 'hunter', 'construction',
          'summoning', 'dungeoneering', 'divination']

class HiscoreCounts(Task):

    # placeholder date string for updating 'updated' value in each count table
    updated = None

    # default params for requesting hiscore pages
    def_params = {'category_type': 0, 'table': 0, 'page': 0}

    # placeholder pattern for getting the values in a lua table
    re_count = '(?:\[[\'"])?%s(?:[\'"]\])?\s*=\s*[\'"](.*?)[\'"]\s*,?'

    # config for making requests to runescape api
    url = 'http://services.runescape.com/m=hiscore/ranking'
    last = None
    # reducing this and making large amounts of HTTP requests to runescape.com
    # can cause the used IP to be (temporarily?) blacklisted
    throttle = 12

    # placeholders used for logging rate limiting
    num_reqs = 0
    err_time = None

    # storage for saving the updated counts in case of being unable to update the page
    # once all data has been gathered
    new_counts = {}

    def __init__(self, config:dict):
        """Set up the HiscoreCounts task."""
        super().__init__(config, 'cresbot.tasks.hiscorecounts')
        
        # set updated date string
        self.updated = datetime.now().strftime('%d %B %Y').lstrip('0')

    def _get_page(self, params:dict):
        """Get the content of a RuneScape Hiscores page.

        Args:
            params: A dict containing the parameters to send to the hiscores URL.

        Returns:
            An instance of BeautifulSoup containing the parsed hiscores table.

        Raises:
            CresbotError:
        """
        # @todo split this out into an external library?
        # throttle requests
        if self.last is not None:
            diff = time() - self.last

            if diff < self.throttle:
                sleep(self.throttle - diff)
        else:
            print('first request')

        # normalise any exceptions
        try:
            resp = requests.get(self.url, params=params)
        except (requests.HTTPError, requests.ConnectionError) as e:
            raise crexc.CresbotError(e)
            
        self.num_reqs += 1
        self.last = time()

        soup = BeautifulSoup(resp.text)
        errors = soup.select('#errorContent')

        # handle ratelimit
        if len(errors):
            self.log.warning('Rate limit hit after %s pages.')
            
            if self.err_time is not None:
                diff = time() - self.err_time
                self.log.warning('Time since rate limit was last hit: %s.',
                                 diff)
                
            self.err_time = time()
            sleep(30)
            return self._get_page(params)
        
        return soup

    def run(self):
        """Run hiscore counts task."""
        try:
            self.log.info('Getting current counts text.')
            page = self.api.page('Module:Hiscore counts')
            text = page.content
        # @todo handle these separately?
        except (cetexc.ApiError, cetexc.CeterachError) as e:
            self.log.warning('Current counts text count not be found. Error: %s', e)
            # @todo implement fallback if reasonable
            raise crexc.CresbotError(e)
        
        # @todo error handling?
        text = self.get_count(text, 'count_99s', 99, 'LEVEL')
        text = self.get_count(text, 'count_120s', XP_120, 'XP')
        text = self.get_count(text, 'count_200mxp', XP_MAX, 'XP')
        text = self.get_lowest_ranks(text, 'lowest_ranks')

        try:
            # reset the token with each edit
            # otherwise this fails on subsequent runs as it uses the same api instance
            page._api.set_token('edit')
            page.edit(text, 'Updating hiscore counts', bot=True)
        # @todo handle other errors?
        except cetexc.EditError as e:
            self.log.warning('Could not update hiscore counts. Error: %s', e)
            self.log.warning(text)
            raise crexc.CresbotError(e)

    def get_count(self, text:str, count:str, value:int, val_type:str):
        """Look for the last occurance of `value` in each hiscores table and update `text` with it.

        Args:
            text: A string containing all the current counts as a lua table.
            count: The name of the lua table in `text` to update.
            value: An integer representing the value to look for when updating `count`.
            val_type: A string of 'LEVEL' or 'XP' depending on which type of data is being updated.

        Returns:
            A string with the updated counts replacing the old counts.
        """
        if val_type == 'LEVEL':
            val_type = 2
        elif val_type == 'XP':
            val_type = 3

        # @todo save gathered data into a dict so it can be salvaged if required
        #       output to yaml file (readable)?
        params = copy(self.def_params)
        rgx_table = 'local\s*%s\s*=\s*{(.*?)}' % count
        r_table = re.search(rgx_table, text, flags=re.S)
        old_table = r_table.group(1).strip()
        table = r_table.group(1).strip()

        for i, skill in enumerate(SKILLS):
            if skill == 'overall':
                # don't run overall for some counts
                if count in ['count_99s', 'count_120s']:
                    continue

                self.log.info('Getting %s data for %s', value, skill)
                val = value * (len(SKILLS) - 1)
            else:
                self.log.info('Getting %s data for %s', value, skill)
                val = value
            
            r_count = self.re_count % skill
            cur_count = re.search(r_count, table)

            repl = cur_count.group(0)
            num = cur_count.group(1)

            # 25 ranks per page
            start_page = math.ceil(int(num.replace(',', '')) / 25)
            params.update({'table': i, 'page': max(start_page, 1)})

            # if something goes wrong here
            # we skip updating that count, log the error
            # and move onto the next
            try:
                new_count = self.find_value(params, val_type, val)
            # @todo handle more specific exceptions
            except Exception as e:
                self.log.exception(e)
            else:
                table = self.update_count(table, skill, new_count, count)

        # update updated time
        table = self.update_count(table, 'updated', self.updated, count)

        # update text
        text = text.replace(old_table, table)
        self.log.info('%s subtask complete.', count)
        return text

    # the number of variables for this ridiculous
    # figure out how to reduce them
    def find_value(self, params:dict, col:int, value:int, checked:list=None, step:int=1, accel:int=2, first:bool=True, reqs:int=0, up:bool=None, found:bool=False):
        """Scrape the requested hiscores page looking for the last occurance
        of `value`.

        Args:
            params: A dict containing the parameters to query the hiscores
                page with.
            col: An integer between 0 and 3 representing a column in a 4
                column table. For normal usage it should be 2 or 3 for level
                or xp respectively.
            value: An integer representing the level or xp to look for.
            checked: A list of pages already checked.
            step:
            accel:
            first:
            reqs:
            up:
            found:

        Returns:
            An string representing the rank of the last player with `value`.

        Notes:
           This is an internal method and should not be called directly.
           @todo prefix with underscore
        """
        if checked is None:
            checked = []

        reqs += 1

        self.log.debug('page: %s, step: %s, reqs: %s, up: %s, found: %s', params['page'], step,
                       reqs, up, found)

        soup = self._get_page(params)
        rows = (x for x in soup.select('div.tableWrap tbody tr') \
                if not isinstance(x, nstr))
        trs = []

        for tr in rows:
            tds = (x for x in tr.contents if not isinstance(x, nstr))
            trs.append(tuple(tds))

        # check if the last value on the page is `value`
        # if so jump forwards
        last_val = trs[-1][col].a.string.strip().replace(',', '')

        if int(last_val) >= value:
            if first is True:
                first = False
                up = True

            # move the below to an else so we don't jump forward 2 pages straight away

            if up is False and not found:
                found = True

            if up and not found:
                step *= accel
            else:
                step = int(step / accel)

            # track which pages have already been visited
            checked.append(params['page'])
            params['page'] += int(step)
            return self.find_value(params, col, value, checked, step, accel, first, reqs, up, found)

        # check if the first value if less than `value`
        # if so jump backwards
        first_val = trs[0][col].a.string.strip().replace(',', '')

        if int(first_val) < value:
            # check we're not on the first page (no players have `value`)
            if params['page'] == 1:
                return '0'

            if first is True:
                first = False
                up = False

            if up is True and not found:
                found = True

            if not up and not found:
                step *= accel
            else:
                step = int(step / accel)

            # check if the previous page has already been visited
            # to stop an infinite loop
            if (params['page'] - 1) in checked:
                rank = trs[0][0].a.string.strip()

                return rank

            # track which pages have already been visited
            checked.append(params['page'])
            params['page'] -= int(step)
            return self.find_value(params, col, value, checked, step, accel, first, reqs, up, found)

        # we should be on the correct page, so check every value
        # until one is found that matches `value`
        data = []
        
        for tds in trs:
            rank = tds[0].a.string.strip()
            val = tds[col].a.string.strip().replace(',', '')

            if int(val) >= value:
                data.append(rank)
            else:
                break

        self.log.info('No. requests: %s.', reqs)

        return data[-1]

    def get_lowest_ranks(self, text:str, table:str):
        """Get the lowest rank for each skill.

        Args:
            text:
            table:

        Returns:
            A string with the previous counts replaced by the new counts.
        """
        rgx_table = 'local\s*%s\s*=\s*{(.*?)}' % table
        r_table = re.search(rgx_table, text, flags=re.S)
        table = r_table.group(1).strip()
        old_table = r_table.group(1).strip()

        for i, skill in enumerate(SKILLS):
            self.log.info('Getting lowest rank data for %s.', skill)

            # load the first page and look for a link to the last page
            self.log.debug('Getting first page.')
            params = copy(self.def_params)
            params.update({'table': i, 'page': 1})
            soup = self._get_page(params)
            # should be 7 keys here
            page = soup.select('.pageNumbers li a')[-1].string

            # load the page and get the last row of the hiscores table
            self.log.debug('Getting last page.')
            params.update({'page': page})
            soup = self._get_page(params)
            cells = tuple(x for x in soup.select('div.tableWrap tbody tr') \
                          [-1].contents if not isinstance(x, nstr))

            rank = cells[0].a.string.strip()
            lvl = cells[2].a.string.strip()

            # update table
            # @todo don't hardcode the count in this
            table = self.update_count(table, skill + '.rank', rank, 'lowest_ranks')
            table = self.update_count(table, skill, lvl, 'lowest_ranks')

            self.log.info('Minimum level of %s: %s.', skill, lvl)
            self.log.info('Entry rank for %s: %s.', skill, rank)

        # update updated time
        table = self.update_count(table, 'updated', self.updated, 'lowest_ranks')

        # update text
        text = text.replace(old_table, table)
        self.log.info('lowest_ranks subtask complete.')
        return text

    def update_count(self, text:str, key:str, val:str, count:str):
        """Update the value of a key in a lua table.

        Args:
            text:
            key:
            val:

        Returns:
            A string...
        """
        rgx = self.re_count % key
        match = re.search(rgx, text)
        # should we handle exceptions caused by the key not existing?
        old = match.group(0)
        new = old.replace(match.group(1), val)
        ret = text.replace(old, new)

        # store the updated values in a dict so they can be recovered if necessary
        if self.new_counts.get(count, None) is None:
            self.new_counts[count] = {}

        self.new_counts[count].update({key: val})
        
        return ret
