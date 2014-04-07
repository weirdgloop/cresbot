# 
# -----
# This file is part of Cresbot
# Cresbot is Copyright © Matthew Dowdell 2014 <mdowdell244@gmail.com>
# -----
#
# -----

# standard modules
import requests

# cresbot modules
# from .page import Page
# from .file import File

# cresbot default config
_version = '0.1'
_user_agent = 'Cresbot {version}, Python {version}'
_default_config = {
    'throttle': 0,
    'max_retries': 0,
    'maxlag': 5
}

Class Api:

    # storage for tokens
    _tokens = {}
    
    # queries that use get requests
    _get_queries = ('query', 'purge')

    def __init__(self, api_url:str, config:dict):

        # check api_url ends with /api.php
        u = urlparse(api_url)
        if u.path.endswith('api.php'):
            raise ValueError('Invalid API')

        # create session
        self._session = requests.Session()
        self._sessions.headers.update({'User-Agent': _user_agent})

        # attempt to make test api query
        params = {'format': 'json'}
        test = getattr(self._session, 'get')
        res = test(api_url, params=params)
        
        # check api response
        try:
            res.json()
        except ValueError:
            raise ValueError('Invalid API')
        else:
            # api_url is valid
            self._api = api.url

        # merge config with default config
        # set _last_call time as the last time of the request
    
    def call(self, **params) -> dict:
        print('call')
        
        # force format=json
        params['format'] = 'json'

        # add maxlag param
        params['maxlag'] = str(self._config['maxlag'])

        # check when the last call was made
            # if less than the throttle in config
            # sleep for the difference

        # check if query uses get or post requests
        is_get = params['action'] in self._get_queries

        # call api
        # set _last_call time
        
        # extract json of response
            # throw error if unable to coerce to json
        # check for any errors in api response
            # throw any errors received
        # return json response
        
    
    def iterator(self, **params):
        print('iterator')
        # call api through self.call
        # traverse down returned dict
        # if there's only one key in the result
        # keep going until there's more than one or we hit a list
        
        # check how many times the user wants to make the request
        # check if there's any more results to get
        # keep going until we hit the max requested calls
        # or we run out of results
        # merge responses
        
        # return result (list?)
    
    def login(self, username:str, password:str) -> bool:
        print('login')
        # attempt to login
        # will require a token
        # send request again with token
        # check is successful
        # return bool
    
    def logout(self) -> bool:
        print('logout')
        self.call
        # attempt to logout
        # returns [] if successful
    
    def get_tokens(self):
        print('get_tokens')
        # call api for edit and watch tokens
        # watch tokens are unique
        # everything else uses an edit token
        # even if it calls the token something else
        
        # assign result to self_tokens dict