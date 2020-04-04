from meissner.logger import *

class Engine:
    def test(self, payload):
        logger.warning('Using dummy engine ', colored_command(self.__class__.__name__))
        return False

from .chrome import Chrome
