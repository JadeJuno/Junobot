import os

import discord
from discord.ext import commands

import botutilities
import prefix
from config import parse_config

config = parse_config("./config.toml")


parser = prefix.PrefixParser(default="g!")

intents = discord.Intents.all()
allowed_mentions = discord.AllowedMentions(everyone=False)
bot = commands.Bot(command_prefix=parser, case_insensitive=True, intents=intents, allowed_mentions=allowed_mentions)
bot.remove_command("help")

if __name__ == "__main__":
	for filename in os.listdir('./cogs'):
		if filename.endswith('.py'):
			bot.load_extension(f'cogs.{filename[:-3]}')
	if botutilities.check_if_self_hosted():
		_self = input("Self Host? (y/n)\n> ")
		match _self.lower():
			case 'n':
				TOKEN = os.getenv("GOLD_TOKEN")
			case _:
				TOKEN = os.getenv("SELF_TOKEN")
	else:
		TOKEN = os.getenv("GOLD_TOKEN")
	if not TOKEN:
		TOKEN = input("Goldbot's Token: ")

	bot.run(TOKEN)
