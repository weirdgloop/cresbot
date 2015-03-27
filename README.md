cresbot
=======


This is a MediaWiki bot written in Python, designed for use on the [RuneScape Wiki](http://runescape.wikia.com/wiki/RuneScape_Wiki).

## Installing
(just clone from git repo)

(and install dependencies)

## Command line usage
Cresbot is designed to be run from a command line environment.
```
usage: python cresbot.py [-h] [-t [task [task ...]]] config

positional arguments:
  config                Set config file.

optional arguments:
  -h, --help            show this help message and exit
  -t [task [task ...]]  Run tasks on startup. To run all tasks on startup use
                        `all`. To run specific tasks, add them by name
                        delimited by a space. Allowed task names:
                        `hiscorecounts`.
```

## Config
A sample config file can be found in [config-sample.yaml](https://github.com/onei/cresbot/blob/master/config-sample.yaml). This file should be altered for use and used during command line usage.
```yaml
api              : null
api_config       : {defaults: {maxlag: 5}}
api_url          : http://communitytest.wikia.com/api.php
api_username     : USERNAME
api_password     : PASSWORD
```
* `api` is a placeholder for an instance stored in the config when starting cresbot.
* `api_config` represents a dictionary containing configuration options when creating the instance stored in `api`.
* `api_url` is the URL of the MediaWiki wiki API access point.
* `api_username` is the username of the account to log into the MediaWiki API with.
* `api_password` is the password of the account to log into the MediaWiki API with.

```yaml
log_file         : /var/log/cresbot.log
log_level_file   : DEBUG
log_level_stream : INFO
```
* `log_file` is the location of the log file used by cresbot.
* `log_level_file` is the log level setting used when logging to a file.
* `log_level_stream` is the log level setting used when logging via a stream.

```yaml
tasks            : null
```
* `tasks` is a placeholder for the list of tasks requested to be run from the command line.
 
