import os
import shutil
import socket
from enum import Enum

from .constants import CONFIG_PATH


class BotCommands(Enum):
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

    if not os.path.exists(os.path.join(account_path, "main.py")):
        shutil.copyfile(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "resources/main.py"
            ),
            os.path.join(account_path, "main.py"),
        )

    command = BotCommands.JOIN.value
    channel = acc
    msg = ""
    try:
        s.send(bytes(f"{command}==={channel}==={msg}", "utf-8"))
    except (BrokenPipeError, OSError):
        pass


def send_msg(s: socket.socket, msg: str):
    command = BotCommands.SEND.value
    channel = msg.split(" ")[0]
    msg = msg[len(channel) + 1 :]
    s.send(bytes(f"{command}==={channel}==={msg}", "utf-8"))


def disable(s: socket.socket):
    command = BotCommands.KILL.value
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

    command = BotCommands.PART.value
    channel = acc
    msg = ""
    try:
        s.send(bytes(f"{command}==={channel}==={msg}", "utf-8"))
    except (BrokenPipeError, OSError):
        pass


def update(s: socket.socket):
    command = BotCommands.UPDATE.value
    channel = ""
    msg = ""
    s.send(bytes(f"{command}==={channel}==={msg}", "utf-8"))
