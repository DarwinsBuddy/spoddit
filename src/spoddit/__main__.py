import argparse
import logging
import sys
from functools import partial
from logging.config import fileConfig

import spoddit
from spoddit import config, extractor
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
            # TODO extract info from reddit alone ? (r/Music has pretty titles, but maybe make this configurable,
            #      as this may not be always the case)
            logger.debug('Looking up youtube track details...')
            yt_tracks = list(filter(None, extractor.extract(links['youtube'])))
            logger.debug('Found following youtube tracks:')
            for t in yt_tracks:
                logger.debug(f'{t["artist"]} - {t["title"]}') if t['track'] is None else logger.debug(f'{t["track"]}')
            # TODO look up spotify track ID for yt tracks w/ spotify search
            spotify_tracks = links['spotify']
            # TODO extract spotify track ID from spotify track links
            # TODO build a distinct set of all track IDs and filter out all already imported tracks
            # logger.debug('Filtering already imported tracks...')
            # TODO add other tracks to spotify playlist
            # logger.debug('Adding spotify tracks...')

    return 0


if __name__ == '__main__':
    sys.exit(main())
