import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'bluecarbon.db')

SCHEMA = [
    # Users table
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        name TEXT,
        organization TEXT,
        created_at TEXT NOT NULL
    );
    """,
    # Tokens (blockchain carbon tokens)
    """
    CREATE TABLE IF NOT EXISTS tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token_id TEXT UNIQUE,
        project_id TEXT,
        project_name TEXT,
        creator_ngo TEXT,
        ecosystem_type TEXT,
        credit_amount REAL,
        vintage_year INTEGER,
        status TEXT,
        current_owner TEXT,
        mint_date TEXT,
        retired_by TEXT,
        retirement_date TEXT
    );
    """,
    # Transactions (marketplace)
    """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tx_id TEXT UNIQUE,
        token_id TEXT,
        project_id TEXT,
        project_name TEXT,
        seller_id TEXT,
        buyer_id TEXT,
        buyer_name TEXT,
        credits_sold REAL,
        price_per_credit REAL,
        total_value REAL,
        timestamp TEXT,
        status TEXT,
        blockchain_hash TEXT
    );
    """
]

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    for stmt in SCHEMA:
        cur.executescript(stmt)
    conn.commit()
    # Seed default users if not exists
    cur.execute("SELECT COUNT(*) as c FROM users")
    if cur.fetchone()[0] == 0:
        now = datetime.utcnow().isoformat()
        users = [
            ("admin@nccr.gov", generate_password_hash("Admin@123"), "admin", "NCCR Admin", "NCCR"),
            ("ngo@example.org", generate_password_hash("Ngo@123"), "ngo", "Test NGO User", "Green Earth Foundation"),
            ("panchayat@example.in", generate_password_hash("Panchayat@123"), "panchayat", "Coastal Panchayat", "Panchayat"),
            ("industry@example.com", generate_password_hash("Industry@123"), "industry", "Test Industry User", "EcoTech Industries Ltd")
        ]
        for email, ph, role, name, org in users:
            cur.execute(
                "INSERT INTO users (email, password_hash, role, name, organization, created_at) VALUES (?,?,?,?,?,?)",
                (email, ph, role, name, org, now)
            )
        conn.commit()
    conn.close()


def verify_user(email: str, password: str, role: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email=? AND role=?", (email, role))
    row = cur.fetchone()
    conn.close()
    if row and check_password_hash(row["password_hash"], password):
        return dict(row)
    return None


def save_token(token: dict):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR REPLACE INTO tokens
        (token_id, project_id, project_name, creator_ngo, ecosystem_type, credit_amount, vintage_year, status, current_owner, mint_date, retired_by, retirement_date)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            token.get("token_id"), token.get("project_id"), token.get("project_name"), token.get("creator_ngo"),
            token.get("ecosystem_type"), token.get("credit_amount"), token.get("vintage_year"), token.get("status"),
            token.get("current_owner"), token.get("mint_date"), token.get("retired_by"), token.get("retirement_date")
        )
    )
    conn.commit()
    conn.close()


def save_transaction(tx: dict):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR REPLACE INTO transactions
        (tx_id, token_id, project_id, project_name, seller_id, buyer_id, buyer_name, credits_sold, price_per_credit, total_value, timestamp, status, blockchain_hash)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            tx.get("id"), tx.get("token_id"), tx.get("project_id"), tx.get("project_name"), tx.get("seller_id"), tx.get("buyer_id"),
            tx.get("buyer_name"), tx.get("credits_sold"), tx.get("price_per_credit"), tx.get("total_value"),
            tx.get("timestamp"), tx.get("status"), tx.get("blockchain_hash")
        )
    )
    conn.commit()
    conn.close()