import aiosqlite
import os

DB_PATH = "futbol_cards.db"

async def get_db():
    return await aiosqlite.connect(DB_PATH)

async def init_db():
    """Inicializa todas las tablas de la base de datos."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id    INTEGER PRIMARY KEY,
                guild_id   INTEGER NOT NULL,
                rolls_used INTEGER DEFAULT 0,
                wishlist   TEXT    DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                guild_id   INTEGER NOT NULL,
                player_id  TEXT    NOT NULL,
                obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cooldowns (
                user_id    INTEGER NOT NULL,
                guild_id   INTEGER NOT NULL,
                command    TEXT    NOT NULL,
                expires_at REAL    NOT NULL,
                PRIMARY KEY (user_id, guild_id, command)
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_cards_user ON cards(user_id, guild_id)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_cards_player ON cards(player_id)
        """)
        await db.commit()
    print("  ✅ Base de datos inicializada")

# ─── USUARIOS ────────────────────────────────────────────────────────────────

async def ensure_user(user_id: int, guild_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, guild_id) VALUES (?, ?)",
            (user_id, guild_id)
        )
        await db.commit()

async def get_user(user_id: int, guild_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE user_id=? AND guild_id=?",
            (user_id, guild_id)
        ) as cur:
            return await cur.fetchone()

# ─── CARTAS ──────────────────────────────────────────────────────────────────

async def add_card(user_id: int, guild_id: int, player_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO cards (user_id, guild_id, player_id) VALUES (?, ?, ?)",
            (user_id, guild_id, player_id)
        )
        await db.commit()

async def get_user_cards(user_id: int, guild_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT player_id, COUNT(*) as cantidad, MIN(obtained_at) as primera_vez
               FROM cards WHERE user_id=? AND guild_id=?
               GROUP BY player_id ORDER BY primera_vez DESC""",
            (user_id, guild_id)
        ) as cur:
            return await cur.fetchall()

async def count_user_cards(user_id: int, guild_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM cards WHERE user_id=? AND guild_id=?",
            (user_id, guild_id)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0

async def count_unique_cards(user_id: int, guild_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(DISTINCT player_id) FROM cards WHERE user_id=? AND guild_id=?",
            (user_id, guild_id)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0

async def has_card(user_id: int, guild_id: int, player_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT 1 FROM cards WHERE user_id=? AND guild_id=? AND player_id=? LIMIT 1",
            (user_id, guild_id, player_id)
        ) as cur:
            return await cur.fetchone() is not None

async def remove_one_card(user_id: int, guild_id: int, player_id: str) -> bool:
    """Elimina una copia de una carta. Retorna True si se eliminó."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT id FROM cards WHERE user_id=? AND guild_id=? AND player_id=?
               ORDER BY obtained_at DESC LIMIT 1""",
            (user_id, guild_id, player_id)
        ) as cur:
            row = await cur.fetchone()
        if not row:
            return False
        await db.execute("DELETE FROM cards WHERE id=?", (row[0],))
        await db.commit()
        return True

# ─── RANKING ─────────────────────────────────────────────────────────────────

async def get_top_collectors(guild_id: int, limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT user_id, COUNT(*) as total, COUNT(DISTINCT player_id) as unicos
               FROM cards WHERE guild_id=?
               GROUP BY user_id ORDER BY total DESC LIMIT ?""",
            (guild_id, limit)
        ) as cur:
            return await cur.fetchall()

async def get_most_rolled_players(guild_id: int, limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT player_id, COUNT(*) as veces
               FROM cards WHERE guild_id=?
               GROUP BY player_id ORDER BY veces DESC LIMIT ?""",
            (guild_id, limit)
        ) as cur:
            return await cur.fetchall()

# ─── WISHLIST ────────────────────────────────────────────────────────────────

async def get_wishlist(user_id: int, guild_id: int) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT wishlist FROM users WHERE user_id=? AND guild_id=?",
            (user_id, guild_id)
        ) as cur:
            row = await cur.fetchone()
            if row and row[0]:
                return [p for p in row[0].split(",") if p]
            return []

async def set_wishlist(user_id: int, guild_id: int, wishlist: list):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET wishlist=? WHERE user_id=? AND guild_id=?",
            (",".join(wishlist), user_id, guild_id)
        )
        await db.commit()
