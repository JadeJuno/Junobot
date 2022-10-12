import asyncio
import os

import discord
from discord.ext import commands

from libs import prefix, botutils
from libs.config import parse_config

config = parse_config("./config.toml")

parser = prefix.PrefixParser(default=config['default_prefix'])

bot = commands.Bot(command_prefix=parser, case_insensitive=True, intents=discord.Intents.all(),
				   allowed_mentions=discord.AllowedMentions(everyone=False), owner_id=config['owner_id'])


@bot.event
async def on_ready():
	log = bot.get_channel(botutils.config["log_channel"])
	appinfo = await bot.application_info()
	botutils.log(f'"{bot.user.display_name}" is ready.')
	botutils.log(f"Created by {appinfo.owner}.")
	await log.send("Bot Started.")


async def main():
	async with bot:
		cogs = [f'cogs.{cog.removesuffix(".py")}' for cog in os.listdir('./cogs') if cog.endswith('.py')]
		for cog in cogs:
			try:
				await bot.load_extension(cog)
			except commands.errors.NoEntryPointError:
				botutils.log(f"{cog.removeprefix('cogs.')} Failed to load or isn't a Cog.")
		await bot.start(TOKEN)


if __name__ == "__main__":
	if botutils.check_if_self_hosted():
		selfhost = input("Self Host? (y/n)\n> ")
		match selfhost.lower():
			case 'y':
				TOKEN = os.getenv("SELF_TOKEN")
			case _:
				TOKEN = os.getenv("GOLD_TOKEN")
	else:
		TOKEN = os.getenv("GOLD_TOKEN")
	if not TOKEN:
		TOKEN = input("Gøldbot's Token: ")
	asyncio.run(main())
