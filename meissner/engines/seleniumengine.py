from meissner.logger import *
from . import Engine, Result
from smartbytes import *

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import uuid, base64, time


timeout = 2 # XXX: make this a config!

# how many seconds to wait (e.g. for setTimeout-based XSS) before checking status
wait = 1 # XXX: move to config or find better solution

class SeleniumEngine(Engine):
    def __init__(self):
        self.browser = self._get_browser()

    def _get_browser(self):
        return None

    def test(self, payload):
        # build the test
        # XXX: this makes it so we don't support CSPs
        # XXX: make a custom function instead of alert in case the challenge requires alert function
        indicator = str(uuid.uuid4())
        # XXX: will this work for large pages?
        # XXX: if it loads external resources, we may be screwed
        # TODO: support custom filters like --filter=myfile.py which reads from stdin and writes to stdout
        html = smartbytes('<script>alert=console.log.bind(null,"', indicator, '}")</script>\n\n', payload)
        url = 'data:text/html;base64,' + base64.b64encode(bytes(html)).decode('utf-8')

        # load the html
        self.browser.get(url)

        # XXX: this is vuln to race condition.
        loaded = False
        time.sleep(wait)
        start_time = time.time()
        while time.time() - start_time < timeout:
            time.sleep(0.05)

            # check if page has loaded yet
            if any([
                self.browser.execute_script('return document.readyState;') == 'complete',
                self.browser.current_url != url
                ]):
                loaded = True
                break

        if not loaded:
            logging.warning('Page appears to not have loaded despite being given ', timeout, ' seconds!')

        # check if we won or not
        success = False
        for entry in self.browser.get_log('browser'):
            if indicator in entry.get('message', ''):
                success = True
                break

        result = Result(payload, success)
        return result


class Chrome(SeleniumEngine):
    def _get_browser(self):
        # make it headless
        options = webdriver.ChromeOptions()
        options.add_argument('headless')

        # capture logging
        capabilities = DesiredCapabilities.CHROME
        capabilities['goog:loggingPrefs'] = {
            'browser':'ALL'
        }

        return webdriver.Chrome(chrome_options = options, desired_capabilities = capabilities)


class Firefox(SeleniumEngine):
    def _get_browser(self):
        # make it headles
        os.environ['MOZ_HEADLESS'] = '1'

        # XXX: capture logging?

        return webdriver.Firefox()
