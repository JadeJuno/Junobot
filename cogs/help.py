import json
import random

import discord
from discord.ext import commands

from libs import botutils


class GoldHelp(commands.MinimalHelpCommand):
	with open('assets/perms.json') as f:
		PERMS = json.load(f)

	def __init__(self, **options):
		self.command_name = None
		self.appinfo = None
		super().__init__(**options, command_attrs={
				"description": "Shows a list of all the commands of the bot or the details of said commands.",
				"extras": {
					'example': 'help',
					'signature': '[Command]'
				}
			}
		)

	def command_not_found(self, command: str):
		return f'Command "{command}" not found.'

	async def prepare_help_command(self, _, command: str):
		self.command_name = command

	def get_command_signature(self, command: commands.Command):
		try:
			signature = f" {command.extras['signature']}"
		except KeyError:
			signature = f" {command.signature}" if len(command.signature) else ""
			signature = signature.replace("_", " ").title()
		return f"`{self.context.clean_prefix}{command.qualified_name}{signature}`"

	async def send_bot_help(self, mapping):
		self.appinfo = await self.context.bot.application_info()
		embed = discord.Embed(title="Help", color=random.randint(0, 0xffffff))
		for cog, _commands in mapping.items():
			filtered = await self.filter_commands(_commands, sort=True)
			command_signatures = [self.get_command_signature(c) for c in filtered]
			if command_signatures:
				cog_name = getattr(cog, "qualified_name", "No Category")
				if cog_name != "DevCog":
					embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)
		embed.set_footer(
			text=f"<>=Necessary, []=optional.\nTo see more information about a specific command, type {self.context.clean_prefix}help <command>.\n{self.context.bot.user.display_name} was created by {self.appinfo.owner}.",
			icon_url="https://i.imgur.com/ZgG8oJn.png"
		)
		channel = self.get_destination()
		await channel.send(embed=embed)

	async def send_command_help(self, command: commands.Command):
		await command.can_run(self.context)

		try:
			example = command.extras['example']
		except KeyError:
			example = None

		embed = discord.Embed(title=f"{self.context.clean_prefix}{self.command_name}", color=discord.Color.random())

		cog_name = command.cog_name
		embed.add_field(name="**Category**", value=cog_name)

		command_description = command.description if command.description else "WIP"
		embed.add_field(name="**Description**", value=command_description, inline=False)

		if len(command.aliases):
			aliases = [command.qualified_name]
			aliases.extend(command.aliases)
			aliases = [f"`{self.context.clean_prefix}{alias}`" for alias in aliases]
			embed.add_field(name="**Aliases**", value=', '.join(aliases), inline=False)

		if 'permission' in command.extras:
			embed.add_field(name="**Permissions**",
			                value=f'You require "{self.PERMS[command.extras["permission"]]}" permissions to use this command.')
		usage_str = f"{self.get_command_signature(command)}"
		if example:
			usage_str += f"\nE.G.: `{self.context.clean_prefix}{self.command_name} {example}`"
		embed.add_field(name="**Usage**", value=usage_str, inline=False)

		channel = self.get_destination()
		await channel.send(embed=embed)

	async def send_cog_help(self, cog):
		channel = self.get_destination()
		await botutils.error_template(channel, self.command_not_found(cog.qualified_name))


class Help(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self._original_help_command = bot.help_command
		bot.help_command = GoldHelp()
		bot.help_command.cog = self
		botutils.log("Help Command Ready.")

	def cog_unload(self):
		self.bot.help_command = self._original_help_command


async def setup(bot: commands.Bot):
	await bot.add_cog(Help(bot), override=True)
