import os

if "XDG_CONFIG_HOME" in os.environ:
    CONFIG_HOME = os.environ["XDG_CONFIG_HOME"]
elif "APPDATA" in os.environ:
    CONFIG_HOME = os.environ["APPDATA"]
else:
    CONFIG_HOME = os.path.join(os.environ["HOME"], ".config")

CONFIG_PATH = os.path.join(CONFIG_HOME, f"aptbot")


PORT = 26538
LOCALHOST = "127.0.0.1"
