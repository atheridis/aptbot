from aptbot.bot import Message, Commands, Bot


def main(bot: Bot, message: Message):
    msg = message.nick + " you have been scammed KEKW"
    bot.send_privmsg(message.channel, msg)
