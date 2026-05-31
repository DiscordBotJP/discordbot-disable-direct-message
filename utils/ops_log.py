import traceback
from datetime import datetime, timezone
from typing import Any

import aiohttp

from constants import (
    OPS_LOG_HUB_KEY,
    OPS_LOG_HUB_TIMEOUT_SECONDS,
    OPS_LOG_HUB_URL,
    OPS_LOG_ENVIRONMENT,
    OPS_LOG_PROJECT,
)


def exception_message(error: BaseException) -> str:
    return ''.join(traceback.format_exception_only(type(error), error)).strip()


async def send_ops_log(
    *,
    event_type: str,
    severity: str,
    title: str,
    summary: str | None = None,
    message: str | None = None,
    actor: str | None = None,
    guild_id: str | None = None,
    guild_name: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    if not OPS_LOG_HUB_URL or not OPS_LOG_HUB_KEY:
        return

    occurred_at = datetime.now(timezone.utc).isoformat()
    payload: dict[str, Any] = {
        'eventType': event_type,
        'severity': severity,
        'project': OPS_LOG_PROJECT,
        'environment': OPS_LOG_ENVIRONMENT,
        'title': title,
        'summary': summary,
        'message': message,
        'actor': actor,
        'occurredAt': occurred_at,
        'dedupeKey': make_dedupe_key(event_type, severity, guild_id),
        'normalized': {
            'guildId': guild_id,
            'guildName': guild_name,
            **(extra or {}),
        },
    }

    headers = {'Content-Type': 'application/json'}
    if OPS_LOG_HUB_KEY:
        headers['x-log-hub-key'] = OPS_LOG_HUB_KEY

    try:
        timeout = aiohttp.ClientTimeout(total=OPS_LOG_HUB_TIMEOUT_SECONDS)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(OPS_LOG_HUB_URL, json=payload, headers=headers) as response:
                if response.status >= 400:
                    text = await response.text()
                    print(f'[ops-log-hub] send failed: {response.status} {text}')
    except Exception as error:
        print(f'[ops-log-hub] send failed: {error}')


def make_dedupe_key(event_type: str, severity: str, guild_id: str | None) -> str:
    bucket = datetime.now(timezone.utc).strftime('%Y%m%d%H%M')
    return ':'.join(
        [
            OPS_LOG_PROJECT,
            OPS_LOG_ENVIRONMENT,
            severity,
            event_type,
            guild_id or 'global',
            bucket,
        ]
    )
