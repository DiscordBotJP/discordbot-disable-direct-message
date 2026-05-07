import datetime
import os
import discord
from discord.ext import commands
from discord.ext import tasks
from daug.utils.dpyexcept import excepter
from daug.utils.dpylog import dpylogger


def _parse_guild_id_set(value: str) -> set[int]:
    guild_ids: set[int] = set()
    for part in value.split(','):
        stripped = part.strip()
        if not stripped:
            continue
        if stripped.isdigit():
            guild_ids.add(int(stripped))
    return guild_ids


class AutoDisableDirectMessageCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.target_hours = int(os.getenv('DM_DISABLE_TARGET_HOURS', '24'))
        self.min_remaining_hours = int(os.getenv('DM_DISABLE_MIN_REMAINING_HOURS', '12'))
        self.enabled_guild_ids = _parse_guild_id_set(os.getenv('DM_DISABLE_ENABLED_GUILD_IDS', ''))
        self.auto_disable.start()

    def _is_target_guild(self, guild: discord.Guild) -> bool:
        if not self.enabled_guild_ids:
            return True
        return guild.id in self.enabled_guild_ids

    @tasks.loop(hours=6)
    @excepter
    @dpylogger
    async def auto_disable(self):
        now = discord.utils.utcnow()
        target_until = now + datetime.timedelta(hours=self.target_hours)
        minimum_until = now + datetime.timedelta(hours=self.min_remaining_hours)

        for guild in self.bot.guilds:
            if not self._is_target_guild(guild):
                continue

            current_until = guild.dms_disabled_until
            if current_until is not None and current_until >= minimum_until:
                continue

            invites_disabled_until = getattr(guild, 'invites_disabled_until', None)

            try:
                await guild.edit(
                    invites_disabled_until=invites_disabled_until,
                    dms_disabled_until=target_until,
                )
            except discord.errors.Forbidden:
                pass

    @auto_disable.before_loop
    async def before_auto_disable(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutoDisableDirectMessageCog(bot))
