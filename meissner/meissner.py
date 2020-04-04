from meissner.logger import *
import meissner

from smartbytes import *
import threading, time


class Meissner:
    '''
    arg dictionary: must be a list of smartbytes
    '''
    def __init__(self, harness, dictionary, filters = None, engine = None):
        self.harness = harness
        self.dictionary = dictionary
        self.filters = filters or list()
        self.engine = engine or meissner.engines.Chrome


    '''
    test a payload and return whether or not it popped an alert dialog
    '''
    def _format(self, payload):
        return self._filter(self._harness(payload))


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

    '''
    finish job
    '''
    def stop(self):
        logging.debug('Waiting for mutator to clean up...')
        self.mutator.running = False
        self.mutator.join()

        logging.debug('Waiting for engine workers to finish...')
        self.pool.running = False
        self.pool.join()

        return True


    '''
    begin fuzzing and report progress. do this in foreground
    '''
    def start(self, threads = 4):
        self.solutions = list()

        logging.debug('Initializing engine pool with ', colored_command(threads), ' threads...')
        self.pool = meissner.EnginePool(self, threads = threads)

        logging.debug('Populating jobs list...')
        max_jobs = 100000 # XXX: make dynamic limit
        self.tested = 0
        self.mutator = meissner.Mutator(self, max_jobs)
        self.mutator.start()
        while len(self.mutator.jobs) <= threads:
            time.sleep(1)

        logging.debug('Finished. Starting all engines...')
        self.pool.start()

        try:
            last_tested = 0
            status_wait = 5 # in seconds
            while self.pool.running:
                time.sleep(status_wait)
                rate = ((self.tested - last_tested)/status_wait)

                # give some status information
                info = {
                    'jobs/sec' : '%.2f' % rate + (
                        # https://github.com/Arinerron/meissner/wiki/My-fuzzer-is-running-slowly!
                        '\n' if rate > 3 else colored(' (slow? read ' + colored_command('https://bit.ly/39Gggy8') + ')', ['red', 'bold']) + '\n'
                    ),

                    'solutions' : '%d / %d' % (len(self.solutions), self.tested)
                }

                max_length = max([len(x) for x in info.keys()])
                message = ['Status update on ', colored_command(time.strftime("%c")), '\n']
                for key, val in info.items():
                    message += [
                        '... ',
                        colored(colored_command(key) + ' '*(max_length-len(key)), ['green', 'bold']),
                        ' | ',
                        colored(val, ['green'])
                    ]
                logging.info(*message)

                last_tested = self.tested

            self.mutator.running = self.pool.running
            logging.error('Meissner finished all fuzzing jobs. Please report this.')
        except KeyboardInterrupt:
            logging.info('Stopping Meissner...')
            self.stop()
