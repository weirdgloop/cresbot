#

"""Configuration used for Cresbot tasks."""

import toml


class Config:
    """A representation of the configuration file used by Cresbot."""

    def __init__(self, log_dir: str, username: str, password: str):
        """

        :param str log_dir:
        :param str username:
        :param str password:
        """
        self.log_dir = log_dir
        self.username = username
        self.password = password

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        args = {
            "log_dir": self.log_dir,
            "username": self.username,
            "password": "********",
        }

        ret = "{}({})".format(cls, ", ".join(["{}={!r}".format(k, v) for k, v in args.items()]))
        return ret

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
            )
