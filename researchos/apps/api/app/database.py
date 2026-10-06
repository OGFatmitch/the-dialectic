import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parents[3] / "data" / "researchos.db"


def database_path() -> Path:
    return Path(os.environ.get("RESEARCHOS_DB", DEFAULT_PATH))


@contextmanager
def connect():
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialize() -> None:
    schema = (Path(__file__).with_name("schema.sql")).read_text()
    with connect() as connection:
        connection.executescript(schema)


def decode(row):
    if row is None:
        return None
    value = dict(row)
    if "authors" in value:
        value["authors"] = json.loads(value["authors"])
    return value
