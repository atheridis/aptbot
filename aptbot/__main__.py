import socket
import aptbot.args
import time
import aptbot.args_logic
import aptbot.bot
import os
import sys
import importlib
import importlib.util
import traceback
from threading import Thread
from dotenv import load_dotenv
from types import ModuleType
from aptbot import *

load_dotenv()


def handle_message(bot: aptbot.bot.Bot, modules: dict[str, ModuleType]):
    while True:
        messages = bot.receive_messages()
        for message in messages:
            if not message.channel:
                continue
            # if message.command:
            #     print(
            #         f"#{message.channel} ({message.command.value}) | \
            # {message.nick}: {message.value}"
            #     )
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
        time.sleep(0.1)


def start(bot: aptbot.bot.Bot, modules: dict[str, ModuleType]):
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
                aptbot.bot.Message({}, "", None, channel, ""),
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
        module_path = os.path.join(account_path, f"main.py")
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
            print(traceback.format_exc())
            print(f"Problem Loading Module: {e}")
        else:
            modules[channel] = module
        sys.path.remove(account_path)


def initialize(bot: aptbot.bot.Bot):
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
        bot = aptbot.bot.Bot(NICK, OAUTH)
    else:
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
            if aptbot.args_logic.Commands.JOIN.value in command:
                bot.join_channel(channel)
            elif aptbot.args_logic.Commands.SEND.value in command:
                bot.send_privmsg(channel, msg)
            elif aptbot.args_logic.Commands.KILL.value in command:
                sys.exit()
            elif aptbot.args_logic.Commands.UPDATE.value in command:
                load_modules(modules)
            elif aptbot.args_logic.Commands.PART.value in command:
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
    argsv = aptbot.args.parse_arguments()
    os.makedirs(CONFIG_PATH, exist_ok=True)
    if argsv.enable:
        listener()

    s = socket.socket()
    try:
        s.connect((LOCALHOST, PORT))
    except ConnectionRefusedError:
        pass

    if argsv.add_account:
        aptbot.args_logic.add_account(s, argsv.add_account)
    if argsv.disable_account:
        aptbot.args_logic.disable_account(s, argsv.disable_account)
    if argsv.send_message:
        aptbot.args_logic.send_msg(s, argsv.send_message)
    if argsv.disable:
        aptbot.args_logic.disable(s)
    if argsv.update:
        aptbot.args_logic.update(s)
    s.close()


if __name__ == "__main__":
    main()
