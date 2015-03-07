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
import logging

def get_logger(config:dict, name:str):
    """Create an instance of `Logger`.

    Args:
        config: A dict containing configuration settings.
        name: A string representing the name of the script submitting to
            the log.

    Returns:
        An instance of Logger with file and stream handlers.
    """

    log = logging.getLogger(name)
    # required to set default level or nothing is output
    log.setLevel('DEBUG')

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                  '%Y-%m-%d %H:%M:%S')

    if config['log_file'] is not None:
        # @todo would this be easier to have separate logs for each day/task run?
        fh = logging.FileHandler(config.get('log_file'))
        fh.setLevel(config.get('log_level_file'))
        fh.setFormatter(formatter)
        log.addHandler(fh)

    # @todo implement email logging for errors
    # http://stackoverflow.com/a/6187851/1942596
    # limit to top level errors

    sh = logging.StreamHandler()
    sh.setLevel(config.get('log_level_stream', 'INFO'))
    sh.setFormatter(formatter)
    log.addHandler(sh)

    # prevent duplicate log entries being added
    log.propagate = False

    return log
