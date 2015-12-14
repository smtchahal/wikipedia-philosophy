# The Philosophy Game

A Python module that allows you to play Wikipedia's
["Getting to Philosophy"](https://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy)
game.

## Brief summary

Clicking on the first non-parenthesized, non-italicized link, in the
main text of a Wikipedia article, and then repeating the process for
subsequent articles, usually eventually gets one to the Philosophy article.
(See
[this Wikipedia essay](https://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy)
for more information)

The Philosophy Game, written in Python, lets you do the clicking
programmatically.

## Basic usage

```python
from philosophy import *
my_first_wiki_page = 'Python (programming language)'
game = PhilosophyGame()
for s in game.trace(my_first_wiki_page):
    print s
```

## Handling errors
```python
from philosophy import *
my_first_wiki_page = 'Python (programming language)'
game = PhilosophyGame()
try:
    for s in game.trace(my_first_wiki_page):
        print(s)
except ConnectionError:
	# raised when unable to connect to 'https://en.wikipedia.org/w/api.php'
    sys.exit('Network error, please check your connection')
except MediaWikiError as e:
	# raised when the MediaWiki API returns an error
    sys.exit('MediaWiki error {1}: {2}'.format(e.errors['code'], e.errors['info']))
except LoopException:
	# raised when a loop is detected
    sys.exit('Loop detected, exiting...')
except InvalidPageNameError as e:
	# raised when an invalid pagename is passed to trace()
    sys.exit(e)
except LinkNotFoundError as e:
	# raised when no appropriate link could be found in the article
    sys.exit(e)
```

## Dependencies
Wikipedia Philosophy Game depends on the following Python libraries.
* [Requests](http://docs.python-requests.org/)
* [lxml](http://lxml.de/)

## Example
I've included a simple ready-to-use [example script](example.py) that you can
start using immediately without making your own.

Just fire up your favorite terminal emulator, grant the script execute
permission, and run the script with the initial Wikipedia page name
as the first parameter. On a linux distro, the transcript
might look like this.

```
$ chmod +x example.py
$ ./example.py "Python (programming language)"
General-purpose programming language
Computer software
Computer
Computer program
Instruction set
Computer architecture
Electronic engineering
Engineering
Mathematics
Quantity
Property (philosophy)
Modern philosophy
Philosophy
---
Took 13 link(s) and 33.8522 seconds
```
