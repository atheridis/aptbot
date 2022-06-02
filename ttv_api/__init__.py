import json
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Union

import urllib3
from dotenv import load_dotenv

load_dotenv()

NICK = os.getenv("APTBOT_NICK")
OAUTH = os.getenv("APTBOT_OAUTH")
CLIENT_ID = os.getenv("APTBOT_CLIENT_ID")

HEADER = {
    "Authorization": f"Bearer {OAUTH}",
    "Client-Id": f"{CLIENT_ID}",
    "Content-Type": "application/json",
}

BASE_URL = "https://api.twitch.tv/helix/"


class URL(Enum):
    ads = BASE_URL + "channels/commercial"
    analytics = BASE_URL + "analytics"
    channels = BASE_URL + "channels"
    emotes_channel = BASE_URL + "chat/emotes"
    emotes_global = BASE_URL + "chat/emotes/global"
    streams = BASE_URL + "streams"
    users = BASE_URL + "users"
