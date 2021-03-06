"""
Datadog reporting for Dogbot.
"""
import logging

import datadog as dd

from dog import Cog

logger = logging.getLogger(__name__)


class Datadog(Cog):
    def __init__(self, bot):
        super().__init__(bot)
        self.reporting_task = bot.loop.create_task(self.datadog_report())

    def __unload(self):
        logger.debug('Cancelling Datadog reporting task.')
        if self.reporting_task:
            self.reporting_task.cancel()

    async def on_guild_join(self, g):
        await self.datadog_increment('discord.guilds.additions')

    async def on_guild_remove(self, g):
        await self.datadog_increment('discord.guilds.removals')

    async def on_command(self, ctx):
        await self.datadog_increment('dogbot.commands')

    async def datadog_increment(self, metric):
        try:
            await self.bot.loop.run_in_executor(None, dd.statsd.increment, metric)
        except Exception:
            logger.exception('Failed to report metric')

    async def datadog_report(self):
        dd.initialize(**self.bot.cfg['monitoring']['datadog'])

        while True:
            def report():
                try:
                    dd.statsd.gauge('discord.guilds', len(self.bot.guilds))
                    dd.statsd.gauge('discord.voice.clients', len(self.bot.voice_clients))
                    dd.statsd.gauge('discord.users', len(self.bot.users))
                    dd.statsd.gauge('discord.users.humans', sum(1 for user in self.bot.users if not user.bot))
                    dd.statsd.gauge('discord.users.bots', sum(1 for user in self.bot.users if user.bot))
                except RuntimeError:
                    logger.warning('Couldn\'t report metrics, trying again soon.')
                else:
                    logger.debug('Successfully reported metrics.')

            logger.debug('Reporting metrics to DataDog...')
            await self.bot.loop.run_in_executor(None, report)
            await asyncio.sleep(5)


def setup(bot):
    if 'datadog' not in bot.cfg['monitoring']:
        logger.warning('No Datadog configuration detected, not going to report statistics to Datadog.')
        return

    bot.add_cog(Datadog(bot))
