import psycopg2

from redcrab.postgres_schema import (
    COMMENTS_INPUTS,
    COMMENTS_PARAMS,
    COMMENTS_STATEMENT,
    DATABASE,
    SUBMISSIONS_INPUTS,
    SUBMISSIONS_PARAMS,
    SUBMISSIONS_STATEMENT
)


def _create_database(host, user, password):
    """
    Create the database
    """
    db_connection = psycopg2.connect(host=host, user=user, password=password, database="postgres")
    with db_connection.cursor() as cursor:
        db_connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor.execute("CREATE USER {}".format(DATABASE["owner"]))
        cursor.execute("CREATE DATABASE {};".format(DATABASE["name"], DATABASE["owner"]))
    db_connection.close()


def _create_tables(host, user, password):
    """
    Create all tables we will store our data
    """
    # no password for now
    db_connection = psycopg2.connect(host=host, user=DATABASE["owner"], database=DATABASE["name"])
    with db_connection.cursor() as cursor:
        for table, vals in DATABASE["tables"].iteritems():
            tablesql = "create table {} ({}".format(
                table,
                ",".join(["{} {}".format(name, type_) for name, type_ in vals["rows"]])
            )
            if vals.get("pk"):
                tablesql = "{},primary key ({})".format(tablesql, vals["pk"])
            if vals.get("fk"):
                tablesql = "{},foreign key ({}) references {} ({})".format(
                    tablesql,
                    vals["fk"]["child_key"],
                    vals["fk"]["parent_table"],
                    vals["fk"]["parent_key"]
                )
            tablesql = "{});".format(tablesql)
            cursor.execute(tablesql)
            # GRANT ALL because why not right?
            cursor.execute("GRANT ALL ON {} TO {};".format(table, DATABASE["owner"]))
    db_connection.commit()
    db_connection.close()


def build_database(host, user, password):
    """
    Set up the database user, the database, the tablespace and set all grants
    """
    _create_database(host, user, password)
    _create_tables(host, user, password)


def create_connection(host, password):
    db_connection = psycopg2.connect(
        host=host, database=DATABASE["name"], user=DATABASE["owner"], password=password
    )
    with db_connection.cursor() as cursor:
        cursor.execute(COMMENTS_STATEMENT)
        cursor.execute(SUBMISSIONS_STATEMENT)
    return db_connection


def store_comment(comment, submission, db_connection):
    """
    Takes a comment object and stores it in the database
    """
    dict_ = {}
    for name, _ in COMMENTS_PARAMS:
        if name == "sub_id":  # special unicorn case
            # we could get it out of the comments but thats more HTTP requests
            dict_["sub_id"] = submission.id
        else:
            dict_[name] = getattr(comment, name).replace("'", "''")

    with db_connection.cursor() as cursor:
        try:
            cursor.execute(COMMENTS_INPUTS.format(**dict_))
        # rollback if we duplicate a primary key
        except psycopg2.IntegrityError:
            db_connection.rollback()
        else:
            db_connection.commit()


def store_submission(submission, db_connection):
    """
    Takes a submission object and stores it in the database
    """
    dict_ = {
        name: getattr(submission, name).replace("'", "''") for name, _ in SUBMISSIONS_PARAMS
    }
    with db_connection.cursor() as cursor:
        try:
            cursor.execute(SUBMISSIONS_INPUTS.format(**dict_))
        except psycopg2.IntegrityError as err:
            db_connection.rollback()
            raise err
        else:
            db_connection.commit()
