import time
from threading import Event

from aptbot import Bot, Commands, Message


# Starts when the bot is enabled
# Sends the message "Hello, world!" every 2 minutes to the channel
# stop_event is set to True, when you disable the account with aptbot -d "account_name"
def start(bot: Bot, message: Message, stop_event: Event):
    while not stop_event.is_set():
        bot.send_message(message.channel, "Hello, world!")
        time.sleep(120)


def main(bot: Bot, message: Message):
    # Check whether the message sent is a message by a user in chat
    # and not some notification.
    if message.command == Commands.PRIVMSG:
        # Check the content of the message and if the first word is '!hello'
        # send a reply by creating a new thread.
        # You can also use `message.nick` instead of `message.tags['display-name']`
        # but then the message sent back
        # will contain the name of the user in all lowercase
        if message.value.split()[0] == "!hello":
            bot.send_message(
                message.channel,
                f"hello {message.tags['display-name']}",
                reply=message.tags["id"],
            )
