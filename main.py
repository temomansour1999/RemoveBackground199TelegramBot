import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from rembg import remove
from PIL import Image

# ====== Environment Variables ======
BOT_TOKEN  = os.getenv("BOT_TOKEN")
CHANNEL    = os.getenv("CHANNEL")  # Example "@MyChannel"

# ===================================
bot = Client("bgRemoverBot", bot_token=BOT_TOKEN)
users = {}  # store user language

# ================== START ==================
@bot.on_message(filters.command("start"))
async def start(_, msg):
    users[msg.chat.id] = None
    await msg.reply(
        "Choose Language:\nاختر لغتك:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("English 🇺🇸", callback_data="lang_en")],
            [InlineKeyboardButton("العربية 🇮🇶", callback_data="lang_ar")],
        ])
    )

# ================ LANGUAGE SELECT ================
@bot.on_callback_query(filters.regex("lang_"))
async def choose_lang(_, cb):
    lang = cb.data.split("_")[1]
    users[cb.from_user.id] = lang

    text = "Join the channel to continue 👇" if lang=="en" else "يرجى الانضمام للقناة 👇"
    await cb.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Channel", url=f"https://t.me/{CHANNEL.replace('@','')}")],
            [InlineKeyboardButton("Done ✓" if lang=="en" else "تم ✓", callback_data="check")],
        ])
    )

# ================ CHECK SUBSCRIPTION ================
@bot.on_callback_query(filters.regex("check"))
async def check(_, cb):
    try:
        member = await bot.get_chat_member(CHANNEL, cb.from_user.id)
        if member.status in ["member","administrator","creator"]:
            lang = users.get(cb.from_user.id, "en")
            return await cb.message.edit_text(
                "Send me a photo 🔽" if lang=="en" else "أرسل صورتك الآن 🔽"
            )
    except:
        pass

    await cb.answer(
        "You must join the channel first!" 
        if users.get(cb.from_user.id)=="en" else "يجب ان تنضم للقناة اولاً!",
        show_alert=True
    )

# ================ REMOVE BACKGROUND ================
@bot.on_message(filters.photo)
async def remove_background(_, message):
    lang = users.get(message.chat.id, "en")
    await message.reply("Processing..." if lang == "en" else "جاري معالجة الصورة...")

    input_image = await message.download()
    output_image = "output.png"

    try:
        img = Image.open(input_image)
        result = remove(img)        # background removed
        result.save(output_image)   # save as png

        await message.reply_document(output_image)

        os.remove(output_image)
    except Exception as e:
        await message.reply(f"Error ❌\n{e}")

    os.remove(input_image)

# ================== RUN BOT ==================
if __name__ == "__main__":
    bot.run()
