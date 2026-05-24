import datetime
import discord
from discord.ext import commands
from discord.ext import tasks
from daug.utils.dpyexcept import excepter
from daug.utils.dpylog import dpylogger

from utils.ops_log import exception_message, send_ops_log


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
        updated_count = 0
        forbidden_count = 0
        unexpected_error_count = 0

        await send_ops_log(
            event_type='auto_disable_started',
            severity='info',
            title='DM auto disable task started',
            summary='Started updating dms_disabled_until for joined guilds.',
            extra={
                'guildCount': len(self.bot.guilds),
                'dmsDisabledUntil': dms_disabled_until.isoformat(),
            },
        )

        for guild in self.bot.guilds:
            invites_paused_until = guild.invites_paused_until
            try:
                await guild.edit(
                    invites_disabled_until=invites_paused_until,
                    dms_disabled_until=dms_disabled_until,
                )
                updated_count += 1
            except discord.errors.Forbidden as error:
                forbidden_count += 1
                await send_ops_log(
                    event_type='auto_disable_forbidden',
                    severity='warning',
                    title='DM auto disable skipped: missing permission',
                    summary='Bot could not edit guild security settings due to missing permission.',
                    message=str(error),
                    guild_id=str(guild.id),
                    guild_name=guild.name,
                    extra={
                        'dmsDisabledUntil': dms_disabled_until.isoformat(),
                    },
                )
            except Exception as error:
                unexpected_error_count += 1
                await send_ops_log(
                    event_type='auto_disable_error',
                    severity='error',
                    title='DM auto disable failed for guild',
                    summary='Unexpected error while updating guild security settings.',
                    message=exception_message(error),
                    guild_id=str(guild.id),
                    guild_name=guild.name,
                    extra={
                        'dmsDisabledUntil': dms_disabled_until.isoformat(),
                    },
                )

        await send_ops_log(
            event_type='auto_disable_completed',
            severity='info' if unexpected_error_count == 0 else 'warning',
            title='DM auto disable task completed',
            summary='Finished updating dms_disabled_until for joined guilds.',
            extra={
                'guildCount': len(self.bot.guilds),
                'updatedCount': updated_count,
                'forbiddenCount': forbidden_count,
                'unexpectedErrorCount': unexpected_error_count,
                'dmsDisabledUntil': dms_disabled_until.isoformat(),
            },
        )

    @auto_disable.before_loop
    async def before_auto_disable(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutoDisableDirectMessageCog(bot))
