"""
database.py

Handles SQLite connection setup and seeds the database with realistic
fake campaign data spread across four ad channels. Run this file directly
to (re)create and seed the database:

    python database.py
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "campaigns.db")

# Seed data: 12 campaigns across 4 channels, with intentionally varied
# performance so the optimization algorithm has something meaningful to say.
# Search and Video are strong performers here; Display is deliberately weak,
# Social is middling. Numbers are in INR to match the DeltaX JD context.
SEED_CAMPAIGNS = [
    # (name, channel, spend, clicks, conversions, revenue)
    ("Diwali Sale - Search Brand", "Search", 45000, 3200, 210, 168000),
    ("Diwali Sale - Search Generic", "Search", 38000, 2600, 150, 112000),
    ("New Year Push - Search", "Search", 30000, 2100, 130, 98000),

    ("Diwali Sale - Instagram Reels", "Social", 42000, 5100, 95, 71000),
    ("Brand Awareness - Facebook Feed", "Social", 36000, 4300, 60, 48000),
    ("Retargeting - Instagram Stories", "Social", 22000, 2800, 55, 46000),

    ("Diwali Sale - Display Banners", "Display", 40000, 6200, 40, 26000),
    ("Category Push - Display Network", "Display", 35000, 5400, 32, 21000),
    ("Retargeting - Display GDN", "Display", 28000, 4100, 25, 17000),

    ("Diwali Sale - YouTube Skippable", "Video", 33000, 2900, 140, 132000),
    ("Product Demo - YouTube InStream", "Video", 27000, 2200, 95, 89000),
    ("Brand Film - YouTube Bumper", "Video", 18000, 3100, 40, 41000),
]


def get_connection():
    """Returns a SQLite connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(reset: bool = True):
    """Creates the campaigns table and seeds it with fake data.

    reset=True drops any existing table first, so re-running this file
    always gives you a clean, predictable dataset.
    """
    conn = get_connection()
    cur = conn.cursor()

    if reset:
        cur.execute("DROP TABLE IF EXISTS campaigns")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            channel TEXT NOT NULL,
            spend REAL NOT NULL,
            clicks INTEGER NOT NULL,
            conversions INTEGER NOT NULL,
            revenue REAL NOT NULL
        )
        """
    )

    cur.execute("SELECT COUNT(*) FROM campaigns")
    count = cur.fetchone()[0]

    if count == 0:
        cur.executemany(
            """
            INSERT INTO campaigns (name, channel, spend, clicks, conversions, revenue)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            SEED_CAMPAIGNS,
        )
        conn.commit()
        print(f"Seeded {len(SEED_CAMPAIGNS)} campaigns into {DB_PATH}")
    else:
        print(f"Database already has {count} campaigns, skipped seeding.")

    conn.close()


if __name__ == "__main__":
    init_db(reset=True)
