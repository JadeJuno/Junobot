import asyncio
import datetime

import discord
from discord.ext import commands

from libs import botutils


class Moderation(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		botutils.log("Moderation Cog ready!")

	@commands.has_permissions(ban_members=True)
	@commands.command(
		description='Unbans a specified user.',
		extras={
			'example': "KoganeSirnight#9389",
			'permission': 'ban_members'
		}
	)
	async def unban(self, ctx, *, member):
		banned_users = await ctx.guild.bans()
		member_name, member_discriminator = member.split('#')
		for ban_entry in banned_users:
			user = ban_entry.user
			if (user.name, user.discriminator) == (member_name, member_discriminator):
				await ctx.guild.unban(user)
				await ctx.send(f'Unbanned {user.mention}.')
				return
			await botutils.error_template(ctx, f'{user.mention} is not banned.')

	@commands.has_permissions(manage_nicknames=True)
	@commands.command(
		aliases=("rename",),
		description="Renames me to whatever name you want.",
		extras={
			'example': "Silverbot",
			'permission': 'manage_nicknames'
		}
	)
	async def nickname(self, ctx: commands.Context, *, nickname: str):
		if len(nickname) > 32:
			await botutils.error_template(ctx,
			                              f'"{nickname}" has more than 32 characters and therefore can\'t fit as my nickname.')
			return
		await ctx.guild.me.edit(nick=nickname)
		await ctx.send(f'Successfully changed my nickname to "{nickname}".')

	@commands.has_permissions(moderate_members=True)
	@commands.command(
		aliases=("timeout",),
		description='Times out ("mutes") a mentioned user for a set amount of time.',
		extras={
			'example': "@KoganeSirnight#9389 10 minutes Bitching.",
			'permission': 'moderate_members'
		}
	)
	async def mute(self, ctx, member: discord.Member, duration, timescale, *, reason=None):
		timescale = timescale.lower()
		timescales = {
			's': 'seconds', 'second': 'seconds',
			'm': 'minutes', 'minute': 'minutes',
			'h': 'hours', 'hour': 'hours',
			'd': 'days', 'day': 'days',
			'w': 'weeks', 'week': 'weeks'
		}

		if timescale not in timescales and timescale not in timescales.values():
			await botutils.error_template(ctx, f'"{timescale}" is not a valid Time Scale')
			return
		if member.is_timed_out():
			await botutils.error_template(ctx, f"{member} is already timed out.")
			return

		try:
			timescale = timescales[timescale]
		except KeyError:
			pass

		time_data = {timescale: int(duration)}
		delta = datetime.timedelta(**time_data)
		try:
			await member.timeout(delta, reason=reason)
			await ctx.send(f'Muted {member} for {duration} {timescale} with reason "{reason}".')
		except discord.errors.HTTPException:
			await botutils.error_template(ctx, f"Invalid amount of time to time {member} out for.")

	@commands.has_permissions(manage_messages=True)
	@commands.command(
		description="Deletes a certain amount of messages on the channel it's used on.",
		extras={
			'example': 10,
			'permission': 'manage_messages'
		}
	)
	async def clear(self, ctx: commands.Context, amount: int):
		await ctx.message.delete()
		deleted_messages = await ctx.channel.purge(limit=amount)
		clear_message = await ctx.send(f'Cleared {len(deleted_messages)} messages.')
		await asyncio.sleep(1)
		await clear_message.delete()

	@commands.has_permissions(ban_members=True)
	@commands.command(
		description="Bans a mentioned user.",
		extras={
			'example': '@KoganeSirnight#9389 Identity Theft',
			'permission': 'ban_members'
		}
	)
	async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = None):
		if not member.guild_permissions.administrator:
			await member.ban(reason=reason)
			await ctx.send(f'Banned {member} with reason "{reason}".')
		else:
			await botutils.error_template(ctx, f"{member} has a higher permission level than myself.")

	@commands.has_permissions(kick_members=True)
	@commands.command(
		description="Kicks a mentioned user.",
		extras={
			'example': '@KoganeSirnight#9389 Identity Theft',
			'permission': 'kick_members'
		}
	)
	async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = None):
		if not member.guild_permissions.administrator:
			await member.kick(reason=reason)
			await ctx.send(f'Kicked {member} with reason "{reason}".')
		else:
			await botutils.error_template(ctx, f"{member} has a higher permission level than myself.")

	@commands.has_permissions(manage_messages=True)
	@commands.command(
		description="Pins the message you reply to. If you're not replying to a message, it'll pin the message right above yours.",
		extras={
			'permission': 'manage_messages'
		}
	)
	async def pin(self, ctx: commands.Context):
		if ctx.message.reference:
			await ctx.message.reference.resolved.pin()
		else:
			messages = await ctx.history(limit=2).flatten()
			messages.remove(ctx.message)
			await messages[0].pin()

	@ban.error
	@kick.error
	@mute.error
	async def member_converter_error(self, ctx: commands.Context, error: Exception):
		if isinstance(error, commands.errors.MemberNotFound):
			await botutils.error_template(ctx, f'"`{ctx.current_argument}`" is not a valid member.')


async def setup(client):
	await client.add_cog(Moderation(client), override=True)
