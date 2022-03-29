import inspect
import logging
import sys
import re
import functools
import inspect
import logging
import re
from pathlib import Path

from telethon import events

from pathlib import Path
from telethon import events
from pymongo import MongoClient
from TGN import MONGO_DB_URI
from TGN import telethn
from TGN import telethn as bot
LOAD_PLUG = None
SUDO_USERS = 1669178360
client = MongoClient()
client = MongoClient(MONGO_DB_URI)
db = client["TGN"]
gbanned = db.gban

def register(**args):
    """ Registers a new message. """
    pattern = args.get("pattern", None)

    r_pattern = r"^[/!.]"

    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = "(?i)" + pattern

    args["pattern"] = pattern.replace("^/", r_pattern, 1)

    def decorator(func):
        telethn.add_event_handler(func, events.NewMessage(**args))
        return func

    return decorator


def command(**args):
    args["func"] = lambda e: e.via_bot_id is None

    stack = inspect.stack()
    previous_stack_frame = stack[1]
    file_test = Path(previous_stack_frame.filename)
    file_test = file_test.stem.replace(".py", "")
    if 1 == 0:
        return print("stupidity at its best")
    else:
        pattern = args.get("pattern", None)
        allow_sudo = args.get("allow_sudo", False)
        allow_edited_updates = args.get("allow_edited_updates", False)
        args["incoming"] = args.get("incoming", False)
        args["outgoing"] = True
        if bool(args["incoming"]):
            args["outgoing"] = False

        try:
            if pattern is not None and not pattern.startswith("(?i)"):
                args["pattern"] = "(?i)" + pattern
        except:
            pass

        reg = re.compile("(.*)")
        if not pattern == None:
            try:
                cmd = re.search(reg, pattern)
                try:
                    cmd = (
                        cmd.group(1).replace("$", "").replace("\\", "").replace("^", "")
                    )
                except:
                    pass

                try:
                    CMD_LIST[file_test].append(cmd)
                except:
                    CMD_LIST.update({file_test: [cmd]})
            except:
                pass

        if allow_sudo:
            args["from_users"] = list(SUDO_USERS)
            # Mutually exclusive with outgoing (can only set one of either).
            args["incoming"] = True
        del allow_sudo
        try:
            del args["allow_sudo"]
        except:
            pass

        if "allow_edited_updates" in args:
            del args["allow_edited_updates"]

        def decorator(func):
            if allow_edited_updates:
                telethn.add_event_handler(func, events.MessageEdited(**args))
            telethn.add_event_handler(func, events.NewMessage(**args))
            return func

        return decorator


def chataction(**args):
    """ Registers chat actions. """

    def decorator(func):
        telethn.add_event_handler(func, events.ChatAction(**args))
        return func

    return decorator


def userupdate(**args):
    """ Registers user updates. """

    def decorator(func):
        telethn.add_event_handler(func, events.UserUpdate(**args))
        return func

    return decorator


def inlinequery(**args):
    """ Registers inline query. """
    pattern = args.get("pattern", None)

    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = "(?i)" + pattern

    def decorator(func):
        telethn.add_event_handler(func, events.InlineQuery(**args))
        return func

    return decorator


def callbackquery(**args):
    """ Registers inline query. """

    def decorator(func):
        telethn.add_event_handler(func, events.CallbackQuery(**args))
        return func

    return decorator


def bot(**args):
    pattern = args.get("pattern")
    r_pattern = r"^[/]"

    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = "(?i)" + pattern

    args["pattern"] = pattern.replace("^/", r_pattern, 1)
    stack = inspect.stack()
    previous_stack_frame = stack[1]
    file_test = Path(previous_stack_frame.filename)
    file_test = file_test.stem.replace(".py", "")
    reg = re.compile("(.*)")

    if pattern is not None:
        try:
            cmd = re.search(reg, pattern)
            try:
                cmd = cmd.group(1).replace("$", "").replace("\\", "").replace("^", "")
            except BaseException:
                pass

            try:
                FUN_LIST[file_test].append(cmd)
            except BaseException:
                FUN_LIST.update({file_test: [cmd]})
        except BaseException:
            pass

    def decorator(func):
        async def wrapper(check):
            if check.edit_date:
                return
            if check.fwd_from:
                return
            if check.is_group or check.is_private:
                pass
            else:
                print("i don't work in channels")
                return
            if check.is_group:
               if check.chat.megagroup:
                  pass
               else:
                  print("i don't work in small chats")
                  return
                          
            users = gbanned.find({})
            for c in users:
                if check.sender_id == c["user"]:
                    return
            try:
                await func(check)
                try:
                    LOAD_PLUG[file_test].append(func)
                except Exception:
                    LOAD_PLUG.update({file_test: [func]})
            except BaseException:
                return
            else:
                pass

        telethn.add_event_handler(wrapper, events.NewMessage(**args))
        return wrapper

    return decorator


def Emli(**args):
    pattern = args.get("pattern", None)
    disable_edited = args.get("disable_edited", False)
    ignore_unsafe = args.get("ignore_unsafe", False)
    unsafe_pattern = r"^[^/!#@\$A-Za-z]"
    group_only = args.get("group_only", False)
    disable_errors = args.get("disable_errors", False)
    insecure = args.get("insecure", False)
    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = "(?i)" + pattern

    if "disable_edited" in args:
        del args["disable_edited"]

    if "ignore_unsafe" in args:
        del args["ignore_unsafe"]

    if "group_only" in args:
        del args["group_only"]

    if "disable_errors" in args:
        del args["disable_errors"]

    if "insecure" in args:
        del args["insecure"]

    if pattern:
        if not ignore_unsafe:
            args["pattern"] = args["pattern"].replace("^.", unsafe_pattern, 1)

async def get_all_admin_chats(event):
    lul_stark = []
    all_chats = [
        d.entity
        for d in await event.client.get_dialogs()
        if (d.is_group or d.is_channel)
    ]
    for i in all_chats:
        if i.creator or i.admin_rights:
            lul_stark.append(i.id)
    return lul_stark


async def is_admin(event, user):
    sed = await event.client.get_permissions(event.chat_id, user)
    if sed.is_admin:
        is_mod = True
    else:
        is_mod = False
    return is_mod
