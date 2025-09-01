from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import random
import string
import json
import os
import asyncio
from server import keep_alive   # ✅ Flask server import
from dotenv import load_dotenv   # ✅ Load .env file

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ✅ Admins list (apna ID + dusre user ka ID)
ADMINS = [1350597307, 1140856158]

# JSON file jisme codes save honge
DATA_FILE = "codes.json"

# Load codes from JSON
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        code_file_map = json.load(f)
else:
    code_file_map = {}

# ✅ Unique code generator
def generate_code():
    return "vid" + ''.join(random.choices(string.digits, k=2)) + ''.join(random.choices(string.ascii_lowercase, k=1))

# ✅ Save codes to JSON
def save_codes():
    with open(DATA_FILE, "w") as f:
        json.dump(code_file_map, f)

# ✅ Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args:
        code = args[0]
        if code in code_file_map:
            file_info = code_file_map[code]
            file_id = file_info["file_id"]
            # Send file and get sent message
            sent_msg = await update.message.reply_document(file_id, caption="✅ Yeh rahi tumhari file 👇")
            # Schedule auto-delete after 2 minutes
            asyncio.create_task(auto_delete(context, sent_msg.chat_id, sent_msg.message_id))
        else:
            await update.message.reply_text("❌ Invalid code!")
    else:
        await update.message.reply_text("👋 Send a valid code like `/start vidXX`")

# ✅ Auto-delete function
async def auto_delete(context: ContextTypes.DEFAULT_TYPE, chat_id, message_id):
    await asyncio.sleep(120)  # 2 minutes
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except:
        pass  # ignore if already deleted

# ✅ File upload by Admin
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMINS:
        await update.message.reply_text("❌ Only admin can upload files.")
        return

    file = update.message.document or update.message.video
    if not file:
        await update.message.reply_text("❌ Please send a valid document or video.")
        return

    file_id = file.file_id
    code = generate_code()
    code_file_map[code] = {
        "file_id": file_id
    }
    save_codes()  # Save to JSON

    await update.message.reply_text(
        f"✅ File saved with code: `{code}`\n\n👉 Share this link:\n`https://t.me/{context.bot.username}?start={code}`",
        parse_mode="Markdown"
    )

# ✅ Main function
def main():
    keep_alive()   # ✅ Flask server ko start karo (Railway ke liye)
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.VIDEO, handle_file))

    print("🤖 Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
