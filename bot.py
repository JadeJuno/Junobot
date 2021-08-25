import asyncio
import os
import random

import discord
from discord.ext import commands

import prefix
from config import parse_config

config = parse_config("./config.toml")

origin_commands = ("datapacks", "<#843834879736283156>", "")

whitelisted_links = ["https://mediafire.com/", "https://github.com/", "https://planetminecraft.com/", "https://docs.google.com/"]
temp_white = whitelisted_links[:]
for link in temp_white:
	whitelisted_links.append(link.replace("://", "://www."))
temp_white.clear()
whitelisted_links = tuple(whitelisted_links)


def is_bot_owner(ctx):
	return ctx.author.id in config["owners_id"]


parser = prefix.PrefixParser(default="g.")

intents = discord.Intents.all()
client = commands.Bot(command_prefix=parser, case_insensitive=True, intents=intents)
client.remove_command("help")

log = client.get_channel(config["log_channel"])
log2 = client.get_channel(838025060983767051)


@client.event
async def on_ready():
	global log
	log = client.get_channel(config["log_channel"])


def embed_template(ctx, title=None, description=None, footer="", image: str = "", icon: str = ""):
	embed = discord.Embed(description=description, color=random.randint(0, 0xffffff))
	if icon != "":
		embed.set_author(name=title, icon_url=icon)
	else:
		embed.set_author(name=title)
	embed.set_footer(
		text=f"{footer}\nTo see more information about a specific command, type {ctx.prefix}help <command>.\nGøldbot was created by Golder06#7041.",
		icon_url="https://i.imgur.com/ZgG8oJn.png")
	embed.set_thumbnail(url="https://i.imgur.com/8bOl5gU.png")
	if image != "":
		embed.set_image(url=image)
	return embed


@client.command(name="help")
async def _help(ctx, command=None):
	if command is None:
		title = "Commands"
		with open("help_texts/general_help.txt", "r", encoding='utf-8') as file:
			help_text = file.read()
		with open("help_texts/mod_help.txt", "r", encoding='utf-8') as file:
			mod_text = file.read()
		with open("help_texts/owner_help.txt", "r", encoding='utf-8') as file:
			owner_text = file.read()
		if ctx.author.guild_permissions.administrator:
			help_text += mod_text
		if is_bot_owner(ctx):
			help_text += owner_text
	else:
		command = command.lower()
		try:
			title = command.capitalize()
			with open(f"help_texts/specific_help/{command}.txt", encoding='utf-8') as file:
				help_text = file.read()
		except FileNotFoundError:
			title = "Error!"
			help_text = "Command not found."
	embed = embed_template(ctx, title, help_text.format(prefix=ctx.prefix), "\n<>=Necessary, []=optional.")
	await ctx.send(embed=embed)


@client.command()
async def prefix(ctx, new_prefix=None):
	perm = ctx.author.guild_permissions.administrator
	if new_prefix is None:
		await ctx.send(f"Server's prefix currently set to `{ctx.prefix}`.")
	else:
		if perm:
			sv = str(ctx.guild.id)
			parser.update(sv, new_prefix)
			await ctx.send(f"Prefix changed to `{new_prefix}`!")
		else:
			raise commands.CheckFailure

if __name__ == "__main__":
	for filename in os.listdir('./cogs'):
		if filename.endswith('.py'):
			client.load_extension(f'cogs.{filename[:-3]}')

	TOKEN = "NzkxMDY2MzQ5MjUzODIwNDc4.X-Jv8g.bEiIuTfej1rshqehrR_v1T5rvsk"
	TOKEN = "NTczNjgwMjQ0MjEzNjc4MDgx.XMuXXA.ywRBVp3AnGQjCiRwjYJsk3Oryk4"

	client.run(TOKEN)
