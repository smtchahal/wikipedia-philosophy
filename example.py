#!/usr/bin/env python
from __future__ import print_function
from philosophy import *
import sys
import time
import argparse

def process(game):
    try:
        for s in game.trace():
            print(s)
    except KeyboardInterrupt:
        print('\n---\nScript interrupted', file=sys.stderr)
        print('Visited {0} link(s), never reached "{1}", taking {2} seconds'
            .format(game.link_count,
            game.end,
            round(time.time() - start_time, 4)))
        sys.exit(1)

    except ConnectionError:
        return False
        sys.exit('Network error, please check your connection')

    except MediaWikiError as e:
        print('Error: {0}: {1}'.format(e.errors['code'], e.errors['info'],
                file=sys.stderr))
        return False

    except LoopException:
        print('---\nLoop detected, quitting...')
        print('Visited {0} link(s), got a loop, taking {1} seconds'.format(
                        game.link_count,
                        round(time.time() - start_time, 4)))
        return False

    except InvalidPageNameError as e:
        print('---')
        print(e, file=sys.stderr)
        print('Visited {0} link(s), got an invalid page name, taking {1} seconds'
                .format(game.link_count, round(time.time() - start_time, 4)))
        return False

    except LinkNotFoundError as e:
        print('---')
        print(e, file=sys.stderr)
        print(('Visited {0} link(s), could not find appropriate link'
                 + ' in last link, taking {1} seconds')
                .format(game.link_count, round(time.time() - start_time, 4)))
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

args = getargs()
args.end = ' '.join(args.end)

try:
    if len(args.page) == 0:
        game = PhilosophyGame(end=args.end, dont_stop=args.dont_stop)
    else:
        page = ' '.join(args.page)
        game = PhilosophyGame(page=page, end=args.end, dont_stop=args.dont_stop)
except ConnectionError as e:
    print('Connection error, please check your connection')
    sys.exit(1)

i = 1
while True:
    start_time = time.time()
    if process(game):
        print('---')
        print('Took {0} link(s) and {1} seconds'.format(
                                    game.link_count,
                                    round(time.time() - start_time, 4)))
    if i == args.times:
        break
    else:
        # New line for separation
        print('')

    game = PhilosophyGame(end=args.end, dont_stop=args.dont_stop)
    i += 1
