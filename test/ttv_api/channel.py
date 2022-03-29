import ttv_api.channel
import ttv_api.users


def test_get_channel():
    channel = ttv_api.channel.get_channels("141981764")
    if isinstance(channel, list):
        assert channel[0].broadcaster_id == "141981764"
        assert channel[0].broadcaster_login == "twitchdev"
    else:
        raise Exception("Didn't find channel")


def test_get_user():
    user = ttv_api.users.get_users(user_logins=[
                                   "skgyo1238r923hrugo", "f43uif3ef", "fweuifhewuidw"])
    if isinstance(user, list):
        print(user)
        # assert user[0].user_id == "141981764"
        # assert user[0].login == "twitchdev"
    else:
        raise Exception("Didn't find channel")


if __name__ == "__main__":
    test_get_channel()
    test_get_user()
    print("Everytinhg passed")
