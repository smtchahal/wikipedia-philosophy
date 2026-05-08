from unittest.mock import patch, MagicMock, PropertyMock

import pytest

import philosophy
from philosophy import valid_page_name, strip_parentheses, trace
from philosophy.exceptions import (
    InvalidPageNameError,
    LinkNotFoundError,
    LoopException,
    MediaWikiError,
)


# ── helpers ──────────────────────────────────────────────────────────────────

def _resp(data):
    m = MagicMock()
    m.json.return_value = data
    return m


def _empty_resp(status_code=503):
    m = MagicMock()
    m.status_code = status_code
    m.json.side_effect = ValueError('No JSON object could be decoded')
    return m


def _parse(title, html):
    return _resp({'parse': {'title': title, 'text': {'*': html}}})


def _error(code='missingtitle', info='The page you specified does not exist'):
    return _resp({'error': {'code': code, 'info': info}})


def _random(title):
    return _resp({'query': {'random': [{'title': title}]}})


LINK_TO_PHILOSOPHY = '<div><p><a href="/wiki/Philosophy">Philosophy</a></p></div>'
LINK_TO_A = '<div><p><a href="/wiki/A_page">A page</a></p></div>'
LINK_TO_B = '<div><p><a href="/wiki/B_page">B page</a></p></div>'
NO_WIKI_LINKS = '<div><p>No valid links here at all.</p></div>'


@pytest.fixture(autouse=True)
def clear_visited():
    philosophy.visited.clear()
    yield
    philosophy.visited.clear()


# ── valid_page_name ───────────────────────────────────────────────────────────

class TestValidPageName:
    NON_MAINSPACE = [
        'File:', 'File talk:', 'Wikipedia:', 'Wikipedia talk:',
        'Project:', 'Project talk:', 'Portal:', 'Portal talk:',
        'Special:', 'Help:', 'Help talk:', 'Template:', 'Template talk:',
        'Talk:', 'Category:', 'Category talk:',
    ]

    def test_rejects_non_mainspace(self):
        assert all(not valid_page_name(p) for p in self.NON_MAINSPACE)

    def test_accepts_regular_pages(self):
        for page in ['Sandwich', 'Philosophy', 'Python (programming language)']:
            assert valid_page_name(page)


# ── strip_parentheses ─────────────────────────────────────────────────────────

class TestStripParentheses:
    CASES = {
        'Hello (world)!': 'Hello !',
        'The <a href="https://en.wikipedia.org/wiki/Encyclopedia_(disambiguation)">encyclopedia</a> looks pretty (((good))).':
            'The <a href="https://en.wikipedia.org/wiki/Encyclopedia_(disambiguation)">encyclopedia</a> looks pretty .',
        '< (hello)': None,
        '< (goodbye) >': None,
        '(hello) there': ' there',
        '(sometimes) <(things) get> <complicated (do they?)':
            ' <(things) get> <complicated (do they?)',
        '(an entire string contained within parentheses)': '',
        "This isn't (my)) fault, okay?": "This isn't ) fault, okay?",
        'There ((you are), my friend.': 'There ',
        'You can (ignore all of this. Even this, (and this.) All of it.':
            'You can ',
        '<a b(rules are for everyone)': None,
        "<a <b (doesn't matter <who you are>> everyone has to follow rules)": None,
        '<a<coach goes (over there)> (and)> (he seems to <find>) <(nothing)':
            '<a<coach goes (over there)> (and)>  <(nothing)',
    }

    @pytest.mark.parametrize('s,expected', [
        (k, k if v is None else v) for k, v in CASES.items()
    ])
    def test_cases(self, s, expected):
        assert strip_parentheses(s) == expected

    def test_empty_string(self):
        assert strip_parentheses('') == ''

    def test_no_parens(self):
        assert strip_parentheses('plain text') == 'plain text'


# ── trace() ───────────────────────────────────────────────────────────────────

