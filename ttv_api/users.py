from ttv_api import *


@dataclass
class User:
    user_id: str
    login: str
    display_name: str
    user_type: str
    broadcaster_type: str
    description: str
    profile_image_url: str
    offline_image_url: str
    view_count: int
    created_at: datetime


def get_users(
    user_ids: list[str] = [], user_logins: list[str] = []
) -> Optional[list[User]]:
    params = "?"
    for user_id in user_ids:
        params += f"id={user_id}&"
    for user_login in user_logins:
        params += f"login={user_login}&"

    http = urllib3.PoolManager()
    r = http.request(
        "GET",
        URL.users.value + params,
        headers=HEADER,
    )
    if r.status != 200:
        return None

    data = json.loads(r.data.decode("utf-8"))["data"]
    users = []

    for user in data:
        dt = datetime.strptime(user["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        users.append(
            User(
                user["id"],
                user["login"],
                user["display_name"],
                user["type"],
                user["broadcaster_type"],
                user["description"],
                user["profile_image_url"],
                user["offline_image_url"],
                user["view_count"],
                dt,
            )
        )
    return users
