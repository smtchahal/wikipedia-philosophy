#!/usr/bin/env python3

import philosophy
from philosophy.exceptions import *
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

def getargs():
    parser = argparse.ArgumentParser(description='Play The Philosophy Game')
    parser.add_argument('start', action='store', type=str,
        metavar='initial-pagename', nargs='*',
        help='the initial Wikipedia pagename to start with')
    parser.add_argument('-e', '--end', action='store', nargs='+',
        default=['Philosophy'], type=str, metavar='end', dest='end',
        help='Wikipedia pagename to terminate at (default: \'Philosophy\')')
    parser.add_argument('-i', '--infinite', action='store_true',
        help="""don't stop execution until a loop is found or
            a valid link cannot be found""", dest='infinite')
    parser.add_argument('-t', '--times', action='store', dest='times',
        default=1, type=int, metavar='times',
        help="""run the script this many times, selecting a random
            page every time except the first (default: 1)
            (anything less than 1 is infinity)""")

    return parser.parse_args()

def process(names, args, times=1):
    raised = False
    start_time = time.time()
    try:
        link_count = -1
        for s in names:
            if s == args.end:
                print(bcolors.BOLD + s + bcolors.ENDC)
            else:
                print(s)
            link_count += 1
    except ConnectionError:
        print_err('Network error, please check your connection')
        sys.exit(1)

    except MediaWikiError as e:
        print_err('Error: {0}: {1}'.format(
                    e.errors['code'],
                    e.errors['info']))
        raised = True

    except LoopException as e:
        print_log('---\n{0}, quitting...'.format(e))
        print_log('Visited {0} link(s), got a loop, taking {1} seconds'.format(
                        link_count,
                        round(time.time() - start_time, 4)))
        raised = True

    except InvalidPageNameError as e:
        print_err(e)
        raised = True

    except LinkNotFoundError as e:
        print_err(e)
        print_log('---')
        print_log(('Visited {0} link(s), could not find appropriate link'
                 + ' in last link, taking {1} seconds').format(
                        link_count,
                        round(time.time() - start_time, 4)))
        raised = True

    if not raised:
        print_log('---')
        print_log('Took {0} hop(s) and {1} seconds'.format(
                        link_count,
                        round(time.time() - start_time, 4)))

    if times == args.times:
        return

    # New line for separation
    print('')

    names = philosophy.trace(end=args.end, infinite=args.infinite)
    process(names, args, times=times+1)

def main():
    args = getargs()
    args.start = ' '.join(args.start)
    args.end = ' '.join(args.end)

    if args.start == '':
        args.start = None
    if args.end == '':
        args.end = 'Philosophy'

    names = philosophy.trace(page=args.start,
            end=args.end,
            infinite=args.infinite)
    process(names, args)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_err('Script interrupted')
        sys.exit(1)
