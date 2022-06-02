import argparse


def parse_arguments() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        prog="aptbot",
        description="A chat bot for twitch.tv",
    )

    arg_parser.add_argument(
        "-a",
        "--add-account",
        type=str,
        help=f"Add an account to connect with the bot",
    )

    arg_parser.add_argument(
        "-d",
        "--disable-account",
        type=str,
        help=f"Disable an account from the bot",
    )

    arg_parser.add_argument(
        "-s",
        "--send-message",
        type=str,
        help=f"Send a message to skgyorugo",
    )

    arg_parser.add_argument(
        "--enable",
        default=False,
        action="store_true",
        help=f"Enable the bot",
    )

    arg_parser.add_argument(
        "--disable",
        default=False,
        action="store_true",
        help=f"Disable the bot",
    )

    arg_parser.add_argument(
        "--update",
        default=False,
        action="store_true",
        help=f"Update the bot",
    )

    return arg_parser.parse_args()
