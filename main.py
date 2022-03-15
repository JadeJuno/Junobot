import asyncio
import os

import discord
from discord.ext import commands

import prefix
import botutilities
from config import parse_config

config = parse_config("./config.toml")

parser = prefix.PrefixParser(default="g!")

bot = commands.Bot(command_prefix=parser, case_insensitive=True, intents=discord.Intents.all(), allowed_mentions=discord.AllowedMentions(everyone=False))
bot.remove_command("help")


@bot.command()
async def prefix(ctx, new_prefix=None):
	if new_prefix is None:
		await ctx.send(f"Server's prefix currently set to `{ctx.prefix}`.")
	else:
		if ctx.author.guild_permissions.administrator:
			if new_prefix.lower() == "reset":
				parser.remove(str(ctx.guild.id))
				await ctx.send(f"Prefix reset back to `{parser.default}`!")
			else:
				parser.update(str(ctx.guild.id), new_prefix)
				await ctx.send(f"Prefix changed to `{new_prefix}`!")
		else:
			raise commands.MissingPermissions(missing_permissions=['administrator'])


async def main():
	async with bot:
		for filename in os.listdir('./cogs'):
			if filename.endswith('.py'):
				await bot.load_extension(f'cogs.{filename[:-3]}')

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

		await bot.start(TOKEN)

if __name__ == "__main__":
	asyncio.run(main())
