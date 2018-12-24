#

"""
"""

import pytest

from lib.config import Config
from lib.mediawiki import Api

@pytest.fixture(scope='session')
def config(request) -> Config:
    """
    """
    file_path = request.config.getoption('--config')
    return Config.from_toml(file_path)


@pytest.fixture
def api_instance(config: Config) -> Api:
    """
    """
    return Api(config.username, config.password, config.api_path)
