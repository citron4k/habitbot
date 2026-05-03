from telegram import Update
from telegram.ext import ContextTypes

from database import get_habits, get_streak, get_total_checkins


def streak_emoji(streak: int) -> str:
    if streak == 0:
        return "😴"
    elif streak < 3:
        return "🌱"
    elif streak < 7:
        return "🔥"
    elif streak < 30:
        return "💪"
    else:
        return "🏆"


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    habits = await get_habits(user_id)

    if not habits:
        await update.message.reply_text(
            "📋 У тебя нет привычек. Добавь: `/add Медитация`",
            parse_mode="Markdown"
        )
        return

    text = "📊 *Твоя статистика:*\n\n"

    for h in habits:
        streak = await get_streak(h["id"], user_id)
        total = await get_total_checkins(h["id"], user_id)
        emoji = streak_emoji(streak)

        text += (
            f"*{h['name']}*\n"
            f"  {emoji} Streak: {streak} дн.\n"
            f"  📆 Всего выполнено: {total} раз\n\n"
        )

    await update.message.reply_text(text, parse_mode="Markdown")