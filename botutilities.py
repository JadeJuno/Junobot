import random

import discord

import bot
from config import parse_config

parser = bot.parser

config = parse_config("./config.toml")


def is_bot_owner(ctx):
	return ctx.author.id in config["owners_id"]


async def is_not_report_banned(ctx):
	return ctx.author.id not in await get_report_banned()


def check_if_self_hosted():
	try:
		with open(r"C:\Users\cient\OneDrive\Escritorio\Don't delete this text file.txt", "r"):  # No, "cient" is not my real name, idk why my PC's username is "cient".
			pass
		return True
	except FileNotFoundError:
		return False


def embed_template(ctx, title=None, description=None, footer="", add_def_footer=True, image: str = "", icon: str = ""):
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


async def get_report_banned():
	ban_list = bot.client.get_channel(920775229008142356)
	messages = []
	async for msg in ban_list.history():
		if msg.author == bot.client.user:
			try:
				messages.append(int(msg.content))
			except ValueError:
				continue
	return messages


def ping_all_bot_owners():
	owners_pings = []
	for snfk_id in config["owners_id"]:  # "snfk" = "snowflake".
		owners_pings.append(f"<@{snfk_id}>")
	return ', '.join(owners_pings)
