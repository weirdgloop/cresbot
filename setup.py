# ----------------------------------------------------------------------
# Copyright (c) 2015 Matthew Dowdell <mdowdell244@gmail.com>.
# This file is part of Cresbot.
#
# Cresbot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cresbot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cresbot.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------

from setuptools import setup

setup(
    name = 'cresbot',
    version = '0.0.1',
    author = 'Matthew Dowdell',
    author_email = 'mdowdell244@gmail.com',
    description = 'description',
    license = 'GPLv3',
    url = 'https://github.com/onei/cresbot',
    packages = ['cresbot', 'cresbot.tasks'],
    install_requires = ['beautifulsoup4', 'ceterach', 'pyyaml', 'requests', 'schedule'],
    classifiers = [
        'Development Status :: 1 - Planning',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4'
    ]
)
