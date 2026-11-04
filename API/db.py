
import sqlite3
from pathlib import Path

DATABASE = Path(__file__).with_name("ll_universe.db")


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            score_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            ship_name TEXT,
            FOREIGN KEY (player_id) REFERENCES players(player_id)
        )
    """)

    cursor.execute("PRAGMA table_info(scores)")
    score_columns = {row["name"] for row in cursor.fetchall()}

    if "ship_name" not in score_columns:
        cursor.execute(
            "ALTER TABLE scores ADD COLUMN ship_name TEXT"
        )

    connection.commit()
    connection.close()


def register_player(nickname):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO players (nickname) VALUES (?)",
            (nickname,)
        )
        connection.commit()
        player_id = cursor.lastrowid

    except sqlite3.IntegrityError:
        cursor.execute(
            "SELECT player_id FROM players WHERE nickname = ?",
            (nickname,)
        )
        player = cursor.fetchone()

        if player is None:
            connection.close()
            raise

        player_id = player["player_id"]

    connection.close()
    return player_id


def save_score(player_id, score, ship_name=None):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO scores (player_id, score, ship_name)
        VALUES (?, ?, ?)
        """,
        (player_id, score, ship_name)
    )

    connection.commit()
    connection.close()


def get_leaderboard():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT players.nickname, scores.score, scores.ship_name
        FROM players
        JOIN scores ON scores.player_id = players.player_id
        WHERE scores.score_id = (
            SELECT candidate.score_id
            FROM scores AS candidate
            WHERE candidate.player_id = players.player_id
            ORDER BY candidate.score DESC, candidate.score_id DESC
            LIMIT 1
        )
        ORDER BY scores.score DESC
        LIMIT 10
    """)

    leaderboard = [dict(row) for row in cursor.fetchall()]

    connection.close()
    return leaderboard


def clear_leaderboard():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM scores")
    deleted = cursor.rowcount

    connection.commit()
    connection.close()

    return deleted
