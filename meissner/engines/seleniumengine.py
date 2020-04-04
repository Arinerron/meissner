from meissner.logger import *
from . import Engine, Result

from selenium import webdriver


class SeleniumEngine(Engine):
    def __init__(self):
        self.browser = self._get_browser()

    def _get_browser(self):
        return None

    def test(self, payload):
        success = False
        result = Result(payload, success)
        return result


class Chrome(SeleniumEngine):
    def _get_browser(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        return webdriver.Chrome(chrome_options=options)


class Firefox(SeleniumEngine):
    def _get_browser(self):
        os.environ['MOZ_HEADLESS'] = '1'
        return webdriver.Firefox()
