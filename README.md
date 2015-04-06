cresbot
=======


This is a MediaWiki bot written in Python, designed for use on the [RuneScape Wiki](http://runescape.wikia.com/wiki/RuneScape_Wiki).

## Installing
To install, simply clone this repository via git:
```
git clone git://github.com/onei/cresbot.git
```

Then install the required dependencies:
```
pip install -r requirements.txt
```
Note that this is only tested with the latest version of each dependency. Older versions may work, but are not supported.

## Command line usage
Cresbot is designed to be run from as a background task in a command line environment.
```
usage: ./cresbot.py [-h] [-t [task [task ...]]] config

positional arguments:
  config                Set path to config file.

optional arguments:
  -h, --help            show this help message and exit
  -t [task [task ...]]  Run tasks on startup. To run all tasks on startup use
                        `all`. To run specific tasks, add them by name
                        delimited by a space. Allowed task names:
                        `hiscorecounts`.
```
* You may have to mark `cresbot.py` as executable, which can be done by running `chmod +x cresbot.py`.
* For Windows users, the usage is `python cresbot.py [-h] [-t [task [task ...]]] config`.

## Config
A sample config file can be found in [config-sample.yaml](https://github.com/onei/cresbot/blob/master/config-sample.yaml). This file should be altered for use and used during command line usage. This is normally saved within the cresbot directory.
```yaml
api                   : null
api_config            : {defaults: {maxlag: 5}}
api_url               : http://communitytest.wikia.com/api.php
api_username          : USERNAME
api_password          : PASSWORD

log_file              : /home/username/cresbot/logs/cresbot.log
log_file_level        : DEBUG
log_email             : false
log_email_level       : ERROR
log_email_mailhost    :
    - smtp.gmail.com
    - 587
log_email_from        : foo@gmail.com
log_email_to          :
    - bar@gmail.com
    - baz@gmail.com
log_email_subject     : Cresbot Error
log_email_credentials :
    - USERNAME
    - PASSWORD
log_email_secure      : []

# task config
tasks                 : null

```
* `api` is a placeholder for an instance stored in the config when starting cresbot.
* `api_config` represents a dictionary containing configuration options when creating the instance stored in `api`.
* `api_url` is the URL of the MediaWiki wiki API access point.
* `api_username` is the username of the account to log into the MediaWiki API with.
* `api_password` is the password of the account to log into the MediaWiki API with.
* `log_file` is the location of the log file used by cresbot. Remember to crate the directory before running the script to avoid errors. This is normally the logs subdirectory within the cresbot directory.
* `log_file_level` is the log level setting used when logging to a file.
* `log_email` is a boolean to enable email logging, normally used exclusively for exceptions. This should be set to either `true` or `false`.
* `log_email_level` is the log level setting used when logging via emails. It is strongly recommended to leave this as `ERROR`.
* `log_email_mailhost` is the mailhost to send the email from. This should either simply be the name of the host, e.g. `smtp.gmail.com`, or a list containing the host and the port (see example above).
* `log_email_from` is the email address to send the email from.
* `log_email_to` is a list of email addresses to send emails to.
* `log_email_subject` is the subject of the email to send.
* `log_email_credentials` is a list of credentials to log in with. If used, this should be the username followed by the password. Otherwise, set to `null`.
* `log_email_secure` is a list that's passed to `smtplib.SMTP.starttls`. If used, it should either be an empty list, a list containing the the name of a keyfile or a list containing the names of the keyfile and certificate.
* `tasks` is a placeholder for the list of tasks requested to be run from the command line.

### Notes
* Email logging options are largely a direct copy from the arguments used in [logging.handlers.SMTPHandler](https://docs.python.org/3.4/library/logging.handlers.html#logging.handlers.SMTPHandler) prefixed with `log_email_`. See there for more details.
* `log_email_mailhost` and `log_email_credentials` are converted from lists to tuples to workaround [issue #22646](https://bugs.python.org/issue22646) which may not be found in some distributions of Python 3.4.
* For email logging via Gmail, you will need to turn access for less secure apps on via [Less Secure Apps - Account Settings](https://www.google.com/settings/security/lesssecureapps).
