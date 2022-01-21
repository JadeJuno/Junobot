import calendar
import difflib
import io
import traceback

import discord
from discord.ext import commands

import botutilities


class CommandErrorHandler(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.log = None

	@commands.Cog.listener()
	async def on_ready(self):
		self.log = self.client.get_channel(botutilities.config["log_channel"])

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		if hasattr(ctx.command, 'on_error'):
			return

		cog = ctx.cog
		if cog:
			if cog._get_overridden_method(cog.cog_command_error) is not None:
				return

		if isinstance(error, commands.CommandNotFound):
			cmd = ctx.invoked_with
			cmds = [cmd.name for cmd in self.client.commands]
			matches = difflib.get_close_matches(cmd, cmds, n=1)
			if len(matches) > 0:
				await ctx.reply(f'Command "{cmd}" not found, did you mean "{matches[0]}"?')
			return

		error = getattr(error, 'original', error)

		if isinstance(error, commands.DisabledCommand):
			await ctx.reply(f'`{ctx.prefix}{ctx.command}` has been disabled.')

		elif isinstance(error, commands.NoPrivateMessage):
			try:
				await ctx.author.send(f'`{ctx.prefix}{ctx.command}` can not be used in Private Messages.')
			except discord.HTTPException:
				pass

		elif isinstance(error, commands.MissingRequiredArgument):
			missing_param = error.param.name.replace("_", " ").capitalize().strip()
			await ctx.reply(f"Error: Missing argument `{missing_param}`.")

		elif isinstance(error, commands.MissingPermissions):
			missing_perm = error.missing_permissions[0].title()
			await ctx.reply(f'Error: You are missing the `{missing_perm}` permission to run this command.')

		else:
			check_message = await ctx.send(
				"There was an unexpected error. Do you want to send the details to the bot owner?")
			await check_message.add_reaction("\U00002705")
			await check_message.add_reaction("\U0000274c")

			def check(r, u):
				user_check = (u.id == ctx.author.id or u.guild_permissions.administrator or u.id in botutilities.config[
					"owners_id"]) and not u.bot
				return user_check and r.message == check_message and str(r.emoji) in ("\U00002705", "\U0000274c")

			reaction, user = await self.client.wait_for('reaction_add', check=check)
			if str(reaction.emoji) == "\U00002705":
				tback = traceback.format_exception(type(error), error, error.__traceback__)
				str_tback = ""
				for line in tback:
					str_tback += line
				content = botutilities.make_bug_report_file(ctx)
				with io.StringIO() as file:
					file.write(content)
					file.seek(0)
					await self.log.send(
						f'{botutilities.ping_all_bot_owners()}\n Uncatched Exception in "{ctx.guild.name}" at <t:{int(calendar.timegm(ctx.message.created_at.utctimetuple()))}>: ```python\n{str_tback}\n```\n\nMessage that caused the error: `{ctx.message.content}`',
						file=discord.File(fp=file,
										  filename=f"bug_report_{calendar.timegm(ctx.message.created_at.utctimetuple())}.txt"))
				return await ctx.send("Error Message sent.")
			elif str(reaction.emoji) == "\U0000274c":
				return await ctx.send("Understood.")


def setup(client):
	client.add_cog(CommandErrorHandler(client), override=True)
