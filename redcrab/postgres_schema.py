DATABASE = {
    "name": "redcrab",
    "tables": {
        "comments": {
            "rows": {
                "id": "char(7)",
                "sub_id": "char(7)",
                "body": "text",
            },
            "pk": "id",
            "fk": {
                "child_key": "sub_id",
                "parent_table": "submissions",
                "parent_key": "id",
            },
        },
        "submissions": {
            "rows": {
                "id": "char(7)",
                "title": "text",
            },
            "pk": "id",
        },
    },
    "owner": "redcrab",
    "permissions": "ALL",
}
