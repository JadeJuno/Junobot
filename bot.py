import os
import random

import discord
from discord.ext import commands

import prefix
from config import parse_config

config = parse_config("./config.toml")

"""
origin_commands = (
	"datapacks", "<#843834879736283156>", 'commands', "rule", "rules", "help", "whitelisted", "whitelist",
	"whitelistedlinks", 'transbee', 'wiki', 'channelonly', 'avd', "addonsvsdatapacks", 'addonvsdatapack', 'tias',
	'try-it-and-see', 'tryit', 'try-it', 'tryitandsee', 'transratkid', 'bibee', 'invite', 'escape')
"""

whitelisted_links = ["https://mediafire.com/", "https://github.com/", "https://planetminecraft.com/",
					 "https://docs.google.com/", "https://curseforge.com/", "https://modrinth.com"]
temp_white = whitelisted_links[:]
for _link in temp_white:
	whitelisted_links.append(_link.replace("://", "://www."))
temp_white.clear()
whitelisted_links = tuple(whitelisted_links)


def is_bot_owner(ctx):
	return ctx.author.id in config["owners_id"]


def check_if_self_hosted():
	try:
		with open(r"C:\Users\cient\OneDrive\Escritorio\Don't delete this text file.txt", "r") as f:
			str(f.read())
		return True
	except FileNotFoundError:
		return False


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


parser = prefix.PrefixParser(default="g!")

intents = discord.Intents.all()
allowed_mentions = discord.AllowedMentions(everyone=False)
client = commands.Bot(command_prefix=parser, case_insensitive=True, intents=intents, allowed_mentions=allowed_mentions)
client.remove_command("help")

log = client.get_channel(config["log_channel"])


@client.event
async def on_ready():
	global log
	log = client.get_channel(config["log_channel"])


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


@client.command(name="help")
async def _help(ctx, command=None):
	mod_commands = ("ban", "clear", "kick", "pin", "unban")
	if command is None:
		title = "Commands"
		with open("help_texts/general_help.txt", "r", encoding='utf-8') as file:
			help_text = file.read()
		if ctx.author.guild_permissions.administrator:
			with open("help_texts/mod_help.txt", "r", encoding='utf-8') as file:
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
				footer = ""
		else:
			try:
				title = command.capitalize()
				with open(f"help_texts/specific_help/{command}.txt", encoding='utf-8') as file:
					help_text = file.read()
				footer = "\n<>=Necessary, []=optional."
			except FileNotFoundError:
				title = "Error!"
				help_text = "Command not found."
				footer = ""
	embed = embed_template(ctx, title, help_text.format(prefix=ctx.prefix), footer, add_def_footer=True)
	await ctx.send(embed=embed)


@client.command()
async def prefix(ctx, new_prefix=None):
	if not check_if_self_hosted():
		if new_prefix is None:
			await ctx.send(f"Server's prefix currently set to `{ctx.prefix}`.")
		else:
			if ctx.author.guild_permissions.administrator:
				if new_prefix.lower() == "reset":
					parser.update(str(ctx.guild.id), parser.default)
					await ctx.send(f"Prefix reset back to `{parser.default}`!")
				else:
					parser.update(str(ctx.guild.id), new_prefix)
					await ctx.send(f"Prefix changed to `{new_prefix}`!")
			else:
				raise commands.MissingPermissions(missing_permissions=['administrator'])


if __name__ == "__main__":
	for filename in os.listdir('./cogs'):
		if filename.endswith('.py'):
			client.load_extension(f'cogs.{filename[:-3]}')
	TOKEN = os.getenv("GOLD_TOKEN")
	if not TOKEN:
		TOKEN = input("Goldbot's Token: ")

	client.run(TOKEN)
