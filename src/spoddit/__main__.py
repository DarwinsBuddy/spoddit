import argparse
import logging
import sys
from functools import partial
from logging.config import fileConfig

from IPython.lib import pretty

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
            tracks = []
            # TODO extract info from reddit alone ? (r/Music has pretty titles, but maybe make this configurable,
            #      as this may not be always the case)
            logger.debug('Looking up youtube track details...')
            yt_tracks = [
                spoddit.TrackRecipe.from_track_dict(td) for td in
                list(filter(None, extractor.get_youtube_metadata(links['youtube'])))
            ]
            logger.debug('Found following youtube tracks:')
            for t in yt_tracks:
                logger.debug(f'>>> {t}')
            # look up spotify track ID for yt tracks w/ spotify search
            tracks += session.spotify_session.search_tracks(yt_tracks)
            # spotify_tracks = links['spotify']
            # TODO extract spotify track ID from spotify track links
            if args.dry_run:
                logger.debug('[DRY] Skipping adding tracks to playlist')
            else:
                logger.debug('Filtering already imported tracks...')
                # build a distinct set of all track IDs and filter out all already imported tracks
                playlist_tracks = [t['track'] for t in session.spotify_session.get_playlist_tracks(playlist['id'])]
                new_tracks = session.spotify_session.diff_track_list(playlist_tracks, tracks)
                logger.debug(f'Found {len(new_tracks)}/{len(tracks)} new tracks')
                if len(tracks) > 0:
                    # add other tracks to spotify playlist
                    logger.debug('Adding spotify tracks...')
                    session.spotify_session.add_to_playlist(playlist['id'], new_tracks)
                else:
                    logger.debug('Nothing to add')
    return 0


if __name__ == '__main__':
    sys.exit(main())
