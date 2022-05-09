import json
import random

import discord
from discord.ext import commands

import botutilities


class GoldHelp(commands.MinimalHelpCommand):

	description = "Shows a list of all the commands of the bot or the details of said commands."
	with open('assets/perms.json') as f:
		PERMS = json.load(f)

	def __init__(self, **options):
		self.command_name = None
		super().__init__(**options)

	def command_not_found(self, string: str):
		return f'Command "{string}" not found.'

	async def prepare_help_command(self, ctx, command):
		self.command_name = command

	def get_command_signature(self, command):
		try:
			signature = f" {command.extras['signature']}"
		except KeyError:
			signature = f" {command.signature}" if len(command.signature) else ""
			signature = signature.replace("_", " ").title()
		return f"`{self.context.clean_prefix}{command.qualified_name}{signature}`"

	async def send_bot_help(self, mapping):
		embed = discord.Embed(title="Help", color=random.randint(0, 0xffffff))
		for cog, _commands in mapping.items():
			filtered = await self.filter_commands(_commands, sort=True)
			command_signatures = [self.get_command_signature(c) for c in filtered]
			if command_signatures:
				cog_name = getattr(cog, "qualified_name", "No Category")
				if cog_name != "DevCog" and cog_name != "GoldHelpCog":
					embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)
		embed.set_footer(
			text=f"<>=Necessary, []=optional.\nTo see more information about a specific command, type {self.context.clean_prefix}help <command>.\nGøldbot was created by Golder06#7041.",
			icon_url="https://i.imgur.com/ZgG8oJn.png"
		)
		channel = self.get_destination()
		await channel.send(embed=embed)

	async def send_command_help(self, command: commands):
		try:
			example = command.extras['example']
		except KeyError:
			example = None

		embed = discord.Embed(title=f"{self.context.clean_prefix}{self.command_name}", color=random.randint(0, 0xffffff))
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
		await botutilities.error_template(channel, self.command_not_found(cog.qualified_name))


class GoldHelpCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self._original_help_command = bot.help_command
		bot.help_command = GoldHelp()
		bot.help_command.cog = self
		print("Help Command Ready.")

	def cog_unload(self):
		self.bot.help_command = self._original_help_command


async def setup(client):
	await client.add_cog(GoldHelpCog(client), override=True)


async def _help(ctx, command=None):
	# UNUSED
	await ctx.send("The Help command is being rewritten due to dumb security issues. Please wait.")

	footer = ""
	mod_commands = ("ban", "clear", "kick", "pin", "unban")
	if command is None:
		title = "Commands"
		with open("help_texts/general_help.txt", encoding='utf-8') as file:
			help_text = file.read()
		if ctx.author.guild_permissions.administrator:
			with open("help_texts/mod_help.txt", encoding='utf-8') as file:
				help_text += file.read()
		footer = "\n<>=Necessary, []=optional."
	else:
		command = command.lower()
		if command in mod_commands:
			if ctx.author.guild_permissions.administrator:
				title = command.capitalize()
				with open(f"help_texts/specific_help/{command}.txt", encoding='utf-8') as file:
					help_text = file.read()
				footer = "\n<>=Necessary, []=optional."
			else:
				title = "Error!"
				help_text = f"You don't have permissions to use `{command}`"
		else:
			try:
				title = command.capitalize()
				with open(f"help_texts/specific_help/{command}.txt", encoding='utf-8') as file:
					help_text = file.read()
				footer = "\n<>=Necessary, []=optional."
			except FileNotFoundError:
				title = "Error!"
				help_text = "Command not found."
	embed = botutilities.embed_template(title, help_text.format(prefix=ctx.clean_prefix), footer)
	await ctx.send(embed=embed)
