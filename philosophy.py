"""
The Philosophy Game
~~~~~~~~~~~~~~~~~~~~~~~~~

Clicking on the first non-parenthesized, non-italicized link,
in the main text of a Wikipedia article, and then repeating
the process for subsequent articles, usually eventually gets
one to the Philosophy article. (See
https://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy
for more information)

The Philosophy Game, written in Python, lets you do the clicking
programmatically.

Basic usage:

    >>> from philosophy import philosophy_game
    >>> for page in philosophy_game():
    ...     print(page)

Handling errors:
    >>> from philosophy import *
    >>> try:
    ...     print(list(philosophy_game())
    ... except ConnectionError:
    ...     sys.exit('Network error, please check your connection')
    ... except MediaWikiError as e:
    ...     sys.exit('MediaWiki API error {1}: {2}'.format(e.errors['code'],
    ...                                                e.errors['info']))
    ... except LoopException:
    ...     sys.exit('Loop detected, exiting...')
    ... except InvalidPageNameError as e:
    ...     sys.exit(e)
    ... except LinkNotFoundError as e:
    ...     sys.exit(e)
    ...

Advanced options:

In this example, we set `end` to 'Multicellular organism', so that
instead of stopping at 'Philosophy', trace() stops there.
    >>> print(list(page='Sandwich', end='Multicellular organism')):

In the following example, we set `infinite` to True, so that
trace() disregards the value of `end` and doesn't stop.
    >>> print(list(philosophy_game(page='Sliced bread', infinite=True)))

Note that `philosophy_game()` will always raise exceptions in case a loop
is detected or if valid link cannot be found within the page.
"""

import requests
import urllib
from requests.exceptions import ConnectionError
import lxml.html as lh

def valid_page_name(page):
    """
    Checks for valid mainspace Wikipedia page name
    """
    NON_MAINSPACE = [ 'File:',
                        'File talk:',
                        'Wikipedia:',
                        'Wikipedia talk:',
                        'Project:',
                        'Project talk:',
                        'Portal:',
                        'Portal talk:',
                        'Special:',
                        'Help:',
                        'Help talk:',
                        'Template:',
                        'Template talk:',
                        'Talk:',
                        'Category:',
                        'Category talk:' ]
    return all(non_main not in page for non_main in NON_MAINSPACE)

def strip_parentheses(string):
    """
    Remove parentheses from a string, leaving
    parentheses between <tags> in place

    Args:
        string: the string to remove parentheses from
    Returns:
        the processed string after removal of parentheses
    """
    p = a = 0
    result = ''
    for c in string:
        # When outside of parentheses within <tags>
        if p < 1:
            if c == '<':
                a += 1
            if c == '>':
                a -= 1

        # When outside of <tags>
        if a < 1:
            if c == '(':
                p += 1
            if p > 0:
                result += ' '
            else:
                result += c
            if c == ')':
                p -= 1

        # When inside of <tags>
        else:
            result +=c

    return result

class MediaWikiError(Exception):
    """
    Raised when the MediaWiki API returns an error.
    """
    def __init__(self, message, errors):
        super(MediaWikiError, self).__init__(message)
        self.errors = errors

class LoopException(Exception):
    """
    Raised when a loop is detected.
    """
    pass

class InvalidPageNameError(Exception):
    """
    Raised when an invalid page name is
    passed to trace().
    """
    pass

class LinkNotFoundError(Exception):
    """
    Raised when no valid link is found
    after parsing.
    """
    pass

def philosophy_game(page=None, end='Philosophy', whole_page=False, infinite=False, visited=[]):
    """
    Visit the first non-italicized, not-within-parentheses
        link of page recursively until the page end
        (default: 'Philosophy') is reached.

    Args:
        page: The Wikipedia page name to page with
        (default: a random page)
        end: The Wikipedia page name to end at
        (default: 'Philosophy')
        whole_page: Parse the whole parse rather than just
        the lead section (default: False)
        infinite: Only stop execution when either a loop is encountered
        or no valid link could be found
    Returns:
        A generator with the page names generated in sequence
        in real time (including page and end).
    Raises:
        MediaWikiError: if MediaWiki API responds with an error
        requests.exceptions.ConnectionError: if cannot initiate request
        LoopException: if a loop is detected
        InvalidPageNameError: if invalid page name is passed as argument
        LinkNotFoundError: if a valid link cannot be found for
        page
    """
    BASE_URL = 'https://en.wikipedia.org/w/api.php'
    HEADERS = { 'User-Agent': 'The Philosophy Game/0.1',
                'Accept-Encoding': 'gzip'}
    if page is None:
        params = dict(action='query', list='random', rnlimit=1,
                    rnnamespace=0, format='json')
        result = requests.get(BASE_URL, params=params,
                            headers=HEADERS).json()
        if 'error' in result:
            del visited[:]
            raise MediaWikiError('MediaWiki error',
                result['error'])
        page = result['query']['random'][0]['title']

    if not valid_page_name(page):
        del visited[:]
        raise InvalidPageNameError("Invalid page name '{0}'"
                                    .format(page))
    link_count = 0

    if not valid_page_name(page):
        del visited[:]
        raise InvalidPageNameError("Invalid page name '{0}'"
                .format(page))
    params = dict(action='parse', page=page, prop='text',
                format='json', redirects=1)

    if not whole_page:
        params['section'] = 0

    result = requests.get(BASE_URL, params=params,
                headers=HEADERS).json()

    if 'error' in result:
        del visited[:]
        raise MediaWikiError('MediaWiki error',
            result['error'])

    title = result['parse']['title'].encode('utf-8')

    # Don't yield if whole page requested
    # (which should only be done as a second attempt)
    if not whole_page:
        yield title

    # This needs to be done AFTER yield title
    # (The only) normal termination
    if not infinite and page == end:
        del visited[:]
        return
    raw_html = result['parse']['text']['*'].encode('utf-8')
    html = lh.fromstring(raw_html)

    # This takes care of most MediaWiki templates,
    # images, red links, hatnotes, italicized text
    # and anything that's strictly not text-only
    for elm in html.cssselect('.reference,span,div,.thumb,'
                            + 'table,a.new,i,#coordinates'):
        elm.drop_tree()

    html = lh.fromstring(strip_parentheses(lh.tostring(html)))
    link_found = False
    for elm, attr, link, pos in html.iterlinks():
        # Because .iterlinks() picks up 'src' and the like too
        if attr != 'href':
            continue
        next_page = link

        # Must be a valid internal wikilink
        if not next_page.startswith('/wiki/'):
            continue

        # Extract the Wikipedia page name
        next_page = next_page[len('/wiki/'):]

        # Decode escaped characters
        next_page = urllib.unquote(next_page)

        # Skip non-valid names
        if not valid_page_name(next_page):
            continue

        # Links use an underscore ('_')
        # instead of a space (' '), this
        # fixes that
        next_page = next_page.replace('_', ' ')

        # Eliminate named anchor, if any
        pos = next_page.find('#')
        if pos != -1:
            next_page = next_page[:pos]

        # Detect loop
        if next_page in visited:
            del visited[:]
            raise LoopException('Loop detected')

        link_found = True
        link_count += 1
        visited.append(page)

        for m in philosophy_game(page=next_page, end=end, visited=visited):
            yield m

        break
    if not link_found:
        if whole_page:
            del visited[:]
            raise LinkNotFoundError(
                    'No valid link found in page "{0}"'.format(
                        page.encode('utf-8')))
        else:
            for m in philosophy_game(page=page,
                    whole_page=True, end=end,
                    visited=visited):
                yield m
