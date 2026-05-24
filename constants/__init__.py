from dotenv import load_dotenv
from os import getenv

load_dotenv()

TOKEN = getenv('DISCORD_BOT_TOKEN')

OPS_LOG_HUB_URL = getenv(
    'OPS_LOG_HUB_URL',
    'https://ops-log-hub.up.railway.app/api/ingest/discord-bot',
)
OPS_LOG_HUB_KEY = getenv('OPS_LOG_HUB_KEY')
OPS_LOG_HUB_ENVIRONMENT = getenv('OPS_LOG_HUB_ENVIRONMENT', 'production')
OPS_LOG_HUB_PROJECT = getenv('OPS_LOG_HUB_PROJECT', 'discordbot_disable_direct_message')
OPS_LOG_HUB_TIMEOUT_SECONDS = float(getenv('OPS_LOG_HUB_TIMEOUT_SECONDS', '5'))
