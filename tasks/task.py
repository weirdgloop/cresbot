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

from cresbot.logging import create_log

class Task:
    def __init__(self):
        """Placeholder method all `Task` subclasses should implement."""
        raise NotImplementedError('"__init__" method not implemented.')
    
    def run(self):
        """Placeholder method all `Task` subclasses should implement."""
        raise NotImplementedError('"run" method not implemented.')

    def create_log(self, name:str='UnknownTask'):
        """A wrapper for `cresbot.logging.create_log` for easy creation of
        task logs.

        Args:
            name: A string represennting the task name.

        Returns:
            An instance of `logging.Logger` with file and stream handlers.
        """
        log = create_log('tasks.log', name)
        return log
