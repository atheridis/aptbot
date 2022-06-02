# Examples

Add an account using `aptbot --add-account "account_name"`.
A directory will be created in `~/.config/aptbot/` on Linux
or `%APPDATA%\aptbot\` on Windows with the twitch name of that account.

The contents of each example directory here should mimic the contents of the
directory with the twitch name.

Each account directory should contain a `main.py` file
with the most minimal code being:

```python
from aptbot import Bot, Message, Commands

# Runs at the beginning, when the account connects.
# Can be used for an infinite loop within the account,
# so the bot send messages, even when chat is dead.
def start(bot: Bot, message: Message):
    pass

# Gets ran every time the IRC channel sends a message.
# This can either be a message from a user
# a raid, when a mod deletes a message, etc.
def main(bot: Bot, message: Message):
    pass
```
