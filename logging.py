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

import cresbot

def create_log(file:str, name:str):
    """Create an instance of `Logger`.

    Args:
        file: A string representing name of the log file.
        name: A string representing the name of the script submitting to
            the log.

    Returns:
        An instance of Logger with file and stream handlers.
    """
    abspath = os.path.abspath(__file__)
    fpath = os.path.join(os.path.dirname(abspath), 'logs', file)

    log = logging.getLogger(name)
    log.setLevel('DEBUG')

    fh = logging.FileHandler(fpath)
    sh = logging.StreamHandler()

    fh.setLevel(cresbot.FILE_LOG_LEVEL)
    sh.setLevel(cresbot.STREAM_LOG_LEVEL)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                  '%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)

    log.addHandler(fh)
    log.addHandler(sh)

    return log
