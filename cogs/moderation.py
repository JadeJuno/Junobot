import asyncio
import datetime
import typing
from typing import Optional

import discord
from discord.ext import commands

from libs import botutils
from libs.botutils import to_timescale


class Moderation(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		botutils.log("Moderation Cog ready!")

	@commands.has_permissions(manage_nicknames=True)
	@commands.command(
		aliases=("rename",),
		description="Renames me to whatever name you want.",
		extras={
			'example':    "Jadebot",
			'permission': 'manage_nicknames'
		}
	)
	async def nickname(self, ctx: commands.Context, *, nickname: str):
		if len(nickname) > 32:
			await botutils.error_template(ctx,
										  f'"{nickname}" has more than 32 characters and therefore can\'t fit as my nickname.')
			return
		await ctx.me.edit(nick=nickname)
		await ctx.send(f'Successfully changed my nickname to "{nickname}".')

	@commands.has_permissions(moderate_members=True)
	@commands.command(
		aliases=("timeout",),
		description='Times out ("mutes") a mentioned user for a set amount of time.',
		extras={
			'example':    "@koganesirnight 10 minutes Bitching.",
			'permission': 'moderate_members'
		}
	)
	async def mute(self, ctx: commands.Context, member: discord.Member, duration: int, timescale: to_timescale, *,
				   reason: typing.Optional[str] = None):
		if member.is_timed_out():
			await botutils.error_template(ctx, f"{member} is already timed out.")
			return

		time_data = {timescale: duration}
		delta = datetime.timedelta(**time_data)
		try:
			await member.timeout(delta, reason=reason)
			await ctx.send(f'Muted {member} for `{duration}` {timescale} with reason "{reason}".')
		except discord.errors.HTTPException:
			await botutils.error_template(ctx, f"Invalid amount of time to time {member} out for.")

	@mute.error
	async def mute_error(self, ctx: commands.Context, error: Exception):
		if isinstance(error, commands.BadArgument):
			await botutils.error_template(ctx, f'"{ctx.current_argument}" is not a valid Time Scale')

	@commands.has_permissions(manage_messages=True)
	@commands.command(
		description="Deletes a certain amount of messages on the channel it's used on.",
		extras={
			'example':    10,
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
			'example':    '@koganesirnight Identity Theft',
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
			'example':    '@koganesirnight Identity Theft',
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
			message = ctx.message.reference.resolved
		else:
			messages = [message async for message in ctx.history(limit=2)]
			messages.remove(ctx.message)
			message = messages[0]

		try:
			await message.pin()
		except discord.HTTPException:
			await botutils.error_template(ctx, "Could not pin the specified message.")

	@ban.error
	@kick.error
	@mute.error
	async def member_converter_error(self, ctx: commands.Context, error: Exception):
		if isinstance(error, commands.errors.MemberNotFound):
			await botutils.error_template(ctx, f'"`{ctx.current_argument}`" is not a valid member.')


async def setup(client):
	await client.add_cog(Moderation(client), override=True)
