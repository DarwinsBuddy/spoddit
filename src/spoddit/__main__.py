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
        logger.info('Creating playlist')
        playlist = dry(session.spotify_session.create_playlist, **subreddit_config)
        if playlist is not None or args.dry_run:
            logger.info(f'Scraping reddit for {subreddit}')
            # TODO: extend this to a throttled, paged version for huge limit calls
            subs = list(session.reddit_session.subreddit(subreddit).hot(limit=subreddit_config['limit']))
            # EXTRACT track recipes from reddit titles
            logger.debug('TITLE lookup')
            for s in subs:
                logger.debug(f' ++ {s.title}')
            title_extracted_tracks = [spoddit.TrackRecipe.from_title(sub.title) for sub in subs]
            logger.debug(f'Found {len(title_extracted_tracks)}')
            # EXTRACT track recipes from reddit links
            logger.debug('LINKS lookup')
            _links = session.reddit_session.get_links(subs)
            links_extracted_tracks = extractor.extract_track_recipes(_links)
            logger.debug(f'Found {len(links_extracted_tracks)}')

            for tt in links_extracted_tracks + title_extracted_tracks:
                logger.debug(f' +++ {tt} +++')
            # look up spotify track ID for yt tracks w/ spotify search
            tracks = session.spotify_session.search_tracks(
                links_extracted_tracks + title_extracted_tracks
            )
            # spotify_tracks = links['spotify']
            # TODO extract spotify track ID from spotify track links
            if args.dry_run:
                logger.debug('[DRY] Skipping adding tracks to playlist')
            else:
                logger.debug('Filtering already imported tracks')
                # build a distinct set of all track IDs and filter out all already imported tracks
                playlist_tracks = [t['track'] for t in session.spotify_session.get_playlist_tracks(playlist['id'])]
                new_tracks = session.spotify_session.diff_track_list(playlist_tracks, tracks)
                logger.debug(f'{len(new_tracks)}/{len(tracks)} new tracks')
                if len(new_tracks) > 0:
                    # add other tracks to spotify playlist
                    logger.debug('Adding tracks to spotify playlist')
                    session.spotify_session.add_to_playlist(playlist['id'], new_tracks)
                else:
                    logger.debug('Nothing to add')
    return 0


if __name__ == '__main__':
    sys.exit(main())
