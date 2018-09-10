# Copyright (C) 2018 Matthew Dowdell <mdowdell244@gmail.com>

"""
"""


class CresbotError(Exception):
	pass


if True:
	class MediaWikiError(CresbotError):
		pass

	if True:
		class AuthError(MediaWikiError):
			pass

		if True:
			class LoginError(AuthError):
				pass

			class LogoutError(AuthError):
				pass

	class HiscoresError(CresbotError):
		pass
