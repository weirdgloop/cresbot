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

from abc import ABCMeta, abstractmethod

from log import get_logger

class Task:
    """Abstract class for tasks."""

    __metaclass__ = ABCMeta

    log = None
    api = None

    @abstractmethod
    def __init__(self, config:dict, filename:str):
        """Set up api and logger instances for later use.

        Arguments:
            config: Config dictionary created on start up.
            filename: The name of the file to be used during logging.
        """
        self.log = get_logger(config, filename)
        self.api = config.get('api')

    @abstractmethod
    def run(self):
        """Run the task."""
        pass
