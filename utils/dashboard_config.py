import asyncio
import base64
import hashlib
import hmac
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from constants import DASHBOARD_CONFIG_BOT_ID, DASHBOARD_CONFIG_SECRET, DASHBOARD_CONFIG_URL, TOKEN


@dataclass(frozen=True)
class GuildDashboardSetting:
    guild_id: str
    enabled: bool
    interval_minutes: int
    anchor_time: str
    timezone: str


class DashboardSettings:
    def __init__(self, payload: dict[str, Any] | None) -> None:
        self.payload = payload or {}
        self.defaults = self.payload.get('defaults') or {}
        self.settings = {
            str(setting.get('guildId')): setting
            for setting in self.payload.get('settings', [])
            if setting.get('guildId')
        }

    def for_guild(self, guild_id: int | str) -> GuildDashboardSetting:
        raw = {
            **self.defaults,
            **self.settings.get(str(guild_id), {}),
        }
        return GuildDashboardSetting(
            guild_id=str(guild_id),
            enabled=raw.get('enabled') is not False,
            interval_minutes=int(raw.get('intervalMinutes') or 360),
            anchor_time=str(raw.get('anchorTime') or '00:00'),
            timezone=str(raw.get('timezone') or 'Asia/Tokyo'),
        )

    def shortest_interval_minutes(self, fallback: int) -> int:
        values = [
            self.for_guild(guild_id).interval_minutes
            for guild_id in self.settings
            if self.for_guild(guild_id).enabled
        ]
        return min(values) if values else fallback


def bot_id_from_token() -> str:
    token_head = TOKEN.split('.', 1)[0]
    padding = '=' * (-len(token_head) % 4)
    return base64.urlsafe_b64decode(f'{token_head}{padding}').decode()


async def fetch_dashboard_settings() -> DashboardSettings:
    if not DASHBOARD_CONFIG_SECRET:
        return DashboardSettings(None)

    bot_id = DASHBOARD_CONFIG_BOT_ID or bot_id_from_token()
    base_url = DASHBOARD_CONFIG_URL.rstrip('/')
    url = f'{base_url}/{bot_id}'
    parsed = urlparse(url)
    path = parsed.path
    timestamp = str(int(time.time() * 1000))
    signature = _sign(f'{timestamp}.GET.{path}', DASHBOARD_CONFIG_SECRET)

    def request_settings() -> dict[str, Any] | None:
        request = urllib.request.Request(
            url,
            headers={
                'Accept': 'application/json',
                'X-Dashboard-Timestamp': timestamp,
                'X-Dashboard-Signature': f'v1={signature}',
            },
            method='GET',
        )
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return json.loads(response.read().decode())
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            return None

    return DashboardSettings(await asyncio.to_thread(request_settings))


def _sign(value: str, secret: str) -> str:
    digest = hmac.new(secret.encode(), value.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip('=')
