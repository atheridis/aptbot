import socket
from enum import Enum
from dataclasses import dataclass
from typing import Optional


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
    tags: dict
    nick: str
    command: Optional[Commands]
    channel: str
    value: str


class Bot:
    def __init__(self, nick: str, oauth_token: str, client_id: str):
        self.irc = socket.socket()
        self.server = "irc.twitch.tv"
        self.port = 6667
        self.nick = nick
        self.oauth_token = oauth_token
        self.client_id = client_id

    def send_command(self, command: str):
        self.irc.send((command + "\r\n").encode())

    def connect(self):
        self.irc.connect((self.server, self.port))
        self.send_command(f"PASS oauth:{self.oauth_token}")
        self.send_command(f"NICK {self.nick}")
        self.send_command(f"CAP REQ :twitch.tv/membership")
        self.send_command(f"CAP REQ :twitch.tv/tags")
        self.send_command(f"CAP REQ :twitch.tv/commands")

    def join_channel(self, channel: str):
        self.send_command(f"{Commands.JOIN.value} #{channel}")

    def leave_channel(self, channel: str):
        self.send_command(f"{Commands.PART.value} #{channel}")

    def send_privmsg(self, channel: str, text: str):
        self.send_command(f"{Commands.PRIVMSG.value} #{channel} :{text}")

    @staticmethod
    def parse_message(received_msg: str) -> Message:
        message = Message({}, "", None, "", "")

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
            return Message({}, "", None, "", "")
        elif not received_msg:
            return Message({}, "", None, "", "")
        return Bot.parse_message(received_msg)

    def receive_messages(self) -> list:
        messages = []
        received_msgs = self.irc.recv(2048).decode()
        for received_msgs in received_msgs.split("\r\n"):
            messages.append(self._handle_message(received_msgs))
        return messages