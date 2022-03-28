# A Powerful Music And Management Bot
# Property Of Rocks Indian Largest Chatting Group
# Without Credit (Mother Fucker)
# Rocks © @Dr_Asad_Ali © Rocks
# Owner Asad + Harshit
# Roses are red, Violets are blue, A face like yours, Belongs in a zoo


import html
from io import BytesIO
from typing import Optional, List

from telegram import ChatPermissions
from telegram import Message, Update, Bot, User, Chat
from telegram.error import BadRequest, TelegramError
from telegram.ext import run_async, CommandHandler, MessageHandler, Filters
from telegram.utils.helpers import mention_html
import html
from io import BytesIO
from typing import Optional, List

from telegram import Message, Update, Bot, User, Chat
from telegram.error import BadRequest, TelegramError
from telegram.ext import run_async, CommandHandler, MessageHandler, Filters
from telegram.utils.helpers import mention_html


import TGN.modules.sql.global_mutes_sql as sql
from TGN import dispatcher, EVENT_LOGS, SUPPORT_CHAT, DRAGONS, DEMONS, GBAN_ERRORS
from TGN.modules.helper_funcs.chat_status import dev_plus
from TGN.modules.helper_funcs.chat_status import user_admin, is_user_admin
from TGN.modules.helper_funcs.extraction import extract_user, extract_user_and_text
from TGN.modules.helper_funcs.filters import CustomFilters
from TGN.modules.sql.users_sql import get_all_chats

GMUTE_ENFORCE_GROUP = 6

STRICT_GMUTE = True
OWNER_ID = 1669178360
OFFICERS = 1669178360
SUPPORT_USERS = 1669178360
SUDO_USERS = 1669178360
USERMUTED = 5253594251


ERROR_DUMP = EVENT_LOGS

