from platform import python_version as y
from telegram import __version__ as o
from pyrogram import __version__ as z
from telethon import __version__ as s
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import filters
from TGN import pbot
from TGN.utils.errors import capture_err
from TGN.utils.functions import make_carbon


@pbot.on_message(filters.command("carbon"))
@capture_err
async def carbon_func(_, message):
    if not message.reply_to_message:
        return await message.reply_text("`Reply to a text message to make carbon.`")
    if not message.reply_to_message.text:
        return await message.reply_text("`Reply to a text message to make carbon.`")
    m = await message.reply_text("`Preparing Carbon`")
    carbon = await make_carbon(message.reply_to_message.text)
    await m.edit("`Uploading`")
    await pbot.send_photo(message.chat.id, carbon)
    await m.delete()
    carbon.close()


MEMEK = "https://telegra.ph/file/d915971ae531844d8e96b.jpg"

@pbot.on_message(filters.command("about"))
async def repo(_, message):
    await message.reply_photo(
        photo=MEMEK,
        caption=f"""✨ **Hᴇʏ I Aᴍ GodfatherBot** 

**🧑‍💻 Powered By : [GodfatherNetwork](https://t.me/The_Godfather_Network)**
**Dev -  : [Null-coder](https://t.me/Shubhanshutya)**
**Dev 2  : [Boo](https://t.me/Timesisnotwaiting)**
**Owner Hu vro  : [Akki](https://t.me/Godfatherakkii)**
**You already know I am music and music bot so why I introduced my self  .**

**My fev word only for girls Can you Marry me 🥀 because I like you .**
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Update", url="https://t.me/The_Godfather_Network"), 
                    InlineKeyboardButton(
                        "Support", url="https://t.me/GodfatherSupport")
                ]
            ]
        )
    )
