import random

import discord
from discord.ext import commands

import botutilities


class GoldHelp(commands.MinimalHelpCommand):
	def __init__(self, **options):
		self.command_name = None
		self.needed_perms = None
		self.description = "Shows a list of all the commands of the bot or the details of said commands."
		self.perms_dict = {
			"read_messages": "View Channel", "view_channel": "View Channel",
			"send_messages": "Send Messages", "send_tts_messages": "Send Text-to-Speech Messages",
			"manage_messages": "Manage Messages", "embed_links": "Embed Links",
			"attach_files": "Attach Files", "read_message_history": "Read Message History",
			"mention_everyone": "Mention @everyone, @here and All Roles",
			"external_emojis": "Use External Emoji", "use_external_emojis": "Use External Emoji",
			"view_guild_insights": "View Server Insights", "conect": "Connect", "speak": "Speak",
			"mute_members": "Mute Members", "deafen_members": "Deafen Members",
			"move_members": "Move Members", "use_voice_activation": "Use Voice Activity",
			"change_nickname": "Change Nickname", "manage_nicknames": "Manage Nicknames",
			"manage_roles": "Manage Roles", "manage_permissions": "Manage Roles",
			"manage_webhooks": "Manage Webhooks", "manage_emojis": "Manage Emojis and Stickers",
			"manage_emojis_and_stickers": "Manage Emojis and Stickers",
			"use_slash_commands": "Use Application Commands", "request_to_speak": "Request to Speak",
			"manage_events": "Manage Events", "manage_threads": "Manage Threads",
			"create_public_threads": "Create Public Threads",
			"create_private_threads": "Create Private Threads",
			"external_stickers": "Use External Stickers",
			"use_external_stickers": "Use External Stickers",
			"send_messages_in_threads": "Send Messages in Threads",
			"use_embedded_activities": "Use Activities", "moderate_members": "Timeout Members",
			"create_instant_invite": "Create Invite", "kick_members": "Kick Members",
			"ban_members": "Ban Members", "administrator": "Administrator"
		}
		super().__init__(**options)

	def command_not_found(self, string: str) -> str:
		return f'Error: Command "{string}" not found.'

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
			example = command.signature

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
							value=f'You require "{self.perms_dict[command.extras["permission"]]}" permissions to use this command.')

		embed.add_field(name="**Usage**",
						value=f"{self.get_command_signature(command)}\nE.G.: `{self.context.clean_prefix}{self.command_name}{' ' if example else ''}{example}`",
						inline=False)

		channel = self.get_destination()
		await channel.send(embed=embed)

	async def send_cog_help(self, cog):
		channel = self.get_destination()
		await channel.send(self.command_not_found(cog.qualified_name))


class GoldHelpCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self._original_help_command = bot.help_command
		bot.help_command = GoldHelp()
		bot.help_command.cog = self

	def cog_load(self):
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
