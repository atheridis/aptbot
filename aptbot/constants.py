import os

if os.name == "posix":
    if "XDG_CONFIG_HOME" in os.environ and "XDG_CACHE_HOME" in os.environ:
        CONFIG_PATH = os.path.join(os.environ["XDG_CONFIG_HOME"], f"aptbot")
        CONFIG_LOGS = os.path.join(os.environ["XDG_CACHE_HOME"], "aptbot")
    else:
        CONFIG_PATH = os.path.join(os.environ["HOME"], ".config/aptbot")
        CONFIG_LOGS = os.path.join(os.environ["HOME"], ".cache/aptbot/logs")
elif os.name == "nt":
    if "APPDATA" in os.environ:
        CONFIG_PATH = os.path.join(os.environ["APPDATA"], "aptbot/accounts")
        CONFIG_LOGS = os.path.join(os.environ["APPDATA"], "aptbot/logs")
    else:
        print(
            "APPDATA is not set, something must be very wrong.",
            file=sys.stderr,
        )
        sys.exit(1)
else:
    print("Your OS is not supported", file=sys.stderr)
    sys.exit(1)

MAIN_FILE_NAME = "main.py"


PORT = 26538
LOCALHOST = "127.0.0.1"

os.makedirs(CONFIG_LOGS, exist_ok=True)
CONFIG_FILE = os.path.join(CONFIG_LOGS, "aptbot.log")
# open(CONFIG_FILE, "a").close()

LOGGING_DICT = {
    "version": 1,
    "formatters": {
        "simple": {"format": "[%(levelname)s] %(asctime)s: %(name)s; %(message)s"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "INFO",
            "formatter": "simple",
            "filename": CONFIG_FILE,
            "when": "w0",
            "utc": True,
            "backupCount": 3,
        },
    },
    "loggers": {
        "basicLogger": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": "no",
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"],
    },
    "disable_existing_loggers": False,
}
