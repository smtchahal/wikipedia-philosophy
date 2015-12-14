#!/usr/bin/env python
from __future__ import print_function
from philosophy import *
from sys import argv
import sys
import time

if len(argv) != 2:
    sys.exit('Usage: {0} "Wikipedia page"'.format(argv[0]))

page = argv[1]

game = PhilosophyGame(page)
try:
    start_time = time.time()
    for s in game.trace(page):
        print(s)
except KeyboardInterrupt:
    print('\n---\nScript interrupted', file=sys.stderr)
    print('Visited {0} link(s), never reached Philosophy, taking {1} seconds'
            .format(game.link_count, round(time.time() - start_time, 4)))
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
    print('InvalidPageNameError: {0}'.format(e), file=sys.stderr)
    print('Visited {0} link(s), got an invalid page name, taking {1} seconds'
            .format(game.link_count, round(time.time() - start_time, 4)))
    sys.exit(1)
except LinkNotFoundError as e:
    print('Visited {0} link(s), could not find appropriate link,\
            taking {1} seconds'
            .format(game.link_count, round(time.time() - start_time, 4)))
    sys.exit('LinkNotFoundError: {0}'.format(e))

print('---')
print('Took {0} link(s) and {1} seconds'
    .format(game.link_count, round(time.time() - start_time, 4)))
