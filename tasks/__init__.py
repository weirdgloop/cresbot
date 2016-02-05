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

from time import time, sleep

from schedule import Scheduler

from utils.log import get_logger
import utils.exceptions as crexc
from tasks.hiscorecounts import HiscoreCounts

# stored as a dict so specific tasks can be run if desired
tasks = {
    'hiscorecounts': HiscoreCounts
}

def run_task(task, config:dict, log):
    """Run a task.

    Arguments:
        task: An instance that implements the Task abstract class.
        config: Main configuration dictionary created on start up.
        log: Instance of Logger to log exceptions with.
    """
    start_time = time()

    try:
        t = task(config)
        log.info('Starting %s task.', task.__name__)
        t.run()

        # convert time to complete into minutes
        complete_time = int((time() - start_time) / 60)
        log.info('%s task finished. Task run time : %s minutes.', task.__name__, complete_time)
    except crexc.CresbotError as e:
        log.exception(e)

def start_tasks(config:dict):
    """Queue tasks ready for next scheduled run. Also start any requested tasks, depending on
    configuration options.

    Arguments:
        config: Main configuration dictionary created on start up.
    """
    log = get_logger(config, 'cresbot.tasks')

    # store Scheduler instance for easy references to jobs
    # <https://github.com/dbader/schedule>
    s = Scheduler()

    # queue tasks ready next scheduled run
    log.info('Queueing tasks for next scheduled run.')

    for name, task in tasks.items():
        job = s.every().day.at('00:00').do(run_task, task, config, log)
        tasks[name] = job

    # check if any tasks should be run on startup
    if len(config.get('tasks')):
        log.info('Attempting to run start up task(s).')

        if 'all' in config.get('tasks'):
            config.update({'tasks': tasks.keys()})

        for task in config.get('tasks'):
            tasks.get(task).run()
    else:
        log.info('No start up tasks found.')

    while True:
        s.run_pending()
        sleep(1)
