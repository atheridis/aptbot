import socket
import os
from enum import Enum
from aptbot import CONFIG_PATH


class Commands(Enum):
    JOIN = "JOIN"
    PART = "PART"
    SEND = "SEND"
    KILL = "KILL"
    UPDATE = "UPDATE"


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

    command = Commands.JOIN.value
    channel = acc
    msg = ""
    s.send(bytes(f"{command}==={channel}==={msg}", "utf-8"))


def send_msg(s: socket.socket, msg: str):
    command = Commands.SEND.value
    channel = msg.split(' ')[0]
    msg = msg[len(channel) + 1:]
    s.send(bytes(f"{command}==={channel}==={msg}", "utf-8"))


def disable(s: socket.socket):
    command = Commands.KILL.value
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

    command = Commands.PART.value
    channel = ""
    msg = ""
    s.send(bytes(f"{command}==={channel}==={msg}", "utf-8"))


def update(s: socket.socket):
    command = Commands.UPDATE.value
    channel = ""
    msg = ""
    s.send(bytes(f"{command}==={channel}==={msg}", "utf-8"))
