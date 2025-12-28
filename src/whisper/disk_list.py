from typing import Optional
from .rand_tools import RandTools
import os
import sqlite3
from pathlib import Path


class DiskList:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = 'disk-list-' + RandTools.random_string(10) + '.sqlite'
        self.db_file_path: Path = Path(db_path)
        self.db = sqlite3.connect(db_path)
        cursor: sqlite3.Cursor = self.db.cursor()
        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS t (idx INTEGER PRIMARY KEY, value BLOB)")
        finally:
            cursor.close()
        self.db.commit()

    def destroy(self) -> None:
        if not self.db_file_path.exists():
            return
        self.db.close()
        try:
            os.remove(self.db_file_path)
        except PermissionError:
            print("Unable to remove file: " + str(self.db_file_path), flush=True)
        self.db = None

    def append(self, value: str) -> None:
        cursor: sqlite3.Cursor = self.db.cursor()
        try:
            cursor.execute("INSERT INTO t(value) VALUES (?)", (value,))
        finally:
            cursor.close()
        self.db.commit()

    def reset(self) -> None:
        cursor: sqlite3.Cursor = self.db.cursor()
        try:
            cursor.execute("DELETE FROM t")
        finally:
            cursor.close()

    def __getitem__(self, index: int) -> str:
        cursor: sqlite3.Cursor = self.db.cursor()
        try:
            row = cursor.execute("SELECT value FROM t WHERE idx=?", (index+1,)).fetchone()
            if row is None:
                raise IndexError(index)
        finally:
            cursor.close()
        return row[0]

    def __setitem__(self, index: int, value: str) -> None:
        cursor: sqlite3.Cursor = self.db.cursor()
        try:
            cur = cursor.execute("UPDATE t SET value=? WHERE idx=?", (value, index+1))
            if cur.rowcount == 0:
                raise IndexError(index)
        finally:
            cursor.close()
        self.db.commit()

    def __len__(self) -> int:
        cursor: sqlite3.Cursor = self.db.cursor()
        try:
            count: int = cursor.execute("SELECT COUNT(*) FROM t").fetchone()[0]
        finally:
            cursor.close()
        return count
