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

import os
from argparse import ArgumentParser

import yaml
from ceterach.api import MediaWiki

from .log import get_logger
from .tasks import start_tasks
from .exceptions import CresbotError

# set available command line arguments
parser = ArgumentParser(prog='$ python -m cresbot')
parser.add_argument('-p',
                    dest='api_password',
                    help='Set the password to log into the MediaWiki API with.',
                    metavar='password',
                    required=True)
parser.add_argument('-l',
                    dest='log_file',
                    help='(optional) Set the path to the log file.',
                    metavar='/path/to/log/file')
parser.add_argument('-t',
                    choices=['all', 'hiscorecounts'],
                    default=[],
                    dest='tasks',
                    help='(optional) Run specific tasks on startup.',
                    metavar='taskname',
                    nargs='*')

# parse arguments into a dictionary
args = parser.parse_args()
args = vars(args)

# set tasks to None if there's no specified tasks
# defaults to a list due to `... -t` producing an empty list anyway
if not len(args.get('tasks')):
    # can't use `.update()` here as it won't work for None
    # maybe delete it instead?
    args['tasks'] = None

# load config from file
config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.yaml')

# check file exists first
if not os.path.isfile(config_path):
    raise CresbotError('Config fle could not be found. Path: %s' % config_path)

with open(config_path) as f:
    config = yaml.load(f)
    # merge args into config
    config.update(args)

# setup logging
log = get_logger(config, 'cresbot')

# setup api instance
api = MediaWiki(config.get('api_url'), config.get('api_config'))
logged_in = api.login(config.get('api_username'), config.get('api_password'))

# check login attempt was successful
if not logged_in:
    log.error('Incorrect username or password. Username: %s; Password: %s',
              config.get('api_username'), config.get('api_password'))
    raise CresbotError('Incorrect password or username.')

# store in config for convenience
config.update({'api': api})

log.info('Setup complete!')

try:
    start_tasks(config)
except Exception as e:
    log.exception('Uncaught exception: %s', e)
