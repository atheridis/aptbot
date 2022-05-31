import logging
import re
import socket
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union

logger = logging.getLogger(__name__)


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
        self._irc = socket.socket()
        self._server = "irc.chat.twitch.tv"
        self._port = 6667
        self._nick = nick
        self._oauth_token = oauth_token
        self._connected_channels = []

    def send_command(self, command: str):
        if "PASS" not in command:
            logger.debug(f"< {command}")
        self._irc.send((command + "\r\n").encode())

    def connect(self):
        self._irc.connect((self._server, self._port))
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
                command = replied_command + f"{Commands.PRIVMSG.value} #{channel} :{t}"
                self.send_command(command)
        else:
            command = replied_command + f"{Commands.PRIVMSG.value} #{channel} :{text}"
            self.send_command(command)

    @staticmethod
    def _replace_escaped_space_in_tags(tag_value: str) -> str:
        new_tag_value = ""
        ignore_next = False
        for i in range(len(tag_value)):
            if ignore_next:
                ignore_next = False
                continue
            if not tag_value[i] == "\\":
                new_tag_value += tag_value[i]
                ignore_next = False
                continue
            if i + 1 == len(tag_value):
                new_tag_value += tag_value[i]
                break
            if tag_value[i + 1] == "\\":
                new_tag_value += "\\"
            elif tag_value[i + 1] == "s":
                new_tag_value += " "
            ignore_next = True

    @staticmethod
    def parse_message(received_msg: str) -> Message:
        split = re.search(
            r"(?:(?:@(.+))\s)?:(?:(?:(\w+)!\w+@\w+\.)?.+)\s(\w+)\s\#(\w+)\s:?(.+)?",
            received_msg,
        )

        if not split:
            return Message()

        tags = {}
        if split[1]:
            for tag in split[1].split(";"):
                tag_name, tag_value = tag.split("=")
                if tag.split("=")[0] == "reply-parent-msg-body":
                    tag_value = Bot._replace_escaped_space_in_tags(tag.split("=")[1])
                tags[tag_name] = " ".join(tag_value.split())

        nick = split[2]
        try:
            command = Commands[split[3]]
        except KeyError:
            return Message()
        channel = split[4]
        value = " ".join(split[5].split())

        return Message(
            tags=tags,
            nick=nick,
            command=command,
            channel=channel,
            value=value,
        )

    def _handle_message(self, received_msg: str) -> Message:
        logger.debug(received_msg)
        if received_msg == "PING :tmi.twitch.tv":
            self.send_command("PONG :tmi.twitch.tv")
            return Message()
        elif not received_msg:
            return Message()
        return Bot.parse_message(received_msg)

    def receive_messages(self) -> list[Message]:
        messages = []
        received_msgs = self._irc.recv(2048)
        for received_msgs in received_msgs.decode("utf-8").split("\r\n"):
            messages.append(self._handle_message(received_msgs))
        return messages
