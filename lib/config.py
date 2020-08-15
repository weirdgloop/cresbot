#

"""
"""

import toml


class Config:
    """A representation of the configuration file used by Cresbot."""

    def __init__(self, log_dir: str, username: str, password: str, api_path: str):
        """

        :param str log_dir:
        :param str username:
        :param str password:
        :param str api_path:
        """
        self.log_dir = log_dir
        self.username = username
        self.password = password
        self.api_path = api_path

    @classmethod
    def from_toml(cls, file_path: str):
        """Parse a config file into a ``Config`` instance.

        :param str file_path:
        """
        with open(file_path) as fh:
            content = fh.read()
            parsed_toml = toml.loads(content)

            return cls(
                parsed_toml["log_dir"],
                parsed_toml["username"],
                parsed_toml["password"],
                parsed_toml["api_path"],
            )
