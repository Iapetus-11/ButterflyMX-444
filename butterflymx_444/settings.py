import json
import os

from dotenv import load_dotenv
from pydantic import parse_obj_as

from butterflymx_444.models.user import User
from butterflymx_444.utils import parse_bool

load_dotenv()

DEBUG = parse_bool(os.environ.get('DEBUG'))

CORS_ORIGINS = os.environ['CORS_ORIGINS'].split(',')

OAUTH_CLIENT_ID = os.environ['OAUTH_CLIENT_ID']
OAUTH_CLIENT_SECRET = os.environ['OAUTH_CLIENT_SECRET']

BUTTERFLYMX_EMAIL = os.environ['BUTTERFLYMX_EMAIL']
BUTTERFLYMX_PASSWORD = os.environ['BUTTERFLYMX_PASSWORD']

USERS = parse_obj_as(list[User], json.loads(os.environ['USERS']))

JWT_SECRET = os.environ['JWT_SECRET']
JWT_EXPIRATION_DAYS = int(os.environ['JWT_EXPIRATION_DAYS'])
