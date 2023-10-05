import sqlite3
from contextlib import contextmanager

CANNED_INSERTS = {
    "char_sub_matrix": """
        insert into char_sub_matrix
               ( char1,  char2,  char_set,  score,  sub)
        values (:char1, :char2, :char_set, :score, :sub);
        """,
}

CANNED_SELECTS = {
    "char_sub_matrix": """
        select * from char_sub_matrix where char_set = :char_set
        """,
}

CANNED_DELETES = {
    "char_sub_matrix": """
        delete from char_sub_matrix where char_set = :char_set
        """,
}


@contextmanager
def connect(db_path):
    """Add a row factory to the normal connection context manager."""
    try:
        with sqlite3.connect(db_path) as cxn:
            cxn.row_factory = sqlite3.Row
            yield cxn
    finally:
        pass


def execute(cxn, sql, params=None):
    params = params if params else []
    return cxn.execute(sql, params)


def select(cxn, sql, one_column=False, **kwargs):
    rows = cxn.execute(sql, dict(kwargs))

    if one_column:
        return [r[0] for r in rows]

    return [dict(r) for r in rows]


def update(cxn, sql, **kwargs):
    cxn.execute(sql, dict(kwargs))


def canned_insert(cxn, table, batch):
    sql = CANNED_INSERTS[table]
    cxn.executemany(sql, batch)


def canned_select(cxn, key, one_column=False, **kwargs):
    sql = CANNED_SELECTS[key]

    if kwargs.get("limit"):
        sql += " limit :limit"

    rows = select(cxn, sql, one_column=one_column, **kwargs)
    return rows


def canned_delete(cxn, table, **kwargs):
    sql = CANNED_DELETES[table]
    cxn.execute(sql, dict(kwargs))
