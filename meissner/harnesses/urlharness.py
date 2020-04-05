from . import Harness, placeholder
from meissner.logger import *

import requests, urllib.parse

_default_method = 'GET'

class URLHarness(Harness):
    def __init__(self, url, method = _default_method):

        self.url = url

        # TODO: support POST requests
        self.method = {
            'GET' : requests.get
        }.get(method.strip().upper())

        logging.debug('... using ', colored_command(method.strip().upper()), ' request to URL: ', colored_command(url))

        if not self.method:
            logging.warning('Request method ', colored_command(method), ' is unknown. Defaulting to ', colored_command(_default_method), '...')
            self.method = _default_method


    def test(self, payload):
        url = self.url.format(**{
            placeholder : urllib.parse.quote_from_bytes(bytes(payload), safe = '')
        })

        response = self.method(url)
        return response.content
