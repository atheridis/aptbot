import websocket
import time
import re
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Union


class Commands(Enum):
    CLEARCHAT = "CLEARCHAT"
    CLEARMSG = "CLEARMSG"
    HOSTTARGET = "HOSTTARGET"
    NOTICE = "NOTICE"
    RECONNECT = "RECONNECT"
    ROOMSTATE = "ROOMSTATE"
    USERNOTICE = "USERNOTICE"
    USERSTATE = "USERSTATE"
    GLOBALUSERSTATE = "GLOBALUSERSTATE"
    PRIVMSG = "PRIVMSG"
    JOIN = "JOIN"
    PART = "PART"


@dataclass
class Message:
    tags: dict[str, str] = field(default_factory=dict)
    nick: str = ""
    command: Optional[Commands] = None
    channel: str = ""
    value: str = ""


class Bot:
    def __init__(self, nick: str, oauth_token: str):
        self._irc = websocket.WebSocket()
        self._server = "wss://irc-ws.chat.twitch.tv:443"
        self._nick = nick
        self._oauth_token = oauth_token
        self._connected_channels = []

    def send_command(self, command: str):
        if "PASS" not in command:
            print(f"< {command}")
        self._irc.send((command + "\r\n").encode())

    def connect(self):
        self._irc.connect(self._server)
        self.send_command(f"PASS oauth:{self._oauth_token}")
        self.send_command(f"NICK {self._nick}")
        self.send_command(f"CAP REQ :twitch.tv/membership")
        self.send_command(f"CAP REQ :twitch.tv/tags")
        self.send_command(f"CAP REQ :twitch.tv/commands")

    def join_channel(self, channel: str):
        self.send_command(f"{Commands.JOIN.value} #{channel}")
        self._connected_channels.append(channel)

    def join_channels(self, channels: list[str]):
        for channel in channels:
            self.join_channel(channel)

    def leave_channel(self, channel: str):
        self.send_command(f"{Commands.PART.value} #{channel}")
        self._connected_channels.remove(channel)

    def send_privmsg(self, channel: str, text: Union[list[str], str], reply=None):
        if reply:
            replied_command = f"@reply-parent-msg-id={reply} "
        else:
            replied_command = ""
        if isinstance(text, list):
            for t in text:
                # print(
                #     f"#{channel} ({Commands.PRIVMSG.value}) | {self._nick}: {t}")
                command = replied_command + f"{Commands.PRIVMSG.value} #{channel} :{t}"
                self.send_command(command)
        else:
            # print(f"#{channel} ({Commands.PRIVMSG.value}) | {self._nick}: {text}")
            command = replied_command + f"{Commands.PRIVMSG.value} #{channel} :{text}"
            self.send_command(command)

    @staticmethod
    def parse_message(received_msg: str) -> Message:
        # print(received_msg)
        message = Message()

        value_start = received_msg.find(
            ":", received_msg.find(" ", received_msg.find(" ") + 1)
        )
        if value_start != -1:
            message.value = received_msg[value_start:][1:]
            received_msg = received_msg[: value_start - 1]

        parts = received_msg.split(" ")

        for part in parts:
            if part.startswith("@"):
                part = part[1:]
                for tag in part.split(";"):
                    tag = tag.split("=")
                    try:
                        message.tags[tag[0]] = tag[1]
                    except IndexError:
                        message.tags[tag[0]] = ""
            elif part.startswith(":"):
                part = part[1:]
                if "!" in part:
                    message.nick = part.split("!")[0]
            elif part in set(command.value for command in Commands):
                message.command = Commands(part)
            elif part.startswith("#"):
                part = part[1:]
                message.channel = part

        message.value = " ".join(message.value.split())

        if not message.tags.get("reply-parent-msg-body", None):
            print(message)
            return message

        rep = message.tags["reply-parent-msg-body"]
        new_rep = ""
        ignore_next = False
        for i in range(len(rep)):
            if ignore_next:
                ignore_next = False
                continue
            if not rep[i] == "\\":
                new_rep += rep[i]
                ignore_next = False
                continue
            if i + 1 == len(rep):
                new_rep += rep[i]
                break
            if rep[i + 1] == "\\":
                new_rep += "\\"
            elif rep[i + 1] == "s":
                new_rep += " "
            ignore_next = True

        message.tags["reply-parent-msg-body"] = " ".join(new_rep.split())

        print(message)
        return message

    def _handle_message(self, received_msg: str) -> Message:
        if received_msg == "PING :tmi.twitch.tv":
            self.send_command("PONG :tmi.twitch.tv")
            return Message()
        elif not received_msg:
            return Message()
        return Bot.parse_message(received_msg)

    def receive_messages(self) -> list[Message]:
        messages = []
        received_msgs = self._irc.recv()
        for received_msgs in received_msgs.split("\r\n"):
            messages.append(self._handle_message(received_msgs))
        return messages
