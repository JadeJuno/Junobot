import discord
from discord.ext import commands

import botutilities


class Utility(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		print("Utility Cog ready!")

	@commands.command(description="Sends a link to invite me to another server.")
	async def invite(self, ctx):
		invite_url = discord.utils.oauth_url(str(self.bot.user.id))
		emb = discord.Embed(title="Invite Link",
							description=f"Here's the invite link for {self.bot.user.name}: [Invite]({invite_url})")
		await ctx.send(embed=emb)

	@commands.check(botutilities.is_not_report_banned)
	@commands.command(
		aliases=('bugreport', 'reportbug', 'bug-report', 'report-bug'),
		description="Let's you make a direct bug report to my creator if needed. Allows for sending images and other attachments as well.",
		extras={
			'example': "The `g!translate` command is broken."
		}
	)
	async def report(self, ctx, *, message):
		report_channel = self.bot.get_channel(920770517424816179)
		if len(ctx.message.attachments) > 0:
			attachments = [await attachment.to_file(spoiler=attachment.is_spoiler()) for attachment in
						   ctx.message.attachments]
		else:
			attachments = None
		embed = botutilities.embed_template(title=f"{ctx.author.name}#{ctx.author.discriminator}",
											description=f">>> {message}", footer=f"User ID: {ctx.author.id}",
											icon=ctx.author.display_avatar.url)
		owner_ping = self.bot.get_user(self.bot.owner_id).mention
		await report_channel.send(f'{owner_ping}\nReported from "{ctx.guild.name}" ({ctx.guild.id}):', embed=embed, files=attachments)
		await ctx.send(f"Bug Report sent successfully")

	@commands.command(description='Sends "Pong!" and the latency of the bot.')
	async def ping(self, ctx):
		await ctx.send(f':ping_pong: Pong! {self.bot.latency * 1000:.0f}ms.')


async def setup(bot):
	await bot.add_cog(Utility(bot), override=True)
