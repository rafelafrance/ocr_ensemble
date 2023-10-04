import inspect
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Union

from . import canned_sql

DbPath = Union[Path, str]


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
    sql = canned_sql.CANNED_INSERTS[table]
    cxn.executemany(sql, batch)


def canned_select(cxn, key, one_column=False, **kwargs):
    sql = canned_sql.CANNED_SELECTS[key]

    if kwargs.get("limit"):
        sql += " limit :limit"

    rows = select(cxn, sql, one_column=one_column, **kwargs)
    return rows


def canned_delete(cxn, table, **kwargs):
    sql = canned_sql.CANNED_DELETES[table]
    cxn.execute(sql, dict(kwargs))


# ######################### runs table ################################################
def insert_run(cxn, args, comments: str = "") -> int:
    __, file, line, func, *_ = inspect.stack()[1]
    caller = f"file name: {Path(file).name}, function: {func}, line: {line}"

    json_args = json.dumps({k: str(v) for k, v in vars(args).items()})

    sql = """
        insert into runs ( caller,  args,  comments)
                  values (:caller, :args, :comments);
        """
    cxn.execute(sql, (caller, json_args, comments))
    results = cxn.execute("select seq from sqlite_sequence where name = 'runs';")

    return results.fetchone()[0]


def update_run_finished(cxn, run_id: int):
    sql = """
        update runs set finished = datetime('now', 'localtime') where run_id = ?
        """
    cxn.execute(sql, (run_id,))


def update_run_comments(cxn, run_id: int, comments: str):
    sql = """
        update runs set comments = ?, finished = datetime('now', 'localtime')
         where run_id = ?"""
    cxn.execute(sql, (comments, run_id))
