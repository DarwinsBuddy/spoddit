from functools import partial

import spotipy
from requests import HTTPError
from spotipy import SpotifyException

import logging

from spoddit import secrets

logger = logging.getLogger(__name__)


def get_all(paged_function_handle, limit=0, start_page=0):
    """
    Bundles several calls which are paginated by the spotify api
    :param paged_function_handle:
    :param limit:
    :param start_page:
    :return: result set
    """
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
        if not secrets.has_section('Spotify'):
            logger.error(f'Malformed or missing .secrets.conf. Create one base on provided .secret-template.conf')
            exit(3)
        self.scheme = 'http://'
        self._api = self._login()
        # get current user
        self.user = self._api.current_user()

    def is_logged_in(self):
        """
        Checks whether user is logged in.
        :return: true if user is logged in, otherwise false
        """
        return (self._api is not None and
                self._api.current_user()['id'].lower() == self.username.lower())

    def get_playlists(self):
        """
        Bundles calls to playlists endpoint taking care of pagination
        :return: playlists
        """
        return get_all(self._api.current_user_playlists)

    def get_tracks(self, playlist_id):
        """
        Bundles calls to tracks endpoint taking care of pagination
        :param playlist_id:
        :return: tracks
        """
        return get_all(partial(self._api.playlist_tracks, playlist_id))

    def create_playlist(self, playlist_name, public=False, description='Created by spoddit'):
        """
        Creates a playlist in the logged in users spotify account, if it doesn't exist yet
        :param playlist_name: name for the playlist to create
        :param public: if the playlist should be publicly available
        :param description: A description provided for the playlist
        """
        playlists = self.get_playlists()
        if playlist_name in [p['name'] for p in playlists]:
            logger.warning(f'Cannot create playlist "{playlist_name}" as it already exists')
            return None
        else:
            logger.info(f'Creating playlist "{playlist_name}"')
            return self._api.user_playlist_create(
                user=self.user['id'],
                name=playlist_name,
                public=public,
                description=description
            )

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
            client_id=secrets.get('Spotify', 'CLIENT_ID'),
            client_secret=secrets.get('Spotify', 'CLIENT_SECRET'),
            redirect_uri=f'{self.scheme}{self.redirect_url}',
            show_dialog=True)
        if token:
            _spotify = spotipy.Spotify(auth=token)
        else:
            logger.error(f'Unable to get spotify auth token for {self.username}')

        return _spotify

    def demo(self):
        """
        A demo call to the spotify API
        """
        try:
            results = self._api.current_user_saved_tracks()
            for item in results['items']:
                track = item['track']
                print(track['name'] + ' - ' + track['artists'][0]['name'])
        except (HTTPError, SpotifyException) as e:
            exit(e.errno)

    # delegate everything else to the api
    def __getattr__(self, name):
        return getattr(self._api, name)
