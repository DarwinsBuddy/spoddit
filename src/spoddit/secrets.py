from configparser import ConfigParser
import logging
from logging.config import fileConfig
from pathlib import Path

fileConfig('log.conf')
logger = logging.getLogger(__name__)

_SECRETS_PATH = '.secrets.conf'

_secrets = None
logger.debug(f'<<<<<<<< {_SECRETS_PATH} >>>>>>>>')

# config file location passed by arguments
if Path(_SECRETS_PATH).is_file():
    _secrets = ConfigParser()
    _secrets.read([_SECRETS_PATH])
    logger.debug(dict(_secrets.items())) if _secrets is not None else logger.debug('No config provided')

if _secrets is None:
    logger.error(f'{_SECRETS_PATH} not found')
    exit(4)


# delegate everything else to _config
def __getattr__(name):
    return getattr(_secrets, name)
