import importlib
import importlib.util
import logging
import logging.config
import os
import socket
import sys
import time
import traceback
from dataclasses import dataclass
from threading import Event, Thread
from types import ModuleType

from dotenv import load_dotenv

from . import args_logic
from .args import parse_arguments
from .bot import Bot, Message
from .constants import (CONFIG_LOGS, CONFIG_PATH, LOCALHOST, LOGGING_DICT,
                        MAIN_FILE_NAME, PORT)

logging.config.dictConfig(LOGGING_DICT)
logger = logging.getLogger(__name__)

load_dotenv()


@dataclass(frozen=True)
class Channel:
    name: str
    module: ModuleType
    thread: Thread
    stop_event: Event

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


def handle_message(bot: Bot, channels: set[Channel]):
    while True:
        messages = bot.get_messages()
        for message in messages:
            if not message.channel:
                continue
            for channel in channels:
                if channel.name != message.channel:
                    continue
                Thread(
                    target=channel.module.main, args=(bot, message), daemon=True
                ).start()
                break


def run_start(channels: set[Channel]):
    for channel in channels:
        channel.thread.start()


def disable_channel(channel_name: str, channels: set[Channel]):
    for channel in channels:
        if channel.name != channel_name:
            continue
        channel.stop_event.set()
        logger.debug(f"Event set for {channel}")
        channels.remove(channel)
        logger.debug(f"{channel} removed")
        break


def enable(bot: Bot, channels: set[Channel]):
    load_modules(bot, channels)
    message_handler_thread = Thread(
        target=handle_message,
        args=(
            bot,
            channels,
        ),
        daemon=True,
    )
    message_handler_thread.start()


def load_modules(bot: Bot, channels: set[Channel]):
    old_channels = channels.copy()
    channels.clear()
    channel_names = [
        c
        for c in os.listdir(CONFIG_PATH)
        if os.path.isdir(os.path.join(CONFIG_PATH, c))
    ]
    channel_names = filter(lambda x: not x.startswith("."), channel_names)
    for channel_name in channel_names:
        channel_path = os.path.join(CONFIG_PATH, channel_name)
        sys.path.append(channel_path)
        module_path = os.path.join(channel_path, MAIN_FILE_NAME)
        spec = importlib.util.spec_from_file_location(
            "main",
            module_path,
        )
        if not spec or not spec.loader:
            logger.warning(f"Problem loading for {channel_path}")
            sys.path.remove(channel_path)
            continue
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            logger.exception(f"Problem Loading Module: {e}")
            logger.exception(traceback.format_exc())
        else:
            for channel in old_channels:
                if channel_name != channel.name:
                    continue
                stop_event = channel.stop_event
                thread = channel.thread
                logger.debug(
                    f"Copied stop_event and thread for account: {channel.name}"
                )
                break
            else:
                stop_event = Event()
                thread = Thread(
                    target=module.start,
                    args=(bot, Message(channel=channel_name), stop_event),
                    daemon=True,
                )
                logger.debug(
                    f"Created stop event and thread for account: {channel_name}"
                )
            channels.add(
                Channel(
                    name=channel_name,
                    module=module,
                    thread=thread,
                    stop_event=stop_event,
                ),
            )
        sys.path.remove(channel_path)
    new_channels = channels.difference(old_channels)
    run_start(new_channels)


def initialize(bot: Bot):
    logger.debug("Initializing...")
    channels = [
        c
        for c in os.listdir(CONFIG_PATH)
        if os.path.isdir(os.path.join(CONFIG_PATH, c))
    ]
    channels = filter(lambda x: not x.startswith("."), channels)
    bot.join_channels(channels)


def listener():
    NICK = os.getenv("APTBOT_NICK")
    OAUTH = os.getenv("APTBOT_PASS")
    if NICK and OAUTH:
        bot = Bot(NICK, OAUTH)
    else:
        logger.error(
            "The environment variables:\nAPTBOT_NICK\nAPTBOT_PASS\nare not set."
        )
        time.sleep(3)
        sys.exit(1)
    if not bot.connect():
        logger.error("Twitch couldn't authenticate your credentials")
        time.sleep(3)
        sys.exit(1)
    initialize(bot)
    channels: set[Channel] = set()
    message_loop = Thread(
        target=enable,
        args=(
            bot,
            channels,
        ),
        daemon=True,
    )
    message_loop.start()
    s = socket.socket()
    s.bind((LOCALHOST, PORT))
    s.listen(5)

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
                bot.send_message(channel, msg)
            elif args_logic.BotCommands.KILL.value in command:
                bot.disconnect()
                c.close()
                s.close()
                sys.exit()
            elif args_logic.BotCommands.UPDATE.value in command:
                load_modules(bot, channels)
            elif args_logic.BotCommands.PART.value in command:
                disable_channel(channel, channels)
                bot.leave_channel(channel)

        time.sleep(1)


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
