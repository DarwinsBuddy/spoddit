import argparse
import sys
from configparser import ConfigParser
import logging
from logging.config import fileConfig
from pathlib import Path

from spoddit.util.regexps import SUBREDDIT_REGEX


# TODO: Introduce a way to enable specific scraper functionality (title, youtube-link, spotify-link, etc.)
#       individually for every r/* section

def parse_args(argv):
    # TODO: Integrate arguments to overwrite specific options of our config
    # import config
    # Do argv default this way, as doing it in the functional
    # declaration sets it at compile time.
    if argv is None:
        argv = sys.argv

    # Parse any config specification
    # We make this parser with add_help=False so that
    # it doesn't parse -h and print help.
    arg_parser = argparse.ArgumentParser(
        description=__doc__,  # printed with -h/--help
        # Don't mess with format of description
        # formatter_class=argparse.RawDescriptionHelpFormatter,
        # Turn off help, so we print all options in response to -h
        add_help=False
    )
    args, remaining_argv = arg_parser.parse_known_args()
    # Parse rest of arguments
    # Don't suppress add_help here so it will handle -h
    parser = argparse.ArgumentParser(
        # Inherit options from config_parser
        # parents=[config_parser]
    )
    # parser.set_defaults(**defaults)
    parser.add_argument('-d', '--dry-run', dest='dry_run', action='store_true')
    args = parser.parse_args(remaining_argv)

    return args


fileConfig('log.conf')
logger = logging.getLogger(__name__)


def dry_handle(dry_run, function_handle, *args, **kwargs):
    if dry_run:
        logger.info(f'[DRY] Skipping {function_handle.__name__}')
        return None
    else:
        # filter out all non-expected keywords of the function_handle
        expected = {keyword: kwargs[keyword] for keyword in function_handle.__code__.co_varnames if keyword in kwargs}
        return function_handle(*args, **expected)


_CONFIG_PATH = 'spoddit.conf'
_DEFAULT_SUBREDDIT_LIMIT = 50

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
        if _config.has_option(section, 'playlist_name'):
            # get raw name of subreddit
            match = SUBREDDIT_REGEX.match(section)
            if match is not None:
                subreddit = list(match.groups()).pop()

                scraper_map[subreddit] = {
                    'playlist_name': _config.get(section, 'playlist_name'),
                    'limit': _config.getint(section, 'limit', fallback=_DEFAULT_SUBREDDIT_LIMIT),
                    'public': _config.getboolean(section, 'public', fallback=False),
                    'description': _config.get(section,
                                               'description',
                                               fallback=f'From subreddit {section} created by spoddit')
                }
                logger.debug(f'Mapping found - Subreddit:{section} Playlist:{scraper_map[subreddit]["playlist_name"]}')
            else:
                logger.error(f'Congratulations. You spotted a thought to be impossible error.')
                logger.error(f'{section} both starts with "r/" and does not match regex "{SUBREDDIT_REGEX}')
                logger.error(f'Contact the maintainer of this package on github and get yourself a pat on the back')
        else:
            logger.warning(f'Section {section} missing option "playlist_name". Skipping.')


# delegate everything else to _config
def __getattr__(name):
    return getattr(_config, name)
