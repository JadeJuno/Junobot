import discord
from discord.ext import commands

import os
import random

from config import parse_config
import prefix


config = parse_config(".\config.py")


def is_bot_owner(ctx):
	return ctx.author.id in config["owners_id"]


parser = prefix.PrefixParser(default="g!")


client = commands.Bot(command_prefix=parser, case_insensitive=True)

client.remove_command("help")
owner = None

@client.event
async def on_ready():
	global owner
	owner = await client.fetch_user(config["owners_id"][0])

def embed_template(ctx, title=None, description=None, footer=None, image: str = None, icon: str = None):
	embed = discord.Embed(description=description, color=random.randint(0, 0xffffff))
	embed.set_author(name=title, icon_url=icon)
	embed.set_footer(
		text=f"{footer}\nTo see more information about a specific command, type {ctx.prefix}help <command>.\nGøldbot was created by {owner.name}.",
		icon_url="https://i.imgur.com/ZgG8oJn.png")
	embed.set_thumbnail(url="https://i.imgur.com/8bOl5gU.png")
	if image is not None:
		embed.set_image(url=image)
	return embed


@client.command("help")
async def _help(ctx, command=None):
	if command is None:
		footer = ""
		with open("Help/general_help.txt", "r") as file:
			help_text = file.read()
		with open("Help/mod_help.txt", "r") as file:
			mod_text = file.read()
		with open("Help/owner_help.txt", "r") as file:
			owner_text = file.read()
		title = "Commands"
		if ctx.author.guild_permissions.administrator:
			help_text += mod_text
		if is_bot_owner(ctx):
			help_text += owner_text
	else:
		footer = "\n<>=Necessary, []=optional."
		try:
			title = command.capitalize()
			with open(f"Help/Specific Helps/{command}.txt") as file:
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
		await ctx.send(f"Server's prefix currently set to {ctx.prefix}.")
	else:
		if perm:
			sv = str(ctx.guild.id)
			parser.update(sv, new_prefix)
			await ctx.send(f"Prefix changed to {new_prefix}!")
		else:
			raise commands.CheckFailure


for filename in os.listdir('./cogs'):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')

TOKEN = "NTczNjgwMjQ0MjEzNjc4MDgx.XMuXXA.ywRBVp3AnGQjCiRwjYJsk3Oryk4"
client.run(TOKEN)
