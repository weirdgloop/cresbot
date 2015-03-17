import os
from argparse import ArgumentParser

import yaml
from ceterach.api import MediaWiki

from .log import get_logger
from .tasks import start_tasks
from .exceptions import CresbotError

def main():
    # set available command line arguments
    parser = ArgumentParser()
    parser.add_argument('config',
                        help='Set config file.')
    parser.add_argument('-t',
                        choices=['all', 'hiscorecounts'],
                        default=[],
                        dest='tasks',
                        help='Run tasks on startup. To run all tasks on startup use `all`. To run specific tasks, add them by name delimited by a space. Allowed task names: `hiscorecounts`.',
                        metavar='task',
                        nargs='*')

    # parse arguments into a dictionary
    args = parser.parse_args()
    args = vars(args)

    # load config from file
    config_path = args.pop('config', 0)

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

if __name__ == '__main__':
    main()
