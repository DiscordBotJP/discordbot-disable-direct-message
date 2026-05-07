import datetime
import discord
from discord.ext import commands
from discord.ext import tasks
from daug.utils.dpyexcept import excepter
from daug.utils.dpylog import dpylogger


class AutoDisableDirectMessageCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.auto_disable.start()

    @tasks.loop(hours=6)
    @excepter
    @dpylogger
    async def auto_disable(self):
        now = discord.utils.utcnow()
        dms_disabled_until = now + datetime.timedelta(hours=24)

        for guild in self.bot.guilds:
            invites_paused_until = guild.invites_paused_until
            try:
                await guild.edit(
                    invites_disabled_until=invites_paused_until,
                    dms_disabled_until=dms_disabled_until,
                )
            except discord.errors.Forbidden:
                pass

    @auto_disable.before_loop
    async def before_auto_disable(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutoDisableDirectMessageCog(bot))
