cresbot
=======

This is a MediaWiki bot written in Python, designed for use on the [RuneScape Wiki](http://runescape.wikia.com/wiki/RuneScape_Wiki).

== Dependencies ==
The following dependencies are required available from [PyPi]():
* [Requests](https://pypi.python.org/pypi/requests)
* [BeautifulSoup4](https://pypi.python.org/pypi/beautifulsoup4/4.3.2)

The following dependencies are required, which currently need to be downloaded with git:
* [Ceterach](https://github.com/Riamse/ceterach)

== Usage ==
Cresbot is designed to be started through the command line:
```$ python -m cresbot [-v] [-t:task1,task2,...,taskn] [-l[:path/to/log/file]] [-p:password]```

The options are as follows:
* `-v` denotes test mode, which sets the log level for stream to DEBUG, see [logging log levels](), and prevents logging to file. This is primarily designed for testing in a Windows environment prior to full release.
* `-t` is for specifying one or more tasks to run, each separated by a comma. This allows failed tasks to run again once the error that caused them to fail has been fixed.
* `-l` is for disabling file logging for testing on a Windows environment. However, a log file path may also be set through this option.
* `-p` sets the password used to log into the MediaWiki API. If this is not set here, it will be prompted for once the config and logs have been set up.
