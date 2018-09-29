#! /usr/bin/env python3

"""
"""

import argparse
import logging
import os
from pprint import pprint

from lib.config import Config
from lib.exception import MediaWikiError, ExchangeTemplateMissingError, \
    ExchangeTemplateConvertedError
from lib.mediawiki import Api
from lib.rswiki import ExchangeItem
from lib.util import setup_logging


LOG_FILE_FMT = 'migrateexchange-{}.log'
FAILED_FILE = 'failed.txt'
EXCLUDE_PAGES = ['Module:Exchange/test']

total_revisions = 0

def main():
    """
    Program entry point.
    """
    args = parse_args()
    config = Config.from_toml(args.config)
    setup_logging(args, config, LOG_FILE_FMT)
    logger = logging.getLogger('migrateexchange')

    api = Api(config.username, config.password, config.api_path)

    cur_path = os.path.dirname(os.path.abspath(__file__))
    failed_path = os.path.join(cur_path, FAILED_FILE)

    if not args.start:
        try:
            # empty file at the start of the run
            os.remove(failed_path)
        except FileNotFoundError:
            pass

    with api:
        if args.modules:
            ap_params = {'list': 'allpages',
                         'apnamespace': 828,
                         'apprefix': 'Exchange/',
                         'aplimit': 'max'}
            rv_params = {'prop': 'revisions',
                         'rvprop': 'ids|content|timestamp',
                         'rvlimit': 'max',
                         'path': 'revisions'}

            if args.start:
                ap_params['apfrom'] = args.start

            for page in api.iterator(**ap_params):
                title = page['title']

                if title.endswith('/Data') or title in EXCLUDE_PAGES:
                    continue

                title_parts = title.split('/', maxsplit=1)

                if title_parts[1].startswith(('1/3', '1/2', '2/3')):
                    with open(failed_path, 'a') as fh:
                        fh.write('Title: {!s}: Error: Page title should contain fraction entities\n'
                                 .format(title))

                if not args.revisions:
                    text = api.get_page_content(title)
                    total_revisions += 1
                    check_content_module(title, text, failed_path)
                else:
                    rv_params['titles'] = title

                    for revision in api.iterator(**rv_params):
                        total_revisions += 1
                        try:
                            text = revision['*']
                            revision_id = revision['revid']
                        except KeyError:
                            pprint(revision)
                            raise

                        check_content_module(title, text, failed_path, True, revision_id)

        if args.pages:
            ap_params = {'list': 'allpages',
                         'apnamespace': 112,
                         'aplimit': 'max'}
            rv_params = {'prop': 'revisions',
                         'rvprop': 'ids|content|timestamp',
                         'rvlimit': 'max',
                         'path': 'revisions'}

            if args.start:
                ap_params['apfrom'] = args.start

            for page in api.iterator(**ap_params):
                title = page['title']

                if title.endswith('/Data') or title in EXCLUDE_PAGES:
                    continue

                rv_params['titles'] = title

                for revision in api.iterator(**rv_params):
                    total_revisions += 1
                    try:
                        text = revision['*']
                        revision_id = revision['revid']
                    except KeyError:
                        pprint(revision)
                        raise

                    check_content_page(title, text, failed_path, revision_id)


def parse_args() -> argparse.Namespace:
    """
    Handle command line arguments.

    :return: The found arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', required=True)
    parser.add_argument('--start', required=False)
    parser.add_argument('--revisions', action='store_true', default=False)

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--modules', action='store_true')
    group.add_argument('--pages', action='store_true')
    group.add_argument('--both', action='store_true')

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-v', '--verbose', action='store_true')
    group.add_argument('-q', '--quiet', action='store_true')

    args = parser.parse_args()

    if args.both:
        args.pages = True
        args.modules = True

    if args.pages:
        args.revisions = True

    return args


def check_content_module(title: str, text: str, failed_path: str,
                         allow_category_nil: bool = False, revision_id: int = None):
    """
    """
     # ignore redirects
    if text.upper().startswith('#REDIRECT'):
        return

    title = title.replace(' ', '_')

    if revision_id is not None:
        title += '?oldid={}'.format(revision_id)

    try:
        item = ExchangeItem.from_module(text, allow_category_nil=allow_category_nil)
        print('Parsed {} successfully'.format(title))
    except Exception as exc:
        print('Failed to parse {}: {!s}'.format(title, exc))

        with open(failed_path, 'a') as fh:
            fh.write('Title: {}, Error: {!s}\n'.format(title, exc))


def check_content_page(title: str, text: str, failed_path: str,
                       revision_id: int = None):
    """
    """
    logger = logging.getLogger('migrateexchange')

    # ignore redirects
    if text.strip().upper().startswith('#REDIRECT'):
        return

    title = title.replace(' ', '_')

    if revision_id is not None:
        title += '?oldid={}'.format(revision_id)

    try:
        item = ExchangeItem.from_page(text)
        print('Parsed {} successfully'.format(title))
    except (ExchangeTemplateMissingError, ExchangeTemplateConvertedError):
        pass
    except Exception as exc:
        logger.error('Failed to parse %s', title)
        logger.exception(exc)

        with open(failed_path, 'a') as fh:
            fh.write('Title: {}, Error: {!s}\n'.format(title, exc))



if __name__ == '__main__':
    main()
