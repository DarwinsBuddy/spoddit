import logging

from . import util
from .reddit import RedditSession
from .spotify import SpotifySession

_DEFAULT_CONFIG_PATH = './spoddit.conf'

logger = logging.getLogger(__name__)


class SpodditSession:

    def __init__(self, config_path=None):
        self.config_path = config_path or _DEFAULT_CONFIG_PATH
        defaults = {
            'spotify': {
                'username': ''
            },
            'general': {
                'port': 1236
            }
        }
        config = util.parse_config(self.config_path, defaults)

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
        if self.reddit_session.is_logged_in():
            logger.debug(f'Successfully authenticated at Reddit')
        else:
            logger.error(f'Failed to authenticate at Reddit')
            exit(2)

