from typing import Optional, Generator
import os
import sqlite3
from pathlib import Path
from dataclasses import dataclass
from .rand_tools import RandTools
from .types import Bit

@dataclass
class Section:
    position: int
    original_text: str
    expected_bit: Optional[Bit]
    traduction: Optional[str]

class SteganoDb:

    def __init__(self, db_path: Optional[str] = None, init: bool = True):
        if db_path is None:
            db_path = 'file-db-' + RandTools.random_string(10) + '.sqlite'
        self.db_file_path: Path = Path(db_path)
        self.db = sqlite3.connect(db_path)
        if init:
            cursor = self.db.cursor()
            try:
                cursor.execute("""CREATE TABLE IF NOT EXISTS t ("idx" INTEGER PRIMARY KEY,
                                                                "position" INTEGER NOT NULL,
                                                                "original_text" TEXT NOT NULL,
                                                                "expected_bit" integer DEFAULT NULL,
                                                                "traduction" TEXT DEFAULT NULL)
                               """)
            finally:
                cursor.close()
        self.db.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.destroy()

    def close(self) -> None:
        self.db.close()
        self.db = None

    def destroy(self) -> None:
        if not self.db_file_path.exists():
            return
        self.db.close()
        try:
            os.remove(self.db_file_path)
        except PermissionError:
            print("Unable to remove file: " + str(self.db_file_path), flush=True)
        self.db = None

    def add_original_text(self, position: int, original_text: str) -> None:
        cursor = self.db.cursor()
        try:
            cursor.execute('INSERT INTO t ("position", "original_text") VALUES (?, ?)', (position, original_text,))
        finally:
            cursor.close()
        self.db.commit()

    def set_expected_bit(self, position: int, expected_bit: Bit) -> None:
        cursor = self.db.cursor()
        try:
            cursor.execute('UPDATE t SET "expected_bit"=? WHERE "position"=?', (expected_bit, position,))
        finally:
            cursor.close()
        self.db.commit()

    def set_traduction(self, position: int, traduction: str) -> None:
        cursor = self.db.cursor()
        try:
            cursor.execute('UPDATE t SET "traduction"=? WHERE "position"=?', (traduction, position,))
        finally:
            cursor.close()
        self.db.commit()

    def get_section_by_position(self, position: int) -> Section:
        cursor = self.db.cursor()
        try:
            row = cursor.execute('SELECT "idx", "position", "original_text", "expected_bit", "traduction" FROM t WHERE "position"=?', (position,)).fetchone()
            if row is None:
                raise ValueError("Invalid position: {}".format(position))
        finally:
            cursor.close()
        return Section(position=row[1], original_text=row[2], expected_bit=row[3], traduction=row[4])

    def __len__(self) -> int:
        cursor = self.db.cursor()
        try:
            count: int = cursor.execute("SELECT COUNT(*) FROM t").fetchone()[0]
        finally:
            cursor.close()
        return count

    def get_sections(self) -> Generator[Section, None, None]:
        cursor = self.db.cursor()
        try:
            for row in cursor.execute('SELECT "idx", "position", "original_text", "expected_bit", "traduction" FROM t ORDER BY "position"'):
                yield Section(position=row[1], original_text=row[2], expected_bit=row[3], traduction=row[4])
        finally:
            cursor.close()
