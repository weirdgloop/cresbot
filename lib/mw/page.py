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

class Page:
    def __init__(self, identity=None):
        print(identity)

    def content(self, new_text=None):
        """Get or set the text of a page"""
        # @todo handle edit conflicts?
        if new_text is None:
            return 'get current content'

        # won't work, but illustrates the concept for now
        if new_text == 'string':
            return 'set text'

        if new_text == 'method':
            cur_text = self.content()
            text = new_text(cur_text)
            return self.content(text)
