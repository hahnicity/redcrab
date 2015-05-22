import psycopg2


def create_connection(host, db, user, password):
    db_connection = psycopg2.connect(host=host, database=db, user=user, password=password)
    # Create all prepared statements. For now keep a fairly minimal schema. Schema will likely
    # be the thing that I need to change most frequently in the future but for now I just want
    # something functional that suits my purposes
    with db_connection.cursor() as cursor:
        cursor.execute(
            "PREPARE comment_insert (text, char, char) AS INSERT INTO comments VALUES ($1, $2, $3);"
        )
        cursor.execute(
            "PREPARE submission_insert (text, char) AS INSERT INTO submissions VALUES ($1, $2);"
        )
    return db_connection


def store_comment(comment, submission, db_connection):
    """
    Takes a comment object and stores it in the database
    """
    body = comment.body.replace("'", "''")
    with db_connection.cursor() as cursor:
        try:
            cursor.execute(
                u"EXECUTE comment_insert('{}', '{}', '{}');".format(body, comment.id, submission.id)
            )
        # The big thing that I always see is that duplicates of the same comment make it into
        # any tree of comments generated by praw. The problem might actually reside in the reddit
        # API but either way we should just catch any IntegrityErrors coming from duplication of
        # primary keys and just rollback
        except psycopg2.IntegrityError:
            db_connection.rollback()
        except Exception as err:
            import pdb; pdb.set_trace()
        else:
            db_connection.commit()


def store_submission(submission, db_connection):
    """
    Takes a submission object and stores it in the database
    """
    title = submission.title.replace("'", "''")
    with db_connection.cursor() as cursor:
        # Don't catch any IntegrityErrors here for now. We can revisit this assumption later.
        cursor.execute(u"EXECUTE submission_insert('{}', '{}');".format(title, submission.id))
        db_connection.commit()
