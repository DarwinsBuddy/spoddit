import re
from configparser import ConfigParser
import logging
from logging.config import fileConfig
from pathlib import Path

fileConfig('log.conf')
logger = logging.getLogger(__name__)

_CONFIG_PATH = 'spoddit.conf'
_DEFAULT_SUBREDDIT_LIMIT = 50
_SUBREDDIT_REGEX = r'r\/(.*)'

defaults = {
    'General': {
        'port': 1337
    },
    'Spotify': {
        'username': None
    }
}

_config = None
logger.debug(f'<<<<<<< {_CONFIG_PATH} >>>>>>>')
# config file location passed by arguments
if Path(_CONFIG_PATH).is_file():
    _config = ConfigParser()
    _config.read([_CONFIG_PATH])
    defaults.update(dict(_config.items()))
    logger.debug(dict(_config.items())) if _config is not None else logger.debug('No config provided')

if _config is not None:
    logger.debug('CONFIG:')
    for section in _config.sections():

        logger.debug(f'{section}')
        for (key, value) in _config.items(section):
            logger.debug(f'  {key} = {value}')
else:
    logger.warning(f'config "{_CONFIG_PATH}" not found')

scraper_map = dict()
# parse subreddit/playlist mappings
for section in _config.sections():
    if section.startswith('r/'):
        if _config.has_option(section, 'playlist'):
            # get raw name of subreddit
            match = re.match(_SUBREDDIT_REGEX, section)
            if match is not None:
                subreddit = list(match.groups()).pop()

                scraper_map[subreddit] = {
                    'playlist': _config.get(section, 'playlist'),
                    'limit': _DEFAULT_SUBREDDIT_LIMIT
                }
                logger.debug(f'Mapping found - Subreddit:{section} Playlist:{scraper_map[subreddit]["playlist"]}')
            else:
                logger.error(f'Congratulations. You spotted a thought to be impossible error.')
                logger.error(f'{section} both starts with "r/" and does not match regex "{_SUBREDDIT_REGEX}')
                logger.error(f'Contact the maintainer of this package on github and get yourself a pat on the back')
        else:
            logger.warning(f'Section {section} missing option "playlist". Skipping.')


# delegate everything else to _config
def __getattr__(name):
    return getattr(_config, name)
