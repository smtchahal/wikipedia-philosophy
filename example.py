#!/usr/bin/env python
from __future__ import print_function
from philosophy import *
import sys
import time
import argparse

parser = argparse.ArgumentParser(description='Play The Philosophy Game')
parser.add_argument('page', action='store', type=str,
    metavar='initial-pagename', nargs='*',
    help='the initial Wikipedia pagename to start with')
parser.add_argument('-e', '--end', action='store', default='Philosophy',
    type=str, metavar='end', dest='end',
    help='Wikipedia pagename to terminate at (default: \'Philosophy\')')
parser.add_argument('-d', '--dont-stop', action='store_true',
    help="""don't stop execution until a loop is found or
    a valid link cannot be found""", dest='dont_stop')

args = parser.parse_args()
if len(args.page) == 0:
    game = PhilosophyGame(end=args.end,
        dont_stop=args.dont_stop)
else:
    page = ' '.join(args.page)
    game = PhilosophyGame(page=page, end=args.end,
        dont_stop=args.dont_stop)

try:
    start_time = time.time()
    for s in game.trace():
        print(s)
except KeyboardInterrupt:
    print('\n---\nScript interrupted', file=sys.stderr)
    print('Visited {0} link(s), never reached {1}, taking {2} seconds'
            .format(game.link_count, game.end,
            round(time.time() - start_time, 4)))
    sys.exit(1)
except ConnectionError:
    sys.exit('Network error, please check your connection')
except MediaWikiError as e:
    sys.exit('Error: {0}: {1}'.format(e.errors['code'], e.errors['info']))
except LoopException:
    print('---\nLoop detected, quitting...')
    print('Visited {0} link(s), got a loop, taking {1} seconds'
            .format(game.link_count, round(time.time() - start_time, 4)))
    sys.exit(1)
except InvalidPageNameError as e:
    print('---')
    print(e, file=sys.stderr)
    print('Visited {0} link(s), got an invalid page name, taking {1} seconds'
            .format(game.link_count, round(time.time() - start_time, 4)))
    sys.exit(1)
except LinkNotFoundError as e:
    print('---')
    print(e, file=sys.stderr)
    print(('Visited {0} link(s), could not find appropriate link'
             + ' in last link, taking {1} seconds')
            .format(game.link_count, round(time.time() - start_time, 4)))
    sys.exit(1)

print('---')
print('Took {0} link(s) and {1} seconds'
    .format(game.link_count, round(time.time() - start_time, 4)))
