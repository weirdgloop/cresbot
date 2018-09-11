#! /usr/bin/env python3

"""
"""

# TODO: add support for overall counts

import argparse
from collections import defaultdict
from datetime import datetime
import logging
import os
import re
import sys

from lib.mediawiki import Api
from lib.config import Config
from lib.hiscores import Hiscores, Skill
from lib.exception import MediaWikiError, HiscoresError


LOG_FILE_FMT = 'hiscorecounts-{}.log'
PAGE_NAME = 'Module:Hiscore counts'


def main():
    """
    Program entry point.
    """
    args = parse_args()
    config = Config.from_toml(args.config)
    setup_logging(args, config)

    hiscores = Hiscores()
    logger = logging.getLogger(__name__)
    start = datetime.utcnow()

    try:
        cur_counts = get_current_counts(config)
        new_counts = update_counts(cur_counts, hiscores)

        save_counts(config, new_counts)
    except Exception as exc:
        logger.exception(exc)
    else:
        logger.info('Hiscore counts completed successfully')
    finally:
        # TODO: update stats
        # TODO: keep track of errors found while getting new counts
        pass



def parse_args() -> argparse.Namespace:
    """
    Handle command line arguments.

    :return: The found arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', required=True)

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-v', '--verbose', action='store_true')
    group.add_argument('-q', '--quiet', action='store_true')

    return parser.parse_args()


def setup_logging(args: argparse.Namespace, config: Config):
    """
    """
    if args.quiet:
        log_level = logging.WARNING
    elif args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    log_format = '[%(asctime)s][%(levelname)s][%(name)s] %(message)s'
    date_format = '%H:%M:%S'

    base_logger = logging.getLogger()
    base_logger.setLevel(log_level)

    formatter = logging.Formatter(log_format, datefmt=date_format)

    cur_date = datetime.utcnow()
    log_path = os.path.join(config.log_dir,
                            LOG_FILE_FMT.format(cur_date.strftime('%Y-%m-%d_%H-%M-%S')))

    fh = logging.FileHandler(filename=log_path)

    fh.setLevel(log_level)
    fh.setFormatter(formatter)

    base_logger.addHandler(fh)

    # attach a stream handler if this is being run manually
    if sys.stdout.isatty():
        sh = logging.StreamHandler()

        sh.setLevel(log_level)
        sh.setFormatter(formatter)

        base_logger.addHandler(sh)

    # force urllib to be quiet
    urllib_logger = logging.getLogger('urllib3')
    urllib_logger.setLevel(logging.WARNING)


def get_current_counts(config) -> str:
    """
    """
    api = Api(config.username, config.password, config.api_path)

    with api:
        text = api.get_page_content(PAGE_NAME)

    keys = ['count_99s',
            'count_99s_ironman',
            'count_120s',
            'count_120s_ironman',
            'count_200mxp',
            'count_200mxp_ironman',
            'lowest_ranks']

    ret = defaultdict(dict)
    rgx = re.compile(r'(\w+?)\[[\'"](.+?)[\'"]\]\s*=\s*[\'"]([\d,]+?)[\'"]')

    for line in text.split('\n'):
        if any([line.startswith(x) for x in keys]):
            res = rgx.match(line)

            if res is None:
                continue

            value = int(res.group(3).replace(',', ''))
            ret[res.group(1)][res.group(2)] = value

    return ret


def update_counts(current_counts: dict, hiscores: Hiscores) -> dict:
    """
    """
    logger = logging.getLogger(__name__)

    count_99s = current_counts.get('count_99s', {})
    count_99s_ironman = current_counts.get('count_99s_ironman', {})
    count_120s = current_counts.get('count_120s', {})
    count_120s_ironman = current_counts.get('count_120s_ironman', {})
    count_200mxp = current_counts.get('count_200mxp', {})
    count_200mxp_ironman = current_counts.get('count_200mxp_ironman', {})
    lowest_ranks = current_counts.get('lowest_ranks', {})

    for skill in Skill:
        if skill == Skill.OVERALL:
            continue

        name = skill.name.lower()

        try:
            count_99s[name] = hiscores.get_99s(skill, count_99s.get(name, 1))
        except HiscoresError as exc:
            logger.error('Unable to get 99s count for %s', name)
            logger.exception(exc)

        try:
            count_99s_ironman[name] = hiscores.get_99s_ironman(skill, count_99s_ironman.get(name, 1))
        except HiscoresError as exc:
            logger.error('Unable to get 99s ironman count for %s', name)
            logger.exception(exc)

        try:
            count_120s[name] = hiscores.get_120s(skill, count_120s.get(name, 1))
        except HiscoresError as exc:
            logger.error('Unable to get 120s count for %s', name)
            logger.exception(exc)

        try:
            count_120s_ironman[name] = hiscores.get_120s_ironman(skill, count_120s_ironman.get(name, 1))
        except HiscoresError as exc:
            logger.error('Unable to get 120s ironman count for %s', name)
            logger.exception(exc)

        try:
            count_200mxp[name] = hiscores.get_200m_xp(skill, count_200mxp.get(name, 1))
        except HiscoresError as exc:
            logger.error('Unable to get 200m XP count for %s', name)
            logger.exception(exc)

        try:
            count_200mxp_ironman[name] = hiscores.get_200m_xp_ironman(skill, count_200mxp_ironman.get(name, 1))
        except HiscoresError as exc:
            logger.error('Unable to get 200m XP ironman count for %s', name)
            logger.exception(exc)

        try:
            lowest = hiscores.get_lowest_rank(skill)
            lowest_ranks[name] = lowest['level']
            lowest_ranks[name + '.rank'] = lowest['rank']
        except HiscoresError as exc:
            logger.error('Unable to get lowest rank data for %s', name)
            logger.exception(exc)

    now = datetime.utcnow()
    cur_date = now.strftime('%d %B %Y')

    count_99s['updated'] = cur_date
    count_99s_ironman['updated'] = cur_date
    count_120s['updated'] = cur_date
    count_120s_ironman['updated'] = cur_date
    count_200mxp['updated'] = cur_date
    count_200mxp_ironman['updated'] = cur_date
    lowest_ranks['updated'] = cur_date

    return {
        'count_99s': count_99s,
        'count_99s_ironman': count_99s_ironman,
        'count_120s': count_120s,
        'count_120s_ironman': count_120s_ironman,
        'count_200mxp': count_200mxp,
        'count_200mxp_ironman': count_200mxp_ironman,
        'lowest_ranks': lowest_ranks,
    }


def save_counts(config: Config, new_counts: dict):
    """
    """
    logger = logging.getLogger(__name__)
    api = Api(config.username, config.password, config.api_path)

    with api:
        text = api.get_page_content(PAGE_NAME)

        for table, counts in new_counts.items():
            for skill, value in counts.items():
                pattern = r'{}\[[\'"]{}[\'"]\]\s*=\s*[\'"]([\d,]+?)[\'"]'.format(table, skill)

                if skill == 'updated':
                    pattern = r'{}\[[\'"]{}[\'"]\]\s*=\s*[\'"]([\w ]+?)[\'"]'.format(table, skill)
                    replace = '{}["{}"] = "{}"'.format(table, skill, value)
                else:
                    pattern = r'{}\[[\'"]{}[\'"]\]\s*=\s*[\'"]([\d,]+?)[\'"]'.format(table, skill)
                    replace = '{}["{}"] = "{:,}"'.format(table, skill, value)

                text = re.sub(pattern, replace, text)

        api.edit_page(PAGE_NAME, text, 'Updating hiscore counts')


if __name__ == '__main__':
    main()
