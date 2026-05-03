from datetime import date
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from database import get_habits, get_today_checkins, mark_done, unmark_done


def build_checkin_keyboard(habits: list[dict], done_ids: set[int]) -> InlineKeyboardMarkup:
    keyboard = []
    for h in habits:
        icon = "✅" if h["id"] in done_ids else "⬜"
        keyboard.append([
            InlineKeyboardButton(
                f"{icon} {h['name']}",
                callback_data=f"checkin_{h['id']}"
            )
        ])
    return InlineKeyboardMarkup(keyboard)


async def checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    habits = await get_habits(user_id)

    if not habits:
        await update.message.reply_text(
            "📋 У тебя нет привычек. Добавь: `/add Медитация`",
            parse_mode="Markdown"
        )
        return

    done_ids = await get_today_checkins(user_id)
    keyboard = build_checkin_keyboard(habits, done_ids)

    total = len(habits)
    done = len(done_ids)

    await update.message.reply_text(
        f"📅 *{date.today().strftime('%d %B %Y')}*\n"
        f"Выполнено: {done}/{total}\n\n"
        "Нажимай на привычки, чтобы отметить:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


async def checkin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    habit_id = int(query.data.split("_")[1])
    today = str(date.today())

    done_ids = await get_today_checkins(user_id)

    if habit_id in done_ids:
        await unmark_done(habit_id, user_id, today)
    else:
        await mark_done(habit_id, user_id, today)

    habits = await get_habits(user_id)
    done_ids = await get_today_checkins(user_id)
    keyboard = build_checkin_keyboard(habits, done_ids)

    total = len(habits)
    done = len(done_ids)

    all_done = done == total and total > 0
    header = "🎉 *Все привычки выполнены! Отличная работа!*\n\n" if all_done else ""

    await query.edit_message_text(
        f"{header}📅 *{date.today().strftime('%d %B %Y')}*\n"
        f"Выполнено: {done}/{total}\n\n"
        "Нажимай на привычки, чтобы отметить:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )