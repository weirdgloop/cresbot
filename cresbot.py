#!/usr/bin/env python3
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

"""
Command line usage docs

Config docs (generate config-sample.yaml from this?)
"""

import os
from argparse import ArgumentParser

import yaml
from ceterach.api import MediaWiki

from utils.log import get_logger
from utils.exceptions import SetupError
import tasks

def main():
    """Set up configuration and start any required scripts or tasks.

    Raises:
        SetupError
    """
    # set available command line arguments
    parser = ArgumentParser(prog='./cresbot.py')
    parser.add_argument('config',
                        help='Set path to config file.')
    parser.add_argument('-t',
                        choices=['all', 'hiscorecounts'],
                        default=[],
                        dest='tasks',
                        help='Run tasks on startup. To run all tasks on startup use `all`. To run specific tasks, add them by name delimited by a space. Allowed task names: `hiscorecounts`.',
                        metavar='task',
                        nargs='*')

    # parse arguments and convert to a dictionary
    args = parser.parse_args()
    args = vars(args)

    # load config from file
    config_path = args.pop('config', 0)

    with open(config_path) as f:
        try:
            config = yaml.load(f)
        except FileNotFoundError as e:
            raise SetupError from e

        # merge args into config
        config.update(args)

    # setup logging
    try:
        log = get_logger(config, 'cresbot')
    except FileNotFoundError as e:
        raise SetupError('Log file could not be found. Please check the directory exists.') from e

    # setup api instance
    api = MediaWiki(config.get('api_url'), config.get('api_config'))

    try:
        logged_in = api.login(config.get('api_username'), config.get('api_password'))
    # @todo catch more specific exception
    #       ApiError?
    except Exception as e:
        raise SetupError('MediaWiki API URL could not be verified. Please check your config file.') from e

    # check login attempt was successful
    if not logged_in:
        raise SetupError('Incorrect password or username in config.')

    # clean up
    api.logout()

    # store in config for convenience
    config.update({'api': api})

    log.info('Setup complete!')

    try:
        tasks.start_tasks(config)
    except Exception as e:
        log.exception('Uncaught exception: %s', e)

main()
