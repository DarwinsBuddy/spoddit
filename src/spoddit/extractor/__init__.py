import logging
from collections import defaultdict

import pafy
import re

logger = logging.getLogger(__name__)

# regex to get rid of those [Official something] tags
_CLEANUP_REGEXES = [
    re.compile(r'(?P<part1>.*)(\[.*Official.*\])(?P<part2>.*)'),
    re.compile(r'(?P<part1>.*)(\(.*\))(?P<part2>.*)'),
]

_YOUTUBE_REGEXES = [
    # regex to match artist and title (most common form)
    r'(?P<artist>.+)\s+[^\s\w]{1}\s+(?P<title>.*)',
    # regex to match the whole string, if above form(s) are not applicable
    r'(?P<track>.+)'
]

_COMBINED_REGEX = re.compile(r'|'.join(_YOUTUBE_REGEXES))


def _cleanup_title(title):
    cleaned_text = title
    for regex in _CLEANUP_REGEXES:
        cleanup_matches = regex.search(title)
        if cleanup_matches is not None:
            cleaned_text = cleanup_matches['part1'] + cleanup_matches['part2']
        else:
            cleaned_text = title
    return cleaned_text

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
            logger.debug(f'Extracting metadata of link {pos}/{len(links)} ...')
            extraction_result += [get_youtube_metadata(link)]
        logger.debug(f'Finished extracting metadata of {len(links)} links')
        return extraction_result
    elif type(links) == str:
        link = links
        try:
            metadata = pafy.new(link)
            title = _cleanup_title(metadata.title)
            logger.debug(f'Cleaned title: {title}')
            matches = _COMBINED_REGEX.search(title)
            return defaultdict(None, matches.groupdict())
        except (OSError, Exception) as e:
            logger.warning(f'Error while scraping youtube metadata from {link}')
            logger.warning(e)
            return None
    else:
        logger.warning(f'Function called with unsupported type {type(links)}')
        return None
