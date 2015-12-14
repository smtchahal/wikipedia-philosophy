"""
This script plays Wikipedia's philosophy game
(http://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy)
for you.

Note that this script simply skips
non-existent pages ("red links"),
rather than warning about them
"""

import requests
from requests.exceptions import ConnectionError
import lxml.html as lh
import json

class MediaWikiError(Exception):
    def __init__(self, message, errors):
        super(MediaWikiError, self).__init__(message)
        self.errors = errors

class LoopException(Exception):
    pass

class PhilosophyGame():
    def __init__(self):
        self.link_count = 0
        self.visited = []

    @staticmethod
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


    def trace(self, page):
        """Visit the first non-italicized, not-within-parentheses
            link of page recursively until the page 'Philosophy'
            is reached.

        Args:
            page: The Wikipedia page name to visit.
        Raises:
            MediaWikiError: if MediaWiki API responds with an error
            requests.exceptions.ConnectionError: if cannot initiate request
            LoopException: if a loop is detected

        """
            
        if page == 'Philosophy':
            return
        url = 'https://en.wikipedia.org/w/api.php'
        payload = dict(action='parse', page=page, prop='text', 
                    section=0, format='json', redirects=1)

        response = requests.get(url, params=payload)
        res_json = json.loads(response.content)

        if 'error' in res_json:
            raise MediaWikiError('MediaWiki error',
                {'code': res_json['error']['code'],
                'info': res_json['error']['info']})

        raw_html = res_json['parse']['text']['*'].encode('utf-8')
        html = lh.fromstring(PhilosophyGame.strip_parentheses(raw_html))

        # This takes care of most MediaWiki templates,
        # images, red links, hatnotes, italicized text 
        # and anything that's strictly not text-only
        for elm in html.cssselect('.reference,div[class],table,a.new,i,#coordinates'):
            elm.drop_tree()

        for elm, attr, link, pos in html.iterlinks():
            # Because .iterlinks() picks up 'src' links too
            if attr != 'href':
                continue
            next_page = link

            # Must be a valid internal wikilink
            if next_page[:len('/wiki/')] != '/wiki/':
                continue

            # Extract the Wikipedia page name
            next_page = next_page[len('/wiki/'):]

            # Eliminates pages outside of mainspace
            if next_page.find(':') != -1:
                continue

            # Eliminate named anchor, if any
            pos = next_page.find('#')
            if pos != -1:
                next_page = next_page[:pos]

            # Links use an underscore ('_')
            # instead of a space (' '), this
            # fixes that
            next_page = next_page.replace('_', ' ')

            # Detect loop
            if next_page in self.visited:
                raise LoopException('Loop detected')

            self.link_count += 1
            self.visited.append(page)

            # Recursively yield
            yield next_page
            for m in self.trace(next_page):
                yield m
            break
