import logging
import time

from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired,
    PeerIdInvalid,
    UsernameNotOccupied,
    UserNotParticipant,
)
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup

from TGN import DRAGONS as SUDO_USERS
from TGN import pbot
from TGN.modules.sql import forceSubscribe_sql as sql

logging.basicConfig(level=logging.INFO)

static_data_filter = filters.create(
    lambda _, __, query: query.data == "onUnMuteRequest"
)


@pbot.on_callback_query(static_data_filter)
def _onUnMuteRequest(client, cb):
    user_id = cb.from_user.id
    chat_id = cb.message.chat.id
    chat_db = sql.fs_settings(chat_id)
    if chat_db:
        channel = chat_db.channel
        chat_member = client.get_chat_member(chat_id, user_id)
        if chat_member.restricted_by:
            if chat_member.restricted_by.id == (client.get_me()).id:
                try:
                    client.get_chat_member(channel, user_id)
                    client.unban_chat_member(chat_id, user_id)
                    cb.message.delete()
                    # if cb.message.reply_to_message.from_user.id == user_id:
                    # cb.message.delete()
                except UserNotParticipant:
                    client.answer_callback_query(
                        cb.id,
                        text=f"❗ Join our @{channel} channel and press 'Unmute Me' button.",
                        show_alert=True,
                    )
            else:
                client.answer_callback_query(
                    cb.id,
                    text="❗ You have been muted by admins due to some other reason.",
                    show_alert=True,
                )
        else:
            if (
                not client.get_chat_member(chat_id, (client.get_me()).id).status
                == "administrator"
            ):
                client.send_message(
                    chat_id,
                    f"❗ **{cb.from_user.mention} is trying to UnMute himself but i can't unmute him because i am not an admin in this chat add me as admin again.**\n__#Leaving this chat...__",
                )

            else:
                client.answer_callback_query(
                    cb.id,
                    text="❗ Warning! Don't press the button when you cn talk.",
                    show_alert=True,
                )


@pbot.on_message(filters.text & ~filters.private & ~filters.edited, group=1)
def _check_member(client, message):
    chat_id = message.chat.id
    chat_db = sql.fs_settings(chat_id)
    if chat_db:
        user_id = message.from_user.id
        if (
            not client.get_chat_member(chat_id, user_id).status
            in ("administrator", "creator")
            and not user_id in SUDO_USERS
        ):
            channel = chat_db.channel
            try:
                client.get_chat_member(channel, user_id)
            except UserNotParticipant:
                try:
                    sent_message = message.reply_text(
                        "Welcome {} 🎉 \n **You haven't joined our @{} Channel yet**👷 \n \nPlease Join [Our Channel](https://t.me/{}) and hit the **UNMUTE ME** Button. \n \n ".format(
                            message.from_user.mention, channel, channel
                        ),
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        "🌟Join Channel⭐",
                                        url="https://t.me/{}".format(channel),
                                    )
                                ],
                                [
                                    InlineKeyboardButton(
                                        "🔇Unmute Me🔕", callback_data="onUnMuteRequest"
                                    )
                                ],
                            ]
                        ),
                    )
                    client.restrict_chat_member(
                        chat_id, user_id, ChatPermissions(can_send_messages=False)
                    )
                except ChatAdminRequired:
                    sent_message.edit(
                        "😕 **GodfatherBot is not admin here..**\n__Give me ban permissions and retry.. \n#Ending FSub...__"
                    )

            except ChatAdminRequired:
                client.send_message(
                    chat_id,
                    text=f"😕 **I not an admin of @{channel} channel.**\n__Give me admin of that channel and retry.\n#Ending FSub...__",
                )


