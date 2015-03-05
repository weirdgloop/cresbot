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

# @todo move this into a .yaml file?
_config = {
    # default setting for test mode
    # altered depending on arguments passed during command line usage
    'test_mode': False,

    # ceterach api config
    'api_url': 'http://runescape.wikia.com/api.php',
    'api_config': {'defaults': {'maxlag': 5}},
    'api_username': 'Cresbot',
    'api_password': None,
    'api': None,

    # cresbot.logging config
    # stream log level will be changed to 'DEBUG' during test mode
    # file and email logging is disabled during test mode
    # 'log_file': '/var/log/cresbot.log',
    'log_file': None,
    'log_level_stream': 'INFO',
    'log_level_file': 'DEBUG',
    # @todo implement
    'log_level_email': 'ERROR',

    # task config
    # set to `True` to run all tasks, `False` to run no tasks
    #
    # can also be a list of specific tasks to run
    # allowed keys: 'hiscorecounts'
    #
    # altered depending on arguments passed during command line usage
    # if run in test_mode
    'tasks': True,
    # whether to run all tasks on startup or to wait until the next scheduled
    # time to run
    'tasks_startup': False
}

def get_config(args:list):
    """Get the current settings defined in the config file.

    Args:
        args: A list containing the command line arguments.

    Returns:
        A dict containing the settings defined in the config file updated with the settings passed
        from the command line.
    """
    config = _config

    for arg in args:
        # debug/test mode
        if arg == '-v':
            config.update({
                'test_mode': True,
                'log_level_stream': 'DEBUG'
            })

            if not any('-l' in a for a in args):
                config.update({'log_file': None})

        # run specific tasks straight away
        # or run all tasks straight away
        if arg.startswith('-t'):
            tasks = arg[3:]
            tasks = tasks.split(' ')

            if not len(tasks):
                tasks = True
            # apparently sys.argv normalises -foo:bar,baz,quux
            # to -foo:bar baz quux
            config.update({
                'tasks': tasksm
                'tasks_startup': True
            })

        # (un)set log file
        if arg.startswith('-l'):
            log_file = arg[3:]

            config.update({'log_file': None if log_file == '' else log_file})

        # set password
        if arg.startswith('-p'):
            # @todo try to move this into a config file as well
            password = arg[3:]
            config.update({'api_password': password})

    return config
