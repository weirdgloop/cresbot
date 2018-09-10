cresbot
=======

This is a MediaWiki bot written in Python, designed for use on the RuneScape Wiki.

## Installing
To install, simply clone this repository via git:
```
git clone git://github.com/onei/cresbot.git
```

Set the following environment variables:
```bash
export LANG="en_GB.UTF-8"
export LC_ALL="en_GB.UTF-8"
```

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
Hiscorecounts update `Module:Hiscore counts` on the wiki.

```
usage: hiscorecounts.py [-h] -c CONFIG [-v | -q]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
  -v, --verbose
  -q, --quiet
```

## Config
A sample config file can be found in `config.sample.toml`. This file should be altered for use and used during command line usage. This is normally saved within the cresbot directory.

```toml
# the URI for the wii's api.php endpoint
api_path = 'https://rs.weirdgloop.org/api.php'
# the username as provided by Special:BotPasswords
username = 'username@name'
# the password as provided by Special:BotPasswords
password = 'password_token'
```