@dev_plus
def gmute(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect..",
        )
        return

    if int(user_id) in DEV_USERS:
        message.reply_text(
            "That user is part of the Association\nI can't act against our own.",
        )
        return

    if user_id == bot.id:
        message.reply_text("You uhh...want me to punch myself?")
        return

    if user_id in [777000, 1087968824]:
        message.reply_text("Fool! You can't attack Telegram's native tech!")
        return

    try:
        user_chat = bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user.")
            return ""
        return

    if user_chat.type != "private":
        message.reply_text("That's not a user!")
        return

    if sql.is_user_gmuted(user_id):

        if not reason:
            message.reply_text(
                "This user is already gbanned; I'd change the reason, but you haven't given me one...",
            )
            return

        old_reason = sql.update_gmute_reason(
            user_id,
            user_chat.username or user_chat.first_name,
            reason,
        )
        if old_reason:
            message.reply_text(
                "This user is already gbanned, for the following reason:\n"
                "<code>{}</code>\n"
                "I've gone and updated it with your new reason!".format(
                    html.escape(old_reason),
                ),
                parse_mode=ParseMode.HTML,
            )

        else:
            message.reply_text(
                "This user is already gbanned, but had no reason set; I've gone and updated it!",
            )

        return

    message.reply_text("On it!")

    start_time = time.time()
    datetime_fmt = "%Y-%m-%dT%H:%M"
    current_time = datetime.utcnow().strftime(datetime_fmt)

    if chat.type != "private":
        chat_origin = "<b>{} ({})</b>\n".format(html.escape(chat.title), chat.id)
    else:
        chat_origin = "<b>{}</b>\n".format(chat.id)

    log_message = (
        f"#GMUTED\n"
        f"<b>Originated from:</b> <code>{chat_origin}</code>\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>Banned User:</b> {mention_html(user_chat.id, user_chat.first_name)}\n"
        f"<b>Banned User ID:</b> <code>{user_chat.id}</code>\n"
        f"<b>Event Stamp:</b> <code>{current_time}</code>"
    )

    if reason:
        if chat.type == chat.SUPERGROUP and chat.username:
            log_message += f'\n<b>Reason:</b> <a href="https://telegram.me/{chat.username}/{message.message_id}">{reason}</a>'
        else:
            log_message += f"\n<b>Reason:</b> <code>{reason}</code>"

    if EVENT_LOGS:
        try:
            log = bot.send_message(EVENT_LOGS, log_message, parse_mode=ParseMode.HTML)
        except BadRequest as excp:
            log = bot.send_message(
                EVENT_LOGS,
                log_message
                + "\n\nFormatting has been disabled due to an unexpected error.",
            )

    else:
        send_to_list(bot, log_message, html=True)

    sql.gmute_user(user_id, user_chat.username or user_chat.first_name, reason)

    chats = get_user_com_chats(user_id)
    gbanned_chats = 0

    for chat in chats:
        chat_id = int(chat)

        # Check if this group has disabled gbans
        if not sql.does_chat_gban(chat_id):
            continue

        try:
            bot.ban_chat_member(chat_id, user_id)
            gbanned_chats += 1

        except BadRequest as excp:
            if excp.message in GBAN_ERRORS:
                pass
            else:
                message.reply_text(f"Could not gban due to: {excp.message}")
                if EVENT_LOGS:
                    bot.send_message(
                        EVENT_LOGS,
                        f"Could not gban due to {excp.message}",
                        parse_mode=ParseMode.HTML,
                    )
                else:
                    send_to_list(
                        bot,
                        DRAGONS,
                        f"Could not gban due to: {excp.message}",
                    )
                sql.ungban_user(user_id)
                return
        except TelegramError:
            pass

    if EVENT_LOGS:
        log.edit_text(
            log_message + f"\n<b>Chats affected:</b> <code>{gbanned_chats}</code>",
            parse_mode=ParseMode.HTML,
        )
    else:
        send_to_list(
            bot,
            DRAGONS,
            f"Gban complete! (User banned in <code>{gbanned_chats}</code> chats)",
            html=True,
        )

    end_time = time.time()
    gban_time = round((end_time - start_time), 2)

    if gban_time > 60:
        gban_time = round((gban_time / 60), 2)
        message.reply_text("Done! Gbanned.", parse_mode=ParseMode.HTML)
    else:
        message.reply_text("Done! Gbanned.", parse_mode=ParseMode.HTML)

    try:
        bot.send_message(
            user_id,
            "#EVENT"
            "You have been marked as Malicious and as such have been banned from any future groups we manage."
            f"\n<b>Reason:</b> <code>{html.escape(user.reason)}</code>"
            f"</b>Appeal Chat:</b> @{SUPPORT_CHAT}",
            parse_mode=ParseMode.HTML,
        )
    except:
        pass

@dev_plus
def ungmute(update, context):
    message = update.effective_message  # type: Optional[Message]
    bot = context.bot
    args = context.args
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text("You don't seem to be referring to a user.")
        return

    user_chat = bot.get_chat(user_id)
    if user_chat.type != 'private':
        message.reply_text("That's not a user!")
        return

    if not sql.is_user_gmuted(user_id):
        message.reply_text("This user is not gmuted!")
        return

    muter = update.effective_user  # type: Optional[User]

    message.reply_text("I'll let {} speak again, globally.".format(user_chat.first_name))


    chats = get_all_chats()
    for chat in chats:
        chat_id = chat.chat_id

        # Check if this group has disabled gmutes
        if not sql.does_chat_gmute(chat_id):
            continue

        try:
            member = context.bot.get_chat_member(chat_id, user_id)
            if member.status == 'restricted':
                context.bot.restrict_chat_member(chat_id, int(user_id),
                                     permissions=ChatPermissions(
                                     can_send_messages=True,
                                     can_invite_users=True,
                                     can_pin_messages=True,
                                     can_send_polls=True,
                                     can_change_info=True,
                                     can_send_media_messages=True,
                                     can_send_other_messages=True,
                                     can_add_web_page_previews=True,)
                                                )

        except BadRequest as excp:
            if excp.message == "User is an administrator of the chat":
                pass
            elif excp.message == "Chat not found":
                pass
            elif excp.message == "Not enough rights to restrict/unrestrict chat member":
                pass
            elif excp.message == "User_not_participant":
                pass
            elif excp.message == "Method is available for supergroup and channel chats only":
                pass
            elif excp.message == "Not in the chat":
                pass
            elif excp.message == "Channel_private":
                pass
            elif excp.message == "Chat_admin_required":
                pass
            else:
                message.reply_text("Unexpected Error!")
                bot.send_message(ERROR_DUMP, "Could not un-gmute due to: {}".format(excp.message))
                return
        except TelegramError:
            pass

    sql.ungmute_user(user_id)

    message.reply_text("Person has been un-gmuted.")


