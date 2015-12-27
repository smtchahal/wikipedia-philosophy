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

    >>> import philosophy
    >>> for page in philosophy.trace():
    ...     print(page)

Handling errors:
    >>> import philosophy
    >>> from philosophy.exceptions import *
    >>> try:
    ...     for page in philosophy.trace():
    ...         print(page)
    ... except ConnectionError:
    ...     sys.exit('Network error, please check your connection')
    ... except MediaWikiError as e:
    ...     sys.exit('MediaWiki API error {0}: {1}'.format(e.errors['code'],
    ...                                                e.errors['info']))
    ... except LoopException:
    ...     sys.exit('Loop detected, exiting...')
    ... except InvalidPageNameError as e:
    ...     sys.exit(e)
    ... except LinkNotFoundError as e:
    ...     sys.exit(e)

Advanced options:

In this example, we set `end` to 'Multicellular organism', so that
instead of stopping at 'Philosophy', trace() stops there.
    >>> print(list(philosophy.trace(page='Sandwich', end='Multicellular'
    ... 'organism')))

In the following example, we set `infinite` to True, so that
trace() disregards the value of `end` and doesn't stop.
    >>> print(list(philosophy.trace(page='Sliced bread', infinite=True)))

Note that `trace()` will always raise exceptions in case a loop
is detected or if valid link cannot be found within the page.
"""

import requests
import urllib.parse
from .exceptions import *
import lxml.html as lh

def valid_page_name(page):
    """
    Checks for valid mainspace Wikipedia page name

    Args:
        page: The page name to validate

    Returns:
        True if `page` is valid, False otherwise
    """
    NON_MAINSPACE = [
                        'File:',
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
                        'Category talk:'
                    ]
    return all(not page.startswith(non_main) for non_main in NON_MAINSPACE)

def strip_parentheses(string):
    """
    Remove parentheses from a string, leaving
    parentheses between <tags> in place

    Args:
        string: the string to remove parentheses from

    Returns:
        the processed string after removal of parentheses
    """
    nested_parentheses = nesting_level = 0
    result = ''
    for c in string:
        # When outside of parentheses within <tags>
        if nested_parentheses < 1:
            if c == '<':
                nesting_level += 1
            if c == '>':
                nesting_level -= 1

        # When outside of <tags>
        if nesting_level < 1:
            if c == '(':
                nested_parentheses += 1
            if nested_parentheses > 0:
                result += ' '
            else:
                result += c
            if c == ')':
                nested_parentheses -= 1

        # When inside of <tags>
        else:
            result += c

    return result

# Used to store pages that have been visited in order to detect loops
# Deleted every time trace() exits (regardless of how)
visited = []

def trace(page=None, end='Philosophy', whole_page=False, infinite=False):
    """
    Visit the first non-italicized, not-within-parentheses
        link of page recursively until the page end
        (default: 'Philosophy') is reached.

    Args:
        page: The Wikipedia page name to page with (default: a random page)

        end: The Wikipedia page name to end at (default: 'Philosophy')

        whole_page: Parse the whole parse rather than just
        the lead section (default: False)

        infinite: Only stop execution when either a loop is encountered
        or no valid link could be found

    Returns:
        A generator with the page names generated in sequence
        in real time (including page and end).

    Raises:
        MediaWikiError: if MediaWiki API responds with an error

        ConnectionError: if cannot initiate request

        LoopException: if a loop is detected

        InvalidPageNameError: if invalid page name is passed as argument

        LinkNotFoundError: if a valid link cannot be found for page
    """
    BASE_URL = 'https://en.wikipedia.org/w/api.php'
    HEADERS = { 'User-Agent': 'The Philosophy Game/0.1',
                'Accept-Encoding': 'gzip' }
    if page is None:
        params = {
            'action': 'query',
            'list': 'random',
            'rnlimit': 1,
            'rnnamespace': 0,
            'format': 'json'
        }
        result = requests.get(BASE_URL, params=params, headers=HEADERS).json()
        if 'error' in result:
            del visited[:]
            raise MediaWikiError('MediaWiki error', result['error'])

        page = result['query']['random'][0]['title']

    if not valid_page_name(page):
        del visited[:]
        raise InvalidPageNameError("Invalid page name '{0}'".format(page))

    params = {
        'action': 'parse',
        'page': page,
        'prop': 'text',
        'format': 'json',
        'redirects': 1
    }

    if not whole_page:
        params['section'] = 0

    result = requests.get(BASE_URL, params=params, headers=HEADERS).json()

    if 'error' in result:
        del visited[:]
        raise MediaWikiError('MediaWiki error', result['error'])

    page = result['parse']['title']

    # Detect loop
    if page in visited:
        del visited[:]
        raise LoopException('Loop detected')

    # Don't yield if whole page requested
    # (which should only be done as a second attempt)
    if not whole_page:
        yield page

    # This needs to be done AFTER yield title
    # (The only) normal termination
    if not infinite and page == end:
        del visited[:]
        return

    raw_html = result['parse']['text']['*']
    html = lh.fromstring(raw_html)

    # This takes care of most MediaWiki templates,
    # images, red links, hatnotes, italicized text
    # and anything that's strictly not text-only
    for elm in html.cssselect('.reference,span,div,.thumb,'
                            'table,a.new,i,#coordinates'):
        elm.drop_tree()

    html = lh.fromstring(strip_parentheses(lh.tostring(html).decode('utf-8')))
    link_found = False
    for elm, attr, link, pos in html.iterlinks():
        # Because .iterlinks() picks up 'src' and the like too
        if attr != 'href':
            continue
        next_page = link

        if not next_page.startswith('/wiki/'):
            continue

        next_page = next_page[len('/wiki/'):]
        next_page = urllib.parse.unquote(next_page)

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

        link_found = True
        visited.append(page)

        for m in trace(page=next_page, end=end):
            yield m

        break

    if not link_found:
        if whole_page:
            del visited[:]
            raise LinkNotFoundError(
                'No valid link found in page "{0}"'.format(page)
            )
        else:
            for m in trace(page=page, whole_page=True, end=end):
                yield m
