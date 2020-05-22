import logging
from collections import defaultdict

import pafy
import re

logger = logging.getLogger(__name__)

_YOUTUBE_REGEXES = [
    # regex to match artist and title (most common form)
    r'(?P<artist>.+)\s+.{1}\s+(?P<title>.*)',
    # regex to match the whole string, if above form(s) are not applicable
    r'(?P<track>.+)'
]

_COMBINED_REGEX = re.compile(r'|'.join(_YOUTUBE_REGEXES))


def extract(links):

    if type(links) == list:
        extraction_result = []
        for pos, link in enumerate(links, start=1):
            logger.debug(f'Extracting metadata of link {pos}/{len(links)} ...')
            extraction_result += [extract(link)]
        logger.debug(f'Finished extracting metadata of {len(links)} links')
        return extraction_result
    elif type(links) == str:
        link = links
        try:
            metadata = pafy.new(link)
            matches = _COMBINED_REGEX.search(metadata.title)
            return defaultdict(None, matches.groupdict())
        except (OSError, Exception) as e:
            logger.warning(f'Error while scraping youtube metadata from {link}')
            logger.warning(e)
            return None
    else:
        logger.warning(f'Function called with unsupported type {type(links)}')
        return None
