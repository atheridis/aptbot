import logging
import re
import socket
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Optional, Union

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


class ABCBot(ABC):
    @abstractmethod
    def send_message(self, channel: str, text: Union[list[str], str], reply=None):
        pass


class Bot(ABCBot):
    def __init__(self, nick: str, oauth_token: str):
        self._server = "irc.chat.twitch.tv"
        self._port = 6667
        self._nick = nick
        self._oauth_token = oauth_token
        self._connected_channels = set()
        self._buffered_messages = []

    def _send_command(self, command: str):
        if "PASS" not in command:
            logger.info(f"< {command}")
        self._irc.send((command + "\r\n").encode())

    def connect(self) -> bool:
        self._connect()
        connected = self._connected()
        return connected

    def _connect(self) -> None:
        self._irc = socket.socket()
        self._irc.connect((self._server, self._port))
        logger.debug("Connecting...")
        self._send_command(f"PASS oauth:{self._oauth_token}")
        self._send_command(f"NICK {self._nick}")
        self._send_command(
            f"CAP REQ :twitch.tv/membership twitch.tv/tags twitch.tv/commands"
        )

    def join_channel(self, channel: str):
        self._send_command(f"{Commands.JOIN.value} #{channel}")
        self._connected_channels.add(channel)

    def join_channels(self, channels: Iterable):
        for channel in channels:
            self.join_channel(channel)

    def leave_channel(self, channel: str):
        self._send_command(f"{Commands.PART.value} #{channel}")
        try:
            self._connected_channels.remove(channel)
        except KeyError as e:
            logger.exception("Account isn't enabled")
            logger.exception(e)

    def send_message(self, channel: str, text: Union[list[str], str], reply=None):
        if reply:
            replied_command = f"@reply-parent-msg-id={reply} "
        else:
            replied_command = ""
        if isinstance(text, list):
            for t in text:
                command = replied_command + f"{Commands.PRIVMSG.value} #{channel} :{t}"
                self._send_command(command)
        else:
            command = replied_command + f"{Commands.PRIVMSG.value} #{channel} :{text}"
            self._send_command(command)

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
        return new_tag_value

    @staticmethod
    def _parse_message(received_msg: str) -> Message:
        split = re.search(
            r"(?:@(.+)\s)?:(?:(?:(\w+)!\w+@\w+\.)?.+)\s(\w+)\s(?:\#(\w+)|\*)\s:?(.+)?",
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

        nick = split[2] if split[2] else ""
        try:
            command = Commands[split[3]]
        except KeyError:
            return Message()
        channel = split[4] if split[4] else ""
        try:
            value = " ".join(split[5].split())
        except AttributeError:
            value = ""

        return Message(
            tags=tags,
            nick=nick,
            command=command,
            channel=channel,
            value=value,
        )

    def _handle_message(self, received_msg: str) -> Message:
        logger.info(f"> {received_msg}")
        if received_msg == "PING :tmi.twitch.tv":
            self._send_command("PONG :tmi.twitch.tv")
            return Message()
        elif not received_msg:
            return Message()
        return Bot._parse_message(received_msg)

    def _receive_messages(self) -> bytes:
        for _ in range(10):
            try:
                received_msgs = self._irc.recv(2048)
            except ConnectionResetError as e:
                logger.exception(e)
                time.sleep(1)
                self._restart_connection()
            else:
                break
        else:
            logger.error("Unable to connect to twitch. Exiting")
            sys.exit(1)
        return received_msgs

    def _connected(self) -> bool:
        received_msgs = self._receive_messages()
        for received_msg in received_msgs.decode("utf-8").split("\r\n"):
            self._buffered_messages.append(self._handle_message(received_msg))
        if self._buffered_messages[0] == Message(
            {},
            "",
            Commands.NOTICE,
            "",
            "Login authentication failed",
        ):
            logger.debug(f"Not connected")
            return False
        logger.debug(f"Connected")
        return True

    def get_messages(self) -> list[Message]:
        messages = []
        messages.extend(self._buffered_messages)
        self._buffered_messages = []
        received_msgs = self._receive_messages()
        for received_msg in received_msgs.decode("utf-8").split("\r\n"):
            messages.append(self._handle_message(received_msg))
        return messages

    def disconnect(self) -> None:
        logger.debug("Disconnecting...")
        self._irc.close()

    def _restart_connection(self):
        self.disconnect()
        time.sleep(5)
        self._connect()
        self.join_channels(self._connected_channels)
        time.sleep(2)

    # Aliasing method names for backwards compatibility
    send_privmsg = send_message
