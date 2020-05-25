import logging
import re
from collections import defaultdict

from . import util, config
from .reddit import RedditSession
from .spotify import SpotifySession

_TRACK_REGEXPS = [
    # regex to match artist and title (most common form)
    r'(?P<artist>.+)\s+[^\s\w]{1}\s+(?P<title>.*)',
    # regex to match the whole string, if above form(s) are not applicable
    r'(?P<track>.+)'
]

_COMBINED_REGEX = re.compile(r'|'.join(_TRACK_REGEXPS))

# regex to get rid of those [Official something] tags
_CLEANUP_REGEXPS = [
    re.compile(r'(?P<part1>.*)(\[.*\])(?P<part2>.*)'),
    re.compile(r'(?P<part1>.*)(\(.*\))(?P<part2>.*)'),
]

_TRIM_REGEXP = re.compile(r'[^\w]*(?P<trimmed>[\w\s]*(\s+[^\w]{1}\s+)[\s\w]*)[^\w]*')

_DEFAULT_CONFIG_PATH = './spoddit.conf'
logger = logging.getLogger(__name__)


class TrackRecipe:

    @staticmethod
    def _cleanup_title(title):
        cleaned_text = title
        for regex in _CLEANUP_REGEXPS:
            cleanup_matches = regex.search(title)
            if cleanup_matches is not None:
                cleaned_text = cleanup_matches['part1'] + cleanup_matches['part2']
            else:
                cleaned_text = title
        trimmed_matches = _TRIM_REGEXP.search(cleaned_text)
        if trimmed_matches is not None:
            return trimmed_matches.groupdict()['trimmed']
        else:
            return cleaned_text

    @staticmethod
    def from_title(title):
        cleaned_title = TrackRecipe._cleanup_title(title)
        matches = _COMBINED_REGEX.search(cleaned_title)
        return TrackRecipe.from_track_dict(defaultdict(None, matches.groupdict()))

    @staticmethod
    def from_track_dict(track_dict):
        return TrackRecipe(
            artist=track_dict['artist'],
            title=track_dict['title'],
            track=track_dict['track']
        )

    def __init__(self, artist, title, track):
        self.artist = artist
        self.title = title
        self.track = track

    def __repr__(self):
        return f'track={self.track}, artist={self.artist}, title={self.title}'

    def get_query(self):
        """
        Extracts a query
        :return: query
        """
        if self.artist is not None and self.title is not None:
            return f'{self.artist} {self.title}'
        elif self.track is not None:
            return f'{self.track}'
        else:
            return None


class SpodditSession:

    def __init__(self):
        """
        A SpodditSession establishes a wrapped session to reddit (anonymous)
        and one to spotify (authenticated)
        """
        # Log into spotify
        username = config.get('Spotify', 'username')
        port = config.get('General', 'port')

        logger.info(f'Logging into Spotify as {username}')
        self.spotify_session = SpotifySession(username, port)
        if self.spotify_session.is_logged_in():
            logger.debug(f'Successfully logged in as {username}')
        else:
            logger.error(f'Failed to login in as {username}')
            exit(1)

        # Log into Reddit
        logger.info(f'Authenticating against Reddit')
        self.reddit_session = RedditSession()
        if self.reddit_session.is_authenticated():
            logger.debug(f'Successfully authenticated at Reddit')
        else:
            logger.error(f'Failed to authenticate at Reddit')
            exit(2)
