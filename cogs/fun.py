import random
import re

import discord
from discord.ext import commands

import botutilities


class Fun(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.log = None
		self.my_guild = None

	async def cog_load(self):
		print("Fun Cog ready!")

	@commands.Cog.listener()
	async def on_ready(self):
		self.my_guild = self.bot.get_guild(botutilities.config["guild_id"])

	@commands.command(
		name='8ball',
		description="You can ask a yes or no question to the omniscient  Magic :8ball: Ball, and it will answer it.",
		extras={'example': 'Am I loved?'}
	)
	async def _8ball(self, ctx, *, question):
		ball_predicts = ("It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.",
						 "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.",
						 "Signs point to yes.", "Reply hazy, try again.", "Ask again later.",
						 "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
						 "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.",
						 "Very doubtful.")
		if question.endswith("?"):
			if question.strip() == "?":
				prediction = "That's not a question, that's a question sign..."
			elif "love" in question.lower():  # lol
				prediction = random.choice(ball_predicts[-5:])
			else:
				prediction = random.choice(ball_predicts)
		else:
			prediction = "That's not a question..."
		await ctx.send(f'Question: {question}\nThe ***:8ball:BALL*** says: {prediction}')

	@commands.command(
		aliases=('colour',),
		description="Sends an image with a solic color specified in Hexadecimal Code.",
		extras={"example": "#32A852"}
	)
	async def color(self, ctx, hex_color):
		hex_color = hex_color.replace('#', '')

		if re.search(re.compile("([0123456789abcdef])+", re.I), hex_color) or len(hex_color) != 6:
			await ctx.send(f"Error: `#{hex_color}` is not a valid Hex Color code.")
			return
		img = f"https://dummyimage.com/300/{hex_color}/&text=+"
		embed = botutilities.embed_template(footer=f'#{hex_color}', color=int(hex_color, 16), image=img)
		await ctx.send(embed=embed)

	@commands.command(
		description="Give the bot some options *(More than 1)* and it will randomly choose between them.",
		extras={
			"signature": "<option 1, option 2, option 3, (...)>",
			"example": "Yes, No, Perhaps"
		}
	)
	async def choose(self, ctx, *, options):
		divided_options: list = options.split(",")
		if len(divided_options) >= 2:
			for option in divided_options:
				if not option:
					divided_options.remove(option)
			await ctx.send(f"Gøldbot chooses: `{random.choice(divided_options).strip()}`.")
		else:
			await ctx.send(
				f"I can't just choose between {len(divided_options)} choice. *(to divide the choices you should put a comma between them)*.")

	@commands.command(
		aliases=("coinflip", "flipcoin", "coin"),
		description="Flip a coin and see if it lands on heads or tails."
	)
	async def flip(self, ctx):
		await ctx.send(f"-Flip!-\nIt landed on {random.choice(('heads', 'tails'))}!")

	@commands.command(
		aliases=("rolldice", "diceroll", "dice"),
		description="Roll a die with X number of faces *(6 by default)*.",
		extras={
			'example': "20",
			"signature": "[Number of Sides=6]"
		}
	)
	async def roll(self, ctx, faces=6.0):
		if type(faces) is float and faces != int(faces):
			await ctx.send(
				f"Error: You can't roll a die with a non-whole amout of faces, you {faces}-dimensional being!")
			return
		if faces > 2:
			try:
				faces = int(faces)
			except ValueError:
				await ctx.send("Error: You can't roll a die with a non-numeric amount of faces...")
			result = random.randint(1, faces)
			print(result)
			if faces <= 6:
				result = discord.utils.get(self.my_guild.emojis, name=f"Dice{result}")
			await ctx.send(f"Rolled a d{faces}.\nIt landed on **{result}**!")
		elif faces == 2:
			await ctx.send(f"... A 2 sided die is a coin... Use the `{ctx.prefix}flip` command.")
		elif faces <= 1:
			await ctx.send("... You serious?")

	@roll.error
	async def roll_error(self, ctx, error):
		if isinstance(error, commands.BadArgument):
			await ctx.send("Error: You can't roll a die with a non-numeric amount of faces...")

	@commands.command(
		description="Send a message with the text you wrote **in quotation marks** and deletes your message. If the channel is defined, it'll send the message to said channel.",
		extras={
			"signature": '"<message>" [channel]',
			"example": '"Hi, my name is Gøldbot and I\'m sentient." #general`'
		}
	)
	async def say(self, ctx, message, channel: discord.TextChannel = None):
		if len(message.strip()) == 0:
			await ctx.send("Error: You can't send an empty message.")
			return
		if channel is None:
			channel = ctx.channel
		if not channel.permissions_for(ctx.author).send_messages:
			await ctx.send(f"Error: You don't have permissions to talk in {channel.mention}")
			return
		if channel.guild.id != ctx.guild.id:
			await ctx.send(f"Error: {channel.mention} is not in {ctx.guild.name}")
			return
		if message.lower().startswith("i am") or message.lower().startswith("i'm"):
			if "stupid" in message.lower():
				message = f"{ctx.author.mention} is stupid."
			elif "dumb" in message.lower():
				message = f"{ctx.author.mention} is dumb."
		await discord.Message.delete(ctx.message, delay=0)
		await channel.send(message)


async def setup(bot):
	await bot.add_cog(Fun(bot), override=True)
