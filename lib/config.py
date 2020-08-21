#

"""Configuration used for Cresbot tasks."""

from typing import List

import toml


__all__ = ["WikiConfig", "WikisConfig", "Config"]


class WikiConfig:
    """A representation of a wiki configuration used by Cresbot."""

    def __init__(self, api_path: str, username: str, password: str):
        """

        :param str api_path:
        :param str username:
        :param str password:
        """
        self.api_path = api_path
        self.username = username
        self.password = password

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        args = {
            "api_path": self.api_path,
            "username": self.username,
            "password": "********",
        }

        ret = "{}({})".format(cls, ", ".join(["{}={!r}".format(k, v) for k, v in args.items()]))
        return ret


class WikisConfig:
    """
    """

    def __init__(self, en: WikiConfig, pt_br: WikiConfig):
        """
        """
        if not isinstance(en, WikiConfig):
            en = WikiConfig(**en)

        if not isinstance(pt_br, WikiConfig):
            pt_br = WikiConfig(**pt_br)

        self.en = en
        self.pt_br = pt_br

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        args = {
            "en": self.en,
            "pt_br": self.pt_br,
        }

        ret = "{}({})".format(cls, ", ".join(["{}={!r}".format(k, v) for k, v in args.items()]))
        return ret


class Config:
    """A representation of the configuration file used by Cresbot."""

    def __init__(self, log_dir: str, proxies: List[str], wiki: WikisConfig):
        """

        :param str log_dir:
        :param List[str] proxies:
        :param WikisConfig wiki:
        """
        if not isinstance(wiki, WikisConfig):
            wiki = WikisConfig(**wiki)

        self.log_dir = log_dir
        self.proxies = proxies
        self.wiki = wiki

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        args = {
            "log_dir": self.log_dir,
            "proxies": self.proxies,
            "wiki": self.wiki,
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

            return cls(**parsed_toml)
