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
from logging.handlers import SMTPHandler

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

    # optional file logging
    if config.get('log_file', None) is not None:
        # @todo have separate logs for each day/task run
        fh = logging.FileHandler(config.get('log_file'))
        fh.setLevel(config.get('log_level_file'))
        fh.setFormatter(formatter)
        log.addHandler(fh)

    # optional email logging
    if config.get('log_email', False):
        # http://bytes.com/topic/python/answers/760212-examples-logger-using-smtp
        # need to subclass SMTPHandler for gmail support
        pass
        """
        smtp = SMTPHandler(
            mailhost = tuple(config.get('log_email_host')),
            fromaddr = config.get('log_email_from'),
            toaddrs = config.get('log_email_to'),
            subject = config.get('log_email_subject'),
             # @todo move this to a single config option
            credentials = (config.get('log_email_username'), config.get('log_email_password'))
        )
        smtp.setLevel(config.get('log_level_email'))
        smtp.setFormatter(formatter)
        log.addHandler(smtp)
        """


    # default stream logging
    sh = logging.StreamHandler()
    sh.setLevel(config.get('log_level_stream', 'INFO'))
    sh.setFormatter(formatter)
    log.addHandler(sh)

    # prevent duplicate log entries being added
    log.propagate = False

    return log
