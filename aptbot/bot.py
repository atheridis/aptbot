import socket
import time
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
    def __init__(self, nick: str, oauth_token: str, client_id: str):
        self._irc = socket.socket()
        self._server = "irc.chat.twitch.tv"
        self._port = 6667
        self._nick = nick
        self._oauth_token = oauth_token
        self._client_id = client_id
        self._connected_channels = []

    def send_command(self, command: str):
        if "PASS" not in command:
            print(f"< {command}")
        self._irc.send((command + "\r\n").encode())

    def connect(self):
        self._irc.connect((self._server, self._port))
        time.sleep(1.5)
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

    def send_privmsg(self, channel: str, text: Union[list[str], str]):
        if isinstance(text, list):
            for t in text:
                print(
                    f"#{channel} ({Commands.PRIVMSG.value}) | {self._nick}: {t}")
                self.send_command(
                    f"{Commands.PRIVMSG.value} #{channel} :{t}")
                time.sleep(1.5)
        else:
            print(f"#{channel} ({Commands.PRIVMSG.value}) | {self._nick}: {text}")
            self.send_command(f"{Commands.PRIVMSG.value} #{channel} :{text}")

    @staticmethod
    def parse_message(received_msg: str) -> Message:
        print(received_msg)
        message = Message()

        value_start = received_msg.find(
            ':',
            received_msg.find(' ', received_msg.find(' ') + 1)
        )
        if value_start != -1:
            message.value = received_msg[value_start:][1:]
            received_msg = received_msg[:value_start - 1]

        parts = received_msg.split(' ')

        for part in parts:
            if part.startswith('@'):
                part = part[1:]
                for tag in part.split(';'):
                    tag = tag.split('=')
                    try:
                        message.tags[tag[0]] = tag[1]
                    except IndexError:
                        message.tags[tag[0]] = ""
            elif part.startswith(':'):
                part = part[1:]
                if '!' in part:
                    message.nick = part.split('!')[0]
            elif part in set(command.value for command in Commands):
                message.command = Commands(part)
            elif part.startswith('#'):
                part = part[1:]
                message.channel = part

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
        received_msgs = self._irc.recv(2048).decode()
        for received_msgs in received_msgs.split("\r\n"):
            messages.append(self._handle_message(received_msgs))
        return messages