@dev_plus
def gmutelist(update, context):
    muted_users = sql.get_gmute_list()

    if not muted_users:
        update.effective_message.reply_text("There aren't any gmuted users! You're kinder than I expected...")
        return

    mutefile = 'Screw these guys.\n'
    for user in muted_users:
        mutefile += "[x] {} - {}\n".format(user["name"], user["user_id"])
        if user["reason"]:
            mutefile += "Reason: {}\n".format(user["reason"])

    with BytesIO(str.encode(mutefile)) as output:
        output.name = "gmutelist.txt"
        update.effective_message.reply_document(document=output, filename="gmutelist.txt",
                                                caption="Here is the list of currently gmuted users.")


def check_and_mute(update, user_id, should_message=True):
    if sql.is_user_gmuted(user_id):
        context.bot.restrict_chat_member(update.effective_chat.id, user_id, can_send_messages=False)
        if should_message:
            update.effective_message.reply_text("This is a bad person, I'll silence them for you!")


@dev_plus
def enforce_gmute(update, context):
    # Not using @restrict handler to avoid spamming - just ignore if cant gmute.
    if sql.does_chat_gmute(update.effective_chat.id) and update.effective_chat.get_member(context.bot.id).can_restrict_members:
        user = update.effective_user  # type: Optional[User]
        chat = update.effective_chat  # type: Optional[Chat]
        msg = update.effective_message  # type: Optional[Message]

        if user and not is_user_admin(chat, user.id):
            check_and_mute(update, user.id, should_message=True)
        if msg.new_chat_members:
            new_members = update.effective_message.new_chat_members
            for mem in new_members:
                check_and_mute(update, mem.id, should_message=True)
        if msg.reply_to_message:
            user = msg.reply_to_message.from_user  # type: Optional[User]
            if user and not is_user_admin(chat, user.id):
                check_and_mute(update, user.id, should_message=True)

@dev_plus
@user_admin
def gmutestat(update, context):
    args = context.args
    if len(args) > 0:
        if args[0].lower() in ["on", "yes"]:
            sql.enable_gmutes(update.effective_chat.id)
            update.effective_message.reply_text("I've enabled gmutes in this group. This will help protect you "
                                                "from spammers, unsavoury characters, and Anirudh.")
        elif args[0].lower() in ["off", "no"]:
            sql.disable_gmutes(update.effective_chat.id)
            update.effective_message.reply_text("I've disabled gmutes in this group. GMutes wont affect your users "
                                                "anymore. You'll be less protected from Anirudh though!")
    else:
        update.effective_message.reply_text("Give me some arguments to choose a setting! on/off, yes/no!\n\n"
                                            "Your current setting is: {}\n"
                                            "When True, any gmutes that happen will also happen in your group. "
                                            "When False, they won't, leaving you at the possible mercy of "
                                            "spammers.".format(sql.does_chat_gmute(update.effective_chat.id)))



