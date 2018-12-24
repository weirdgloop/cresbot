#

"""
"""

import pytest

from lib.mediawiki import Api


def test_login(api_instance: Api):
    """Test that logging in using the API is successful."""
    kwargs = {'action': 'query', 'meta': 'userinfo'}

    # check we're logged out to start
    res = api_instance.get_userinfo()
    assert res['id'] == 0

    with api_instance:
        # check we're now logged in
        res = api_instance.get_userinfo()
        assert res['id'] != 0

    # check we have been logged out again
    res = api_instance.get_userinfo()
    assert res['id'] == 0


def test_get_token(api_instance: Api):
    """
    """
    with api_instance:
        # get basic csrf token
        token = api_instance.get_token()
        assert isinstance(token, str)

        # get multiple tokens
        tokens = api_instance.get_token(['csrf', 'watch'])
        assert len(tokens.keys()) == 2
        assert 'csrf' in tokens
        assert 'watch' in tokens


def test_iterator():
    """
    """
    pass
