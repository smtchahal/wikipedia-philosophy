#!/usr/bin/env python
from __future__ import print_function
from philosophy import *
from sys import argv
import sys
import time

if len(argv) == 1:
    game = PhilosophyGame()
else:
    page = ''
    for i in xrange(1, len(argv)):
        if i > 1:
            page += ' ' + argv[i]
        else:
            page += argv[i]
    game = PhilosophyGame(page)

try:
    start_time = time.time()
    for s in game.trace():
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
    print(e, file=sys.stderr)
    print('Visited {0} link(s), got an invalid page name, taking {1} seconds'
            .format(game.link_count, round(time.time() - start_time, 4)))
    sys.exit(1)
except LinkNotFoundError as e:
    print('Visited {0} link(s),', 'could not find appropriate link',
            'in last link, taking {1} seconds'
            .format(game.link_count, round(time.time() - start_time, 4)))
    sys.exit(e)

print('---')
print('Took {0} link(s) and {1} seconds'
    .format(game.link_count, round(time.time() - start_time, 4)))
