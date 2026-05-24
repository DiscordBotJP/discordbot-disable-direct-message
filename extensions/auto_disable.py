import datetime
import discord
from discord.ext import commands
from discord.ext import tasks
from daug.utils.dpyexcept import excepter
from daug.utils.dpylog import dpylogger

from utils.ops_log import exception_message, send_ops_log


INCIDENT_NOTICE_MESSAGE_TYPES = {
    discord.MessageType.guild_incident_alert_mode_enabled,
    discord.MessageType.guild_incident_alert_mode_disabled,
}


def normalize_incident_until(
    value: datetime.datetime | None,
    now: datetime.datetime,
) -> datetime.datetime | None:
    if value is None:
        return None

    if value <= now:
        return None

    return value


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
            invites_disabled_until = normalize_incident_until(
                invites_paused_until,
                now,
            )
            try:
                await guild.edit(
                    invites_disabled_until=invites_disabled_until,
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
                        'invitesPausedUntil': invites_paused_until.isoformat()
                        if invites_paused_until
                        else None,
                        'invitesDisabledUntil': invites_disabled_until.isoformat()
                        if invites_disabled_until
                        else None,
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
                        'invitesPausedUntil': invites_paused_until.isoformat()
                        if invites_paused_until
                        else None,
                        'invitesDisabledUntil': invites_disabled_until.isoformat()
                        if invites_disabled_until
                        else None,
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

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.guild is None:
            return

        if message.type not in INCIDENT_NOTICE_MESSAGE_TYPES:
            return

        try:
            await message.delete()
        except discord.errors.NotFound:
            return
        except discord.errors.Forbidden as error:
            await send_ops_log(
                event_type='incident_notice_delete_forbidden',
                severity='warning',
                title='Incident notice delete skipped: missing permission',
                summary='Bot could not delete Discord incident security notice.',
                message=str(error),
                guild_id=str(message.guild.id),
                guild_name=message.guild.name,
                extra={
                    'channelId': str(message.channel.id),
                    'messageId': str(message.id),
                    'messageType': message.type.name,
                },
            )
        except Exception as error:
            await send_ops_log(
                event_type='incident_notice_delete_error',
                severity='error',
                title='Incident notice delete failed',
                summary='Unexpected error while deleting Discord incident security notice.',
                message=exception_message(error),
                guild_id=str(message.guild.id),
                guild_name=message.guild.name,
                extra={
                    'channelId': str(message.channel.id),
                    'messageId': str(message.id),
                    'messageType': message.type.name,
                },
            )

    @auto_disable.before_loop
    async def before_auto_disable(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutoDisableDirectMessageCog(bot))
