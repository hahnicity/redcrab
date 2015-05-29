from argparse import ArgumentParser
from getpass import getpass

from praw import Reddit

from redcrab import constants
from redcrab.crawler import set_submission
from redcrab.postgres import create_connection, build_database


def add_db_args(parser):
    parser.add_argument("--db-user", default="redcrab", help="The database user")
    parser.add_argument("--db-password", help="The database password")
    parser.add_argument(
        "--db-host", help="The name of host where the database is", default="localhost"
    )


def build_db_parser():
    """
    Build the parser for the database schema setter
    """
    parser = ArgumentParser()
    add_db_args(parser)
    return parser


def build_reddit_parser():
    parser = ArgumentParser()
    add_db_args(parser)
    parser.add_argument("subreddit", help="The subreddit you want to parse")
    parser.add_argument("--username", help="The reddit username")
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
    for sub in getattr(subreddit, method)(limit=limit):
        set_submission(db_connection, sub, sub.comments)
    db_connection.close()


def db_builder():
    args = build_db_parser().parse_args()
    build_database(args.db_host, args.db_user, args.db_password)


def reddit_parser():
    args = build_reddit_parser().parse_args()
    db_connection = create_connection(args.db_host, args.db_password)
    reddit = Reddit(user_agent=args.user_agent)
    subreddit = reddit.get_subreddit(args.subreddit)
    if args.username:
        password = getpass("Enter reddit password: ")
        reddit.login(args.username, password)
    single_threaded_impl(subreddit, db_connection, args.sub_limit, args.method)
