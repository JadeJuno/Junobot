import difflib
import discord
import traceback
from discord.ext import commands

from bot import config, is_bot_owner, is_origin_mod

command_list = ['8ball', 'ban', 'choose', 'clear', 'coinflip', 'detect', 'dieroll', 'flip', 'flipcoin', 'google',
				'googleit', 'googlesearch', 'help', 'kick', 'langlist', 'language', 'languagelist', 'morse',
				'morsecode', 'pin', 'ping', 'prefix', 'roll', 'rolldie', 'say', 'translate', 'unban', 'wikipedia']


class CommandErrorHandler(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.log = None

	@commands.Cog.listener()
	async def on_ready(self):
		self.log = self.client.get_channel(config["log_channel"])

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		if hasattr(ctx.command, 'on_error'):
			return

		cog = ctx.cog
		if cog:
			if cog._get_overridden_method(cog.cog_command_error) is not None:
				return

		if isinstance(error, commands.CommandNotFound):
			command = ctx.message.content.lstrip(ctx.prefix).split(" ")
			command = command[0]
			for com in command_list:
				similarity = difflib.SequenceMatcher(None, command, com).ratio()
				if similarity >= 0.6:
					await ctx.send(f"Error: That command doesn't exist. Did you mean `{ctx.prefix}{com}`?")
			return

		error = getattr(error, 'original', error)

		if isinstance(error, commands.DisabledCommand):
			await ctx.send(f'{ctx.command} has been disabled.')

		elif isinstance(error, commands.NoPrivateMessage):
			try:
				await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
			except discord.HTTPException:
				pass

		elif isinstance(error, commands.MissingRequiredArgument):
			missing_param = error.param.name.replace("_", " ").capitalize()
			await ctx.send(f"Error: Missing argument `{missing_param}`.")

		else:
			check_message = await ctx.send(
				"There was an unexpected error. Do you want to send the details to the bot owner?")
			await check_message.add_reaction("\U00002705")
			await check_message.add_reaction("\U0000274c")

			def check(r, u):
				user_check = u.id == ctx.author.id or u.guild_permissions.administrator or is_origin_mod(ctx) or is_bot_owner(ctx) and ctx.author.bot
				return user_check and r.message == check_message and str(r.emoji) in ["\U00002705", "\U0000274c"]

			reaction, user = await self.client.wait_for('reaction_add', check=check)
			if str(reaction.emoji) == "\U00002705":
				tback = traceback.format_exception(type(error), error, error.__traceback__)
				str_tback = ""
				for line in tback:
					str_tback += line
				await self.log.send(
					f'Unknown Exception in "{ctx.message.channel.guild.name}": ```python\n{str_tback}\n```\n\nMessage that caused the error: `{ctx.message.content}`')
			elif str(reaction.emoji) == "\U0000274c":
				return await ctx.send("Understood.")


def setup(client):
	client.add_cog(CommandErrorHandler(client))
