from argparse import ArgumentParser
from getpass import getpass

from praw import Reddit

from redcrab import constants
from redcrab.crawler import set_submission
from redcrab.postgres import create_connection


def build_parser():
    parser = ArgumentParser()
    parser.add_argument("subreddit", help="The subreddit you want to parse")
    parser.add_argument("--username", help="The reddit username")
    parser.add_argument("--db-user", default="redcrab", help="The database user")
    parser.add_argument("--db-name", default="redcrab", help="The name of the database")
    parser.add_argument("--db-password", help="The database password")
    parser.add_argument("--db-host", help="The name of host where the database is", default="localhost")
    parser.add_argument(
        "--sub-limit",
        type=int,
        help="The limit to the number of submissions we want to get"
    )
    parser.add_argument(
        "--user-agent",
        required=True,
        help="The user agent to make requests with"
    )
    parser.add_argument(
        "--method",
        required=True,
        choices=constants.METHODS,
        help="Choose the way to get reddit submissions"
    )
    return parser


def single_threaded_impl(subreddit, db_connection, limit, method):
    for sub, comments in [(sub, sub.comments) for sub in getattr(subreddit, method)(limit=limit)]:
        set_submission(db_connection, sub, comments)
    db_connection.close()


def main():
    args = build_parser().parse_args()
    db_connection = create_connection(args.db_host, args.db_name, args.db_user, args.db_password)
    reddit = Reddit(user_agent=args.user_agent)
    subreddit = reddit.get_subreddit(args.subreddit)
    if args.username:
        password = getpass("Enter reddit password: ")
        reddit.login(args.username, password)
    single_threaded_impl(subreddit, db_connection, args.sub_limit, args.method)
