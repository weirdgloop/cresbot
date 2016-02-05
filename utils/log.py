# ----------------------------------------------------------------------
# Copyright (c) 2015-2016 Matthew Dowdell <mdowdell244@gmail.com>.
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

    # file logging
    if config.get('log_file') is not None:
        no_log = False

        fh = logging.FileHandler(config.get('log_file'))
        fh.setLevel(config.get('log_file_level', 'DEBUG'))
        fh.setFormatter(formatter)
        log.addHandler(fh)

    # email logging
    if config.get('log_email', False):
        no_log = False

        mailhost = config.get('log_email_mailhost')
        credentials = config.get('log_email_credentials')

        # bug workaround, see <https://bugs.python.org/issue22646>
        # fixed in python 3.4, see <https://hg.python.org/cpython/rev/d15708f13266>
        # should be fixed, but don't chance it when python is packaged with OS's
        if isinstance(mailhost, list):
            mailhost = tuple(mailhost)
        if isinstance(credentials, list):
            credentials = tuple(credentials)

        mh = logging.handlers.SMTPHandler(
            mailhost = mailhost,
            fromaddr = config.get('log_email_from'),
            toaddrs = config.get('log_email_to'),
            subject = config.get('log_email_subject'),
            credentials = credentials,
            secure = config.get('log_email_secure')
        )

        mh.setLevel(config.get('log_level_email', 'ERROR'))
        mh.setFormatter(logging.Formatter('''
            Message level: %(levelname)s
            Location:      %(pathname)s:%(lineno)d
            Time:          %(asctime)s

            Message:

            %(message)s
        '''))
        log.addHandler(mh)

    # backup stream handler
    # only added of no other logging is enabled
    if no_log:
        sh = logging.StreamHandler()
        sh.setLevel(config.get('log_level_stream', 'DEBUG'))
        sh.setFormatter(formatter)
        log.addHandler(sh)

    # prevent duplicate log entries being added
    log.propagate = False

    return log
