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
import math
from datetime import datetime
from copy import copy
from itertools import filterfalse
from time import time, sleep

from bs4 import BeautifulSoup, NavigableString as nstr

from cresbot.tasks.task import Task
from cresbot.login import login
from cresbot.lib.mw import Api
from cresbot.lib.rs.runescaperequest import RuneScapeRequest as RsReq

class HiscoreCounts(Task):

    _XP_120 = 104273167
    _XP_99 = 13034431
    _XP_MAX = 200000000
    _LVL_99 = 99
    _LVL_MAX = 2595

    _LVL = 2
    _XP = 3

    _updated = None
    _mwapi = None
    _rsrequest = None

    _skills = ['overall', 'attack', 'defence', 'strength', 'constitution',
               'ranged', 'prayer', 'magic', 'cooking', 'woodcutting',
               'fletching', 'fishing', 'firemaking', 'crafting', 'smithing',
               'mining', 'herblore', 'agility', 'thieving', 'slayer',
               'farming', 'runecrafting', 'hunter', 'construction',
               'summoning', 'dungeoneering', 'divination']

    _params = {'category_type': 0, 'table': 0, 'page': 0}

    def __init__(self):
        self.set_log('HiscoreCounts')
        self._updated = datetime.now().strftime('%d %B %Y').lstrip('0')
        self._mwapi = Api('http://runescape.wikia.com')
        self._mwapi.login('Cresbot', login('Cresbot'))
        self._rsreq = RsReq('http://services.runescape.com/m=hiscore/ranking',
                            12)

    def run(self):
        """Run hiscore counts task"""
        # @todo write something to do self._mwapi.page('PAGENAME').text()
        text = self.get_text('Module:Hiscore counts')
        self._log.info('Starting HiscoreCounts task.')
        
        #text = self.get_count(text, 'count_99s', self._LVL, self._LVL_99)
        #text = self.get_count(text, 'count_120s', self._XP, self._XP_120)
        #text = self.get_count(text, 'count_200mxp', self._XP, self._XP_MAX)
        text = self.get_lowest_ranks(text, 'lowest_ranks')

        self._log.info('HiscoreCounts task complete.')
        

    def get_text(self, title:str) -> str:
        """Get the text of a wiki page"""
        # ideally this would be a simple method of MWApi
        # but this will have to do until I get the time to write it
        params = {
            'action': 'query',
            'prop': 'revisions',
            'rvprop': 'content',
            'titles': title
        }

        resp = self._mwapi.call(params)
        resp = resp['query']['pages']
        text = resp[tuple(resp.keys())[0]]['revisions'][0]['*']

        return text

    def get_count(self, text:str, count:str, val_type:int, value:int) -> str:
        """Update the specified count.

        Args:
            text: A string containing the current counts as a lua table.
            count: The count to update.
            val_type: The type of value to look for, either `self._XP` or
                `self._LVL`.
            value: The minimum value to look for when updating the count.
                Varies depending on the value of `count`.

        Returns:
            A string with the updated counts replacing the old counts.
        """
        params = copy(self._params)
        rgx_table = 'local\s*%s\s*=\s*{(.*?)}' % count
        rgx_count = '(?:\[[\'"])?%s(?:[\'"]\])?\s*=\s*[\'"](.*?)[\'"]\s*,?'
        r_table = re.search(rgx_table, text, flags=re.S)
        # these are purposefully the same
        # they're used to update `text` below
        old_table = r_table.group(1).strip()
        table = r_table.group(1).strip()

        for i, skill in enumerate(self._skills):
            if skill == 'overall':
                # don't run overall for some counts
                if count in ['count_99s', 'count_120s']:
                    continue

                val = value * (len(self._skills) - 1)
            else:
                val = value

            self._log.info('Getting %s data for %s', value, skill)
            
            r_count = rgx_count % skill
            cur_count = re.search(r_count, table)

            repl = cur_count.group(0)
            num = cur_count.group(1)

            # 25 ranks per page
            start_page = math.floor(int(num.replace(',', '')) / 25)

            # catch for 200mxp overall
            if start_page == 0:
                start_page = 1

            params.update({'table': i, 'page': start_page})
            new_count = self._get_counts(params, val_type, val)
            self._log.info('Number of players with requested value in %s: %s.',
                           skill, new_count)
            repl2 = repl.replace(num, '{:,}'.format(new_count))

            table = table.replace(repl, repl2)

        # update updated time
        updated = re.search(rgx_count % 'updated', table).group(1)
        table = table.replace(updated, self._updated)

        text = text.replace(old_table, table)

        self._log.info('%s subtask complete.', count)
        return text

    def _get_counts(self, params:dict, col:int, value:int, checked:list=[],times:int=0) -> int:
        """Scrape the requested hiscors page looking for the last occurance
        of `value`.

        Args:
            params: A dict containing the parameters to query the hiscores
                page with.
            col: An integer between 0 and 3 representing a column in a 4
                column table. For normal usage it should be 2 or 3 for level
                or xp respectively.
            value: An integer representing the level or xp to look for.
            checked: A list of pages already checked.

        Returns:
            An integer representing the rank of the last player with `value`.

        Notes:
           This is an internal method and should not be called directly.
        """
        resp = self._rsreq.get(params)
        soup = BeautifulSoup(resp.text)
        rows = soup.select('div.tableWrap tbody tr')
        trs = []

        for tr in filterfalse(lambda x: isinstance(x, nstr), rows):
            tds = []
            for td in filterfalse(lambda x: isinstance(x, nstr), tr.contents):
                tds.append(td)

            trs.append(tds)

        if len(trs) == 0:
            self._log.warning('Rate limit hit after %s pages on %s',
                              len(checked), self._skills[params['table']])
            sleep(30)
            return self._get_counts(params, col, value, checked)

        # check if the last value on the page is `value`
        # if so jump to the next page
        last_val = trs[-1][col].a.string \
                   .strip() \
                   .replace(',', '')
        
        if int(last_val) >= value:
            # track which pages have already been visited
            checked.append(params['page'])
            params['page'] += 1
            self._log.debug('Requested value found in last row, moving to next page (%s).',
                            params['page'])
            return self._get_counts(params, col, value, checked)

        # check if the first value if less than `value`
        # if so jump to the previous page
        first_val = trs[0][col].a.string \
                    .strip() \
                    .replace(',', '')

        if int(first_val) < value:
            # check we're not on the first page (no players have `value`)
            if params['page'] == 1:
                return 0

            # check if the previous page has already been visited
            # to stop an infinite loop
            if (params['page'] - 1) in checked:
                rank = trs[0][0].a.string \
                       .strip() \
                       .replace(',', '')

                return int(rank)

            # track which pages have already been visited
            checked.append(params['page'])
            params['page'] -= 1
            self._log.debug('Requested value not found, moving to previous page (%s).',
                            params['page'])
            return self._get_counts(params, col, value, checked)

        # we should be on the correct page, so check every value
        # until one is found that matches `value`
        data = []
        
        for tds in trs:
            rank = tds[0].a.string \
                   .strip() \
                   .replace(',', '')
            val = tds[col].a.string \
                  .strip() \
                  .replace(',', '')

            if int(val) >= value:
                data.append(int(rank))
            else:
                break

        return data[-1]

    def get_lowest_ranks(self, text:str, table:str) -> str:
        """Get the lowest rank for each skill.

        Args:
            text:
            table:

        Returns:
            A string with the previous counts replaced by the new counts.
        """
        rgx_table = 'local\s*%s\s*=\s*{(.*?)}' % table
        rgx_count = '(?:\[[\'"])?%s(?:[\'"]\])?\s*=\s*[\'"](.*?)[\'"]\s*,?'
        r_table = re.search(rgx_table, text, flags=re.S)
        table = r_table.group(1).strip()
        old_table = r_table.group(1).strip()

        for i, skill in enumerate(self._skills):
            self._log.info('Getting lowest rank data for %s.', skill)

            # load the first page and look for a link to the last page
            self._log.debug('Getting first page.')
            params = copy(self._params)
            params.update({'table': i, 'page': 1})
            resp = self._rsreq.get(params)
            soup = BeautifulSoup(resp.text)
            page = soup.select('.pageNumbers li a')[-1].string

            # load the page and get the last row of the hiscores table
            self._log.debug('Getting last page.')
            params.update({'page': page})
            resp = self._rsreq.get(params)
            soup = BeautifulSoup(resp.text)
            last = soup.select('div.tableWrap tbody tr')[-1]

            # select the columns we need
            i = 0
            for td in filterfalse(lambda x: isinstance(x, nstr), last.contents):
                i += 1

                if i == 1:
                    rank = td.a.string \
                           .strip()
                elif i == 3:
                    lvl = td.a.string \
                          .strip()

            # update rank
            rgx_rank = rgx_count % (skill + '.rank')
            r_rank = re.search(rgx_rank, table)
            old_rank = r_rank.group(0)
            new_rank = old_rank.replace(r_rank.group(1), rank)
            table = table.replace(old_rank, new_rank)

            # update level
            rgx_lvl = rgx_count % skill
            r_lvl = re.search(rgx_lvl, table)
            old_lvl = r_lvl.group(0)
            new_lvl = old_lvl.replace(r_lvl.group(1), lvl)
            table = table.replace(old_lvl, new_lvl)

            self._log.info('Minimum level of %s: %s.', skill, lvl)
            self._log.info('Entry rank for %s: %s.', skill, rank)

        text = text.replace(old_table, table)
        self._log.info('lowest_ranks subtask complete.')
        return text


t = HiscoreCounts()
t.run()
