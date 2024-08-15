from typing import List

import sqlcipher3
from cryptography.fernet import Fernet

from filesystem import FileSystem

class Database:
    def __init__(self):
        pass

    def __create_tables(self) -> None:
        conn, cursor = self.get_db_conn()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname VARCHAR(50),
                email VARCHAR(100) NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def get_db_conn(self) -> tuple[sqlcipher3.Connection, sqlcipher3.Cursor]:
        conn = sqlcipher3.connect(FileSystem().UVICORN_DB_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA key = '{FileSystem().get_pragma_key().decode()}'")
        cursor.execute("VACUUM")
        return conn, cursor

    def insert_account(self, email: str, password: str, fullname: str | None = None) -> bool:
        cipher_key =
        conn, cursor = self.get_db_conn()
        try:
            if not cursor.execute("SELECT email FROM accounts WHERE email = ?", (email,)).fetchone():
                cursor.execute(
                    "INSERT INTO accounts (fullname, email, password) VALUES (?, ?, ?)",
                    (fullname, email, FileSystem().get_cipher_key().encrypt(password.encode()).decode())
                )
                return True
            return False
        except Exception as e:
            print(e)
            return False
        finally:
            conn.close()

    def get_accounts(self, emails: List[str] | None = None, columns: List[str] = ["fullname", "email", "password"]) -> list[dict] | None:
        conn, cursor = self.get_db_conn()
        where_clause = f" WHERE email IN ({', '.join(['?' for _ in emails])})" if emails else ""
        cursor.execute(f"SELECT {', '.join(columns)} FROM accounts" + where_clause, emails or [])
        accounts = cursor.fetchall()
        conn.close()
        if accounts:
            return [
                {columns[i]: account[i] if columns[i] != "password" else Fernet(FileSystem().get_cipher_key()).decrypt(account[i].encode()).decode() for i in range(len(columns))}
                for account in accounts
            ]
        else:
            return None
