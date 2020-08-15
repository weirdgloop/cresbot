# Copyright (C) 2018-2020 Matthew Dowdell <mdowdell244@gmail.com>

"""Exceptions for Cresbot."""


__all__ = [
    "CresbotError",
    "MediaWikiError",
    "AuthError",
    "LoginError",
    "LogoutError",
    "EditError",
    "HiscoresError",
]


class CresbotError(Exception):
    """Base exception for Cresbot."""


class MediaWikiError(CresbotError):
    """Base exception for MediaWiki errors."""


class AuthError(MediaWikiError):
    """Authorisation errors in MediaWiki."""


class LoginError(AuthError):
    """Login authorisation errors in MediaWiki."""


class LogoutError(AuthError):
    """Logout authorisation errors in MediaWiki."""


class EditError(MediaWikiError):
    """Edit errors in MediaWiki."""


class HiscoresError(CresbotError):
    """Hiscores errors in RuneScape."""
