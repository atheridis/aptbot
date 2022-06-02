# aptbot

--------
A chatbot for twitch.tv

## Dependencies

--------------

* Python (any >=3.7 version should work)
* python-dotenv
* urllib3

## Install

----------

It is highly recommended you install and run aptbot in a virtual environment.

Clone this repository `git clone https://github.com/atheridis/aptbot.git`,
change to the directory `cd aptbot`, then install the package `pip install .`.

## First Steps

----------

### Adding an account

After installing, you can add an account using `aptbot --add-account "account_name"`.
A directory will be created in `~/.config/aptbot/` on Linux
or `%APPDATA%\aptbot\accounts\` on Windows with the twitch name of that account.

Each account directory should contain a `main.py` file
with the most minimal code being:

```python
from aptbot import Bot, Message, Commands

# Runs at the beginning, when the account connects.
# Can be used for an infinite loop within the account,
# so the bot can send messages, even when chat isn't moving.
def start(bot: Bot, message: Message, stop_event):
    pass

# Gets ran every time the IRC channel sends a message.
# This can either be a message from a user
# a raid, when a mod deletes a message, etc.
def main(bot: Bot, message: Message):
    pass
```

When you add an account using `aptbot --add-account "account_name"`
or `aptbot -a "account_name"`,
the following python file called `main.py` will be created:

```python
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
```

### Activating your bot

Once you have an account set up you can enable the bot by using `aptbot --enable`.
To stop the bot from running use `aptbot --disable` on another terminal.

After testing you would want to run `aptbot --enable` as a daemon, the easiest way
to do that on Linux is to use `nohup aptbot --enable &`. This will leave a `nohup.out`
file in the directory you're in, which may not be ideal. If you wish to have no output
other than the logs provided in `~/.cache/aptbot/logs/aptbot.log` you may use
`nohup aptbot --enable </dev/null >/dev/null 2>&1 &`. You are now free to control
aptbot through any terminal. Type `aptbot --help` to see all available commands.

### More than one file

You can import modules from the same directory that the `main.py` files are in,
but if you want `aptbot --update` to work on them you will need to reload the modules
due to how python handles module imports. Some examples will be coming soon.

## BUGS

-------

* Editing any of the directory names in `~/.config/aptbot/`
or `%APPDATA%\aptbot\accounts\` while the bot is running, may cause weird behaviour.
