import logging

import praw

from spoddit import secrets, util
from spoddit.util import merge_dict

logger = logging.getLogger(__name__)


class RedditSession:
    __SECRET_CONF = '.secret.conf'

    def __init__(self):
        logger.debug('Logging in...')
        if not secrets.has_section('Reddit'):
            logger.error(f'Malformed or missing .secrets.conf. Create one base on provided .secret-template.conf')
            exit(3)
        logger.info('Authenticating at Reddit')
        try:
            # noinspection PyTypeChecker
            self._api = praw.Reddit(client_id=secrets.get('Reddit', 'CLIENT_ID'),
                                    client_secret=None,
                                    user_agent="spoddit")
        except Exception as e:
            logging.error('Unable to authenticate at Reddit. Check the validity of your client secret')
            logging.error(f'{e}')
            self._api = None
            exit(5)

    def is_authenticated(self):
        """
        Checks if client is authenticated
        :return: true if we are authenticated, otherwise false
        """
        return self._api is not None

    @staticmethod
    def get_links(submissions):
        """
        Extracts links from submission provided by the reddit api
        :param submissions:
        :return: dict of link recognized by our regexps
        """
        link_dict = {}
        # this is way faster, than iterating over all regexps separately

        for sub in submissions:
            # we could use sub.url, but in case someone posted more than one url, we have to check the text
            # and sub.url just returns the link to the submissions first comment
            if sub.url.startswith(sub.shortlink):
                search_text = sub.selftext
            else:
                search_text = sub.url

            media_link_matches = util.regexps.COMBINED_MEDIA_LINK_REGEX.match(search_text)
            if media_link_matches is not None:
                link_dict = merge_dict(link_dict, media_link_matches.groupdict())

        # get rid of all None elements within our lists
        for key, value in link_dict.items():
            link_dict[key] = [v for v in value if v]
        return link_dict

    # delegate everything else to the api
    def __getattr__(self, name):
        return getattr(self._api, name)
