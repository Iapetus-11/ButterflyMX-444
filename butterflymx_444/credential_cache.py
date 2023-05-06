import json
import os

from butterflymx import AccessToken

TOKEN_CACHE_FILE = '.token_cache.json'


def load() -> tuple[AccessToken, str] | tuple[None, None]:
    # Load cached oauth credentials
    if os.path.isfile(TOKEN_CACHE_FILE):
        with open(TOKEN_CACHE_FILE, 'r') as token_cache_file:
            data = json.load(token_cache_file)

            return AccessToken(**data['access_token']), data['refresh_token']

    return None, None


def save(access_token: AccessToken, refresh_token: str) -> None:
    with open(TOKEN_CACHE_FILE, 'w+') as token_cache_file:
        data = {
            'access_token': {
                'token': access_token.token,
                'expires_at': access_token.expires_at,
            },
            'refresh_token': refresh_token
        }

        json.dump(data, token_cache_file)
