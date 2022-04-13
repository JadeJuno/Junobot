import calendar
import difflib
import io
import traceback

import discord
from discord.ext import commands

import botutilities


class CommandErrorHandler(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.botutilities = botutilities.BotUtilities(bot)
		print("Error Handler Ready!")

	@commands.Cog.listener()
	async def on_command_error(self, ctx: commands.Context, error):
		timestamp = calendar.timegm(ctx.message.created_at.utctimetuple())
		log = self.bot.get_channel(botutilities.config["log_channel"])
		bot_owner = self.bot.get_user(self.bot.owner_id)

		cog = ctx.cog
		if cog:
			if cog._get_overridden_method(cog.cog_command_error) is not None:
				return

		if isinstance(error, commands.CommandNotFound):
			cmd = ctx.invoked_with
			cmds = [cmd.name for cmd in self.bot.commands]
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
			await botutilities.error_template(ctx, f"Missing argument `{missing_param}`.")

		elif isinstance(error, commands.MissingPermissions):
			missing_perm = error.missing_permissions[0].replace('_', ' ').title()
			await botutilities.error_template(ctx, f'You are missing the `{missing_perm}` permission to run this command.')

		elif isinstance(error, commands.NotOwner):
			await botutilities.error_template(ctx, f"This command is restricted to the owner of this bot.")

		elif isinstance(error, commands.BadArgument) and hasattr(ctx.command, 'on_error'):
			pass

		else:
			check = await self.botutilities.reaction_decision(ctx, "There was an unexpected error. Do you want to send the details to the bot owner?")

			if check:
				tback = traceback.format_exception(type(error), error, error.__traceback__)
				str_tback = ""
				for line in tback:
					str_tback += line
				content = botutilities.make_bug_report_file(ctx)
				with io.StringIO() as file:
					file.write(content)
					file.seek(0)
					owner_ping = bot_owner.mention
					attachs = [discord.File(fp=file, filename=f"bug_report_{timestamp}.txt")]
				log_message = f'{owner_ping}\n Uncatched Exception in "{ctx.guild.name}" at <t:{timestamp}>: ```python\n{str_tback}\n```\n\nMessage that caused the error: `{ctx.message.content}`'
				if len(log_message) > 2000:
					log_message = f'{owner_ping}\n Uncatched Exception in "{ctx.guild.name}" at <t:{timestamp}>. Error message too long.\nMessage that caused the error: `{ctx.message.content}`'
					with io.StringIO() as file2:
						file2.write(str_tback)
						file2.seek(0)
						attachs.append(discord.File(file2, filename=f"error_message_{timestamp}.txt"))
				await log.send(log_message, files=attachs)

				return await ctx.send("Error Message sent.")

			else:
				return await ctx.send("Understood.")


async def setup(client):
	await client.add_cog(CommandErrorHandler(client), override=True)