@pbot.on_message(filters.command(["forcesubscribe", "fsub"]) & ~filters.private)
def config(client, message):
    user = client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status is "creator" or user.user.id in SUDO_USERS:
        chat_id = message.chat.id
        if len(message.command) > 1:
            input_str = message.command[1]
            input_str = input_str.replace("@", "")
            if input_str.lower() in ("off", "no", "disable"):
                sql.disapprove(chat_id)
                message.reply_text("❌ **Force Subscribe is Disabled Successfully.**")
            elif input_str.lower() in ("clear"):
                sent_message = message.reply_text(
                    "**Unmuting all members who are muted by me...**"
                )
                try:
                    for chat_member in client.get_chat_members(
                        message.chat.id, filter="restricted"
                    ):
                        if chat_member.restricted_by.id == (client.get_me()).id:
                            client.unban_chat_member(chat_id, chat_member.user.id)
                            time.sleep(1)
                    sent_message.edit("✅ **Unmuted all members who are muted by me.**")
                except ChatAdminRequired:
                    sent_message.edit(
                        "😕 **I am not an admin in this chat.**\n__I can't unmute members because i am not an admin in this chat make me admin with ban user permission.__"
                    )
            else:
                try:
                    client.get_chat_member(input_str, "me")
                    sql.add_channel(chat_id, input_str)
                    message.reply_text(
                        f"✅ **Force Subscribe is Enabled**\n__Force Subscribe is enabled, all the group members have to subscribe this [channel](https://t.me/{input_str}) in order to send messages in this group.__",
                        disable_web_page_preview=True,
                    )
                except UserNotParticipant:
                    message.reply_text(
                        f"😕 **Not an Admin in the Channel**\n__I am not an admin in the [channel](https://t.me/{input_str}). Add me as a admin in order to enable ForceSubscribe.__",
                        disable_web_page_preview=True,
                    )
                except (UsernameNotOccupied, PeerIdInvalid):
                    message.reply_text(f"❗ **Invalid Channel Username.**")
                except Exception as err:
                    message.reply_text(f"❗ **ERROR:** ```{err}```")
        else:
            if sql.fs_settings(chat_id):
                message.reply_text(
                    f"✅ **Force Subscribe is enabled in this chat.**\n__For this [Channel](https://t.me/{sql.fs_settings(chat_id).channel})__",
                    disable_web_page_preview=True,
                )
            else:
                message.reply_text("❌ **Force Subscribe is disabled in this chat.**")
    else:
        message.reply_text(
            "❗ **Group Creator Required**\n__You have to be the group creator to do that.__"
        )


__help__ = """
* Принудительная подписка:*

❂ GodfatherBot может отключать звук у пользователей, которые не подписаны на ваш канал, пока они не подпишутся.
❂ Когда эта функция включена, я буду отключать звук у неподписанных пользователей и показывать им кнопку отключения звука. Когда они нажмут на кнопку, я отключу их.
❂*Настройка*
*Один создатель*
❂ Добавьте меня в вашу группу как администратора
❂ Добавьте меня в свой канал как администратора 
 
*Команды*
❂ /fsub {имя пользователя канала} - включение и настройка канала.

  💡 Сначала сделайте это...

❂ /fsub - Получить текущие настройки.
❂ /fsub disable - Отключить принудительную подписку...

  💡Если вы отключили fsub, вам нужно снова установить его для работы... /fsub {имя пользователя канала} 

❂ /fsub clear - Отключить звук всем пользователям, которые были отключены мной.

*Федерация*
Все весело, пока спамер не начинает входить в вашу группу, и вам приходится блокировать его. Тогда вам нужно начать запрещать все больше и больше, и это больно.
Но тогда у вас много групп, и вы не хотите, чтобы этот спамер был в одной из ваших групп - как вы можете справиться с этим? Вам придется вручную блокировать его во всех ваших группах?\n
*Больше нет! С Федерацией, вы можете сделать так, чтобы бан в одном чате накладывался на все остальные чаты.\n
Вы даже можете назначить администраторов федерации, так что ваш доверенный администратор сможет запретить всех спамеров в чатах, которые вы хотите защитить.\n
*Команды:*\n
Теперь федерации разделены на 3 секции для вашего удобства.
- `/fedownerhelp`*:* Предоставляет помощь по созданию феди и командам для владельцев.
- `/fedadminhelp`*:* Предоставляет помощь по командам администрирования федерации
- `/feduserhelp`*:* Предоставляет помощь по командам, которые может использовать каждый.
"""
__mod_name__ = "F-Sub/Feds"
