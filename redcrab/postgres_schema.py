def _gen_values(rowspace):
    return "({})".format(
        ", ".join(
            ["${}".format(i + 1) for i in range(len(rowspace))]
        )
    )


def _gen_types(rowspace):
    return "({})".format(
        ", ".join(
            [type.split("(")[0].strip() for _, type in rowspace]
        )
    )


def _gen_inputs(rowspace):
    return "({})".format(
        ", ".join(["'{{{}}}'".format(name) for name, _ in rowspace])
    )


COMMENTS_TABLE_NAME = "comments"
SUBMISSIONS_TABLE_NAME = "submissions"
DATABASE = {
    "name": "redcrab",
    "tables": {
        COMMENTS_TABLE_NAME: {
            "rows": [
                ("body", "text"),
                ("id", "char(7)"),
                ("sub_id", "char(7)"),
            ],
            "pk": "id",
            "fk": {
                "child_key": "sub_id",
                "parent_table": "submissions",
                "parent_key": "id",
            },
        },
        SUBMISSIONS_TABLE_NAME: {
            "rows": [
                ("title", "text"),
                ("id", "char(7)"),
            ],
            "pk": "id",
        },
    },
    "owner": "redcrab",
    "permissions": "ALL",
}

COMMENTS_STATEMENT = "PREPARE comment_insert {} AS INSERT INTO {} VALUES {};".format(
    _gen_types(DATABASE["tables"][COMMENTS_TABLE_NAME]["rows"]),
    COMMENTS_TABLE_NAME,
    _gen_values(DATABASE["tables"][COMMENTS_TABLE_NAME]["rows"])
)
SUBMISSIONS_STATEMENT = "PREPARE submission_insert {} AS INSERT INTO {} VALUES {};".format(
    _gen_types(DATABASE["tables"][SUBMISSIONS_TABLE_NAME]["rows"]),
    SUBMISSIONS_TABLE_NAME,
    _gen_values(DATABASE["tables"][SUBMISSIONS_TABLE_NAME]["rows"]),
)
COMMENTS_PARAMS = DATABASE["tables"][COMMENTS_TABLE_NAME]["rows"]
COMMENTS_INPUTS = u"EXECUTE comment_insert{};".format(_gen_inputs(COMMENTS_PARAMS))
SUBMISSIONS_PARAMS = DATABASE["tables"][SUBMISSIONS_TABLE_NAME]["rows"]
SUBMISSIONS_INPUTS = u"EXECUTE submission_insert{};".format(_gen_inputs(SUBMISSIONS_PARAMS))
