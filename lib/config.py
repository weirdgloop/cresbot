#

"""
"""

import toml


class Config:
    def __init__(self, username: str, password: str, api_path: str):
        """
        """
        self.username = username
        self.password = password
        self.api_path = api_path

    @classmethod
    def from_toml(cls, file_path: str):
        """
        """
        with open(file_path) as fh:
            content = fh.read()
            parsed_toml = toml.loads(content)

            return cls(parsed_toml['username'],
                       parsed_toml['password'],
                       parsed_toml['api_path'])
