import os
import random

import discord
from discord.ext import commands

import prefix
from config import parse_config

config = parse_config("./config.toml")
parser = prefix.PrefixParser(default="g!")


def is_bot_owner(ctx):
	return ctx.author.id in config["owners_id"]


def is_not_report_banned(ctx):
	return ctx.author.id in config["report_banlist"]


def check_if_self_hosted():
	try:
		with open(r"C:\Users\cient\OneDrive\Escritorio\Don't delete this text file.txt", "r") as f:  # No, "cient" is not my real name, idk why my PC's username is "cient".
			str(f.read())
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
