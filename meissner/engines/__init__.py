from meissner.logger import *


'''
this should allow us to do more complex analysis of
results in the future
'''
class Result:
    def __init__(self, payload, success):
        self.payload = payload
        self.success = success

        # set these by hand for more info
        self.error = False


class Engine:
    def test(self, payload):
        logging.warning('Using dummy engine ', colored_command(self.__class__.__name__))
        return False

from .seleniumengine import SeleniumEngine, Chrome, Firefox
