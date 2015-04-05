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

    Arguments:
        config: A dict containing configuration settings.
        name: A string representing the name of the script submitting to
            the log.

    Returns:
        An instance of Logger with file and stream handlers.

    Notes:
        Deleting the log file during idle tme causes logging to malfunction in files where
        Logger is already bound. Find some way to fix it?
    """
    no_log = True

    log = logging.getLogger(name)
    # required to set default level or nothing is output
    log.setLevel('DEBUG')

    # remove any existing handlers
    # prevents duplicate entries with task runs
    log.handlers = []

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                  '%Y-%m-%d %H:%M:%S')

    # optional file logging
    if config.get('log_file') is not None:
        no_log = False
        # @todo utilise <https://docs.python.org/3.4/library/logging.handlers.html#logging.handlers.TimedRotatingFileHandler>
        fh = logging.FileHandler(config.get('log_file'))
        fh.setLevel(config.get('log_level_file', 'DEBUG'))
        fh.setFormatter(formatter)
        log.addHandler(fh)

    # optional email logging
    if config.get('log_email', False):
        # no_log = False
        # <http://bytes.com/topic/python/answers/760212-examples-logger-using-smtp>
        # <https://docs.python.org/3.4/library/logging.handlers.html#logging.handlers.SMTPHandler>
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

    # backup stream logging
    if no_log:
        sh = logging.StreamHandler()
        sh.setLevel(config.get('log_level_stream', 'DEBUG'))
        sh.setFormatter(formatter)
        log.addHandler(sh)

    # prevent duplicate log entries being added
    log.propagate = False

    return log