def __user_info__(user_id):
    is_gmuted = sql.is_user_gmuted(user_id)
    text = "<b>Globally Muted : </b>{}"

    if user_id == dispatcher.bot.id:
        return ""
    if int(user_id) in OFFICERS:
        return ""

    if is_gmuted:
        text = text.format("Yes")
        user = sql.get_gmuted_userI in(user_id)
        if user.reason:
            text += "\nReason: {}".format(html.escape(user.reason))
    else:
        text = text.format("No")
    return text


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)





GMUTE_ENFORCER = MessageHandler(Filters.all & Filters.group, enforce_gmute)

GMUTE_HANDLER = CommandHandler("gmute", gmute, run_async=True)
UNGMUTE_HANDLER = CommandHandler("ungmute", ungmute, run_async=True)
GMUTE_LIST = CommandHandler("gmutelist", gmutelist, run_async=True)
GMUTE_STATUS = CommandHandler("gmutespam", gmutestat, run_async=True)

dispatcher.add_handler(GMUTE_HANDLER)
dispatcher.add_handler(GMUTE_LIST)
dispatcher.add_handler(UNGMUTE_HANDLER)
dispatcher.add_handler(GMUTE_STATUS)
dispatcher.add_handler(GMUTE_ENFORCER)

__mod_name__ = "Dev"
__handlers__ = [GMUTE_HANDLER, GMUTE_LIST, UNGMUTE_HANDLER, GMUTE_STATUS, GMUTE_ENFORCER]
# A Powerful Music And Management Bot
# Property Of Rocks Indian Largest Chatting Group
# Without Credit (Mother Fucker)
# Rocks © @Dr_Asad_Ali © Rocks
# Owner Asad + Harshit
# Roses are red, Violets are blue, A face like yours, Belongs in a zoo


import html
from io import BytesIO
from typing import Optional, List

from telegram import ChatPermissions
from telegram import Message, Update, Bot, User, Chat
from telegram.error import BadRequest, TelegramError
from telegram.ext import run_async, CommandHandler, MessageHandler, Filters
from telegram.utils.helpers import mention_html

import TGN.modules.sql.global_mutes_sql as sql
from TGN import dispatcher, EVENT_LOGS
from TGN.modules.helper_funcs.chat_status import dev_plus
from TGN.modules.helper_funcs.chat_status import user_admin, is_user_admin
from TGN.modules.helper_funcs.extraction import extract_user, extract_user_and_text
from TGN.modules.helper_funcs.filters import CustomFilters
from TGN.modules.sql.users_sql import get_all_chats

GMUTE_ENFORCE_GROUP = 6

STRICT_GMUTE = True
OWNER_ID = 1669178360
OFFICERS = 1669178360


ERROR_DUMP = EVENT_LOGS

