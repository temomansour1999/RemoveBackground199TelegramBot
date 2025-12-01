import os
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==== Environment Variables for Railway ====
BOT_TOKEN  = os.getenv("BOT_TOKEN")
REMOVE_API = os.getenv("REMOVE_API")
CHANNEL    = os.getenv("CHANNEL")  # EXAMPLE: "@MyChannel" or "MyChannelID"

# ================== BOT ====================
bot = Client("bgRemover", bot_token=BOT_TOKEN)

# Store user language in memory (short and fast)
users = {}


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


@bot.on_callback_query(filters.regex("lang_"))
async def choose_lang(_, cb):
    lang = cb.data.split("_")[1]
    users[cb.from_user.id] = lang

    txt = "Join the channel to continue 👇" if lang == "en" else "يرجى الانضمام للقناة للاستمرار 👇"
    await cb.message.edit_text(
        txt,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Channel", url=f"https://t.me/{CHANNEL.replace('@','')}")],
            [InlineKeyboardButton("Done ✓" if lang=="en" else "تم ✓", callback_data="check")]
        ])
    )


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
        "You must join the channel first!" if users.get(cb.from_user.id)=="en" else "يجب ان تنضم للقناة اولاً!",
        show_alert=True
    )


# ========== Background Remove Handler ==========
@bot.on_message(filters.photo)
async def remove_bg(_, msg):
    lang = users.get(msg.chat.id, "en")
    await msg.reply("Processing..." if lang=="en" else "جاري معالجة الصورة...")

    img_path = await msg.download()
    result = requests.post(
        "https://api.remove.bg/v1.0/removebg",
        files={"image_file": open(img_path, "rb")},
        data={"size": "auto"},
        headers={"X-Api-Key": REMOVE_API}
    )

    if result.status_code == 200:
        out = "done.png"
        with open(out, "wb") as f:
            f.write(result.content)
        await msg.reply_document(out)
        os.remove(out)
    else:
        await msg.reply("Error removing background ❌")

    os.remove(img_path)


if __name__ == "__main__":
    bot.run()
