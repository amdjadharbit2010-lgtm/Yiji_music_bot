import os
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-pro")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎹 Piano", callback_data="piano"),
         InlineKeyboardButton("🎸 Guitar", callback_data="guitar")],
        [InlineKeyboardButton("🎻 Violin", callback_data="violin"),
         InlineKeyboardButton("🎺 Trumpet", callback_data="trumpet")],
        [InlineKeyboardButton("🪗 Accordion", callback_data="accordion"),
         InlineKeyboardButton("🥁 Drums", callback_data="drums")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎵 Welcome! Choose your instrument:", reply_markup=reply_markup)

async def choose_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["instrument"] = query.data
    keyboard = [
        [InlineKeyboardButton("😢 Sad", callback_data="sad"),
         InlineKeyboardButton("😊 Happy", callback_data="happy")],
        [InlineKeyboardButton("😌 Calm", callback_data="calm"),
         InlineKeyboardButton("🔥 Energetic", callback_data="energetic")],
        [InlineKeyboardButton("💔 Romantic", callback_data="romantic"),
         InlineKeyboardButton("🌙 Mysterious", callback_data="mysterious")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🎶 Now choose a mood:", reply_markup=reply_markup)

async def choose_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["mood"] = query.data
    keyboard = [
        [InlineKeyboardButton("🟢 Beginner", callback_data="beginner")],
        [InlineKeyboardButton("🟡 Intermediate", callback_data="intermediate")],
        [InlineKeyboardButton("🔴 Advanced", callback_data="advanced")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🎼 Choose your level:", reply_markup=reply_markup)

async def generate_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    level = query.data
    instrument = context.user_data.get("instrument", "piano")
    mood = context.user_data.get("mood", "calm")
    await query.edit_message_text("⏳ Generating your notes...")
    prompt = f"""You are a professional music teacher. Generate detailed sheet music notes for:
- Instrument: {instrument}
- Mood: {mood}
- Level: {level}

Include:
1. A short melody with note names (C, D, E, F, G, A, B)
2. Rhythm pattern
3. Tempo suggestion (BPM)
4. Fingering tips
5. A second variation of the melody

Format it clearly and make it unique every time."""
    response = await model.generate_content_async(prompt)
    keyboard = [[InlineKeyboardButton("🔄 Generate Again", callback_data=level),
                 InlineKeyboardButton("🏠 Start Over", callback_data="restart")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"🎵 Here are your notes:\n\n{response.text}", reply_markup=reply_markup)

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🎹 Piano", callback_data="piano"),
         InlineKeyboardButton("🎸 Guitar", callback_data="guitar")],
        [InlineKeyboardButton("🎻 Violin", callback_data="violin"),
         InlineKeyboardButton("🎺 Trumpet", callback_data="trumpet")],
        [InlineKeyboardButton("🪗 Accordion", callback_data="accordion"),
         InlineKeyboardButton("🥁 Drums", callback_data="drums")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🎵 Choose your instrument:", reply_markup=reply_markup)

instruments = ["piano", "guitar", "violin", "trumpet", "accordion", "drums"]
moods = ["sad", "happy", "calm", "energetic", "romantic", "mysterious"]
levels = ["beginner", "intermediate", "advanced"]

app = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()
app.add_handler(CommandHandler("start", start))
for i in instruments:
    app.add_handler(CallbackQueryHandler(choose_style, pattern=f"^{i}$"))
for m in moods:
    app.add_handler(CallbackQueryHandler(choose_level, pattern=f"^{m}$"))
for l in levels:
    app.add_handler(CallbackQueryHandler(generate_notes, pattern=f"^{l}$"))
app.add_handler(CallbackQueryHandler(restart, pattern="^restart$"))
app.run_polling()
