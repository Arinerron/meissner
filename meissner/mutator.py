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
        # XXX: handle other things? like browser-related errors etc
        payload = str(job)
        if result.success and payload not in self.meissner.solutions:
            # XXX: store in file or something?
            border = colored('-'*40, ['blue', 'bold'])
            border2 = colored('-'*40, ['gray']) + '\n'

            # there may be cases where the backend messes with out payload. There is no way to objectively detect this.
            code_highlighter = lambda code : colored(code, ['lightgreen'])
            payload_highlighter = lambda code, x = [] : colored(code, ['red'] + x)

            output = str(result.payload)
            output_split = output.split(payload)

            message = ['Found a functional XSS payload:\n', border, '\n', payload_highlighter(payload), '\n']

            # don't display injected HTML if it is too long
            if len(output) < 5000: # XXX: how do we choose how long of output code is too long
                message.extend([border2, code_highlighter(output_split.pop(0)), '\n'])
                for separator in output_split:
                    message.append(payload_highlighter(payload, ['underline']))
                    message.append(code_highlighter(separator))
            message.append(border)
            message.append('\n')

            logging.success(*message)
            self.meissner.solutions.append(payload)

        # XXX: this is a bad way to mix things up. we just don't want it to get too boring...
        if random.randint(0, 1000) == 0:
            random.shuffle(self.jobs)

        # XXX: determine if this is an interesting case or not?
        self.generate(base = (job, result))


    def mutate(self, possible_job):
        # XXX: once https://github.com/Arinerron/smartbytes/issues/1 is added, use that
        possible_job = list(possible_job)

        # XXX: improve mutation so it's not this sad
        # TODO: this is just temporary so I can get a working PoC, don't judge plz
        for i in range(random.randint(1, 2)):
            possible_job[random.randint(0, len(possible_job)-1)] = random.randint(0x00, 0xff)

        return smartbytes(possible_job)


    '''
    generate jobs dynamically based
    '''
    def generate(self, base = None):
        dictionary = self.meissner.dictionary.copy() + [
            # the empty value is to try only mutating the input without adding anything
            # theoretically all possible exploits will be generated because of this
            '',
            '\n',

            # we also want to increase the chances of the payload having an alert(1) in it
            # XXX: find a better solution
            'alert(1);',
            'alert(1);',
            'alert(1)',
            '*/alert(1);/*',
            'alert(1);//',
        ]
        random.shuffle(dictionary)

        possible_jobs = list()

        if base:
            base_job, result = base
            base_formatted_job = base_job.format()
        else:
            base_job, result = None, None
            base_formatted_job = smartbytes()

        # XXX: improve algorithm. this kinda sucks
        # we shuffle so that if we are at the max jobs size, it
        # gets a chance to "have other payloads" be generated
        for key in dictionary:
            # try just adding it plain
            possible_job = smartbytes(base_formatted_job) + key
            possible_jobs.append(possible_job)

            # and reverse
            possible_job = smartbytes(key) + smartbytes(base_formatted_job)
            possible_jobs.append(possible_job)

            # XXX: mutation is very poorly written and is buggy right now. :(
            # mutate it a little bit if it didn't error
            # if len(possible_job) and result and (result.success or not result.error) and random.randint(0, 10) != 0: # XXX: this is a bad way to throw in randomness
            #     possible_jobs.append(self.mutate(possible_job))

        for job in possible_jobs:
            if len(self.jobs) > self.max_jobs:
                break
            elif job in self.meissner.tested:
                # we've tested this one already :(
                continue

            if 'alert' not in job:
                continue
            # XXX: move mutations down here. also, find a better solution than what's above

            self.jobs.append(Job(job))


    def run(self):
        self.running = True

        self.generate()
        while self.running:
            # busy wait
            if len(self.jobs) > self.max_jobs:
                time.sleep(0.1) # XXX: smarter solution please
