import importlib
import importlib.util
import logging
import logging.config
import os
import socket
import sys
import time
import traceback
from threading import Thread
from types import ModuleType

from dotenv import load_dotenv

from . import args_logic
from .args import parse_arguments
from .bot import Bot, Message
from .constants import CONFIG_LOGS, CONFIG_PATH, LOCALHOST, LOGGING_DICT, PORT

logging.config.dictConfig(LOGGING_DICT)
logger = logging.getLogger(__name__)

load_dotenv()


def handle_message(bot: Bot, modules: dict[str, ModuleType]):
    while True:
        messages = bot.receive_messages()
        for message in messages:
            if not message.channel:
                continue
            try:
                method = Thread(
                    target=modules[message.channel].main,
                    args=(
                        bot,
                        message,
                    ),
                )
            except KeyError:
                pass
            else:
                method.daemon = True
                method.start()


def start(bot: Bot, modules: dict[str, ModuleType]):
    load_modules(modules)
    message_handler_thread = Thread(
        target=handle_message,
        args=(
            bot,
            modules,
        ),
    )
    message_handler_thread.daemon = True
    message_handler_thread.start()
    for channel in modules:
        update_channel = Thread(
            target=modules[channel].start,
            args=(
                bot,
                Message({}, "", None, channel, ""),
            ),
        )
        update_channel.daemon = True
        update_channel.start()


def load_modules(modules: dict[str, ModuleType]):
    modules.clear()
    channels = [
        c
        for c in os.listdir(CONFIG_PATH)
        if os.path.isdir(os.path.join(CONFIG_PATH, c))
    ]
    channels = filter(lambda x: not x.startswith("."), channels)
    for channel in channels:
        account_path = os.path.join(CONFIG_PATH, f"{channel}")
        sys.path.append(account_path)
        module_path = os.path.join(account_path, "main.py")
        spec = importlib.util.spec_from_file_location(
            "main",
            module_path,
        )
        if not spec or not spec.loader:
            print("Problem loading spec")
            sys.path.remove(account_path)
            continue
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            logger.exception(f"Problem Loading Module: {e}")
            logger.exception(traceback.format_exc())
        else:
            modules[channel] = module
        sys.path.remove(account_path)


def initialize(bot: Bot):
    channels = [
        c
        for c in os.listdir(CONFIG_PATH)
        if os.path.isdir(os.path.join(CONFIG_PATH, c))
    ]
    channels = filter(lambda x: not x.startswith("."), channels)
    for channel in channels:
        if not channel.startswith("."):
            bot.join_channel(channel)


def listener():
    NICK = os.getenv("APTBOT_NICK")
    OAUTH = os.getenv("APTBOT_PASS")
    if NICK and OAUTH:
        bot = Bot(NICK, OAUTH)
    else:
        print(
            "Please set the environment variables:\nAPTBOT_NICK\nAPTBOT_PASS",
            file=sys.stderr,
        )
        time.sleep(3)
        sys.exit(1)
    bot.connect()
    modules = {}
    message_loop = Thread(
        target=start,
        args=(
            bot,
            modules,
        ),
    )
    message_loop.daemon = True
    message_loop.start()
    s = socket.socket()
    s.bind((LOCALHOST, PORT))
    s.listen(5)
    initialize(bot)

    while True:
        c, _ = s.accept()
        msg = c.recv(1024).decode()
        msg = msg.split("===")
        try:
            command = msg[0]
            channel = msg[1]
            msg = msg[2]
        except IndexError:
            pass
        else:
            if args_logic.BotCommands.JOIN.value in command:
                bot.join_channel(channel)
            elif args_logic.BotCommands.SEND.value in command:
                bot.send_privmsg(channel, msg)
            elif args_logic.BotCommands.KILL.value in command:
                sys.exit()
            elif args_logic.BotCommands.UPDATE.value in command:
                load_modules(modules)
            elif args_logic.BotCommands.PART.value in command:
                bot.leave_channel(channel)

        time.sleep(1)


def send(func):
    def inner(*args, **kwargs):
        s = socket.socket()
        s.connect((LOCALHOST, PORT))
        func(s, *args, **kwargs)
        s.close()

    return inner


def main():
    argsv = parse_arguments()
    os.makedirs(CONFIG_PATH, exist_ok=True)
    os.makedirs(CONFIG_LOGS, exist_ok=True)
    if argsv.enable:
        listener()

    s = socket.socket()
    try:
        s.connect((LOCALHOST, PORT))
    except ConnectionRefusedError:
        pass

    if argsv.add_account:
        args_logic.add_account(s, argsv.add_account)
    if argsv.disable_account:
        args_logic.disable_account(s, argsv.disable_account)
    if argsv.send_message:
        args_logic.send_msg(s, argsv.send_message)
    if argsv.disable:
        args_logic.disable(s)
    if argsv.update:
        args_logic.update(s)
    s.close()


if __name__ == "__main__":
    main()
