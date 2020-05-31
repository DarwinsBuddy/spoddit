from configparser import ConfigParser
import logging
from logging.config import fileConfig
from pathlib import Path

fileConfig('config/log.conf')
logger = logging.getLogger(__name__)

_SECRETS_PATH = 'config/.secrets.conf'

_secrets = None
logger.debug(f'<<<<<<<< {_SECRETS_PATH} >>>>>>>>')

# config file location passed by arguments
if Path(_SECRETS_PATH).is_file():
    _secrets = ConfigParser()
    _secrets.read([_SECRETS_PATH])

if _secrets is None:
    logger.error(f'{_SECRETS_PATH} not found')
    exit(4)


# delegate everything else to _config
def __getattr__(name):
    return getattr(_secrets, name)
