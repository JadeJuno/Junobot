import os

import discord
from discord.ext import commands

import botutilities
from config import parse_config

config = parse_config("./config.toml")


parser = botutilities.parser

intents = discord.Intents.all()
allowed_mentions = discord.AllowedMentions(everyone=False)
client = commands.Bot(command_prefix=parser, case_insensitive=True, intents=intents, allowed_mentions=allowed_mentions)
client.remove_command("help")

log = client.get_channel(config["log_channel"])


@client.event
async def on_ready():
	global log
	log = client.get_channel(config["log_channel"])


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
	embed = botutilities.embed_template(ctx, title, help_text.format(prefix=ctx.prefix), footer, add_def_footer=True)
	await ctx.send(embed=embed)


@client.command()
async def prefix(ctx, new_prefix=None):
	if not botutilities.check_if_self_hosted():
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
