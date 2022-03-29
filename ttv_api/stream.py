from ttv_api import *


@dataclass
class Stream:
    stream_id: str
    user_id: str
    login: str
    display_name: str
    game_id: str
    game_name: str
    stream_type: str
    stream_title: str
    viewer_count: int
    started_at: datetime
    language: str
    thumbnail_url: str
    tag_ids: str
    is_mature: bool


def get_streams(
    user_ids: list[str] = [],
    user_logins: list[str] = [],
    game_ids: list[str] = [],
    languages: list[str] = [],
    max_streams: int = 100,
) -> Optional[list[Stream]]:

    streams = []
    params = "?first=100&"
    for user_id in user_ids:
        params += f"user_id={user_id}&"
    for user_login in user_logins:
        params += f"user_login={user_login}&"
    for game_id in game_ids:
        params += f"game_id={game_id}&"
    for language in languages:
        params += f"language={language}&"

    while True:
        http = urllib3.PoolManager()
        r = http.request(
            "GET",
            URL.streams.value + params,
            headers=HEADER,
        )
        if r.status != 200:
            return None

        requested_data = json.loads(r.data.decode("utf-8"))
        data = requested_data["data"]

        for stream in data:
            dt = datetime.strptime(stream["started_at"], "%Y-%m-%dT%H:%M:%SZ")
            streams.append(
                Stream(
                    stream["id"],
                    stream["user_id"],
                    stream["user_login"],
                    stream["user_name"],
                    stream["game_id"],
                    stream["game_name"],
                    stream["type"],
                    stream["title"],
                    stream["viewer_count"],
                    dt,
                    stream["language"],
                    stream["thumbnail_url"],
                    stream["tag_ids"],
                    stream["is_mature"],
                )
            )
            if len(streams) >= max_streams:
                return streams

        try:
            cursor = requested_data["pagination"]["cursor"]
        except KeyError:
            return streams
        else:
            params = f"?first=100&after={cursor}"
