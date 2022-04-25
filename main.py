import asyncio
import os

import discord
from discord.ext import commands

import botutilities
import prefix
from config import parse_config

config = parse_config("./config.toml")

parser = prefix.PrefixParser(default=config['default_prefix'])

bot = commands.Bot(command_prefix=parser, case_insensitive=True, intents=discord.Intents.all(),
				   allowed_mentions=discord.AllowedMentions(everyone=False), owner_id=config['owner_id'])


@bot.event
async def on_ready():
	log = bot.get_channel(botutilities.config["log_channel"])
	appinfo = await bot.application_info()
	print(f'"{bot.user.display_name}" is ready.')
	print(f"Created by {appinfo.owner}.")
	await log.send("Bot Started.")


async def main():
	async with bot:
		for filename in os.listdir('./cogs'):
			if filename.endswith('.py'):
				try:
					await bot.load_extension(f'cogs.{filename[:-3]}')
				except commands.errors.NoEntryPointError:
					print(f"{filename[:-3]} Failed to load...")
		# bot.loop.create_task(change_status_task())  # I've chosen to ignore this.
		await bot.start(TOKEN)


@bot.command(extras={'example': '{prefix}{name} gg'}, description="TEST")
async def prefix(ctx, new_prefix=None):
	if new_prefix:
		if ctx.author.guild_permissions.administrator:
			if new_prefix.lower() == "reset":
				parser.remove(str(ctx.guild.id))
				await ctx.send(f"Prefix reset back to `{parser.default}`.")
			else:
				parser.update(str(ctx.guild.id), new_prefix)
				await ctx.send(f"Prefix changed to `{new_prefix}`.")
		else:
			raise commands.MissingPermissions(missing_permissions=['administrator'])
	else:
		await ctx.send(f"Server's prefix currently set to `{ctx.prefix}`.")


if __name__ == "__main__":
	if botutilities.check_if_self_hosted():
		selfhost = input("Self Host? (y/n)\n> ")
		match selfhost.lower():
			case 'n':
				TOKEN = os.getenv("GOLD_TOKEN")
			case _:
				TOKEN = os.getenv("SELF_TOKEN")
	else:
		TOKEN = os.getenv("GOLD_TOKEN")
	if not TOKEN:
		TOKEN = input("Gøldbot's Token: ")
	asyncio.run(main())
