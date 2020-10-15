import difflib
import discord
import googlesearch
import json
import os
import prefix
import random
import time
import wikipedia
from datetime import datetime
from discord.ext import commands, tasks
from googletrans import Translator
from morsecode import MorseCode


def is_bot_owner(ctx):
	return ctx.author.id == 498606108836102164 or ctx.author.id == 503657339258273812


parser = prefix.PrefixParser(default="g!")

client = commands.Bot(command_prefix=parser, case_insensitive=True)
client.remove_command("help")

command_list = ["8ball", "choose", "flip", "coinflip", "flipcoin", "roll", "rolldie", "dieroll", "say", "help", "google", "googleit", "googlesearch", "language", "detect", "morsecode", "morse", "ping", "pin", "translate", "wikipedia", "ban", "clear", "kick", "prefix", "unban", "alias"]

owner = None

@client.event
async def on_ready():
	global owner
	owner = client.get_user(498606108836102164)
	print("a", owner)


@client.command("help")
async def _help(ctx, command=None):
	footer = ""
	if command is None:
		with open("Help/General Help.txt", "r") as file:
			help_text = file.read()
		with open("Help/Mod Help.txt", "r") as file:
			mod_text = file.read()
		with open("Help/Owner Help.txt", "r") as file:
			owner_text = file.read()
		title = "Commands"
		if ctx.author.guild_permissions.administrator == True:
			help_text += mod_text
		else:
			help_text += f"`{ctx.prefix}prefix`"
		if is_bot_owner(ctx) == True:
			help_text += owner_text
	else:
		footer += "\n<>=Necessary, []=optional."
		i = None
		for com in command_list:
			if com == command:
				i = True
				break
		if i == True:
			title = command.capitalize()
			with open(f"Help/Specific Helps/{command}.txt") as file:
				help_text = file.read()
		else:
			title = "Error!"
			help_text = "Command not found."
	embed = discord.Embed(description=help_text.format(prefix=ctx.prefix), color=random.randint(0, 0xffffff))
	embed.set_author(name=title)
	embed.set_footer(text=f"{footer}\nTo see more information about a specific command, type {ctx.prefix}help <command>.\nGøldbot was created by {owner.name}.", icon_url="https://i.imgur.com/ZgG8oJn.png")
	await ctx.send(embed=embed)


@client.command()
@commands.check(is_bot_owner)
async def load(ctx, extension):
	print(f"Loading {extension.capitalize()}...")
	client.load_extension(f'cogs.{extension}')
	print(f"{extension.capitalize()} loaded!")
	await ctx.send(f'Cog "{extension.capitalize()}" loaded!')


@client.command()
@commands.check(is_bot_owner)
async def unload(ctx, extension="commands"):
	print(f"Unloading {extension.capitalize()}...")
	client.unload_extension(f'cogs.{extension}')
	print(f"{extension.capitalize()} unloaded!")
	await ctx.send(f'{extension.capitalize()} unloaded!')


@client.command()
@commands.check(is_bot_owner)
async def reload(ctx, extension="commands"):
	print(f"Reloading {extension}...")
	client.unload_extension(f'cogs.{extension}')
	client.load_extension(f'cogs.{extension}')
	print(f"{extension.capitalize()} reloaded!")
	await ctx.send(f'{extension.capitalize()} reloaded!')


@load.error
@unload.error
@reload.error
async def load_errors(ctx, error):
	if isinstance(error, commands.ExtensionNotLoaded):
		await ctx.send(f'Error: Specified extension not found.')


@client.command()
async def prefix(ctx, new_prefix=None):
	perm = ctx.author.guild_permissions.administrator
	if new_prefix is None:
		await ctx.send(f"Server's prefix currently set to {ctx.prefix}.")
	else:
		if perm == True:
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
