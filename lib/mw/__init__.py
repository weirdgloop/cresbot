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

import requests

class Api:

    _get_params = ('help', 'purge', 'query')

    def __init__(self, server:str, scriptpath:str=''):
        """Creates an Api instance.

        Args:
            server: Host to connect to. Must include scheme and domain, and
                may optionally include port. Corresponds to the wiki's set
                value of `$wgServer`.
            scriptpath: The scriptpath of the wiki, corresponding to the
                wiki's set value of `$wgScriptPath`.
        """
        # store this separately for future flexibility
        # @example wikia.php requests
        self._server = server
        self._api = server + scriptpath + '/api.php'
        self._session = requests.Session()
        # @todo do something with this?
        # self.tokens = {}

    def call(self, params:dict={}, **more_params) -> dict:
        """Makes an API request.

        Args:
            params: Parameters to send to the API.
            more_params: Parameters to send to the API.
        """
        # merge in more_params
        for k, v in more_params:
            params[k] = v

        # test for GET request
        is_get = params['action'] in self._get_params
        # force json
        params['format'] = 'json'

        req = getattr(self._session, 'get' if is_get else 'post')
        # @todo errors, retries, etc.
        res = req(self._api, **{'params' if is_get else 'data': params})
        return res.json()

        self._request(method, params)

    def login(self, username:str, password:str) -> bool:
        """Logs a user in using `username` and `password`.

        Args:
            username: The username of the user to be logged in.
            password: The associated password of the user to be logged in.

        Returns:
            Boolean indicating the success of the login request.
        """
        params = {
            'action': 'login',
            'lgname': username,
            'lgpassword': password
        }
        
        login = self.call(**params)

        # extract token and send back
        params['lgtoken'] = login['login']['token']
        confirm = self.call(**params)

        if confirm['login']['result'] == 'Success':
            return True

        return False

    def logout(self):
        """Logs the user out.

        Returns:
            Boolean indicating the success of the logour request.
        """
        return self.call(action='logout') == []
