import logging

import praw

from spoddit import secrets

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
            self.api = praw.Reddit(client_id=secrets.get('Reddit', 'CLIENT_ID'), client_secret=None, user_agent="spoddit")
        except Exception as e:
            logging.error('Unable to authenticate at Reddit. Check the validity of your client secret')
            logging.error(f'{e}')
            self.api = None
            exit(5)

    def is_logged_in(self):
        return self.api is not None