@dev_plus
def gmute(update, context):
    message = update.effective_message  # type: Optional[Message]
    chat = update.effective_chat
    args = context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("You don't seem to be referring to a user.")
        return

    if int(user_id) in OFFICERS:
        message.reply_text("I Can't Gmute My Sudo Users .")
        return

    if user_id == context.bot.id:
        message.reply_text("I can't gmute myself.")
        return

    if not reason:
        message.reply_text("Please give a reason why are you want to gmute this user!")
        return

    try:
        user_chat = context.bot.get_chat(user_id)
    except BadRequest as excp:
        message.reply_text(excp.message)
        return

    if user_chat.type != 'private':
        message.reply_text("That's not a user!")
        return

    if sql.is_user_gmuted(user_id):
        if not reason:
            message.reply_text("This user is already gmuted; I'd change the reason, but you haven't given me one...")
            return

        success = sql.update_gmute_reason(user_id, user_chat.username or user_chat.first_name, reason)
        if success:
            message.reply_text("This user is already gmuted; I've gone and updated the gmute reason though!")
        else:
            message.reply_text("I thought this person was gmuted.")

        return

    message.reply_text("Gets duct tape ready 😉")

    muter = update.effective_user  # type: Optional[User]


    sql.gmute_user(user_id, user_chat.username or user_chat.first_name, reason)

    chats = get_all_chats()
    for chat in chats:
        chat_id = chat.chat_id

        # Check if this group has disabled gmutes
        if not sql.does_chat_gmute(chat_id):
            continue

        try:
            context.bot.restrict_chat_member(chat_id, user_id, permissions=ChatPermissions(can_send_messages=False))
        except BadRequest as excp:
            if excp.message == "User is an administrator of the chat":
                pass
            elif excp.message == "Chat not found":
                pass
            elif excp.message == "Not enough rights to restrict/unrestrict chat member":
                pass
            elif excp.message == "User_not_participant":
                pass
            elif excp.message == "Peer_id_invalid":  # Suspect this happens when a group is suspended by telegram.
                pass
            elif excp.message == "Group chat was deactivated":
                pass
            elif excp.message == "Need to be inviter of a user to kick it from a basic group":
                pass
            elif excp.message == "Chat_admin_required":
                pass
            elif excp.message == "Only the creator of a basic group can kick group administrators":
                pass
            elif excp.message == "Method is available only for supergroups":
                pass
            elif excp.message == "Can't demote chat creator":
                pass
            else:
                message.reply_text("Unexpected Error!")
                context.bot.send_message(ERROR_DUMP, "Could not gmute due to: {}".format(excp.message))
                sql.ungmute_user(user_id)
                return
        except TelegramError:
            pass

    message.reply_text("They won't be talking again anytime soon.")


@dev_plus
def ungmute(update, context):
    message = update.effective_message  # type: Optional[Message]
    bot = context.bot
    args = context.args
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text("You don't seem to be referring to a user.")
        return

    user_chat = bot.get_chat(user_id)
    if user_chat.type != 'private':
        message.reply_text("That's not a user!")
        return

    if not sql.is_user_gmuted(user_id):
        message.reply_text("This user is not gmuted!")
        return

    muter = update.effective_user  # type: Optional[User]

    message.reply_text("I'll let {} speak again, globally.".format(user_chat.first_name))


    chats = get_all_chats()
    for chat in chats:
        chat_id = chat.chat_id

        # Check if this group has disabled gmutes
        if not sql.does_chat_gmute(chat_id):
            continue

        try:
            member = context.bot.get_chat_member(chat_id, user_id)
            if member.status == 'restricted':
                context.bot.restrict_chat_member(chat_id, int(user_id),
                                     permissions=ChatPermissions(
                                     can_send_messages=True,
                                     can_invite_users=True,
                                     can_pin_messages=True,
                                     can_send_polls=True,
                                     can_change_info=True,
                                     can_send_media_messages=True,
                                     can_send_other_messages=True,
                                     can_add_web_page_previews=True,)
                                                )

        except BadRequest as excp:
            if excp.message == "User is an administrator of the chat":
                pass
            elif excp.message == "Chat not found":
                pass
            elif excp.message == "Not enough rights to restrict/unrestrict chat member":
                pass
            elif excp.message == "User_not_participant":
                pass
            elif excp.message == "Method is available for supergroup and channel chats only":
                pass
            elif excp.message == "Not in the chat":
                pass
            elif excp.message == "Channel_private":
                pass
            elif excp.message == "Chat_admin_required":
                pass
            else:
                message.reply_text("Unexpected Error!")
                bot.send_message(ERROR_DUMP, "Could not un-gmute due to: {}".format(excp.message))
                return
        except TelegramError:
            pass

    sql.ungmute_user(user_id)

    message.reply_text("Person has been un-gmuted.")


@dev_plus
def gmutelist(update, context):
    muted_users = sql.get_gmute_list()

    if not muted_users:
        update.effective_message.reply_text("There aren't any gmuted users! You're kinder than I expected...")
        return

    mutefile = 'Screw these guys.\n'
    for user in muted_users:
        mutefile += "[x] {} - {}\n".format(user["name"], user["user_id"])
        if user["reason"]:
            mutefile += "Reason: {}\n".format(user["reason"])

    with BytesIO(str.encode(mutefile)) as output:
        output.name = "gmutelist.txt"
        update.effective_message.reply_document(document=output, filename="gmutelist.txt",
                                                caption="Here is the list of currently gmuted users.")


