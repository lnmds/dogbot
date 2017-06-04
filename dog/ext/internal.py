"""
Dogbot internal commands.
"""

import io
import os
from time import monotonic

import discord
import objgraph
import psutil
from discord.ext import commands
from dog import Cog
from dog.core import utils


DETAILED_PING = '''**message create:** {}
**message edit:** {}
**message delete:** {}
'''


class Internal(Cog):
    def __init__(self, bot):
        super().__init__(bot)
        self.socket_events = 0

    async def __local_check(self, ctx):
        return await self.bot.is_owner(ctx.message.author)

    async def on_socket_raw_receive(self, _):
        self.socket_events += 1

    @commands.command()
    async def dstats(self, ctx):
        """ Shows detailed stats. """
        embed = discord.Embed(title='Detailed stats')

        embed.add_field(name='Socket Events', value=utils.commas(self.socket_events))

        # log file
        log_size = os.path.getsize('dog.log')
        kb = log_size / 10 ** 3
        mb = log_size / 10 ** 6
        embed.add_field(name='Log File', value=f'{log_size} bytes\n{round(kb, 2)} KB, {round(mb, 2)} MB')

        # ram
        process = psutil.Process(os.getpid())
        mem = process.memory_info()
        vmem = psutil.virtual_memory()
        total = round(vmem.total / 10 ** 9, 3)
        avail = round(vmem.available / 10 ** 9, 3)
        mem_gb = round(mem.rss / 10 ** 9, 2)
        mem_mb = round(mem.rss / 10 ** 6, 2)
        embed.add_field(name='RAM', value=f'{avail} GB/{total} GB total\n{mem_mb} MB, {mem_gb} GB')

        # owner
        owner = (await ctx.bot.application_info()).owner
        embed.add_field(name='Owner', value=f'{owner.id}\n<@{owner.id}>')

        # guilds
        embed.add_field(name='Guilds', value=f'{utils.commas(len(ctx.bot.guilds))} total')

        async with ctx.bot.pgpool.acquire() as conn:
            record = await conn.fetchrow('SELECT SUM(times_used) FROM command_statistics')
            embed.add_field(name='Commands Ran', value=utils.commas(record['sum']))

        await ctx.send(embed=embed)

    @commands.command()
    async def dping(self, ctx):
        """ Detailed ping. """
        def ms(before, after):
            return str(round((after - before) * 1000, 2)) + 'ms'

        # do it
        before_send = monotonic()
        msg = await ctx.send('...')
        after_send = monotonic()
        await msg.edit(content='..')
        after_edit = monotonic()
        await msg.delete()
        after_delete = monotonic()

        await ctx.send(DETAILED_PING.format(
            ms(before_send, after_send),
            ms(after_send, after_edit),
            ms(after_edit, after_delete)
        ))

    @commands.group()
    async def mem(self, ctx):
        """ Memory statistics. """
        pass

    @mem.command()
    async def count(self, ctx, type_name):
        """ Counts the amount of an object tracked by the GC. """
        cnt = objgraph.count(type_name)
        if not cnt:
            return await ctx.send('Not found.')
        await ctx.send('`{}`: {}'.format(type_name, utils.commas(cnt)))

    @mem.command()
    async def common_types(self, ctx, limit: int=5):
        """ Shows common types tracked by the GC. """
        with io.StringIO() as stdout:
            objgraph.show_most_common_types(limit=limit, file=stdout)
            await ctx.send('```\n{}\n```'.format(stdout.getvalue()))


def setup(bot):
    bot.add_cog(Internal(bot))
