from functools import partial

import spotipy
from requests import HTTPError
from spotipy import SpotifyException

import logging

from .. import util

logger = logging.getLogger(__name__)


def get_all(paged_function_handle, limit=0, start_page=0):
    # TODO: integrate some rate limit check deep down, as this could be a problem
    page_index = start_page
    items = []
    while True:
        page = paged_function_handle(offset=page_index * limit)
        total = page['total']
        limit = page['limit']
        items += page['items']
        page_index += 1
        if len(items) >= total:
            logger.debug(f'items collected so far: {len(items)}')
            return items


class SpotifySession:
    __SECRET_CONF = '.secret.conf'
    _REQUIRED_SPOTIFY_PERMISSIONS = ' '.join([
        'playlist-read-private',
        'playlist-modify-private',
        'playlist-modify-public',
        'playlist-read-collaborative',
        'user-library-read'
    ])

    def __init__(self, username, port):
        self.username = username
        logger.debug('Logging in...')
        self.redirect_url = f'localhost:{port}'
        self.secrets = util.parse_config(self.__SECRET_CONF)
        if self.secrets is None or not self.secrets.has_section('Spotify'):
            logger.error(f'Malformed or missing .secrets.conf. Create one base on provided .secret-template.conf')
            exit(3)
        self.scheme = 'http://'
        self.api = self._login()

    def is_logged_in(self):
        return (self.api is not None and
                self.api.current_user()['id'].lower() == self.username.lower())

    def get_playlists(self):
        return get_all(self.api.current_user_playlists)

    def get_tracks(self, playlist_id):
        return get_all(partial(self.api.playlist_tracks, playlist_id))

    def _login(self):
        """
        Log into spotify with provided username
        :return:
        """
        _spotify = None
        logger.debug(f'OAuth2 redirect url: {self.scheme}{self.redirect_url}')
        token = spotipy.util.prompt_for_user_token(
            username=self.username,
            scope=self._REQUIRED_SPOTIFY_PERMISSIONS,
            client_id=self.secrets.get('Spotify', 'CLIENT_ID'),
            client_secret=self.secrets.get('Spotify', 'CLIENT_SECRET'),
            redirect_uri=f'{self.scheme}{self.redirect_url}',
            show_dialog=True)
        if token:
            _spotify = spotipy.Spotify(auth=token)
        else:
            logger.error(f'Unable to get spotify auth token for {self.username}')

        return _spotify

    def demo(self):
        try:
            results = self.api.current_user_saved_tracks()
            for item in results['items']:
                track = item['track']
                print(track['name'] + ' - ' + track['artists'][0]['name'])
        except (HTTPError, SpotifyException) as e:
            exit(e.errno)
