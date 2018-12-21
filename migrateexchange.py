#! /usr/bin/env python3

"""
Revisions that could not be parsed are reported in failed.txt and to STDOUT.

These failed revisions can be converted to another format using:

    grep -o "oldid=[[:digit:]]*" failed.txt | cut -d'=' -f2 > revisions.txt

This file can then be passed in as the --file argument to retry parsing after fixes have been
completed.
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
EXCLUDE_PAGES = ['Module:Exchange/test']

NS_EXCHANGE = 112
NS_MODULE = 828


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
    failed_path = os.path.join(cur_path, args.failed)
    total_revisions = 0

    if args.csv:
        dirname = os.path.join(cur_path, args.csv)
        os.makedirs(dirname, exist_ok=True)

    if not args.start:
        try:
            # empty file at the start of the run
            os.remove(failed_path)
        except FileNotFoundError:
            pass

    with api:
        if args.modules:
            ap_params = {'list': 'allpages',
                         'apnamespace': NS_MODULE,
                         'apprefix': 'Exchange/',
                         'aplimit': 'max'}
            rv_params = {'prop': 'revisions',
                         'rvprop': 'ids|content|timestamp|user|userid|comment',
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
                    logger.debug(text)
                    check_content_module(title, text, failed_path)
                    return
                else:
                    rv_params['titles'] = title
                    prev = None

                    if args.csv:
                        filename = title.replace('Module:Exchange/', '') \
                                        .replace(' ', '_')
                        csv_filename = os.path.join(cur_path, args.csv, filename + '.csv')

                        with open(csv_filename, 'w') as fh:
                            fh.write(','.join(ExchangeItem._ATTRS +
                                              ('user', 'userid', 'summary', 'timestamp', 'revid')) + '\n')
                    else:
                        csv_filename = None

                    for revision in api.iterator(**rv_params):
                        total_revisions += 1
                        try:
                            text = revision['*']
                            revision_id = revision['revid']
                        except KeyError:
                            logger.error(revision)
                            raise

                        item = check_content_module(title, text, failed_path, True, revision_id)
                        extras = [revision[k] for k in ('user', 'userid', 'comment', 'timestamp', 'revid')]
                        # convert API timestamps to SQL format
                        extras[3] = extras[3].replace('Z', '').replace('T', ' ')

                        for i, e in enumerate(extras):
                            if isinstance(e, str):
                                extras[i] = repr(e)
                            else:
                                extras[i] = str(e)

                        extras = ',' + ','.join(extras)

                        if csv_filename is not None:
                            with open(csv_filename, 'a') as fh:
                                fh.write(item.to_csv() + extras + '\n')

        if args.pages:
            ap_params = {'list': 'allpages',
                         'apnamespace': NS_EXCHANGE,
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
                        logger.error(revision)
                        raise

                    check_content_page(title, text, failed_path, revision_id)

        if args.file:
            with open(args.file) as fh, api:
                for line in fh.readlines():
                    revision_id = int(line.strip())
                    revision = api.get_revision(revision_id)

                    namespace = revision['ns']
                    title = revision['title']
                    content = revision['revisions'][0]['*']

                    if namespace == NS_MODULE:
                        check_content_module(title, content, failed_path, True, revision_id)
                    elif namespace == NS_EXCHANGE:
                        check_content_page(title, content, failed_path, revision_id)



def parse_args() -> argparse.Namespace:
    """
    Handle command line arguments.

    :return: The found arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', required=True)
    parser.add_argument('--failed', required=False, default='failed.txt')
    parser.add_argument('--start', required=False)
    parser.add_argument('--revisions', action='store_true', default=False)
    parser.add_argument('--file', required=False)
    parser.add_argument('--csv', required=False)

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
    logger = logging.getLogger('migrateexchange')

    # ignore redirects
    if text.upper().startswith('#REDIRECT'):
        return

    title = title.replace(' ', '_')

    if revision_id is not None:
        title += '?oldid={}'.format(revision_id)

    try:
        item = ExchangeItem.from_module(text, allow_category_nil=True)
    except Exception as exc:
        logger.exception(exc)
        logger.error('Failed to parse %s: %s', title, str(exc))
        return None
    else:
        logger.debug('Parsed %s successfully', title)
        return item



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
    except (ExchangeTemplateMissingError, ExchangeTemplateConvertedError):
        logger.info('No data to parse for %s', title)
        return None
    except Exception as exc:
        logger.exception(exc)
        logger.error('Failed to parse %s', title)
        return None
    else:
        logger.info('Parsed %s successfully', title)
        return item


if __name__ == '__main__':
    main()