class TestTrace:
    def test_invalid_page_name_raises(self):
        with pytest.raises(InvalidPageNameError):
            list(trace(page='Wikipedia:About'))

    def test_all_non_mainspace_raise(self):
        for prefix in ['File:', 'Category:', 'Special:', 'Help:', 'Talk:']:
            philosophy.visited.clear()
            with pytest.raises(InvalidPageNameError):
                list(trace(page=prefix + 'Something'))

    @patch('philosophy.requests.get')
    def test_api_error_raises_media_wiki_error(self, mock_get):
        mock_get.return_value = _error('missingtitle', 'Page not found')
        with pytest.raises(MediaWikiError) as exc_info:
            list(trace(page='Nonexistent Page'))
        assert exc_info.value.errors['code'] == 'missingtitle'

    @patch('philosophy.requests.get')
    def test_reaches_end(self, mock_get):
        mock_get.side_effect = [
            _parse('Sandwich', LINK_TO_PHILOSOPHY),
            _parse('Philosophy', NO_WIKI_LINKS),
        ]
        result = list(trace(page='Sandwich'))
        assert result == ['Sandwich', 'Philosophy']

    @patch('philosophy.requests.get')
    def test_chain_of_three(self, mock_get):
        mid_html = '<div><p><a href="/wiki/Sandwich">Sandwich</a></p></div>'
        mock_get.side_effect = [
            _parse('Python', mid_html),
            _parse('Sandwich', LINK_TO_PHILOSOPHY),
            _parse('Philosophy', NO_WIKI_LINKS),
        ]
        result = list(trace(page='Python'))
        assert result == ['Python', 'Sandwich', 'Philosophy']

    @patch('philosophy.requests.get')
    def test_loop_raises_loop_exception(self, mock_get):
        # A → B → A (loop)
        mock_get.side_effect = [
            _parse('A page', LINK_TO_B),
            _parse('B page', LINK_TO_A),
            _parse('A page', LINK_TO_B),  # fetched before loop detected via title
        ]
        with pytest.raises(LoopException):
            list(trace(page='A page', end='Z page'))

    @patch('philosophy.requests.get')
    def test_loop_yields_repeated_page_before_raising(self, mock_get):
        mock_get.side_effect = [
            _parse('A page', LINK_TO_B),
            _parse('B page', LINK_TO_A),
            _parse('A page', LINK_TO_B),
        ]
        pages = []
        with pytest.raises(LoopException):
            for p in trace(page='A page', end='Z page'):
                pages.append(p)
        # The looped page is yielded once more before the exception
        assert pages.count('A page') == 2
        assert 'B page' in pages

    @patch('philosophy.requests.get')
    def test_link_not_found_raises(self, mock_get):
        # section=0 has no links → retries with whole_page=True → still no links
        mock_get.side_effect = [
            _parse('Empty Page', NO_WIKI_LINKS),
            _parse('Empty Page', NO_WIKI_LINKS),
        ]
        with pytest.raises(LinkNotFoundError):
            list(trace(page='Empty Page'))

    @patch('philosophy.requests.get')
    def test_link_found_in_whole_page_fallback(self, mock_get):
        # section=0 has no links; whole_page retry finds a link and terminates.
        # Because whole_page=True propagates to the recursive call, the
        # destination page skips its own yield — only the starting page appears.
        mock_get.side_effect = [
            _parse('Sparse Page', NO_WIKI_LINKS),
            _parse('Sparse Page', LINK_TO_PHILOSOPHY),  # whole_page retry
            _parse('Philosophy', NO_WIKI_LINKS),
        ]
        result = list(trace(page='Sparse Page'))
        assert result == ['Sparse Page']

    @patch('philosophy.requests.get')
    def test_random_page_when_none(self, mock_get):
        mock_get.side_effect = [
            _random('Random Article'),
            _parse('Random Article', LINK_TO_PHILOSOPHY),
            _parse('Philosophy', NO_WIKI_LINKS),
        ]
        result = list(trace())
        assert result[0] == 'Random Article'
        assert result[-1] == 'Philosophy'

    @patch('philosophy.requests.get')
    def test_random_page_api_error_raises(self, mock_get):
        mock_get.return_value = _error('unknown', 'Unknown error')
        with pytest.raises(MediaWikiError):
            list(trace())

    @patch('philosophy.requests.get')
    def test_custom_end(self, mock_get):
        mid_html = '<div><p><a href="/wiki/Multicellular_organism">Multicellular organism</a></p></div>'
        mock_get.side_effect = [
            _parse('Sandwich', mid_html),
            _parse('Multicellular organism', NO_WIKI_LINKS),
        ]
        result = list(trace(page='Sandwich', end='Multicellular organism'))
        assert result[-1] == 'Multicellular organism'

    @patch('philosophy.requests.get')
    def test_infinite_mode_does_not_stop_at_end(self, mock_get):
        # A → Philosophy → A → loop
        phi_html = '<div><p><a href="/wiki/A_page">A page</a></p></div>'
        mock_get.side_effect = [
            _parse('A page', LINK_TO_PHILOSOPHY),
            _parse('Philosophy', phi_html),
            _parse('A page', LINK_TO_PHILOSOPHY),  # fetched before loop check
        ]
        pages = []
        with pytest.raises(LoopException):
            for p in trace(page='A page', infinite=True):
                pages.append(p)
        assert 'Philosophy' in pages

    @patch('philosophy.requests.get')
    def test_external_links_ignored(self, mock_get):
        external_html = (
            '<div>'
            '<p><a href="https://example.com">External</a></p>'
            '<p><a href="/wiki/Philosophy">Philosophy</a></p>'
            '</div>'
        )
        mock_get.side_effect = [
            _parse('Start Page', external_html),
            _parse('Philosophy', NO_WIKI_LINKS),
        ]
        result = list(trace(page='Start Page'))
        assert result == ['Start Page', 'Philosophy']

    @patch('philosophy.requests.get')
    def test_non_mainspace_links_skipped(self, mock_get):
        # First valid link is a Category: link (skipped), second is Philosophy
        mixed_html = (
            '<div>'
            '<p><a href="/wiki/Category:Science">Category</a></p>'
            '<p><a href="/wiki/Philosophy">Philosophy</a></p>'
            '</div>'
        )
        mock_get.side_effect = [
            _parse('Start Page', mixed_html),
            _parse('Philosophy', NO_WIKI_LINKS),
        ]
        result = list(trace(page='Start Page'))
        assert result == ['Start Page', 'Philosophy']

    @patch('philosophy.requests.get')
    def test_parenthesized_links_stripped(self, mock_get):
        # The only link is inside parentheses and should be stripped,
        # so trace falls back to whole_page, which has a real link
        paren_html = (
            '<div>'
            '<p>See (<a href="/wiki/Disambiguation">disambiguation</a>)</p>'
            '</div>'
        )
        real_html = (
            '<div>'
            '<p>See (<a href="/wiki/Disambiguation">disambiguation</a>)</p>'
            '<p><a href="/wiki/Philosophy">Philosophy</a></p>'
            '</div>'
        )
        mock_get.side_effect = [
            _parse('Paren Page', paren_html),
            _parse('Paren Page', real_html),  # whole_page retry
            _parse('Philosophy', NO_WIKI_LINKS),
        ]
        # whole_page=True propagates to the recursive call, so Philosophy
        # is reached but not yielded — only 'Paren Page' appears.
        result = list(trace(page='Paren Page'))
        assert result == ['Paren Page']

    @patch('philosophy.requests.get')
    def test_non_href_src_attribute_skipped(self, mock_get):
        # iterlinks() also yields img src= attributes; those must be skipped
        # (line 240: `if attr != 'href': continue`)
        html_with_img = (
            '<p>'
            '<img src="/wiki/some_image.png">'
            '<a href="/wiki/Philosophy">Philosophy</a>'
            '</p>'
        )
        mock_get.side_effect = [
            _parse('Start Page', html_with_img),
            _parse('Philosophy', NO_WIKI_LINKS),
        ]
        result = list(trace(page='Start Page'))
        assert result == ['Start Page', 'Philosophy']

    @patch('philosophy.requests.get')
    def test_inline_style_with_css_child_combinator(self, mock_get):
        # Wikipedia inlines <style> tags whose CSS uses the child combinator (>).
        # strip_parentheses tracks nesting_level via '<' and '>', so a bare '>'
        # in CSS content drives nesting_level negative and corrupts subsequent
        # HTML, causing all links to vanish.  The fix: drop <style>/<script>
        # elements before serialising so they never reach strip_parentheses.
        html_with_style = (
            '<div>'
            '<style>.mw-parser-output .hlist ol>li{counter-increment:x}'
            '.sidebar a>img{max-width:none}</style>'
            '<p><a href="/wiki/Philosophy">Philosophy</a></p>'
            '</div>'
        )
        mock_get.side_effect = [
            _parse('Cricket', html_with_style),
            _parse('Philosophy', NO_WIKI_LINKS),
        ]
        result = list(trace(page='Cricket'))
        assert result == ['Cricket', 'Philosophy']

    @patch('philosophy.requests.get')
    def test_named_anchor_stripped_from_link(self, mock_get):
        # /wiki/Page#Section → 'Page' after anchor is removed
        # (line 260: `next_page = next_page[:pos]`)
        anchor_html = '<p><a href="/wiki/Philosophy#History">Philosophy</a></p>'
        mock_get.side_effect = [
            _parse('Start Page', anchor_html),
            _parse('Philosophy', NO_WIKI_LINKS),
        ]
        result = list(trace(page='Start Page'))
        assert result == ['Start Page', 'Philosophy']

    @patch('philosophy.requests.get')
    def test_empty_response_raises_connection_error(self, mock_get):
        mock_get.return_value = _empty_resp(503)
        from requests.exceptions import ConnectionError as ReqConnError
        with pytest.raises(ReqConnError):
            list(trace(page='Some Page'))

    @patch('philosophy.requests.get')
    def test_empty_response_on_random_page_raises_connection_error(self, mock_get):
        mock_get.return_value = _empty_resp(429)
        from requests.exceptions import ConnectionError as ReqConnError
        with pytest.raises(ReqConnError):
            list(trace())

    @patch('philosophy.requests.get')
    def test_whole_page_retry_propagates_loop(self, mock_get):
        # section=0 has no links → whole_page retry; the retry chain loops
        # back to A, which is in visited.  The loop's `yield page` propagates
        # back through the retry's `for m in ...: yield m` (line 280).
        mock_get.side_effect = [
            _parse('A page', NO_WIKI_LINKS),  # section=0, no links
            _parse('A page', LINK_TO_B),       # whole_page retry
            _parse('B page', LINK_TO_A),       # whole_page (propagated)
            _parse('A page', LINK_TO_B),       # fetched before loop check
        ]
        pages = []
        with pytest.raises(LoopException):
            for p in trace(page='A page', end='Z page'):
                pages.append(p)
        # 'A page' yielded on first visit (line 217) and again via loop
        # detection propagated through line 280
        assert pages.count('A page') == 2
