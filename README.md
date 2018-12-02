# cresbot

This is a MediaWiki bot written in Python, designed for use on the [RuneScape Wiki](https://rs.weirdgloop.org).

## Installing
To install, simply clone this repository via git:
```
git clone git@gitlab.com/weirdgloop/cresbot.git
```

Set the following environment variables:
```bash
export LANG="en_GB.UTF-8"
export LC_ALL="en_GB.UTF-8"
```
It may be prudent to set these in your `~/.bashrc` if they aren't already defined.

Create and activate a virtual environment:
```
python3 -m venv ./venv
source ./venv/bin/activate
```

Then install the required dependencies:
```
pip install -r requirements.txt
```

Note that this is only tested with the latest version of each dependency. Older versions may work, but are not supported.

## Command line usage
Cresbot provides a set of scripts to be used for regular tasks on the wiki.

### Hiscorecounts
Hiscorecounts updates [Module:Hiscore counts](https://runescape.wiki/w/Module:Hiscore_counts) on the wiki.

```
usage: hiscorecounts.py [-h] -c CONFIG [-v | -q]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
  -v, --verbose
  -q, --quiet
```

## Config
A sample config file can be found in `config.sample.toml`. This file should be altered for use and used during command line usage. This should be saved within the cresbot directory as `config.toml`.

```toml
# the logs directory to use
log_dir = '/path/to/cresbot/logs'
# the URI for the wiki's api.php endpoint
api_path = 'https://rs.weirdgloop.org/api.php'
# the username as provided by Special:BotPasswords
username = 'username@name'
# the password as provided by Special:BotPasswords
password = 'password_token'
```

Crontab setup should be along the following lines (use `crontab -e` to edit):
```
# need to use bash as the shell so source works
SHELL=/bin/bash

# run hiscore counts updater ever day at midnight
0 0 * * * cd /path/to/cresbot && source ./venv/bin/activate && ./hiscorecounts.py -c ./config.toml -v

# manage logs
0 12 * * * cd /path/to/cresbot && ./manage-logs.sh
```
