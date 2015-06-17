import argparse
import sys
import re
import json
import requests
from models import auth
import pdb


def create(config, args):
    pass


def read(config, args):
    if (args['all'] is False) and (args['username'] is None):
        print("No user object(s) specified to read.")
        return
    elif args['all'] is True:
        token = auth.get_token(config)
        pass
    elif args['username'] is not None:
        token = auth.get_token(config)
        r = requests.


def update(config, args):
    pass


def delete(config, args):
    pass


def main(config, args):
    description = "Interact with user objects."
    m = re.match(r'^.*\.(.*)$', __name__)
    controller_name = m.groups()[0]
    del sys.argv[1]
    parser = argparse.ArgumentParser(prog="%s %s" % (sys.argv[0], controller_name), description=description)
    subparsers = parser.add_subparsers(dest="action")
    
    # create 
    create_parser = subparsers.add_parser("create", help="create user object")
    create_parser.add_argument("--username", type=str, required=True, help="username of new user")
    create_parser.add_argument("--password", type=str, required=True, help="password of new user")
    create_parser.add_argument("--admin", type=bool, default=False, help="set user as admin")

    # read
    read_parser = subparsers.add_parser("read", help="read user object(s)")
    read_parser.add_argument("--username", type=str, help="username to read")
    read_parser.add_argument("--all", action="store_const", const=True, default=False, help="Display all user objects")

    # update 
    create_parser = subparsers.add_parser("update", help="update existing user object")
    create_parser.add_argument("username", type=str, help="username to update")
    create_parser.add_argument("--username", type=str, required=True, help="username for user")
    create_parser.add_argument("--password", type=str, required=True, help="password for user")
    create_parser.add_argument("--admin", type=bool, default=False, help="set user as admin")

    # delete
    read_parser = subparsers.add_parser("delete", help="delete user object")
    read_parser.add_argument("username", type=str, help="username to delete")
    
    args = vars(parser.parse_args())
    action_map = {
        "create": create,
        "read": read,
        "update": update,
        "delete": delete,
    }
    action_map[args['action']](config, args)
