# Copyright (C) 2018 Matthew Dowdell <mdowdell244@gmail.com>

"""
"""

from json.decoder import JSONDecodeError
import logging

import requests

from ..exception import MediaWikiError


LOGGER = logging.getLogger(__name__)


class Api:
	"""
	"""

	def __init__(self, username: str, password: str, api_path: str):
		"""
		"""
		self.username = username
		self.password = password
		self.api_path = api_path

		self.session = requests.Session()
		self.assert_param = None

	def __enter__(self):
		"""
		"""
		self.login()

	def __exit__(self, err_type, err_val, err_tb):
		"""
		"""
		self.logout()

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
			res.encoding = 'utf-8-sig'
			ret = res.json()
		except JSONDecodeError as exc:
			LOGGER.exception(exc)
			raise MediaWikiError('Unable to decode response: {!s}'.format(res.text)) from exc

		# TODO: check for errors here

		return ret

	def get_token(self, token = 'csrf'):
		"""
		Get a token from the API.

		:param token_type: A string or list, tuple or set of strings containing the tokens
			required. Valid token types are: 'createaccount', 'csrf', 'login', 'patrol',
			'rollback', 'userrights' and 'watch'. The default is 'csrf'. If multiple tokens are
			wanted, either provide a string with a '|' character separating the different types or
			provide a list of the different token types.

		:return: If a single token was requested, the token value will be returned. If multiple
			tokens were requested a dictionary containing them will be returned, e.g.::

				{
					"watchtoken": "<token value>",
            		"patroltoken": "<token value>",
				}
		"""
		if isinstance(token, (list, tuple, set)):
			token = '|'.join(token)

		res = self.__call(action='query', meta='tokens', type=token)
		tokens = res['query']['tokens']

		if len(tokens.keys()) == 1:
			return list(tokens.values())[0]

		return tokens

	def login(self, is_bot: bool = False):
		"""
		Logs into the API using the credentials supplied in the class constructor. This uses the
		old action=login endpoint which requires a password to be set up using Special:BotPasswords
		in newer version of MediaWiki.

		:param bool is_bot: Indicates whether the credentials are for a bot or not. If ``True``,
			subsequent requests will pass ``assert='bot'`` with all API requests. If ``False``,
			subsequent requests will pass ``assert='user'`` with all API requests. This will be
			continued until ``logout`` is called.
		"""
		LOGGER.debug('Logging into %r as %r', self.api_path, self.username)

		token = self.get_token('login')
		res = self.__call(action='login',
			              lgname=self.username,
			              lgpassword=self.password,
			              lgtoken=token)

		if res['login']['result'] != 'Success':
			raise LoginError('Attempted login failed with: {result}: {reason}'
				             .format(**res['login']))

		self.assert_param = 'bot' if is_bot else 'user'

	def logout(self):
		"""
		Logs out of the API.
		"""
		LOGGER.debug('Logging out of %r as %r', self.api_path, self.username)
		self.__call(action='logout')
		self.assert_param = None

	def get_page_content(self, pagename: str) -> str:
		"""
		"""
		LOGGER.debug('Requesting page content of %r', pagename)
		res = self.__call(action='query',
			              prop='revisions',
			              titles=pagename,
			              rvprop='content')

		try:
			pages = res['query']['pages']
			content = pages[list(pages.keys())[0]]['revisions'][0]['*']
		# TODO: make this better
		except KeyError as exc:
			raise MediaWikiError(res) from exc
		else:
			return content

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
				raise EditError('Edit failed: %s', res)
		except KeyError:
			raise MediaWikiError('Unexpected response for edit: %s', res)