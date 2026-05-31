import logging

import discord
from discord.ext import commands

from constants import TOKEN
from utils.ops_log import send_ops_log

EXTENSIONS = (
    'auto_disable',
)


def build_intents() -> discord.Intents:
    intents = discord.Intents.none()
    intents.guilds = True
    intents.guild_messages = True
    return intents


class DisableDirectMessageBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned,
            help_command=None,
            intents=build_intents(),
        )
        self._startup_event_sent = False

    async def setup_hook(self) -> None:
        for extension in EXTENSIONS:
            await self.load_extension(f'extensions.{extension}')

    async def on_ready(self) -> None:
        if self._startup_event_sent:
            return

        self._startup_event_sent = True
        await send_ops_log(
            event_type='startup',
            severity='info',
            title='Discord Bot started',
            summary='disable direct message bot is ready.',
            extra={
                'guildCount': len(self.guilds),
                'botUser': str(self.user),
            },
        )


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    )
    DisableDirectMessageBot().run(TOKEN)


if __name__ == '__main__':
    main()
