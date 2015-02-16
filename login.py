# ----------------------------------------------------------------------
# Copyright (c) 2015 Matthew Dowdell <mdowdell244@gmail.com>.
#
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

# This file is automatically untracked
#
# Remember to remove all passwords when pushing changes to this file
#
# To update the repo with changes, run:
# $ git update-index --no-assume-unchanged login.py
#
# To force this file to be untracked after pushing changes, run:
# $ git update-index --assume-unchanged login.py

_users = {
    'USERNAME': 'PASSWORD'
}

def login(username:str) -> str:
    """Get the associated password for a given username.

    Args:
        username: Username to get the associated password for.

    Returns:
        The associated password for `username`.

    Raises:
        ValueError: Incorrect or unknown username

    """
    try:
        password = _users[username]
    except KeyError:
        raise ValueError('Incorrect or unknown username')

    return password
