from . import Harness, placeholder
from meissner.logger import *

from smartbytes import *

import subprocess

class CommandHarness(Harness):
    def __init__(self, cmd):
        logging.debug('... using command: ', colored_command(cmd))

        self.cmd = cmd
        self.warn_stderr = True

    def test(self, payload):
        command = self.cmd
        write = None

        if placeholder in command:
            # placeholder was found in command, add as arg
            command = self.cmd.copy()
            i = self.cmd.index(placeholder)
            command[i] = str(payload)
        else:
            # otherwise, write to stdin
            write = bytes(payload)

        p = subprocess.Popen(self, command, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

        if write:
            p.stdin.write(payload)

        stdout, stderr = p.communicate()

        # XXX: find a better solution than warn_stderr to not spam console
        if stderr and self.warn_stderr:
            logging.warning('A test case caused data to be written to stderr.\n    case: ', colored_command(str(payload)), '\n    output: ', colored_command(str(smartbytes(stderr))))
            self.warn_stderr = False

        return stdout
