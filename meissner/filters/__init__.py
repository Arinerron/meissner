from meissner.logger import *

class Filter:
    def test(self, payload):
        logging.warning('Using dummy filter ', colored_command(self.__class__.__name__))
        return payload

from .urlencode import URLEncoder
