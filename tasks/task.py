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

import logging

class Task:
    
    def run():
        """Placeholder method all `Task` subclasses should implement."""
        raise NotImplementedError('"run" method not implemented')

    def set_log(self, name:str='UnknownTask', level:str='DEBUG'):
        """Create a Logger instance.

        Args:
            name:
            level:
        """
        log = logging.getLogger(name)
        log.setLevel(level)

        # set handlers and formatter
        # @todo reate wikitext log for pasting to the wiki
        fh = logging.FileHandler('logs/tasks.log')
        sh = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                      '%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)
        sh.setFormatter(formatter)

        # add handlers
        log.addHandler(fh)
        log.addHandler(sh)
        
        self._log = log
