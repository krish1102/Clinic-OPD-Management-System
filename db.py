# db.py
import mysql.connector
from mysql.connector import Error, InterfaceError, OperationalError
from tkinter import messagebox

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root123',
    'database': 'clinicdb',
    'port': 3306
}

class DB:
    def __init__(self, cfg=DB_CONFIG):
        self.cfg = cfg
        self.conn = None
        self.connect()

    def connect(self):
        try:
            self.conn = mysql.connector.connect(**self.cfg)
        except Error as e:
            messagebox.showerror("Database Connection Failed", f"Cannot connect to the database:\n{e}")

    def ensure_connection(self):
        try:
            if not self.conn.is_connected():
                self.connect()
        except:
            self.connect()

    def fetchall(self, q, params=()):
        self.ensure_connection()
        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute(q, params)
            rows = cur.fetchall()
            cur.close()
            return rows
        except (OperationalError, InterfaceError):
            self.connect()
            return self.fetchall(q, params)

    def fetchone(self, q, params=()):
        self.ensure_connection()
        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute(q, params)
            row = cur.fetchone()
            cur.close()
            return row
        except (OperationalError, InterfaceError):
            self.connect()
            return self.fetchone(q, params)

    def execute(self, q, params=()):
        self.ensure_connection()
        try:
            cur = self.conn.cursor()
            cur.execute(q, params)
            self.conn.commit()
            cur.close()
            return True
        except (OperationalError, InterfaceError):
            self.connect()
            return self.execute(q, params)

    def executemany(self, q, params_list):
        self.ensure_connection()
        try:
            cur = self.conn.cursor()
            cur.executemany(q, params_list)
            self.conn.commit()
            cur.close()
            return True
        except (OperationalError, InterfaceError):
            self.connect()
            return self.executemany(q, params_list)

# Shared DB instance
db = DB()
