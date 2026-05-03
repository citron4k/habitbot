from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from database import add_habit_db, get_habits, delete_habit_db


async def add_habit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            "✏️ Укажи название привычки:\n`/add Медитация`",
            parse_mode="Markdown"
        )
        return

    name = " ".join(context.args).strip()
    if len(name) > 50:
        await update.message.reply_text("❌ Название слишком длинное (максимум 50 символов).")
        return

    habits = await get_habits(user_id)
    if len(habits) >= 10:
        await update.message.reply_text("❌ Максимум 10 привычек. Удали одну, чтобы добавить новую.")
        return

    await add_habit_db(user_id, name)
    await update.message.reply_text(f"✅ Привычка *{name}* добавлена!", parse_mode="Markdown")


async def list_habits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    habits = await get_habits(user_id)

    if not habits:
        await update.message.reply_text(
            "📋 У тебя пока нет привычек.\nДобавь первую: `/add Медитация`",
            parse_mode="Markdown"
        )
        return

    text = "📋 *Твои привычки:*\n\n"
    for i, h in enumerate(habits, 1):
        text += f"{i}. {h['name']}\n"

    await update.message.reply_text(text, parse_mode="Markdown")


async def delete_habit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    habits = await get_habits(user_id)

    if not habits:
        await update.message.reply_text("У тебя нет привычек для удаления.")
        return

    keyboard = [
        [InlineKeyboardButton(f"🗑 {h['name']}", callback_data=f"delete_{h['id']}")]
        for h in habits
    ]
    await update.message.reply_text(
        "Какую привычку удалить?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def confirm_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    habit_id = int(query.data.split("_")[1])

    habits = await get_habits(user_id)
    habit = next((h for h in habits if h["id"] == habit_id), None)

    if not habit:
        await query.edit_message_text("❌ Привычка не найдена.")
        return

    await delete_habit_db(habit_id, user_id)
    await query.edit_message_text(f"🗑 Привычка *{habit['name']}* удалена.", parse_mode="Markdown")