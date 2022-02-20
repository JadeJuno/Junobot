import random
import re

import discord
from discord.ext import commands

from config import parse_config


class BotUtilities:
	config = parse_config("./config.toml")

	def is_bot_owner(self, ctx):
		if ctx.author.id not in self.config["owners_id"]:
			raise IsNotBotOwner
		else:
			return True

	@staticmethod
	async def is_not_report_banned(ctx):
		return True

	# return ctx.author.id not in await get_report_banned()

	@staticmethod
	def check_if_self_hosted():
		try:
			with open(
					r"C:\Users\cient\OneDrive\Escritorio\Don't delete this text file.txt"):  # No, "cient" is not my real name, idk why my PC's username is "cient".
				return True
		except FileNotFoundError:
			return False

	@staticmethod
	def embed_template(ctx, title=None, description=None, footer="", add_def_footer=True, image: str = "",
					   icon: str = ""):
		embed = discord.Embed(description=description, color=random.randint(0, 0xffffff))
		if icon != "":
			embed.set_author(name=title, icon_url=icon)
		else:
			embed.set_author(name=title)
		if footer:
			if add_def_footer:
				embed.set_footer(
					text=f"{footer}\nTo see more information about a specific command, type {ctx.prefix}help <command>.\nGøldbot was created by Golder06#7041.",
					icon_url="https://i.imgur.com/ZgG8oJn.png")
			else:
				embed.set_footer(
					text=footer, icon_url="https://i.imgur.com/ZgG8oJn.png")
		embed.set_thumbnail(url="https://i.imgur.com/8bOl5gU.png")
		if image != "":
			embed.set_image(url=image)
		return embed

	@staticmethod
	async def tryreply(ctx, message, reply=False, img=None):
		async with ctx.typing():
			attach = None
			if isinstance(img, str):
				attach = discord.File(fp=f"assets/{img}")
			try:
				return await ctx.message.reference.resolved.reply(message, file=attach)
			except AttributeError:
				if reply:
					return await ctx.reply(message, file=attach)
				else:
					return await ctx.send(message, file=attach)

	"""
	@staticmethod
	async def get_report_banned():
		messages = []
		async for msg in main.ban_list.history():
			if msg.author == main.bot.user:
				try:
					messages.append(int(msg.content))
				except ValueError:
					continue
		return messages
	"""

	def ping_all_bot_owners(self):
		owners_pings = []
		for snfk_id in self.config["owners_id"]:  # "snfk" = "snowflake".
			owners_pings.append(f"<@{snfk_id}>")
		return ', '.join(owners_pings)

	@staticmethod
	def make_bug_report_file(ctx):
		arguments = []
		for arg in ctx.args[2:]:
			_type = str(type(arg))
			_type = re.search("'(.*?)'", _type).group(1)
			arguments.append(f'"{_type} - {arg}"')
		for kw_key, kw_val in ctx.kwargs.items():
			_type = str(type(kw_val))
			_type = re.search("'(.*?)'", _type).group(1)
			arguments.append(f'"{_type.capitalize()} - {kw_key}: {kw_val}"')
		if len(arguments) > 0:
			args_str = ', '.join(arguments)
		else:
			args_str = '"None"'

		content = f'Author: {ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id})\nChannel: {ctx.channel.name} ({ctx.channel.id})\nGuild: {ctx.guild.name} ({ctx.guild.id})\nArguments: {args_str}\n\nMessage: "{ctx.message.content}"\n'

		return content


class IsNotBotOwner(commands.CheckFailure):
	pass