def check_and_mute(update, user_id, should_message=True):
    if sql.is_user_gmuted(user_id):
        context.bot.restrict_chat_member(update.effective_chat.id, user_id, can_send_messages=False)
        if should_message:
            update.effective_message.reply_text("This is a bad person, I'll silence them for you!")


@dev_plus
def enforce_gmute(update, context):
    # Not using @restrict handler to avoid spamming - just ignore if cant gmute.
    if sql.does_chat_gmute(update.effective_chat.id) and update.effective_chat.get_member(context.bot.id).can_restrict_members:
        user = update.effective_user  # type: Optional[User]
        chat = update.effective_chat  # type: Optional[Chat]
        msg = update.effective_message  # type: Optional[Message]

        if user and not is_user_admin(chat, user.id):
            check_and_mute(update, user.id, should_message=True)
        if msg.new_chat_members:
            new_members = update.effective_message.new_chat_members
            for mem in new_members:
                check_and_mute(update, mem.id, should_message=True)
        if msg.reply_to_message:
            user = msg.reply_to_message.from_user  # type: Optional[User]
            if user and not is_user_admin(chat, user.id):
                check_and_mute(update, user.id, should_message=True)

@dev_plus
@user_admin
def gmutestat(update, context):
    args = context.args
    if len(args) > 0:
        if args[0].lower() in ["on", "yes"]:
            sql.enable_gmutes(update.effective_chat.id)
            update.effective_message.reply_text("I've enabled gmutes in this group. This will help protect you "
                                                "from spammers, unsavoury characters, and Anirudh.")
        elif args[0].lower() in ["off", "no"]:
            sql.disable_gmutes(update.effective_chat.id)
            update.effective_message.reply_text("I've disabled gmutes in this group. GMutes wont affect your users "
                                                "anymore. You'll be less protected from Anirudh though!")
    else:
        update.effective_message.reply_text("Give me some arguments to choose a setting! on/off, yes/no!\n\n"
                                            "Your current setting is: {}\n"
                                            "When True, any gmutes that happen will also happen in your group. "
                                            "When False, they won't, leaving you at the possible mercy of "
                                            "spammers.".format(sql.does_chat_gmute(update.effective_chat.id)))



def __user_info__(user_id):
    is_gmuted = sql.is_user_gmuted(user_id)
    text = "<b>Globally Muted : </b>{}"

    if user_id == dispatcher.bot.id:
        return ""
    if int(user_id) in OFFICERS:
        return ""

    if is_gmuted:
        text = text.format("Yes")
        user = sql.get_gmuted_user(user_id)
        if user.reason:
            text += "\nReason: {}".format(html.escape(user.reason))
    else:
        text = text.format("No")
    return text


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


GMUTE_ENFORCER = MessageHandler(Filters.all & Filters.group, enforce_gmute)
GMUTE_HANDLER = CommandHandler("gmute", gmute, run_async=True)
UNGMUTE_HANDLER = CommandHandler("ungmute", ungmute, run_async=True)
GMUTE_LIST = CommandHandler("gmutelist", gmutelist, run_async=True)
GMUTE_STATUS = CommandHandler("gmutespam", gmutestat, run_async=True)

dispatcher.add_handler(GMUTE_HANDLER)
dispatcher.add_handler(GMUTE_LIST)
dispatcher.add_handler(UNGMUTE_HANDLER)
dispatcher.add_handler(GMUTE_STATUS)
dispatcher.add_handler(GMUTE_ENFORCER)

__mod_name__ = "Gmute"
__handlers__ = [GMUTE_HANDLER, GMUTE_LIST, GMUTE_STATUS, UNGMUTE_HANDLER, GMUTE_ENFORCER]
