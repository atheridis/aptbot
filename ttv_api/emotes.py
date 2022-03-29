from ttv_api import *


@dataclass
class Emote:
    emote_id: str
    name: str
    tier: Optional[str]
    emote_type: Optional[str]
    emote_set_id: Optional[str]
    emote_format: list[str]
    scale: list[str]
    theme_mode: list[str]


def get_global_emotes() -> Optional[list[Emote]]:
    http = urllib3.PoolManager()
    r = http.request(
        "GET",
        URL.emotes_channel.value,
        headers=HEADER,
    )

    if r.status != 200:
        return None

    data = json.loads(r.data.decode("utf-8"))["data"]
    emotes = []

    for emote in data:
        emotes.append(
            Emote(
                emote["id"],
                emote["name"],
                None,
                None,
                None,
                emote["format"],
                emote["scale"],
                emote["theme_mode"],
            )
        )

    return emotes


def get_channel_emotes(channel_id: str) -> Optional[list[Emote]]:
    params = f"?broadcaster_id={channel_id}"

    http = urllib3.PoolManager()
    r = http.request(
        "GET",
        URL.emotes_channel.value + params,
        headers=HEADER,
    )

    if r.status != 200:
        return None

    data = json.loads(r.data.decode("utf-8"))["data"]
    emotes = []

    for emote in data:
        emotes.append(
            Emote(
                emote["id"],
                emote["name"],
                emote["tier"],
                emote["emote_type"],
                emote["emote_set_it"],
                emote["format"],
                emote["scale"],
                emote["theme_mode"],
            )
        )

    return emotes


def get_emote_image(emote_id: str, emote_format: str, theme_mode: str, scale: str):
    return f"https://static-cdn.jtvnw.net/emoticons/v2/{emote_id}/{emote_format}/{theme_mode}/{scale}"
