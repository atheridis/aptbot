from aptbot.bot import Message, Commands, Bot


def main(bot: Bot, message: Message):
    msg = ' '.join(message.value.split(' ')[1:])
    msg = (msg + ' ') * 10
    bot.send_privmsg(message.channel, msg)
