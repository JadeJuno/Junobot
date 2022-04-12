import sys
import random
import re

import discord

from config import parse_config

config = parse_config("./config.toml")


class BotUtilities:
	def __init__(self, bot):
		self.bot = bot

	async def reaction_decision(self, ctx, check_str):
		check_message = await ctx.send(check_str)
		await check_message.add_reaction("\U00002705")
		await check_message.add_reaction("\U0000274c")

		def check(reaction_checked, reaction_user):
			user_check = reaction_user.id == ctx.author.id or reaction_user.guild_permissions.administrator and ctx.author.bot
			return user_check and reaction_checked.message == check_message and str(reaction_checked.emoji) in (
				"\U00002705", "\U0000274c")

		reaction, user = await self.bot.wait_for('reaction_add', check=check)
		if str(reaction.emoji) == "\U00002705":
			return True
		elif str(reaction.emoji) == "\U0000274c":
			return False


async def is_not_report_banned(ctx):
	return bool(ctx)  # Just to avoid PyCharm's warning temporarily :p


def check_if_self_hosted():
	return sys.platform == "win32"


def embed_template(title=None, description=None, footer="", image: str = "", icon: str = "",
				   color=None):
	if not color:
		color = random.randint(0, 0xffffff)
	if description:
		embed = discord.Embed(description=description, color=color)
	else:
		embed = discord.Embed(color=color)
	if title:
		if icon:
			embed.set_author(name=title, icon_url=icon)
		else:
			embed.set_author(name=title)
	if footer:
		embed.set_footer(text=footer, icon_url="https://i.imgur.com/ZgG8oJn.png")
	embed.set_thumbnail(url="https://i.imgur.com/8bOl5gU.png")
	if image:
		embed.set_image(url=image)
	return embed


async def error_template(ctx, message, send=True):
	embed = embed_template("ERROR", description=message, color=0xFF0000)
	if send:
		await ctx.reply(embed=embed)
	else:
		return embed


async def tryreply(ctx, message, reply=False, img=None, mention=True):
	async with ctx.typing():
		attach = None
		if isinstance(img, str):
			attach = discord.File(fp=f"assets/{img}")
		try:
			return await ctx.message.reference.resolved.reply(message, file=attach, mention_author=mention)
		except AttributeError:
			if reply:
				return await ctx.reply(message, file=attach, mention_author=mention)
			else:
				return await ctx.send(message, file=attach)


"""
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
