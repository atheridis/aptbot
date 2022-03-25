from aptbot.bot import Bot, Message, Commands
import os
import importlib
import importlib.util
from importlib import reload
import traceback

import tools.raid
reload(tools.raid)


PATH = os.path.dirname(os.path.realpath(__file__))

commands = [
    c for c in os.listdir(PATH) if os.path.isfile(os.path.join(PATH, c))
]
commands.remove(os.path.split(__file__)[1])
specs = {}
for command in commands:
    if command.split('.')[0]:
        specs[command.split('.')[0]] = (
            importlib.util.spec_from_file_location(
                f"{command.split('.')[0]}",
                os.path.join(PATH, command)
            )
        )

modules = {}
for command in specs:
    modules[command] = importlib.util.module_from_spec(specs[command])
    if specs[command] and specs[command].loader:
        try:
            specs[command].loader.exec_module(modules[command])
        except Exception as e:
            print()
            print(traceback.format_exc())
            print(f"Problem Loading Module: {e}")


def main(bot: Bot, message: Message):
    prefix = '?'
    command = message.value.split(' ')[0]
    if message.command == Commands.PRIVMSG and command.startswith(prefix):
        try:
            modules[command[1:]].main(bot, message)
        except KeyError:
            pass

    tools.raid.raid(bot, message)
