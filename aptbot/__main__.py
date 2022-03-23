import socket
import aptbot.args
import time
import aptbot.bot
import os
import sys
import importlib
import importlib.util
import traceback
from threading import Thread
from dotenv import load_dotenv
from types import ModuleType

load_dotenv()

if "XDG_CONFIG_HOME" in os.environ:
    CONFIG_HOME = os.environ["XDG_CONFIG_HOME"]
elif "APPDATA" in os.environ:
    CONFIG_HOME = os.environ["APPDATA"]
else:
    CONFIG_HOME = os.path.join(os.environ["HOME"], ".config")

CONFIG_PATH = os.path.join(CONFIG_HOME, f"aptbot")


PORT = 26538
LOCALHOST = "127.0.0.1"


def loop(bot: aptbot.bot.Bot, modules: dict[str, ModuleType]):
    update_modules(modules)
    while True:
        messages = bot.receive_messages()
        for message in messages:
            if message.channel:
                if message.command:
                    print(
                        f"#{message.channel} ({message.command.value}) | {message.nick}: {message.value}")
                try:
                    method = Thread(
                        target=modules[message.channel].main,
                        args=(bot, message, )
                    )
                except KeyError:
                    pass
                else:
                    method.daemon = True
                    method.start()
        time.sleep(0.01)


def update_modules(modules: dict[str, ModuleType]):
    modules.clear()
    channels = filter(lambda x: not x.startswith('.'), os.listdir(CONFIG_PATH))
    channels = list(channels)
    # print(channels)
    for channel in channels:
        account_path = os.path.join(CONFIG_PATH, f"{channel}")
        sys.path.append(account_path)
        module_path = os.path.join(
            account_path, f"message_interpreter.py")
        spec = importlib.util.spec_from_file_location(
            "message_interpreter",
            module_path,
        )
        if spec and spec.loader:
            foo = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(foo)
            except Exception as e:
                print(traceback.format_exc())
                print(f"Problem Loading Module: {e}")
            else:
                modules[channel] = foo
        sys.path.remove(account_path)


def initialize(bot: aptbot.bot.Bot):
    channels = os.listdir(CONFIG_PATH)
    for channel in channels:
        if not channel.startswith('.'):
            bot.join_channel(channel)


def listener():
    NICK = os.getenv("APTBOT_NICK")
    OAUTH = os.getenv("APTBOT_OAUTH")
    CLIENT_ID = os.getenv("APTBOT_CLIENT_ID")
    if NICK and OAUTH and CLIENT_ID:
        bot = aptbot.bot.Bot(NICK, OAUTH, CLIENT_ID)
    else:
        sys.exit(1)
    bot.connect()
    modules = {}
    message_loop = Thread(target=loop, args=(bot, modules, ))
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
            if "JOIN" in command:
                bot.join_channel(channel)
            elif "SEND" in command:
                bot.send_privmsg(channel, msg)
            elif "KILL" in command:
                sys.exit()
            elif "UPDATE" in command:
                update_modules(modules)
            elif "PART" in command:
                bot.leave_channel(channel)

        time.sleep(1)


def send(func,):
    def inner(*args, **kwargs):
        s = socket.socket()
        s.connect((LOCALHOST, PORT))
        func(s, *args, **kwargs)
        s.close()
    return inner


def add_account(s: socket.socket, acc: str):
    account_path = os.path.join(CONFIG_PATH, f"{acc}")
    hidden_account_path = os.path.join(CONFIG_PATH, f".{acc}")

    try:
        os.rename(hidden_account_path, account_path)
    except FileNotFoundError:
        pass
    os.makedirs(account_path, exist_ok=True)

    # print(os.listdir("."))
    # shutil.copy("message_interpreter.py", account_path)
    try:
        f = open(os.path.join(account_path, "message_interpreter.py"), "r")
    except FileNotFoundError:
        f = open(os.path.join(account_path, "message_interpreter.py"), "a")
        f.write("""from aptbot.bot import Bot, Message, Commands
def main(bot, message: Message):
    pass""")
        f.close()
    else:
        f.close()

    command = "JOIN"
    channel = acc
    msg = ""
    s.send(bytes(f"{command}==={channel}==={msg}", "utf-8"))


def send_msg(s: socket.socket, msg: str):
    command = "SEND"
    channel = msg.split(' ')[0]
    msg = msg[len(channel) + 1:]
    s.send(bytes(f"{command}==={channel}==={msg}", "utf-8"))


def disable(s: socket.socket):
    command = "KILL"
    channel = ""
    msg = ""
    s.send(bytes(f"{command}==={channel}==={msg}", "utf-8"))


def disable_account(s: socket.socket, acc: str):
    account_path = os.path.join(CONFIG_PATH, f"{acc}")
    hidden_account_path = os.path.join(CONFIG_PATH, f".{acc}")
    try:
        os.rename(account_path, hidden_account_path)
    except FileNotFoundError:
        print(f"Account {acc} is already disabled.")

    command = "PART"
    channel = ""
    msg = ""
    s.send(bytes(f"{command}==={channel}==={msg}", "utf-8"))


def update(s: socket.socket):
    command = "UPDATE"
    channel = ""
    msg = ""
    s.send(bytes(f"{command}==={channel}==={msg}", "utf-8"))


def main():
    argsv = aptbot.args.parse_arguments()
    if argsv.enable:
        listener()

    s = socket.socket()
    try:
        s.connect((LOCALHOST, PORT))
    except ConnectionRefusedError:
        pass

    if argsv.add_account:
        add_account(s, argsv.add_account)
    if argsv.disable_account:
        disable_account(s, argsv.disable_account)
    if argsv.send_message:
        send_msg(s, argsv.send_message)
    if argsv.disable:
        disable(s)
    if argsv.update:
        update(s)
    s.close()


if __name__ == "__main__":
    main()
