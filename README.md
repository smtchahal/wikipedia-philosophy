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

## How it works
The module does the following:

1. Parse the [lead section](https://en.wikipedia.org/wiki/MOS:LEAD)
of a Wikipedia page with given title as html, raise an appropriate error
if an error occured while trying to do so (`MediaWikiError`,
`ConnectionError` or `InvalidPageNameError`)
2. Look for internal links in the main text of the page, ignoring any
infoboxes, tables, red links, italicised text, links within parentheses,
or links to pages outside of the Wikipedia mainspace.
3. If any links are found, iterate over the links, and get the first
link's page name.
4. If no links are found, parse the whole page again (not just the lead
section this time)
5. Repeat steps 2-3. If no link is found this time, raise an appropriate
error (`LinkNotFoundError`).
6. Repeat steps 1-5. If the end page is reached (default is "Philosophy;
see [Advanced options](#advanced-options) below), exit. If a loop is
encountered (a loop is when two Wikipedia pages link to each other),
raise an appropriate error (`LoopException`).

## Basic usage

```python
from philosophy import philosophy_game
for s in philosophy_game():
    print(s)
```

## Handling errors

```python
from philosophy import *
my_first_wiki_page = 'Python (programming language)'
try:
    for s in philosophy_game(my_first_wiki_page):
        print(s)
except ConnectionError:
	# raised when unable to connect to 'https://en.wikipedia.org/w/api.php'
    sys.exit('Network error, please check your connection')
except MediaWikiError as e:
	# raised when the MediaWiki API returns an error
    sys.exit('MediaWiki error {0}: {1}'.format(e.errors['code'], e.errors['info']))
except LoopException:
	# raised when a loop is detected
    sys.exit('Loop detected, exiting...')
except InvalidPageNameError as e:
	# raised when an invalid pagename is passed to philosophy_game()
    sys.exit(e)
except LinkNotFoundError as e:
	# raised when no valid link could be found in the article
    sys.exit(e)
```

## Advanced options

In this example, we set `end` to 'Multicellular organism', so that
instead of stopping at 'Philosophy', philosophy_game() stops there.

```python
print(list(philosophy_game(page='Sandwich', end='Multicellular organism')))
```

In the following example, we set `infinite` to `True`, so that
philosophy_game() disregards the value of `end` and doesn't stop.

```python
print(list(philosophy_game(page='Sliced bread', infinite=True,
				end="Doesn't matter")))
```

Note that philosophy_game() will always raise exceptions in case a loop is detected
or if a valid link cannot be found within the page.

## Dependencies
Wikipedia Philosophy Game depends on the following Python libraries.
* [Requests](http://docs.python-requests.org/)
* [lxml](http://lxml.de/)

## Example script
![example.py script in action](example.gif?raw=true "example.py script in action")

I've included a simple ready-to-use [example script](example.py) that you
can start using immediately without making your own.

### Usage examples
Here's the simplest example.
```
$ ./example.py
Python (programming language)
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
As you may see, the script starts at the Wikipedia page
"Python (programming language)" and ends at "Philosophy".

Here's another version.
```
$ ./example.py Sandwich --end "Multicellular organism"
Sandwich
Vegetable
Fruit
Botany
Plant
Multicellular organism
---
Took 15 link(s) and 35.6163 seconds
```
In this example, we start with "Sandwich" and set the `end` parameter to
"Multicellular organism", so we're telling the script to stop at
"Multicellular organism" instead of "Philosophy". You can also use the
`-e` option for setting the `end` parameter.

The following version only stops when loops are detected or when a
valid link cannot be found, ignoring the value of the `end` parameter.
```
$ ./example.py --infinite --end "Doesn't matter"
Shpolskii matrix
Phonon
Physics
Natural science
Science
Knowledge
Awareness
Conscious
Quality (philosophy)
Philosophy
Reality
Existence
Ontology
---
Loop detected, quitting...
Visited 12 link(s), got a loop, taking 28.1101 seconds
```

You can always view help for the script using the `--help` (or `-h`)
parameter.
```
usage: example.py [-h] [-e end [end ...]] [-i] [-t times]
                  [initial-pagename [initial-pagename ...]]

Play The Philosophy Game

positional arguments:
  initial-pagename      the initial Wikipedia pagename to start with

optional arguments:
  -h, --help            show this help message and exit
  -e end [end ...], --end end [end ...]
                        Wikipedia pagename to terminate at (default:
                        'Philosophy')
  -i, --infinite        don't stop execution until a loop is found or a valid
                        link cannot be found
  -t times, --times times
                        run the script this many times (default: 1) (anything
                        less than 1 is infinity)
```
