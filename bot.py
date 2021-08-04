import os
import random

import discord
from discord.ext import commands

import prefix
from config import parse_config

config = parse_config("./config.toml")


def is_bot_owner(ctx):
	return ctx.author.id in config["owners_id"]


def check_if_self_hosted():
	try:
		with open(r"C:\Users\cient\OneDrive\Escritorio\Don't delete this text file.txt", "r") as f:
			str(f.read())
		return True
	except FileNotFoundError:
		return False


if check_if_self_hosted():
	parser = prefix.PrefixParser(default="g.")
else:
	parser = prefix.PrefixParser(default="g!")

client = commands.Bot(command_prefix=parser, case_insensitive=True)

client.remove_command("help")
owner = None
log = None
log2 = None


@client.event
async def on_ready():
	global owner
	global log
	global log2
	owner = await client.fetch_user(config["owners_id"][0])
	log = client.get_channel(config["log_channel"])
	log2 = client.get_channel(838025060983767051)


async def autodelete(message):
	if len(message.attachments) != 0:
		content_type = f"\nAttachment type: {message.attachments[0].content_type}"
	else:
		content_type = ""
	await discord.Message.delete(message, delay=0)
	await message.author.send("Your message in #datapacks was automatically removed because it did not contain a file or a link. (From the Origins Mod server)\n\nPD: If your message got deleted yet you had a link or a datapack, please contact Golder06#7041\nPD2: Please remember that the file has to be a `.zip` file.")
	await log.send(f"Message by {message.author.name}#{message.author.discriminator} deleted in #datapacks.\nMessage: \n> {message.content}\nAttachment List Length: {len(message.attachments)}{content_type}")
	await log2.send(f"Message by {message.author.name}#{message.author.discriminator} deleted in #datapacks.\nAttachment List Length: {len(message.attachments)}")


@client.event
async def on_message(message):
	if message.channel.id == 749571272635187342:  # If the message is in the #datapacks channel and isn't made by a user with administrator permissions it'll check if it has a .zip file attached to it or if it has a link. If it doesn't, the message gets deleted
		if message.author.bot:
			await discord.Message.delete(message, delay=0)
		if message.author.guild_permissions.administrator:
			pass
		elif len(message.attachments) != 0:
			if message.attachments[0].content_type != "application/zip":
				await autodelete(message)
		elif len(message.embeds) == 0:
			await autodelete(message)
	elif message.content.startswith("!<#843834879736283156>"):
		serious = client.get_emoji(821796259333537813)
		try:
			await message.reference.resolved.reply(f"Please use your commands in <#843834879736283156>, so the other channels don't get messy! {serious}")
		except AttributeError:
			await message.channel.send(f"Please use your commands in <#843834879736283156>, so the other channels don't get messy! {serious}")
	else:
		if message.guild.id == 734127708488859831:  # If the message is in the Origins Server, it won't try to process it as a command. (Don't think it'd be a good idea to let people use Gøldbot's commands there.)
			if message.content.startswith("g!") and message.channel.id == 843834879736283156:
				await message.reply(f"Gøldbot commands have been disabled in this server. {random.choices(['~~But you can always add me to your server with this link wink wink <https://discord.com/api/oauth2/authorize?client_id=573680244213678081&permissions=8&scope=bot>~~', ''], [1,10])[0]}")
			else:
				message.reply("Gøldbot commands have been disabled in this server.")
		else:
			await client.process_commands(message)


def embed_template(ctx, title=None, description=None, footer="", image: str = "", icon: str = ""):
	embed = discord.Embed(description=description, color=random.randint(0, 0xffffff))
	if icon != "":
		embed.set_author(name=title, icon_url=icon)
	else:
		embed.set_author(name=title)
	embed.set_footer(
		text=f"{footer}\nTo see more information about a specific command, type {ctx.prefix}help <command>.\nGøldbot was created by {owner.name}.",
		icon_url="https://i.imgur.com/ZgG8oJn.png")
	embed.set_thumbnail(url="https://i.imgur.com/8bOl5gU.png")
	if image != "":
		embed.set_image(url=image)
	return embed


@client.command(name="help")
async def _help(ctx, command=None):
	if command is None:
		title = "Commands"
		with open("help_texts/general_help.txt", "r", encoding='utf-8') as file:
			help_text = file.read()
		with open("help_texts/mod_help.txt", "r", encoding='utf-8') as file:
			mod_text = file.read()
		with open("help_texts/owner_help.txt", "r", encoding='utf-8') as file:
			owner_text = file.read()
		if ctx.author.guild_permissions.administrator:
			help_text += mod_text
		if is_bot_owner(ctx):
			help_text += owner_text
	else:
		command = command.lower()
		try:
			title = command.capitalize()
			with open(f"help_texts/specific_help/{command}.txt", encoding='utf-8') as file:
				help_text = file.read()
		except FileNotFoundError:
			title = "Error!"
			help_text = "Command not found."
	embed = embed_template(ctx, title, help_text.format(prefix=ctx.prefix), "\n<>=Necessary, []=optional.")
	await ctx.send(embed=embed)


@client.command()
async def prefix(ctx, new_prefix=None):
	perm = ctx.author.guild_permissions.administrator
	if new_prefix is None:
		await ctx.send(f"Server's prefix currently set to `{ctx.prefix}`.")
	else:
		if perm:
			sv = str(ctx.guild.id)
			parser.update(sv, new_prefix)
			await ctx.send(f"Prefix changed to `{new_prefix}`!")
		else:
			raise commands.CheckFailure


for filename in os.listdir('./cogs'):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')

if check_if_self_hosted():
	TOKEN = "NzkxMDY2MzQ5MjUzODIwNDc4.X-Jv8g.bEiIuTfej1rshqehrR_v1T5rvsk"
else:
	TOKEN = "NTczNjgwMjQ0MjEzNjc4MDgx.XMuXXA.ywRBVp3AnGQjCiRwjYJsk3Oryk4"

client.run(TOKEN)
