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

import sys

from ceterach.api import MediaWiki

from .config import get_config
from .tasks import run_tasks
from .log import get_logger

# $ python -m cresbot [-v] [-t:task1,task2,...,taskn] [-l[:path/to/log/file]] [-p:password]

def setup(config:dict=None):
    """Set up config and start tasks."""
    # extract command line arguments and merge into config
    args = sys.argv[1:]
    config = get_config(args)

    # setup logging
    log = get_logger(config, __file__)

    # setup ceterach api instance
    api = MediaWiki(config['api_url'], config['api_config'])

    # limit to 3 tries
    for i in range(0, 3):
        if config.get('api_password', None) is None:
            prompt = 'Enter password for %s: ' % config.get['api_username']
            config.update({'api_password': input(prompt).strip()})

        logged_in = api.login(config['api_username'], config['api_password'])

        if logged_in is False:
            if i < 3:
                log.info('Incorrect password for %s. Please try again.', config['api_username'])
                # reset back to `None` to stop infinite loop
                config.update({'api_password': None})
            else:
                log.warning('Number of login attempts exceeded. Exiting.')
        else:
            break

    config['api'] = api

    log.info('Setup complete')

    try:
        run_tasks(config)
    # @todo change to `CresbotError` and allow error to bubble up to
    #       `setup` call as it's an indication of the code needing fixing somewhere
    except Exception as e:
        log.error('Uncaught exception: %s', e)

setup()

