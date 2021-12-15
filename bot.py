import os

import discord
from discord.ext import commands

import prefix
from config import parse_config

config = parse_config("./config.toml")

parser = prefix.PrefixParser(default="g!")

intents = discord.Intents.all()
allowed_mentions = discord.AllowedMentions(everyone=False)
client = commands.Bot(command_prefix=parser, case_insensitive=True, intents=intents, allowed_mentions=allowed_mentions)
client.remove_command("help")

log = client.get_channel(config["log_channel"])


if __name__ == "__main__":
	@client.event
	async def on_ready():
		global log
		log = client.get_channel(config["log_channel"])


	for filename in os.listdir('./cogs'):
		if filename.endswith('.py'):
			client.load_extension(f'cogs.{filename[:-3]}')
	TOKEN = os.getenv("GOLD_TOKEN")
	if not TOKEN:
		TOKEN = input("Goldbot's Token: ")

	client.run(TOKEN)
