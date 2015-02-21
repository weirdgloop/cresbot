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

from datetime import datetime
from cresbot.lib.mw import Api
from cresbot.lib.rs.runescaperequest import RuneScapeRequest
from task import Task
from cresbot.login import login

class HiscoreCounts(Task):

    _XP_120 = 104273167
    _XP_99 = 13034431
    _XP_MAX = 200000000
    _LVL_MAX = 2595

    _updated = None
    _mwapi = None
    _rsrequest = None

    _skills = ['overall', 'attack', 'defence', 'strength', 'constitution',
               'ranged', 'prayer', 'magic', 'cooking', 'woodcutting',
               'fletching', 'fishing', 'firemaking', 'crafting', 'smithing',
               'mining', 'herblore', 'agility', 'thieving', 'slayer',
               'farming', 'runecrafting', 'hunter', 'construction',
               'summoning', 'dungeoneering', 'divination']

    def __init__(self):
        self._updated = datetime.now().strftime('%d %B %Y').lstrip('0')
        self._mwapi = Api('http://runescape.wikia.com')
        self._mwapi.login('Cresbot', login('Cresbot'))
        self._rsrequest = RuneScapeRequest('http://services.runescape.com/m=hiscore/ranking')

    def run(self):
        """Run hiscore counts task"""
        # @todo write something to do self._mwapi.page('PAGENAME').text()
        text = self.get_text('Module:Hiscore counts')
        print(text)

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

        resp = self._mwapi.call(**params)
        resp = resp['query']['pages']
        text = resp[tuple(resp.keys())[0]]['revisions'][0]['*']

        return text

#t = HiscoreCounts()
#t.run()
