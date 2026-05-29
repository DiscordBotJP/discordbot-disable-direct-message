import logging

import discord
from discord.ext import commands

from constants import TOKEN

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

    async def setup_hook(self) -> None:
        for extension in EXTENSIONS:
            await self.load_extension(f'extensions.{extension}')


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    )
    DisableDirectMessageBot().run(TOKEN)


if __name__ == '__main__':
    main()
