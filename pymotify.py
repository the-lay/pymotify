import requests
from time import sleep

class PymotifyException(Exception):
    pass

class Pymotify:

    URL = 'http://127.0.0.1:{0}{1}'

    def __init__(self):
        self.session = requests.session()
        self.csrf_token = self.oauth_token = self.port = None

        # handshake
        try:
            self._find_port()
            self._get_csrf_token()
            self._get_oauth_token()
        except PymotifyException as err:
            print('Error', err)

    # finds the port that Spotify Web Helper is using
    def _find_port(self):
        possible_ports = range(4370, 4390)
        for port in possible_ports:
            try:
                self.session.get(Pymotify.URL.format(port, '/simplecsrf/token.json'), timeout=0.05)
            except requests.Timeout or requests.ConnectionError:
                continue
            self.port = port
            return port
        raise PymotifyException('Have not found Web Helper port: check if Spotify is on? Try restarting it.')

    # general method for local calls to Web Helper
    def _local_call(self, url, req_params={}):
        headers = dict(Origin='https://open.spotify.com')
        params = {
            'oauth': self.oauth_token,
            'csrf': self.csrf_token
        }
        params.update(req_params)

        try:
            res = self.session.get(Pymotify.URL.format(self.port, url), headers=headers, params=params)
        except:
            raise PymotifyException('Connection failed')

        try:
            res_json = res.json()
        except ValueError as err:
            raise PymotifyException('Unable to decode JSON result: {}'.format(err))

        if res_json.get('error'):
            raise PymotifyException('Response error:', int(res_json.get('error').get('type', '0')))

        return res_json

    # obtains CSRF token from Web Helper
    def _get_csrf_token(self):
        res = self._local_call('/simplecsrf/token.json')
        self.csrf_token = res.get('token')

    # obtains OAuth token from open.spotify.com
    def _get_oauth_token(self):
        res = self.session.get('http://open.spotify.com/token')
        self.oauth_token = res.json().get('t')

    # pause
    def pause(self):
        return self._local_call('/remote/pause.json', req_params={'pause': 'true'})

    # unpause
    def unpause(self):
        return self._local_call('/remote/pause.json', req_params={'pause': 'false'})


if __name__ == '__main__':
    a = Pymotify()

    # Pauses current spotify playback, waits 3s and then unpauses
    a.pause()
    sleep(3)
    a.unpause()
