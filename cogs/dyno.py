from discord.ext import commands

import bot
from config import parse_config

config = parse_config("./config.toml")


def is_in_command(ctx):
	return ctx.channel.id == 843834879736283156 or ctx.author.id in config["origins_mods"]


class Dyno(commands.Cog):
	def __init__(self, client):
		self.client = client

	async def cog_check(self, ctx):
		return ctx.channel.guild.id == 734127708488859831 or ctx.author.id in config["owners_id"]

	@commands.command(aliases=("vanillaorigins",))
	async def baseorigins(self, ctx):
		await bot.tryreply(ctx, "https://discord.com/channels/734127708488859831/749571272635187342/894472367315759154")

	@commands.command()
	async def template(self, ctx):
		if is_in_command(ctx):
			await bot.tryreply(ctx, "**Datapack Template**\nThere's a nice template for data-packs which you can use, made by CandyCaneCazoo. This way, you'll know you have the folder structure correct from the start!\nhttps://discord.com/channels/734127708488859831/749571272635187342/867715782825476137", reply=True)
		else:
			serious = self.client.get_emoji(821796259333537813)
			await ctx.reply(f"Please use your commands in <#843834879736283156>, so the other channels don't get messy! {serious}")

	@commands.command()
	async def namespace(self, ctx):
		await bot.tryreply(ctx, "The namespace and the ID should only contain the following symbols:\n\n• `0123456789` Numbers\n• `abcdefghijklmnopqrstuvwxyz` Lowercase letters\n• `_` Underscore\n• `-` Hypen/minus\n• `.` Dot\n\n\nFor example:\n\n`data/Example namespace` is invalid because it has an uppercased letter and a space, whilst `data/example-namespace` is valid.\n\n\nFor more information, visit the official wiki page about namespaces: <https://minecraft.fandom.com/wiki/Namespaced_ID>")

	@commands.command(aliases=('redirect-datapack-dev',))
	async def rdd(self, ctx):
		await bot.tryreply(ctx, "If you need help with a datapack-related issue, feel free to ask in <#810587422303584286> **by creating a thread**!\n\ne.g:", img='https://images-ext-2.discordapp.net/external/0q_wYRTA3vsAgb23pAWLJhX4qXS2KI_OjyNPtakr3bU/https/media.discordapp.net/attachments/901472574159077466/901472620820725810/creating-a-thread.gif')

	@commands.command(aliases=('datapack-debugging-chart',))
	async def rdd(self, ctx):
		try:
			if ctx.channel.parent_id == 810587422303584286:
				return await ctx.reply("This message is already in <#810587422303584286>...")
			await bot.tryreply(ctx, 'https://media.discordapp.net/attachments/810587422303584286/867459174422020146/637612768361327151Datapack_Debugging_Chart_UPDATED.png')
		except AttributeError:
			await bot.tryreply(ctx, 'https://media.discordapp.net/attachments/810587422303584286/867459174422020146/637612768361327151Datapack_Debugging_Chart_UPDATED.png')


def setup(client):
	client.add_cog(Dyno(client), override=True)
