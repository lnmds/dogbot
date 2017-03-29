import logging
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

class DogBot(commands.Bot):
    async def on_ready(self):
        logger.info('logged in as %s', self.user.id)
        print('logged in')
        print(f' name: {self.user.name}#{self.user.discriminator}')
        print(f' id:   {self.user.id}')

        # helpful game
        short_prefix = min(self.command_prefix, key=len)
        help_game = discord.Game(name=f'{short_prefix}help')
        await self.change_presence(game=help_game)