from meissner.logger import *
from meissner.engines import SeleniumEngine

from smartbytes import *
import threading, time


class EngineWorker(threading.Thread):
    def __init__(self, pool, id = 0):
        super(EngineWorker, self).__init__()

        self.pool = pool
        self.id = id
        self._browser_lock = False

        # XXX: do we need a new one every run?
        self.engine = self.pool.meissner.engine()


    def execute(self, job):
        return self.engine.test(str(job))


    def run(self):
        while self.pool.running:
            # busy wait
            if not self.pool.meissner.mutator.jobs:
                time.sleep(0.1)
                continue

            try:
                # get the job OBJECT
                job = self.pool.meissner.mutator.jobs.pop(0)
                self.pool.meissner.tested.append(smartbytes(job))

                # turn it into a str payload
                formatted_job = job.format()

                # pass it through filters
                formatted_job = self.pool.meissner._format(job)

                self._browser_lock = True
                self.pool.meissner.mutator.report(job, self.execute(formatted_job))
                self._browser_lock = False
            except:
                if self.pool.running:
                    logging.exception('Worker ', colored_command(self.id), ' encountered a fatal exception.')
                break


'''
engine pooling
'''
class EnginePool(threading.Thread):
    def __init__(self, fuzzer, threads = 4):
        super(EnginePool, self).__init__()

        self.meissner = fuzzer
        self.threads = list()

        for i in range(1, threads + 1):
            self.threads.append(EngineWorker(self, id = i))

            if i % 10 == 0:
                logging.debug('... created ', colored_command(i), ' workers so far')

        self.running = False


    def run(self):
        self.running = True

        for thread in self.threads:
            thread.start()

        # block until all worker threads are done
        nthreads = len(self.threads)
        i = 0
        while True:
            thread = self.threads[i % len(self.threads)]

            if thread.isAlive() and isinstance(thread.engine, SeleniumEngine):
                # swap out its browser object
                oldbrowser = thread.engine.browser
                engine = self.meissner.engine() # XXX: change this so that we can accept non-selenium engines

                # XXX: race condition :(
                while thread._browser_lock and thread.isAlive():
                    # busy wait
                    time.sleep(0.1)

                thread.engine = engine
                oldbrowser.quit()

                time.sleep(120 / len(self.threads))
            else:
                # otherwise, let's notify that it's done
                thread.join()
                logging.debug('Worker ', colored_command(thread.id), ' finished executing.')

            i += 1
            nthreads -= 1
            if nthreads == 0:
                break
