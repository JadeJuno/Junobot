import asyncio
import os
import random
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks

import botutilities
import prefix
from config import parse_config

config = parse_config("./config.toml")

parser = prefix.PrefixParser(default="g!")

bot = commands.Bot(command_prefix=parser, case_insensitive=True, intents=discord.Intents.all(),
				   allowed_mentions=discord.AllowedMentions(everyone=False), owner_id=498606108836102164)
bot.remove_command("help")

change_loop_interval = random.randint(1, 90)


@tasks.loop(minutes=change_loop_interval)
async def change_status_task():
	global change_loop_interval
	statuses = ('My default prefix is g!.', "If I break, contact Golder06#7041.", 'To see my commands, type g!help.')

	activity = random.choice(statuses)
	await bot.change_presence(status=discord.Status.online, activity=discord.Game(activity))
	time_now = datetime.now()
	print(f'Status changed to "{activity}" ({time_now.strftime("%H:%M")}).')
	change_loop_interval = random.randint(1, 90)
	print(f"Next status change in {change_loop_interval} minutes ({(time_now + timedelta(minutes=change_loop_interval)).strftime('%H:%M')}).")


@bot.event
async def on_ready():
	log = bot.get_channel(botutilities.config["log_channel"])
	appinfo = await bot.application_info()  # crashes here.
	print(f'"{bot.user.display_name}" is ready.')
	print(f"Created by {appinfo.owner}.")
	await log.send("Bot Started.")


async def main():
	async with bot:
		for filename in os.listdir('./cogs'):
			if filename.endswith('.py'):
				await bot.load_extension(f'cogs.{filename[:-3]}')
		# bot.loop.create_task(change_status_task())  # I've chosen to ignore this.
		await bot.start(TOKEN)


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


if __name__ == "__main__":
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
	asyncio.run(main())
