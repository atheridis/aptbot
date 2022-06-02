from aptbot import Bot, Commands, Message


def start(bot: Bot, message: Message):
    pass


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
            bot.send_privmsg(
                message.channel,
                f"hello {message.tags['display-name']}",
                reply=message.tags["id"],
            )
