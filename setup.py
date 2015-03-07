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

# dry run: $ python setup.py install -n [-v]

from setuptools import setup, find_packages

# to install ceterach run:
#   $ pip install git+git://github.com/Riamse/ceterach.git@master#egg=ceterach
# doesn't seem to want to run normally

setup(name = 'cresbot',
	  version = 0.1,
	  packages = find_packages(),
	  package_data = {'cresbot': ['config-sample.yaml']},
	  dependency_links = ['git+git://github.com/Riamse/ceterach.git@master#egg=ceterach'],
	  install_requires = ['beautifulsoup4', 'ceterach', 'requests', 'schedule', 'pyyaml']
)
