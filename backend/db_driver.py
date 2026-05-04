import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional


@dataclass
class Lead:
    id: int
    name: str
    phone: str
    reason: str
    preferred_time: str
    email: str
    notes: str
    status: str


@dataclass
class Customer:
    id: int
    name: str
    phone: str
    email: str
    notes: str


class DatabaseDriver:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or os.getenv("CALL_CENTRE_DB_PATH", "call_centre.sqlite")
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    preferred_time TEXT,
                    email TEXT,
                    notes TEXT,
                    status TEXT NOT NULL DEFAULT 'new',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def create_or_update_customer(
        self,
        name: str,
        phone: str = "",
        email: str = "",
        notes: str = ""
    ) -> Customer:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            existing = None
            if phone:
                cursor.execute("SELECT id FROM customers WHERE phone = ?", (phone,))
                existing = cursor.fetchone()

            if existing:
                cursor.execute(
                    """
                    UPDATE customers
                    SET name = ?, email = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (name, email, notes, existing[0])
                )
                customer_id = existing[0]
            else:
                cursor.execute(
                    "INSERT INTO customers (name, phone, email, notes) VALUES (?, ?, ?, ?)",
                    (name, phone, email, notes)
                )
                customer_id = cursor.lastrowid

            conn.commit()
            return Customer(
                id=customer_id,
                name=name,
                phone=phone,
                email=email,
                notes=notes
            )

    def capture_lead(
        self,
        name: str,
        phone: str,
        reason: str,
        preferred_time: str = "",
        email: str = "",
        notes: str = "",
        status: str = "new"
    ) -> Lead:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO leads (name, phone, reason, preferred_time, email, notes, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (name, phone, reason, preferred_time, email, notes, status)
            )
            lead_id = cursor.lastrowid
            conn.commit()
            return Lead(
                id=lead_id,
                name=name,
                phone=phone,
                reason=reason,
                preferred_time=preferred_time,
                email=email,
                notes=notes,
                status=status
            )

    def find_customer_by_phone(self, phone: str) -> Optional[Customer]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, phone, email, notes FROM customers WHERE phone = ?",
                (phone,)
            )
            row = cursor.fetchone()
            if not row:
                return None

            return Customer(
                id=row[0],
                name=row[1],
                phone=row[2],
                email=row[3],
                notes=row[4]
            )
