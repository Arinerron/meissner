from meissner.logger import *
import meissner

from smartbytes import *

class Meissner:
    def __init__(self, harness, filters = None, engine = None):
        self.harness = harness
        self.filters = filters or list()
        self.engine = engine or meissner.engines.Chrome()

    '''
    test a payload and return whether or not it popped an alert dialog
    '''
    def _test(self, payload):
        output = self._filter(self._harness(payload))
        return self.engine.test(output)


    '''
    pass payload through all configured filters
    '''
    def _filter(self, payload):
        for filter in self.filters:
            payload = smartbytes(filter.filter(payload))

        return payload

    '''
    test xss payload through harness post-filter
    '''
    def _harness(self, payload):
        return smartbytes(self.harness.test(payload))
