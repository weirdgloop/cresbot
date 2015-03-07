cresbot
=======

This is a MediaWiki bot written in Python, designed for use on the [RuneScape Wiki](http://runescape.wikia.com/wiki/RuneScape_Wiki).

## Todo list

* Add ability to install with pip from git
** `pip install git+git://github.com/Riamse/ceterach.git`
* Document command line usage
** Copy/paste from argparse output?
* Implement email logging for exceptions
* Document config file

## Command line usage
Cresbot is designed to be run from a command line environment.
```
$ python -m cresbot -p password [-l /path/to/log/file] [-t [taskname [taskname ...]]]
```

The arguments are as follows:
```
-p password                  Set the password to log into the MediaWiki API with.
-l /path/to/log/file         (optional) Set the path to the log file.
-t [taskname [taskname ...]] (optional) Run specific tasks on startup.
```

Usage and argument help can also be accessed from the command line using `$ python -m cresbot -h`.
