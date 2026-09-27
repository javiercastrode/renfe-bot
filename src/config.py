"""Module to manage the configuration of the bot."""

import os
import sys

def get_bot_token() -> str:
    """Read the environment variable to obtain the bot's secret token.

    :return: The bot instance secret token
    :rtype: str
    """
    token = os.environ.get("BOT_TOKEN")

    if not token:
        print("ERROR: La variable de entorno BOT_TOKEN no está definida.", file=sys.stderr)
        print("Asegúrate de configurarla en tu archivo .env o en el docker-compose.yml", file=sys.stderr)
        sys.exit(1)

    return token
