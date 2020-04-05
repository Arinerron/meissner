#!/usr/bin/env python3

import logging
import traceback
import sys, os, io, selectors
import re


# from: https://stackoverflow.com/a/38662876
def strip_ansi(line):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', line)


# cool custom color logging


class ColorLog(object):
    def __init__(self, logger):
        self._log = logger


    def _log_msg(self, name, *args, **kwargs):
        return getattr(self._log, {
            'success' : 'info',
            'exception' : 'fatal'
        }.get(name, name))(self._format_msg(name, *args, **kwargs))


    def _format_msg(self, name, *args, **kwargs):
        exc_info = kwargs.get('exc_info', False)

        if name == 'exception':
            name = 'fatal'
            exc_info = True
        elif name == 'warn':
            name = 'warning'
        elif name == 'critical':
            name = 'fatal'

        _colored = colored if kwargs.get('use_ansi', True) else lambda s, x : s

        prompt = prompts[name] + ' ' if not kwargs.get('prompt') else kwargs.get('prompt')
        message = _colored(prompt, colormap[name]) + ''.join([_colored(x, colormap[name]) for x in args])

        if exc_info:
            exception = traceback.format_exc().strip()

            prompt = '... ' if not kwargs.get('prompt') else kwargs.get('prompt')
            message += '\n' + '\n'.join([
                prompt + _colored(x, colormap['exception']) for x in exception.split('\n')
            ])

        return message


    def __getattr__(self, name):
        if name in ['debug', 'info', 'warn', 'warning', 'error', 'critical', 'fatal', 'exception', 'success']:
            return lambda *args, **kwargs : self._log_msg(name, *args, **kwargs)

        return getattr(self._log, name)



colored = lambda message, attrs = [] : colors['reset'] + ''.join([colors[x] for x in attrs]) + str(message) + colors['reset']
colored_command = lambda message : colors['bold'] + colors['underline'] + str(message) + colors['reset']

colormap = {
    'debug' : ['italics', 'gray'],
    'info' : ['blue'],
    'warning' : ['bold', 'darkorange'],
    'error' : ['bold', 'lightred'],
    'fatal' : ['bg_red', 'bold_white'],
    'exception' : ['italics', 'darkred'],
    'success' : ['bold', 'green']
}

prompts = {
    'debug' : ' * ',
    'info' : '[*]',
    'warn' : '[!]',
    'warning' : '[!]',
    'error' : '[-]',
    'fatal' : '[-]',
    'success' : '[+]'
}

log_levels = {
    'debug' : logging.DEBUG,
    'info' : logging.INFO,
    'warn' : logging.WARNING,
    'warning' : logging.WARNING,
    'error' : logging.ERROR,
    'critical' : logging.CRITICAL,
    'fatal' : logging.FATAL,
    'success' : logging.FATAL,
}

colors = {
    'lightgray' : '\033[37m',
    'darkgray' : '\033[90m',
    'gray' : '\033[2m',
    'blue' : '\033[34m',
    'green' : '\033[32m',
    'cyan' : '\033[36m',
    'darkorange' : '\033[33m',
    'darkred' : '\033[31m',
    'lightred' : '\033[91m',
    'red' : '\033[91m',
    'yellow' : '\033[33m',
    'lightyellow' : '\033[93m',
    'lightgreen' : '\033[92m',
    'bold_white' : '\033[1;37m',

    'bg_red' : '\033[41m',

    'italics' : '\033[3m',
    'bold' : '\033[01m',
    'underline' : '\033[04m',

    'reset' : '\033[0m'
}


LOG_LEVEL = logging.DEBUG


log = ColorLog(logging.getLogger(__name__))
log.setLevel(LOG_LEVEL)
stdout = logging.StreamHandler()
log.addHandler(stdout)
stdout.setLevel(LOG_LEVEL)
logging = log # XXX: find a cleaner solution plz
