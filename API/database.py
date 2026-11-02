
import sqlite3

DATABASE = "API/ll_universe.db"


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
            FOREIGN KEY (player_id) REFERENCES players(player_id)
        )
    """)

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
        player_id = cursor.fetchone()["player_id"]

    connection.close()
    return player_id


def save_score(player_id, score):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO scores (player_id, score) VALUES (?, ?)",
        (player_id, score)
    )

    connection.commit()
    connection.close()


def get_leaderboard():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT players.nickname, MAX(scores.score) AS score
        FROM players
        JOIN scores ON players.player_id = scores.player_id
        GROUP BY players.player_id
        ORDER BY score DESC
        LIMIT 10
    """)

    leaderboard = [
        dict(row) for row in cursor.fetchall()
    ]

    connection.close()
    return leaderboard
