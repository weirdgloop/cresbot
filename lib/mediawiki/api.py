# Copyright (C) 2018 Matthew Dowdell <mdowdell244@gmail.com>

"""
"""

from json.decoder import JSONDecodeError
import logging
from pprint import pprint
from typing import Union, Iterable

import requests

from ..exception import MediaWikiError, LoginError, EditError, ApiError


LOGGER = logging.getLogger(__name__)


class Api:
    """
    A class to be used to interact with a single MediaWiki instance.
    """

    def __init__(self, username: str, password: str, api_path: str):
        """
        Create a new instance of ``Api``.

        :param str username: The username to log in with. This is not used immediately,
            but during ``login``.
        :param str password: The password for the given username. On recent versions of
            MediaWiki, this should be generated using ``Special:BotPasswords``. See the MediaWiki
            documentation for more details.
        :param str api_path: A string representing the MediaWiki instance to interact with.
            Should contain the protocol, e.g. ``https://`` and the API endpoint, e.g. ``/api.php``.
        """
        self.username = username
        self.password = password
        self.api_path = api_path

        self.session = requests.Session()
        self.assert_param = None

        self.session.headers.update({'User-Agent': 'Cresbot v1.0.0'})

    def __enter__(self):
        """
        Log into the given MediaWiki instance.

        Example::

            api = Api(username='Example', password='secret', api_path='https://example.wiki/api.php')

            with api:
                # logged in

            # logged out
        """
        self.login()

    def __exit__(self, err_type, err_val, err_tb):
        """
        """
        self.logout()

    def __merge_iterable(self, values: Union[str, Iterable]) -> str:
        """
        """
        # already merged, nothing to do
        if isinstance(values, str):
            return values

        for val in values:
            if not isinstance(val, str):
                msg = 'Unexpected type: expected str, found: {} ({})'
                msg = msg.format(type(val), val)

                raise ValueError(msg)

        return '|'.join(values)

    def __call(self, **kwargs) -> dict:
        """
        """
        is_get = kwargs['action'] in ('query',)
        kwargs['format'] = 'json'

        if self.assert_param is not None:
            kwargs['assert'] = self.assert_param

        req = getattr(self.session, 'get' if is_get else 'post')
        res = req(self.api_path, **{'params' if is_get else 'data': kwargs})

        # only log get requests to avoid logging sensitive data
        if is_get:
            LOGGER.debug('Requested: %s', res.url)

        try:
            ret = res.json()
        except JSONDecodeError as exc:
            LOGGER.exception(exc)
            raise MediaWikiError('Unable to decode response: {!r}'.format(res.text)) from exc

        # check for errors
        if 'error' in ret:
            raise APIError(**ret['error'])

        return ret

    def call(self, **kwargs):
        """
        """
        return self.__call(**kwargs)

    def get_token(self, token: Union[str, Iterable]='csrf'):
        """
        Get a token from the API.

        If the API endpoint is for FANDOM, i.e. it contains ``wikia.com`` or ``fandom.com`` the
        option for requesting multiple tokens is disabled.

        :param token: A string or iterable of strings (e.g. set, list, tuple) containing the tokens
            required. Valid token types are: 'createaccount', 'csrf', 'login', 'patrol',
            'rollback', 'userrights' and 'watch'. The default is 'csrf'. If multiple tokens are
            wanted, either provide a string with a '|' character separating the different types or
            provide an iterable of the different token types. Multiple tokens are not supported
            for FANDOM wikis.

        :return: If a single token was requested, the token value will be returned. If multiple
            tokens were requested a dictionary containing them will be returned, e.g.::

                {
                    "watchtoken": "<token value>",
                    "patroltoken": "<token value>",
                }

        :raises ValueError:
        """
        token = self.__merge_iterable(token)

        res = self.__call(action='query', meta='tokens', type=token)
        tokens = res['query']['tokens']

        if len(tokens.keys()) == 1:
            return list(tokens.values())[0]

        return tokens

    def login(self, is_bot: bool=False):
        """
        Logs into the API using the credentials supplied in the class constructor. This uses the
        old action=login endpoint which requires a password to be set up using Special:BotPasswords
        in newer version of MediaWiki.

        :param bool is_bot: Indicates whether the credentials are for a bot or not. If ``True``,
            subsequent requests will pass ``assert='bot'`` with all API requests. If ``False``,
            subsequent requests will pass ``assert='user'`` with all API requests. This will be
            continued until ``logout`` is called. Assertions are not available when interacting
            with a FANDOM wiki.
        """
        LOGGER.debug('Logging into %r as %r', self.api_path, self.username)
        params = {
            'action': 'login',
            'lgname': self.username,
            'lgpassword': self.password,
            'lgtoken': self.get_token('login')
        }

        res = self.__call(**params)

        if res['login']['result'] != 'Success':
            msg = ('Attempted login failed with: {result}: {reason}'
                   .format(**res['login']))
            raise LoginError(msg)

        # check what to use for the assert param
        user_groups = self.get_userinfo('groups')['groups']
        self.assert_param = 'bot' if 'bot' in user_groups else 'user'

    def logout(self):
        """
        Logs out of the API.
        """
        LOGGER.debug('Logging out of %r as %r', self.api_path, self.username)
        self.__call(action='logout')
        self.assert_param = None

    def get_userinfo(self, uiprop: Union[str, Iterable]=None):
        """
        """
        uiprop = self.__merge_iterable(uiprop)
        res = self.__call(action='query', meta='userinfo', uiprop=uiprop)

        return self.__find_result(res['query'])

    def __find_result(self, result: dict, path: str = None):
        """
        """
        while isinstance(result, dict) and len(result.keys()) == 1:
            result = result[list(result.keys())[0]]

        if isinstance(result, dict) and isinstance(path, str):
            for key in path.split('/'):
                # TODO: this should throw an error if it's not there
                if key in result:
                    result = result[key]

        return result

    def iterator(self, path: str = None, **kwargs):
        """
        Generator for ``action=query`` requests.

        This accepts keyword arguments representing the additional parameters passed to
        ``action=query``. However, if ``query-continue`` exists in the response, it will
        automatically make the next call and continue yielding the results. These results are
        found by navigating through the return JSON until it find multiple keys in a sub-dictionary
        of the ``query`` key, which usually indicates the results that are desired.

        Example::

            api = Api(username='Example', password='secret', api_path='https://example.wiki/api.php')

            # find all pages in the mainspace
            for page in api.iterator(list='allpages', apnamespace=0, aplimit=max'):
                print(page['title'])


        :param str path:
        :param **kwargs: Key-value arguments representing the parameters to be passed to the API
            call. ``action=query`` is set automatically and cannot be overridden. For documentation
            on what other arguments can be provided see the API documentation for you MediaWiki
            installation.
        """
        kwargs['action'] = 'query'
        res = self.__call(**kwargs)

        try:
            query = self.__find_result(res['query'], path)
        except KeyError:
            LOGGER.error(res)
            raise

        if isinstance(query, list):
            for item in query:
                yield item
        else:
            yield query

        if 'query-continue' in res:
            from_param = res['query-continue'][list(res['query-continue'].keys())[0]]
            kwargs.update(from_param)
            kwargs['path'] = path

            yield from self.iterator(**kwargs)

        elif 'continue' in res:
            from_param = res['continue']
            kwargs.update(from_param)
            kwargs['path'] = path

            yield from self.iterator(**kwargs)

    def get_page_content(self, pagename: str) -> str:
        """
        """
        LOGGER.debug('Requesting page content of %r', pagename)
        res = self.__call(action='query',
                          prop='revisions',
                          titles=pagename,
                          rvprop='content')

        # get rid of the keys we don't care about
        res.pop('batchcomplete', None)
        res = self.__find_result(res, 'revisions')

        if isinstance(res, list):
            res = res[0]

        return res['*']

    def get_revision(self, revision_id: int) -> dict:
        """
        """
        LOGGER.debug('Requesting revision: %s', revision_id)
        res = self.__call(action='query',
                          prop='revisions',
                          rvprop='content',
                          revids=revision_id)
        return self.__find_result(res)

    def edit_page(self, pagename: str, text: str, summary: str = ''):
        """
        """
        token = self.get_token()

        res = self.__call(action='edit',
                          title=pagename,
                          summary=summary,
                          text=text,
                          token=token)

        try:
            if res['edit']['result'] != 'Success':
                # TODO: improve this
                raise EditError('Edit failed: %s', res)
        except KeyError:
            raise MediaWikiError('Unexpected response for edit: %s', res)
