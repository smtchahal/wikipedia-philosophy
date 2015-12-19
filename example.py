#!/usr/bin/env python
from __future__ import print_function
from philosophy import *
import sys
import time
import argparse

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_err(msg):
    print('{0}{1}{2}{3}'.format(bcolors.FAIL,
                                bcolors.BOLD,
                                msg,
                                bcolors.ENDC),
                    file=sys.stderr)

def print_log(msg):
    print(bcolors.OKGREEN + msg + bcolors.ENDC)

def process(game, start_time):
    try:
        for s in game.trace():
            if s == game.end:
                print(bcolors.BOLD + s + bcolors.ENDC)
                return True
            print(s)
    except ConnectionError:
        return False
        sys.exit('Network error, please check your connection')

    except MediaWikiError as e:
        print_err('Error: {0}: {1}'.format(
                    e.errors['code'],
                    e.errors['info']))
        return False

    except LoopException:
        print_log('---\nLoop detected, quitting...')
        print_log('Visited {0} link(s), got a loop, taking {1} seconds'.format(
                        game.link_count,
                        round(time.time() - start_time, 4)))
        return False

    except InvalidPageNameError as e:
        print_err(e)
        print_log('---')
        print_log('Visited {0} link(s), got an invalid page name,'
                    + ' taking {1} seconds'.format(
                        game.link_count,
                        round(time.time() - start_time, 4)))
        return False

    except LinkNotFoundError as e:
        print_err(e)
        print_log('---')
        print_log(('Visited {0} link(s), could not find appropriate link'
                 + ' in last link, taking {1} seconds').format(
                        game.link_count,
                        round(time.time() - start_time, 4)))
        return False

    return True

def getargs():
    parser = argparse.ArgumentParser(description='Play The Philosophy Game')
    parser.add_argument('page', action='store', type=str,
        metavar='initial-pagename', nargs='*',
        help='the initial Wikipedia pagename to start with')
    parser.add_argument('-e', '--end', action='store',
        default=['Philosophy'], type=str, metavar='end', dest='end',
        nargs='+',
        help='Wikipedia pagename to terminate at (default: \'Philosophy\')')
    parser.add_argument('-d', '--dont-stop', action='store_true',
        help="""don't stop execution until a loop is found or
            a valid link cannot be found""", dest='dont_stop')
    parser.add_argument('-t', '--times', action='store', dest='times',
        default=1, type=int, metavar='times',
        help='''run the script this many times (default: 1)
            (anything less than 1 is infinity)''')

    return parser.parse_args()

def main():
    args = getargs()
    args.end = ' '.join(args.end)

    try:
        if len(args.page) == 0:
            game = PhilosophyGame(end=args.end, dont_stop=args.dont_stop)
        else:
            page = ' '.join(args.page)
            game = PhilosophyGame(page=page, end=args.end, dont_stop=args.dont_stop)
    except ConnectionError:
        print_err('Connection error, please check your connection')
        sys.exit(1)
    except MediaWikiError as e:
        print_err('MediaWikiError: {0}: {1}'.format(e.errors['code'],
                            e.errors['info']))

    i = 1
    while True:
        start_time = time.time()
        if process(game, start_time):
            print_log('---')
            print_log('Took {0} link(s) and {1} seconds'.format(
                                        game.link_count,
                                        round(time.time() - start_time, 4)))
        if i == args.times:
            break
        else:
            # New line for separation
            print('')

        game = PhilosophyGame(end=args.end, dont_stop=args.dont_stop)
        i += 1

try:
    main()
except KeyboardInterrupt:
    print_err('Script interrupted')
    sys.exit(1)
