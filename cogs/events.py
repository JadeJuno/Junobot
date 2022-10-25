import discord
from discord.ext import commands

from libs import botutils


class Events(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		botutils.log("Events ready!")

	async def on_guild_join(self, guild: discord.Guild):
		_ = self.bot.command_prefix[guild.id]

	async def on_guild_remove(self, guild: discord.Guild):
		self.bot.command_prefix.remove(guild.id)


async def setup(bot: commands.Bot):
	await bot.add_cog(Events(bot), override=True)
