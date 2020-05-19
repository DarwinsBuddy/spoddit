import argparse
import logging
import sys
from functools import partial
from logging.config import fileConfig

import spoddit
from spoddit import config
from spoddit.config import parse_args, dry_handle


def main(argv=None):

    # parse args
    args = parse_args(argv)

    # TODO maybe there is a way to make this publicly available after arg parse
    dry = partial(dry_handle, (args.dry_run or False))

    fileConfig('log.conf')
    logger = logging.getLogger()

    if args.dry_run:
        logger.info('Running in dry-run mode')
    logger.debug(args)

    # connect to spotify and reddit
    session = spoddit.SpodditSession()

    for subreddit, subreddit_config in config.scraper_map.items():
        logger.info(f'Scraping reddit for {subreddit}')
        links = session.reddit_session.get_links(subreddit, limit=subreddit_config['limit'])
        for key, values in links.items():
            logger.info(f'Found {len(values)} {key} links')
        logger.info('Creating playlist')
        playlist = dry(session.spotify_session.create_playlist, **subreddit_config)
        if playlist is not None or args.dry_run:
            # logger.debug('Querying for youtube track details...')
            logger.warning('[TBD] YOUTUBE Support: Not yet implemented')
            spotify_tracks = links['spotify']
            # logger.debug('Filtering already imported spotify tracks...')
            # logger.debug('Adding spotify tracks...')

    return 0


if __name__ == '__main__':
    sys.exit(main())
