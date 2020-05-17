import logging
import sys
from logging.config import fileConfig

import spoddit
from spoddit import config


def parse_args(argv):
    # TODO: Integrate arguments to overwrite specific options of our config
    # import config
    # # Do argv default this way, as doing it in the functional
    # # declaration sets it at compile time.
    # if argv is None:
    #     argv = sys.argv

    # # Parse any config specification
    # # We make this parser with add_help=False so that
    # # it doesn't parse -h and print help.
    # arg_parser = argparse.ArgumentParser(
    #    description=__doc__,  # printed with -h/--help
    #    # Don't mess with format of description
    #    # formatter_class=argparse.RawDescriptionHelpFormatter,
    #    # Turn off help, so we print all options in response to -h
    #    add_help=False
    # )
    # args, remaining_argv = arg_parser.parse_known_args()
    # # Parse rest of arguments
    # # Don't suppress add_help here so it will handle -h
    # parser = argparse.ArgumentParser(
    #    # Inherit options from config_parser
    #    parents=[config_parser]
    # )
    # parser.set_defaults(**defaults)
    # # parser.add_argument('--subreddit', metavar='r', type=str, nargs=1)
    # # parser.add_argument('--playlist', metavar='p', type=str, nargs='+')
    # args = parser.parse_args(remaining_argv)
    pass


def main(argv=None):

    # parse args
    parse_args(argv)

    # connect to spotify and reddit
    session = spoddit.SpodditSession()

    fileConfig('log.conf')
    logger = logging.getLogger()

    logger.info('Scraping reddit...')
    for subreddit, subreddit_config in config.scraper_map.items():
        logger.debug(session.reddit_session.get_links(subreddit, limit=subreddit_config['limit']))

    return 0


if __name__ == '__main__':
    sys.exit(main())
