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

from .hiscorecounts import HiscoreCounts
from ..log import get_logger
from .. import exceptions as exc

# stored as a dict so specific tasks can be run if desired
taskdict = {
    'hiscorecounts': HiscoreCounts
}

def run_tasks(config):
    """Run tasks.

    Args:
        config:
    """
    log = get_logger(config, __file__)
    tasks = []

    if config['tasks'] is True:
        tasks = taskdict.values()
    elif isinstance(config['tasks'], list):
        tasks = config['tasks']

    # @todo figure out how to run this on startup (allow disabling on startup)
    #       and then every day at 00:00 UTC
    #       will require running tasks in a separate thread to allow other process to work
    #       allow other threads to check what's going on during task run(s)
    for task in tasks:
        try:
            log.info('Starting %s task.', task.__name__)
            t = task(config)
            t.run()
            log.info('%s task finished.', task.__name__)
        except exc.CresbotError as e:
            log.error(e)

    
    
