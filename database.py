import aiosqlite
from datetime import date

DB_PATH = "habitbot.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                created_at TEXT DEFAULT (date('now'))
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                checked_date TEXT NOT NULL,
                UNIQUE(habit_id, checked_date)
            )
        """)
        await db.commit()


async def add_habit_db(user_id: int, name: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO habits (user_id, name) VALUES (?, ?)",
            (user_id, name)
        )
        await db.commit()
        return cursor.lastrowid


async def get_habits(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM habits WHERE user_id = ? ORDER BY id",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def delete_habit_db(habit_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM habits WHERE id = ? AND user_id = ?",
            (habit_id, user_id)
        )
        await db.execute(
            "DELETE FROM checkins WHERE habit_id = ? AND user_id = ?",
            (habit_id, user_id)
        )
        await db.commit()


async def mark_done(habit_id: int, user_id: int, checked_date: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                "INSERT INTO checkins (habit_id, user_id, checked_date) VALUES (?, ?, ?)",
                (habit_id, user_id, checked_date)
            )
            await db.commit()
            return True
        except Exception:
            return False


async def unmark_done(habit_id: int, user_id: int, checked_date: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM checkins WHERE habit_id = ? AND user_id = ? AND checked_date = ?",
            (habit_id, user_id, checked_date)
        )
        await db.commit()


async def get_today_checkins(user_id: int) -> set[int]:
    today = str(date.today())
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT habit_id FROM checkins WHERE user_id = ? AND checked_date = ?",
            (user_id, today)
        ) as cursor:
            rows = await cursor.fetchall()
            return {row[0] for row in rows}


async def get_streak(habit_id: int, user_id: int) -> int:
    """Считает текущий streak (подряд идущих дней) для привычки."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT checked_date FROM checkins WHERE habit_id = ? AND user_id = ? ORDER BY checked_date DESC",
            (habit_id, user_id)
        ) as cursor:
            rows = await cursor.fetchall()

    if not rows:
        return 0

    from datetime import timedelta
    streak = 0
    current = date.today()

    for (checked_date_str,) in rows:
        checked = date.fromisoformat(checked_date_str)
        if checked == current or checked == current - timedelta(days=1) and streak == 0:
            # Начинаем с сегодня или вчера (если сегодня ещё не отметили)
            if checked == current - timedelta(days=1) and streak == 0:
                pass
            streak += 1
            current = checked - timedelta(days=1)
        elif checked == current:
            streak += 1
            current = checked - timedelta(days=1)
        else:
            break

    return streak


async def get_total_checkins(habit_id: int, user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM checkins WHERE habit_id = ? AND user_id = ?",
            (habit_id, user_id)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def get_all_user_ids() -> list[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT DISTINCT user_id FROM habits") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]