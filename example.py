#!/usr/bin/env python
from __future__ import print_function
from philosophy import *
from sys import argv
import sys
import time

if len(argv) != 2:
    sys.exit('Usage: %s "Wikipedia page"' % argv[0])

page = argv[1]

game = PhilosophyGame()
try:
    start_time = time.time()
    for s in game.trace(page):
        print(s)
except KeyboardInterrupt:
    print('\n---\nScript interrupted', file=sys.stderr)
    print('Visited %d link(s), never reached Philosophy, taking %s seconds'
            % (game.link_count, round(time.time() - start_time, 4)),
            file=sys.stderr)
    sys.exit(1)
except ConnectionError:
    sys.exit('Network error, please check your connection')
except MediaWikiError as e:
    sys.exit('Error: %s: %s' % (e.errors['code'], e.errors['info']))
except LoopException:
    print('---\nLoop detected, quitting...')
    print('Visited %d links, got a loop in %s seconds' 
            % (game.link_count, round(time.time() - start_time, 4)))
    sys.exit(1)
    
print('---')
print('Took %d link(s) and %s seconds'
    % (game.link_count, round(time.time() - start_time, 4)))
