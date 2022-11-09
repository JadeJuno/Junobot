import calendar
import difflib
import io
from traceback import format_exception

import discord
from discord.ext import commands

from libs import botutils
from libs.botutils import error_template


class CommandErrorHandler(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		botutils.log("Error Handler Ready!")

	@commands.Cog.listener()
	async def on_command_error(self, ctx: commands.Context, error: Exception):
		timestamp = calendar.timegm(ctx.message.created_at.utctimetuple())
		log = self.bot.get_channel(botutils.config["log_channel"])
		owner_ping = self.bot.get_user(self.bot.owner_id).mention

		cog = ctx.cog
		if cog:
			if cog._get_overridden_method(cog.cog_command_error) is not None:
				return

		if isinstance(error, commands.CommandNotFound):
			cmd = ctx.invoked_with
			cmds = [cmd.name for cmd in self.bot.commands]
			matches = difflib.get_close_matches(cmd, cmds, n=1)
			if len(matches) > 0:
				await error_template(ctx, f'Command "{cmd}" not found, did you mean "{matches[0]}"?')
			return

		error = getattr(error, 'original', error)

		if isinstance(error, commands.DisabledCommand):
			await error_template(ctx, f'`{ctx.prefix}{ctx.command}` has been disabled.')

		elif isinstance(error, commands.NoPrivateMessage):
			try:
				await error_template(ctx, f'`{ctx.prefix}{ctx.command}` can not be used in Private Messages.')
			except discord.HTTPException:
				pass

		elif isinstance(error, commands.MissingRequiredArgument):
			missing_param = botutils.get_param(error.param)
			await error_template(ctx, f"Missing argument `{missing_param}`.")

		elif isinstance(error, commands.MissingPermissions):
			missing_perm = error.missing_permissions[0].replace('_', ' ').title()
			await error_template(ctx, f'You are missing the `{missing_perm}` permission to run this command.')

		elif isinstance(error, commands.NotOwner):
			await error_template(ctx, "This command is restricted to my owner.")

		elif isinstance(error, botutils.WIPCommandError):
			await error_template(ctx, "This command is a WIP. Please wait.")

		elif isinstance(error, botutils.CommandUnderMaintenanceError):
			await error_template(ctx,
			                     f"This command is under maintenance. Sorry for the inconvenience. Reason: `{error.reason}`.")

		elif isinstance(error, discord.HTTPException) and error.code == 50035:
			await error_template(ctx, "The resulting message for this command is over the character limit.")

		elif isinstance(error, commands.MissingRequiredAttachment):
			await error_template(ctx, "This command requires a file to be attached.")

		elif isinstance(error, commands.BadLiteralArgument):
			param = botutils.get_param(error.param)
			literals = [f"`{literal}`" for literal in error.literals]
			literals_join = ""  # Output should look like "`1`, `2`, `3`, `4`, (...) or `n`"
			for i, literal in enumerate(literals, 1):
				if i == 1:
					literals_join += literal
				elif i == len(literals):
					literals_join += f" or {literal}"
				else:
					literals_join += f", {literal}"

			await error_template(ctx, f'The "{param}" argument has to be either {literals_join}.')

		elif isinstance(error, commands.BadArgument) and hasattr(ctx.command, 'on_error'):
			pass

		# Generic Error
		else:
			str_tback = "".join(format_exception(type(error), error, error.__traceback__))

			content = botutils.make_bug_report_file(ctx)
			with io.StringIO(content) as f:
				# noinspection PyTypeChecker
				attachs = [discord.File(f, filename=f"bug_report_{timestamp}.txt")]

			try:
				guild_name = ctx.guild.name
			except AttributeError:
				guild_name = "A DM"

			log_message = f'{owner_ping}\n Uncatched Exception in "{guild_name}" at <t:{timestamp}>: '
			if len(log_message) + len(f"```python\n{str_tback}\n```") > 2000:
				log_message += f'Error message too long.\nMessage that caused the error: `{ctx.message.content}`'
				with io.StringIO(str_tback) as f:
					# noinspection PyTypeChecker
					attachs.append(discord.File(f, filename=f"error_message_{timestamp}.py"))
			else:
				log_message += f"```python\n{str_tback}\n```"

			await log.send(log_message, files=attachs)

			await ctx.reply("There was an unexpected error. An error report has been sent to my owner.")


async def setup(bot: commands.Bot):
	await bot.add_cog(CommandErrorHandler(bot), override=True)
