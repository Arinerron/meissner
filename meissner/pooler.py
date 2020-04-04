from meissner.logger import *

from smartbytes import *
import threading, time


class EngineWorker(threading.Thread):
    def __init__(self, pool, id = 0):
        super(EngineWorker, self).__init__()

        self.pool = pool
        self.id = id

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

                # turn it into a str payload
                formatted_job = job.format()

                # pass it through filters
                formatted_job = self.pool.meissner._format(job)

                self.pool.meissner.mutator.report(job, self.execute(formatted_job))
            except:
                logging.exception('Worker ', colored_command(self.id), ' encountered a fatal exception.')
                break


'''
engine pooling
'''
class EnginePool(threading.Thread):
    def __init__(self, fuzzer, threads = 4):
        super(EnginePool, self).__init__()

        self.meissner = fuzzer
        self.threads = [
            EngineWorker(self, id = i) for i in range(1, threads + 1)
        ]

        self.running = False


    def run(self):
        self.running = True

        for thread in self.threads:
            thread.start()

        # block until all worker threads are done
        for thread in self.threads:
            thread.join()
            logging.debug('Worker ', colored_command(thread.id), ' finished executing.')
