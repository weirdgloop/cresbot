# Copyright (C) 2018 Matthew Dowdell <mdowdell244@gmail.com>

"""
"""


class CresbotError(Exception):
    pass


if True:
    class MediaWikiError(CresbotError):
        pass

    if True:
        class APIError(MediaWikiError):
            def __init__(self, **kwargs):
                """
                """
                super().__init__(kwargs['info'])

                self.code = kwargs['code']
                self.info = kwargs['info']

        class AuthError(MediaWikiError):
            pass

        if True:
            class LoginError(AuthError):
                pass

            class LogoutError(AuthError):
                pass

        class EditError(MediaWikiError):
            pass

    class HiscoresError(CresbotError):
        pass

    class RSWikiError(CresbotError):
        pass

    if True:
        class ExchangeError(RSWikiError):
            """
            For errors thrown by exchange libraries.
            """
            pass

        if True:
            class ExchangeTemplateMissingError(ExchangeError):
                """
                """
                pass

            class ExchangeTemplateConvertedError(ExchangeError):
                """
                """
                pass
