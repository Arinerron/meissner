#!/usr/bin/env python3

import argparse

from meissner.logger import *
import meissner

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Meissner Lop - XSS Filter Bypass Exploit Fuzzer')
    parser.add_argument('--no-ansi', '-c', default = False, action = 'store_true', help = 'disable ANSI coloring on all output')
    parser.add_argument('--log-level', '-v', default = 'debug', type = str, help = 'set logging level')

    subparsers = parser.add_subparsers(help = 'The sub-command to execute')

    parser_fuzz = subparsers.add_parser('fuzz', aliases = ['test'], help = 'Fuzz for a filter bypass')
    parser_fuzz.set_defaults(subcommand = 'fuzz')

    parser_fuzz.add_argument('--url', '--uri', '-u', default = False, type = str, help = 'use a URL harness, where {xss} is the injection point')
    parser_fuzz.add_argument('--dictionary', '--dict', '-d', default = False, type = str, help = 'the meissner mutation dictionary to use')
    parser_fuzz.add_argument('--filter', '-f', default = [], action='append', help = 'pass the input through a filter before the program')
    parser_fuzz.add_argument('--engine', '--browser', '-e', default = 'chrome', type = str, help = 'the browser rendering engine to use')
    parser_fuzz.add_argument('cmd', nargs = '*', default = None, help = 'the command to execute, where {xss} is the injection point')

    args = parser.parse_args()

    # setup logging

    log_level = args.log_level
    log_level = log_levels.get(log_level, log_level)

    try:
        log_level = int(log_level)
    except ValueError:
        # convert to int if possible
        logging.warn('Unable to convert logging level ', colored_command(log_level), ' to an integer.')

    logging.setLevel(log_level)

    if not 'subcommand' in vars(args):
        logging.info('This is the Meissner Lop XSS fuzzer. For usage, run:\n\n    ', colored_command('%s --help' % sys.argv[0]), '\n')
        exit(0)

    # setup harness

    url = args.url
    command = args.cmd

    if url and command:
        logging.warning('Both a URL and a command were specified. The command will take precedence.')

    if command:
        logging.debug('Using harness ', colored_command('CommandHarness'))
        harness = meissner.harnesses.CommandHarness(command)
    elif url:
        logging.debug('Using harness ', colored_command('URLHarness'))
        harness = meissner.harnesses.URLHarness(url)
    else:
        logging.error('No harness specified. Please use ', colored_command('--url'), ' to specify a URL harness or ', colored_command('-- [command...]'), ' to specify a command harness.')
        exit(1)

    # setup filters

    filters = list()
    _filters = list()
    _invalid_filters = set()
    all_filters = {
        'urlencode' : meissner.filters.urlencode.URLEncoder
    }

    for filter in args.filter:
        if filter.lower() not in all_filters:
            _invalid_filters.add(filter)
        else:
            _filters.append(filter.lower())
            filters.append(all_filters[filter.lower()]())

    if _invalid_filters:
        logging.error('The filters %s are invalid. Please choose a valid filter from the list %s.' % (
            repr(_invalid_filters),
            repr(all_filters.keys())
        ))
        exit(1)

    if filters:
        logging.debug('Using filters: ', colored_command(', '.join(_filters)))

    # setup engine

    # TODO: support more engines
    all_engines = {
        'chrome' : meissner.engines.Chrome
    }

    engine = args.engine.strip().lower()
    if engine in all_engines:
        engine = all_engines[engine]()
    else:
        logging.error('Engine ', colored_command(engine), ' does not exist. Please choose a valid engine from the list %s.' % repr(all_engines.keys()))
        exit(1)

    # begin fuzzing

    logging.info('Initializing Meissner...')

    fuzzer = meissner.Meissner(harness, filters = filters)
