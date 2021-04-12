import os
import random

import discord
from discord.ext import commands

import prefix
from config import parse_config

config = parse_config("./config.toml")


def is_bot_owner(ctx):
	return ctx.author.id in config["owners_id"]


def check_if_self_hosted():
	try:
		with open(r"C:\Users\cient\OneDrive\Escritorio\Don't delete this text file.txt", "r") as f:
			str(f.read())
		return True
	except FileNotFoundError:
		return False


if check_if_self_hosted():
	parser = prefix.PrefixParser(default="g.")
else:
	parser = prefix.PrefixParser(default="g!")

client = commands.Bot(command_prefix=parser, case_insensitive=True)

client.remove_command("help")
owner = None


@client.event
async def on_ready():
	global owner
	owner = await client.fetch_user(config["owners_id"][0])


def embed_template(ctx, title=None, description=None, footer="", image: str = "", icon: str = ""):
	embed = discord.Embed(description=description, color=random.randint(0, 0xffffff))
	if icon != "":
		embed.set_author(name=title, icon_url=icon)
	else:
		embed.set_author(name=title)
	embed.set_footer(
		text=f"{footer}\nTo see more information about a specific command, type {ctx.prefix}help <command>.\nGøldbot was created by {owner.name}.",
		icon_url="https://i.imgur.com/ZgG8oJn.png")
	embed.set_thumbnail(url="https://i.imgur.com/8bOl5gU.png")
	if image != "":
		embed.set_image(url=image)
	return embed


@client.command(name="help")
async def _help(ctx, command=None):
	if command is None:
		footer = ""
		with open("help_texts/general_help.txt", "r", encoding='utf-8') as file:
			help_text = file.read()
		with open("help_texts/mod_help.txt", "r", encoding='utf-8') as file:
			mod_text = file.read()
		with open("help_texts/owner_help.txt", "r", encoding='utf-8') as file:
			owner_text = file.read()
		title = "Commands"
		if ctx.author.guild_permissions.administrator:
			help_text += mod_text
		if is_bot_owner(ctx):
			help_text += owner_text
	else:
		command = command.lower()
		footer = "\n<>=Necessary, []=optional."
		try:
			title = command.capitalize()
			with open(f"help_texts/specific_help/{command}.txt", encoding='utf-8') as file:
				help_text = file.read()
		except FileNotFoundError:
			title = "Error!"
			help_text = "Command not found."
	embed = embed_template(ctx, title, help_text.format(prefix=ctx.prefix), footer)
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


for filename in os.listdir('./cogs'):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')

if check_if_self_hosted():
	TOKEN = "NzkxMDY2MzQ5MjUzODIwNDc4.X-Jv8g.bEiIuTfej1rshqehrR_v1T5rvsk"
else:
	TOKEN = "NTczNjgwMjQ0MjEzNjc4MDgx.XMuXXA.ywRBVp3AnGQjCiRwjYJsk3Oryk4"

client.run(TOKEN)
