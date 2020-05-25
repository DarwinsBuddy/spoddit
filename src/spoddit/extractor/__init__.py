import logging
from functools import partial

import pafy

from spoddit import TrackRecipe

logger = logging.getLogger(__name__)


def get_youtube_metadata(links):
    """
    Given a list of youtube links a list of track_dicts is returned, with
    keys set as 'track', 'title', 'artist'
    :param links:
    :return:
    """
    if type(links) == list:
        extraction_result = []
        for pos, link in enumerate(links, start=1):
            logger.debug(f'Extracting metadata of youtube link {pos}/{len(links)} ...')
            result = get_youtube_metadata(link)
            if result is not None:
                extraction_result += [result]
        logger.debug(f'Finished extracting metadata of {len(links)} youtube links')
        return extraction_result
    elif type(links) == str:
        link = links
        try:
            metadata = pafy.new(link)
            return TrackRecipe.from_title(metadata.title)
        except (OSError, Exception) as e:
            logger.warning(f'Error while scraping youtube metadata from {link}')
            logger.warning(e)
            return None
    else:
        logger.warning(f'Function called with unsupported type {type(links)}')
        return None


def _not_yet_implemented(key, links):
    logger.warning(f'{key} support not yet implemented.')
    return []


extractor_map = {
    'youtube': get_youtube_metadata,
    'spotify': partial(_not_yet_implemented, key='spotify')
}


def extract_track_recipes(links_dict):
    """
    Given a links_dict (provided by RedditSession.get_links)
    it extracts from it a list of TrackRecipes by calling several APIs.
    Currently supported: youtube
    Currently not supported: spotify
    :param links_dict:
    :return: list of TrackRecipes
    """
    result = []
    for key in links_dict.keys():
        logger.info(f'Trying to extract tracks from {len(links_dict[key])} {key} links')
        result += extractor_map[key](links=links_dict[key])
    return result
