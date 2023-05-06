import sys

from butterflymx_444.models.user import User
from butterflymx_444.security import hash_password


def create_user():
    args = sys.argv[1:3]

    if len(args) != 2:
        print("Missing arguments. Please use like so: create_user <username> <password>")
        return

    username, password = args

    hashed_password, salt = hash_password(password)

    print(
        User(username=username, password=hashed_password, salt=salt)
        .json()
        .replace(': ', ':')
        .replace(', ', ',')
    )
