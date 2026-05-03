import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

from handlers.habits import add_habit, list_habits, delete_habit, confirm_delete_callback
from handlers.checkin import checkin, checkin_callback
from handlers.stats import stats
from scheduler import setup_scheduler
from database import init_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")


async def start(update, context):
    await update.message.reply_text(
        "🌿 Привет! Я *HabitBot* — твой трекер привычек.\n\n"
        "Команды:\n"
        "/add <название> — добавить привычку\n"
        "/list — список привычек\n"
        "/done — отметить выполненное за сегодня\n"
        "/stats — статистика и streak 🔥\n"
        "/delete — удалить привычку",
        parse_mode="Markdown"
    )


async def post_init(app):
    await init_db()
    setup_scheduler(app)
    print("✅ HabitBot запущен!")


def main():
    app = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .proxy("http://127.0.0.1:55784")
    .get_updates_proxy("http://127.0.0.1:55784")
    .post_init(post_init)
    .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_habit))
    app.add_handler(CommandHandler("list", list_habits))
    app.add_handler(CommandHandler("done", checkin))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("delete", delete_habit))
    app.add_handler(CallbackQueryHandler(checkin_callback, pattern="^checkin_"))
    app.add_handler(CallbackQueryHandler(confirm_delete_callback, pattern="^delete_"))

    app.run_polling()


if __name__ == "__main__":
    main()