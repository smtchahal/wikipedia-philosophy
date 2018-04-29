import os
import sys

from philosophy import (valid_page_name,
                        strip_parentheses)


def test_valid_page_name():
    NON_MAINSPACE = ['File:',
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
                     'Category talk:']
    assert all(not valid_page_name(non_main) for non_main in NON_MAINSPACE)


def test_strip_parentheses():
    test_cases = {
        'Hello (world)!': 'Hello !',
        'The <a href="https://en.wikipedia.org/wiki/Encyclopedia_(disambiguation)">encyclopedia</a> looks pretty (((good))).': 'The <a href="https://en.wikipedia.org/wiki/Encyclopedia_(disambiguation)">encyclopedia</a> looks pretty .',
        '< (hello)': None,
        '< (goodbye) >': None,
        '(hello) there': ' there',
        '(sometimes) <(things) get> <complicated (do they?)': ' <(things) get> <complicated (do they?)',
        '(an entire string contained within parentheses)': '',
        "This isn't (my)) fault, okay?": "This isn't ) fault, okay?",
        'There ((you are), my friend.': 'There ',
        'You can (ignore all of this. Even this, (and this.) All of it.': 'You can ',
        '<a b(rules are for everyone)': None,
        "<a <b (doesn't matter <who you are>> everyone has to follow rules)": None,
        '<a<coach goes (over there)> (and)> (he seems to <find>) <(nothing)': '<a<coach goes (over there)> (and)>  <(nothing)',
    }
    for param, expected_output in test_cases.items():
        if expected_output is None:
            expected_output = param
        assert strip_parentheses(param) == expected_output
