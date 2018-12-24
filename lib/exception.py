# Copyright (C) 2018 Matthew Dowdell <mdowdell244@gmail.com>

"""
"""


class CresbotError(Exception):
    pass


if True:
    class MediaWikiError(CresbotError):
        pass

    if True:
        class ApiError(MediaWikiError):
            """
            """

            def __init__(self, **kwargs):
                """
                """
                self.code = kwargs['code']
                self.info = kwargs['info']

                super().__init__(kwargs['info'])


        class AuthError(MediaWikiError):
            pass

        if True:
            class LoginError(AuthError):
                """
                """

                def __init__(self, **kwargs):
                    """
                    """
                    self.result
                    self.reason

                    msg = 'Login failed with: {}: {}'.format(self.result, self.reason)
                    super().__init__(msg)


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
