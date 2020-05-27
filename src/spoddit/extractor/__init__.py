import logging
from functools import partial

import pafy

from spoddit import TrackRecipe

logger = logging.getLogger(__name__)


def _extract_by_type(extract_handle, links):
    """
    Providing a list or a string, either iterates over provided list and calls
    the extract handle iteratively or calls the handle directly for provided string
    :param extract_handle:
    :param links: list of links or a single link
    :return:
    """
    if type(links) == list:
        extraction_result = []
        for pos, link in enumerate(links, start=1):
            logger.debug(f'Extracting metadata of {extract_handle.__name__} link {pos}/{len(links)} ...')
            result = extract_handle(link)
            if result is not None:
                extraction_result += [result]
        logger.debug(f'Finished extracting metadata of {len(links)} links')
        return extraction_result
    elif type(links) == str:
        link = links
        try:
            return extract_handle(link)
        except (OSError, Exception) as e:
            logger.warning(f'Error while scraping {extract_handle.__name__} metadata from {link}')
            logger.warning(e)
            return None
    else:
        logger.warning(f'Function called with unsupported type {type(links)}')
        return None


def spotify(link):
    """
    Given a spotify link returns a TrackRecipes
    :param link: spotify link
    :return:
    """
    return TrackRecipe.from_spotify_link(link)


def youtube(link):
    """
    Given a youtube link returns a TrackRecipes
    :param link:
    :return:
    """
    metadata = pafy.new(link)
    return TrackRecipe.from_title(metadata.title)


def _not_yet_implemented(links, key):
    logger.warning(f'{key} support not yet implemented.')
    return []


# TODO support deezer
extractor_map = {
    'youtube': partial(_extract_by_type, youtube),
    'spotify': partial(_extract_by_type, spotify),
    'deezer': partial(_not_yet_implemented, key='deezer')
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
