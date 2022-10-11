import calendar
import io
import os
import random
import typing

import discord
from discord.ext import commands

from libs import botutils


class DevCog(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.log = None
		botutils.log("Dev Cog ready!")

	async def cog_check(self, ctx: commands.Context):
		check = await self.bot.is_owner(ctx.author)
		if check:
			return check
		else:
			raise commands.NotOwner

	@commands.command(name='cog')
	async def coghandle(self, ctx: commands.Context, disc: typing.Literal['load', 'unload', 'reload'], cog: typing.Optional[str]):
		if cog:
			cogs = [f'cogs.{cog}']
		else:
			cogs = [f'cogs.{cog.removesuffix(".py")}' for cog in os.listdir('./cogs') if cog.endswith('.py')]

		done_cogs = []
		match disc.lower():
			case 'load':
				msg = await ctx.send(f'Loading...')
				for cog in cogs:
					try:
						await self.bot.load_extension(cog)
						botutils.log(f'{cog} Loaded.')
						done_cogs.append(cog)
					except commands.errors.ExtensionAlreadyLoaded:
						pass
				if len(done_cogs) > 0:
					await msg.edit(content="Loading complete!")
				else:
					await msg.edit(content="Error: Cog(s) already loaded.")

			case 'unload':
				msg = await ctx.send(f'Unloading...')
				for cog in cogs:
					try:
						await self.bot.unload_extension(cog)
						botutils.log(f'{cog} Unloaded.')
						done_cogs.append(cog)
					except commands.errors.ExtensionNotLoaded:
						pass
				if len(done_cogs) > 0:
					await msg.edit(content="Loading complete!")
				else:
					await msg.edit(content="Error: Cog(s) already unloaded.")

			case 'reload':
				msg = await ctx.send(f'Reloading...')
				for cog in cogs:
					try:
						await self.bot.reload_extension(cog)
					except commands.errors.ExtensionNotLoaded:
						pass
					else:
						botutils.log(f'{cog} Reloaded.')
						done_cogs.append(cog)
				if len(done_cogs) > 0:
					await msg.edit(content="Reloading complete!")
				else:
					await msg.edit(content="Error: Cog(s) was/were all unloaded.")
			case _:
				await ctx.send("Error: Disc not valid.")

	@commands.command()
	async def test(self, ctx: commands.Context):
		print("TEST")
		embed = discord.Embed(title="Title", description="[Test Link](https://www.youtube.com)",
							  color=random.randint(0, 0xffffff), url="https://www.google.com/")
		embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
		embed.set_footer(text=f"*Requested by {ctx.author.name}.*", icon_url=ctx.author.display_avatar.url)
		embed.set_image(url="https://discordpy.readthedocs.io/en/latest/_images/snake.png")
		embed.set_thumbnail(url="https://i.imgur.com/8bOl5gU.png")
		embed.add_field(name="Field 1", value="value 1")
		embed.add_field(name="Field 2", value="value 2")
		embed.add_field(name="Field 3", value="value 3")
		await ctx.send(embed=embed)
		await ctx.send(f"<t:{int(calendar.timegm(ctx.message.created_at.utctimetuple()))}>")
		await botutils.tryreply(ctx, "Test")

	@commands.command(aliases=('autoerror',))
	async def auto_error(self, ctx: commands.Context):
		await ctx.send(f"{int('A')}")

	@commands.command()
	async def banreport(self, ctx, user):
		ban_list = self.bot.get_channel(920775229008142356)
		await ban_list.send(user.id)
		await self.log.send(f"{ctx.user.displayname} banned {user.name}#{user.discriminator} from reporting bugs.")

	@commands.command()
	async def format(self, ctx: commands.Context):
		if ctx.message.reference:
			if len(ctx.message.reference.resolved.embeds) == 0:
				output = ctx.message.reference.resolved.content
			else:
				output = ctx.message.reference.resolved.embeds[0].DESCRIPTION
			with io.StringIO(output) as file:
				# noinspection PyTypeChecker
				await ctx.send("Here's the formatted message:", file=discord.File(fp=file, filename=f'{ctx.message.id}.txt'))

	@commands.command()
	async def help_test(self, ctx: commands.Context):
		await ctx.send("Help Tested.")

	@commands.command()
	async def sync(self, ctx, guild: typing.Optional[int]):
		if guild:
			o = discord.Object(id=guild)
			self.bot.tree.copy_global_to(guild=o)
			await self.bot.tree.sync(guild=o)
			await ctx.send(f"Synced App Commands from {guild}")
		else:
			await self.bot.tree.sync()
			await ctx.send("Synced App Commands")


async def setup(bot):
	await bot.add_cog(DevCog(bot), override=True)
