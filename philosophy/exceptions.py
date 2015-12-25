from requests.exceptions import ConnectionError

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
