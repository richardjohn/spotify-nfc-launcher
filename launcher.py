import ssl
from string import ascii_lowercase
from random import choice
import urllib
import urllib2
import json
import time

# Default port that Spotify Web Helper binds to.
PORT = 4370
ORIGIN_HEADER = {'Origin': 'https://open.spotify.com'}

# I had some troubles with the version of Spotify's SSL cert and Python 2.7 on Mac.
# Did this monkey dirty patch to fix it. Your milage may vary.
def new_wrap_socket(*args, **kwargs):
    kwargs['ssl_version'] = ssl.PROTOCOL_SSLv3
    return orig_wrap_socket(*args, **kwargs)

orig_wrap_socket, ssl.wrap_socket = ssl.wrap_socket, new_wrap_socket

def get_json(url, params={}, headers={}):
    if params:
        url += "?" + urllib.urlencode(params)
    request = urllib2.Request(url, headers=headers)
    return json.loads(urllib2.urlopen(request).read())


def generate_local_hostname():
    """Generate a random hostname under the .spotilocal.com domain"""
    subdomain = ''.join(choice(ascii_lowercase) for x in range(10))
    return subdomain + '.spotilocal.com'


def get_url(url):
    return "https://%s:%d%s" % (generate_local_hostname(), PORT, url)

def get_oauth_token():
    return get_json('http://open.spotify.com/token')['t']


def get_csrf_token():
    # Requires Origin header to be set to generate the CSRF token.
    return get_json(get_url('/simplecsrf/token.json'), headers=ORIGIN_HEADER)['token']


def get_status(oauth_token, csrf_token):
    params = {
        'oauth': oauth_token,
        'csrf': csrf_token,
        # 'returnafter': return_after,
        # 'returnon': ','.join(return_on)
    }
    return get_json(get_url('/remote/status.json'), params=params, headers=ORIGIN_HEADER)

if __name__ == '__main__':
    oauth_token = get_oauth_token()
    csrf_token = get_csrf_token()

    status = get_status(oauth_token, csrf_token)
    try:
        uri = status['track']['album_resource']['uri']
        print uri
    except KeyError, e:
        print "Couldn't find the album for that track"
    except Exception, e:
        print "Unknown error"
    
