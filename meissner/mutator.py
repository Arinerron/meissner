from meissner.logger import *

from smartbytes import *
import threading, random, time


class Job(smartbytes):
    # XXX: get rid of this function lol
    def format(self):
        return self


class Mutator(threading.Thread):
    def __init__(self, fuzzer, max_jobs):
        super(Mutator, self).__init__()

        self.meissner = fuzzer
        self.max_jobs = max_jobs
        self.jobs = list()

        self.running = False

    '''
    figure out how to handle various results

    arg job: the Job object representing the payload that was sent
    arg formatted_job: the str representation of the payload physically executed
    arg result: the output from the execution engine
    '''
    def report(self, job, result):
        self.meissner.tested += 1

        # XXX: handle other things? like browser-related errors etc
        if result.success:
            # XXX: store in file or something?
            logging.info('Found a functional payload:\n\n', repr(job.payload), '\n')
            self.meissner.solutions.append(job.payload)

        # XXX: determine if this is an interesting case or not?
        self.generate(base = (job, result))


    def mutate(self, possible_job):
        # XXX: once https://github.com/Arinerron/smartbytes/issues/1 is added, use that
        possible_job = list(possible_job)

        # XXX: improve mutation so it's not this sad
        # TODO: this is just temporary so I can get a working PoC, don't judge plz
        for i in range(random.randint(1, 4)):
            possible_job[random.randint(0, len(possible_job)-1)] = random.randint(0x00, 0xff)

        return smartbytes(possible_job)


    '''
    generate jobs dynamically based
    '''
    def generate(self, base = None):
        # the empty value is to try only mutating the input without adding anything
        # theoretically all possible exploits will be generated because of this
        dictionary = self.meissner.dictionary + ['']

        possible_jobs = list()

        if base:
            base_job, result = base
            base_formatted_job = base_job.format()
        else:
            base_job, result = None, None
            base_formatted_job = smartbytes()

        # XXX: improve algorithm. this kinda sucks

        for key in dictionary:
            # try just adding it plain
            possible_job = base_formatted_job + key
            possible_jobs.append(possible_job)

            # mutate it a little bit if it didn't error
            if len(possible_job) and result and (result.success or not result.error):
                self.mutate(possible_job)

        self.jobs.extend([
            Job(job) for job in possible_jobs
        ])


    def run(self):
        self.running = True

        while self.running:
            # busy wait
            if len(self.jobs) > self.max_jobs:
                time.sleep(0.1) # XXX: smarter solution please

            self.generate()
