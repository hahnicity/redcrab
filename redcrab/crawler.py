from itertools import chain

from praw.objects import Comment, MoreComments
# For now just use postgres. If someone else comes along in the future wanting
# a different database we can do some plumbing pretty trivally
import psycopg2

from redcrab.postgres import store_comment, store_submission


def bfs_store_comments(comments, submission, db_connection):
    """
    I wrote this algorithm in the hopes that it would be faster than dfs but it isn't
    the real limiter is the time it takes to make calls to the API.
    """
    queue = iter(comments)
    while True:  # Naked whiles make me nervous
        try:
            comment = queue.next()
        except StopIteration:
            return
        if isinstance(comment, Comment):
            store_comment(comment, submission, db_connection)
            if comment.replies:
                queue = chain(queue, comment.replies)
        elif isinstance(comment, MoreComments):
            try:
                nested = comment.comments()
            except:
                continue
            else:
                queue = chain(queue, nested)


def store_comments(comments, submission, db_connection):
    """
    Comments objects have the sticky property of being nested. As a result even if you
    traverse one comment list that doesn't necessarily mean you've traversed them all.

    So just implement a depth-first approach.

    :param list comments: A list/generator that holds all comments we want to store
    :param db_connection: A connection to the database
    """
    for comment in comments:
        if isinstance(comment, Comment):
            if comment.replies:
                store_comments(comment.replies, submission, db_connection)
            store_comment(comment, submission, db_connection)
        elif isinstance(comment, MoreComments):
            # I've seen problems where this function fails because of internal praw reasons. As a
            # result if it fails just continue on.
            try:
                new_comments = comment.comments()
            except:
                continue
            else:
                store_comments(new_comments, submission, db_connection)
        else:
            raise ValueError(
                "Received unexpected object of type {} when asked to store comments"
                .format(type(comment))
            )


def set_submission(db_connection, sub, comments):
    try:
        store_submission(sub, db_connection)
    # If the submission is already in the db continue on
    except psycopg2.IntegrityError:
        return
    else:
        store_comments(comments, sub, db_connection)
