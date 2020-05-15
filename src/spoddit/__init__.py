import logging

from . import util
from .spotify import SpotifySession

_DEFAULT_CONFIG_PATH = './spoddit.conf'

logger = logging.getLogger(__name__)


def auth(config_path=None):
    defaults = {
        'spotify': {
            'username': ''
        },
        'general': {
            'port': 1236
        }
    }
    config = util.parse_config(config_path or _DEFAULT_CONFIG_PATH, defaults)

    username = config.get('Spotify', 'username')
    port = config.get('General', 'port')
    logger.info(f'Logging into Spotify as {username}')
    session = SpotifySession(username, port)
    if session.is_logged_in():
        logger.debug(f'Successfully logged in as {username}')
        return session
    else:
        logger.error(f'Failed to login in as {username}')
        exit(1)


