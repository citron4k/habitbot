from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from database import get_all_user_ids, get_habits, get_today_checkins

REMINDER_HOUR = 9    
REMINDER_MINUTE = 0


async def send_daily_reminder(app):
    user_ids = await get_all_user_ids()

    for user_id in user_ids:
        habits = await get_habits(user_id)
        if not habits:
            continue

        done_ids = await get_today_checkins(user_id)
        undone = [h for h in habits if h["id"] not in done_ids]

        if not undone:
            continue 

        names = "\n".join(f"⬜ {h['name']}" for h in undone)

        try:
            await app.bot.send_message(
                chat_id=user_id,
                text=(
                    "☀️ Не забудь про свои привычки сегодня:\n\n"
                    f"{names}\n\n"
                    "Нажми /done чтобы отметить выполненное."
                ),
                parse_mode="Markdown"
            )
        except Exception:
            pass  


def setup_scheduler(app):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_daily_reminder,
        trigger=CronTrigger(hour=REMINDER_HOUR, minute=REMINDER_MINUTE),
        args=[app],
        id="daily_reminder"
    )
    scheduler.start()
    print(f"⏰ Планировщик запущен. Напоминания в {REMINDER_HOUR:02d}:{REMINDER_MINUTE:02d} UTC")
