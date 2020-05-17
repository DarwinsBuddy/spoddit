from configparser import ConfigParser
import logging
from logging.config import fileConfig
from pathlib import Path

fileConfig('log.conf')
logger = logging.getLogger(__name__)

_CONFIG_PATH = 'spoddit.conf'

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


# delegate everything else to _config
def __getattr__(name):
    return getattr(_config, name)
