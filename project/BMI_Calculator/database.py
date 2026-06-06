"""Database module for BMI Calculator.

Handles SQLite connection, table creation, and all CRUD operations
for BMI records.
"""

import sqlite3
import os
from datetime import datetime

DB_DIR = os.path.join(os.path.dirname(__file__), "database")
DB_PATH = os.path.join(DB_DIR, "bmi_records.db")


def _ensure_db_dir():
    """Create the database directory if it doesn't exist."""
    os.makedirs(DB_DIR, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    """Return a connection to the SQLite database."""
    _ensure_db_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the bmi_records table if it doesn't exist."""
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bmi_records (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                age        INTEGER NOT NULL,
                gender     TEXT    NOT NULL,
                weight     REAL    NOT NULL,
                height     REAL    NOT NULL,
                bmi        REAL    NOT NULL,
                category   TEXT    NOT NULL,
                date_time  TEXT    NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


# ── CRUD Operations ─────────────────────────────────────────────────────────

def save_record(name: str, age: int, gender: str, weight: float,
                height: float, bmi: float, category: str) -> int:
    """Insert a new BMI record and return its ID."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO bmi_records
               (name, age, gender, weight, height, bmi, category, date_time)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, age, gender, weight, height, bmi, category,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_all_records() -> list:
    """Return all records ordered by date descending."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM bmi_records ORDER BY date_time DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_record_by_id(record_id: int) -> dict | None:
    """Return a single record by ID, or None."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM bmi_records WHERE id = ?", (record_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def search_records(query: str) -> list:
    """Search records by name or category (case-insensitive)."""
    conn = get_connection()
    try:
        like = f"%{query}%"
        rows = conn.execute(
            """SELECT * FROM bmi_records
               WHERE name LIKE ? OR category LIKE ?
               ORDER BY date_time DESC""",
            (like, like),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_record(record_id: int, name: str, age: int, gender: str,
                  weight: float, height: float, bmi: float,
                  category: str) -> bool:
    """Update an existing record. Returns True if a row was updated."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """UPDATE bmi_records
               SET name=?, age=?, gender=?, weight=?, height=?,
                   bmi=?, category=?
               WHERE id=?""",
            (name, age, gender, weight, height, bmi, category, record_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def delete_record(record_id: int) -> bool:
    """Delete a record by ID. Returns True if a row was deleted."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM bmi_records WHERE id = ?", (record_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def delete_all_records() -> int:
    """Delete all records. Returns the number of deleted rows."""
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM bmi_records")
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


# ── Statistics ───────────────────────────────────────────────────────────────

def get_statistics() -> dict:
    """Return aggregate statistics, or zeroes if no records exist."""
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT COUNT(*)      AS count,
                      AVG(bmi)       AS avg_bmi,
                      MAX(bmi)       AS max_bmi,
                      MIN(bmi)       AS min_bmi
               FROM bmi_records"""
        ).fetchone()

        count = row["count"] or 0
        if count == 0:
            return {"count": 0, "avg_bmi": 0.0, "max_bmi": 0.0, "min_bmi": 0.0}

        return {
            "count": count,
            "avg_bmi": round(row["avg_bmi"], 2),
            "max_bmi": round(row["max_bmi"], 2),
            "min_bmi": round(row["min_bmi"], 2),
        }
    finally:
        conn.close()


def get_category_distribution() -> dict:
    """Return {category: count} for all records."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT category, COUNT(*) AS cnt
               FROM bmi_records
               GROUP BY category"""
        ).fetchall()
        return {r["category"]: r["cnt"] for r in rows}
    finally:
        conn.close()


def get_bmi_trend() -> list:
    """Return list of {date, bmi} ordered by date ascending."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT date_time, bmi
               FROM bmi_records
               ORDER BY date_time ASC"""
        ).fetchall()
        return [{"date": r["date_time"], "bmi": r["bmi"]} for r in rows]
    finally:
        conn.close()
