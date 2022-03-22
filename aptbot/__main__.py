import socket
import aptbot.args
import time
import aptbot.bot
import os
import sys
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

PORT = 26538
LOCALHOST = "127.0.0.1"


def loop(bot: aptbot.bot.Bot):
    while True:
        messages = bot.receive_messages()
        for message in messages:
            pass
        time.sleep(0.001)


def listener():
    NICK = os.getenv("APTBOT_NICK")
    OAUTH = os.getenv("APTBOT_OAUTH")
    CLIENT_ID = os.getenv("APTBOT_CLIENT_ID")
    print(NICK)
    print(OAUTH)
    print(CLIENT_ID)
    if NICK and OAUTH and CLIENT_ID:
        bot = aptbot.bot.Bot(NICK, OAUTH, CLIENT_ID)
    else:
        sys.exit(1)
    bot.connect()
    bot.join_channel("skgyorugo")
    Thread(target=loop, args=(bot,)).start()
    s = socket.socket()
    s.bind(("", PORT))
    s.listen(5)

    while True:
        c, addr = s.accept()
        msg = c.recv(1024).decode()
        bot.send_privmsg("skgyorugo", msg)
        time.sleep(1)


def send(acc: str):
    s = socket.socket()
    s.connect(("", PORT))
    print("Socket connected")
    s.send(acc.encode())
    s.close()


def main():
    argsv = aptbot.args.parse_arguments()
    if argsv.enable:
        listener()
    if argsv.add_account:
        send(argsv.add_account)
    print("hi")


if __name__ == "__main__":
    main()
