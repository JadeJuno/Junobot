import asyncio
import io
import os
import random
import zipfile

import discord
from discord.ext import commands

import prefix
from config import parse_config

config = parse_config("./config.toml")

origin_commands = (
	"datapacks", "<#843834879736283156>", 'commands', "rule", "rules", "help", "whitelisted", "whitelist",
	"whitelistedlinks", 'transbee', 'wiki', 'channelonly', 'avd', "addonsvsdatapacks", 'addonvsdatapack', 'tias',
	'try-it-and-see', 'tryit', 'try-it', 'tryitandsee', 'transratkid', 'bibee', 'invite', 'escape')  # TO-DO: make a cog for all origin commands.

whitelisted_links = ["https://mediafire.com/", "https://github.com/", "https://planetminecraft.com/",
					 "https://docs.google.com/", "https://curseforge.com/", "https://modrinth.com"]
temp_white = whitelisted_links[:]
for _link in temp_white:
	whitelisted_links.append(_link.replace("://", "://www."))
temp_white.clear()
whitelisted_links = tuple(whitelisted_links)


def is_bot_owner(ctx):
	return ctx.author.id in config["owners_id"]


def is_in_origin_server(ctx):
	return ctx.channel.guild.id == 734127708488859831


def isnt_in_origin_server(ctx):  # I hate that there's no way to inverse a command check...
	return ctx.channel.guild.id != 734127708488859831


def is_origin_mod(ctx):
	return ctx.author.id in config["origins_mods"]


def check_if_self_hosted():
	try:
		with open(r"C:\Users\cient\OneDrive\Escritorio\Don't delete this text file.txt", "r") as f:
			str(f.read())
		return True
	except FileNotFoundError:
		return False


async def tryreply(ctx, message, reply=False, img=None):
	try:
		await ctx.message.reference.resolved.reply(message)
	except AttributeError:
		if reply:
			await ctx.reply(message)
		else:
			await ctx.send(message)


parser = prefix.PrefixParser(default="g!")

intents = discord.Intents.all()
allowed_mentions = discord.AllowedMentions(everyone=False)
client = commands.Bot(command_prefix=parser, case_insensitive=True, intents=intents, allowed_mentions=allowed_mentions)
client.remove_command("help")

log = client.get_channel(config["log_channel"])


@client.event
async def on_ready():
	global log
	log = client.get_channel(config["log_channel"])


async def autodelete(message: discord.Message):
	origin_log = client.get_channel(838025060983767051)
	content = message.content
	log_message = f"**Message:** \n\n> {content}\n\nAttachment List Length: {len(message.attachments)}"
	if len(message.attachments) != 0:
		log_message += f"\nAttachment type: {message.attachments[0].content_type}"
		if message.attachments[0].content_type == 'application/zip':
			url = await message.attachments[0].read()
			zip_from_bytes = zipfile.ZipFile(io.BytesIO(url), "r")
			log_message += f"\n`pack.mcmeta` in zip: {'pack.mcmeta' in zip_from_bytes.namelist()}"
	if message.reference:
		log_message += f"\nReferenced Message: {message.reference.jump_url}"
	await discord.Message.delete(message, delay=0)
	try:
		if message.content.startswith(("!", "?")):
			await message.author.send(
				f"Your message in <#{message.channel.id}> was automatically removed because it was a command. Please use commands in <#843834879736283156>.")
		else:
			await message.author.send(
				f"""Your message in <#{message.channel.id}> was automatically removed because it did not contain a {'''.zip file, the zip file was zipped incorrectly or it didn't include a''' if message.channel.id == 749571272635187342 else '.jar file or a'} whitelisted link.
				
PD: If your message got deleted yet you had a link or a {'zip file' if message.channel.id == 749571272635187342 else 'jar file'}, please DM the creator of the bot Golder06#7041
PD2: If you wanna suggest another link to whitelist, you are also allowed to DM Golder. If you wanna see the full commands list, use `?whitelisted` in <#843834879736283156>
PD3: Also, please check if your datapack is zipped correctly (use `!zip-pack` on <#843834879736283156>)"""
			)
		log_message += "\nDM sent: True"
	except discord.errors.Forbidden:
		log_message += "\nDM sent: False"
	if len(log_message) <= 4096:
		embed = discord.Embed(description=log_message, color=random.randint(0, 0xffffff))
		embed.set_author(
			name=f"Message by {message.author.name}#{message.author.discriminator} deleted in #{message.channel.name}.",
			icon_url=str(message.author.avatar_url))
		embed.set_footer(text=f"{message.author.name}'s ID: {message.author.id}",
						 icon_url="https://i.imgur.com/ZgG8oJn.png")
		await log.send("", embed=embed)
		await origin_log.send("", embed=embed)
	else:
		with open('temp.txt', 'w') as f:
			f.write(content)
		log_message = f"Message by {message.author.name}#{message.author.discriminator} ({message.author.id}) deleted in <#{message.channel.id}>.\nThe message would make the log exceed the 2000 character limit. Sending as Text Document:"
		if len(message.attachments) != 0:
			log_message += f"\nAttachment type: {message.attachments[0].content_type}"
		if message.reference:
			log_message += f"\nReferenced Message: {message.reference.jump_url}"
		with open('temp.txt', 'rb') as f:
			temp = discord.File(f)
		await origin_log.send(log_message, file=temp)
		await asyncio.sleep(1)
		os.remove('temp.txt')


@client.event
async def on_message(message: discord.Message):
	if message.guild is None:  # Modmail
		if message.author.bot:
			return
		modmail = False
		for guild in message.author.mutual_guilds:
			if guild.id == 734127708488859831:
				modmail = True
				break
		if modmail:
			if message.content.startswith("$"):
				channel = client.get_channel(814542424793153556)
				embed = discord.Embed(title=f"{message.author.name}#{message.author.discriminator}")
				embed.set_author(name=message.author.id, icon_url=str(message.author.avatar_url))
				embed.add_field(name="Description:", value=message.content.lstrip('$'))
				mail_message = await channel.send(embed=embed)
				await message.channel.send("Your message has been sent to the Origins Server's Mods.")

				def reply_check(msg):
					try:
						res = msg.reference.message_id == mail_message.id and msg.channel.id == 814542424793153556
					except AttributeError:
						res = False
					return res

				reply = await client.wait_for('message', check=reply_check)
				await message.channel.send(f"{reply.content}")
				await reply.add_reaction("\u2705")
			else:
				await message.channel.send(
					"If you want to contact the Origins Server's Modmail, you have to use `$` as a prefix to your message.")
			return
	elif is_in_origin_server(message):
		origin_log = client.get_channel(838025060983767051)
		if message.channel.id == 749571272635187342:  # Datapack check
			if message.author.bot:
				await discord.Message.delete(message, delay=0)
			if is_origin_mod(message):
				pass
			elif len(message.attachments) != 0:
				if any(link in message.content for link in whitelisted_links):
					return
				elif message.attachments[0].content_type == 'application/zip':
					url = await message.attachments[0].read()
					zip_from_bytes = zipfile.ZipFile(io.BytesIO(url), "r")
					if "pack.mcmeta" not in zip_from_bytes.namelist():
						await autodelete(message)
						return
				else:
					await autodelete(message)
					return
			else:
				if not any(link in message.content for link in whitelisted_links):
					await autodelete(message)
					return
		elif message.channel.id == 848428304003366912:  # Addon check
			if message.author.bot:
				await discord.Message.delete(message, delay=0)
			if is_origin_mod(message):
				pass
			if len(message.attachments) != 0:
				if any(link in message.content for link in whitelisted_links):
					return
				elif message.attachments[0].content_type != "application/java-archive":
					await autodelete(message)
					return
			else:
				if not any(link in message.content for link in whitelisted_links):
					await autodelete(message)
					return
		elif "@everyone" in message.content or "@here" in message.content:
			await discord.Message.delete(message, delay=0)
			await message.author.send("Please don't try to ping everyone. It doesn't work and it's annoying.")
			await origin_log.send(
				f"@everyone attempt by {message.author} ({message.author.id}) deleted in <#{message.channel.id}>:\n>>> {message.content}")
		else:
			if not is_origin_mod(message):
				g_prefix = parser.__getitem__(message.channel.guild.id)
				if message.content.startswith(g_prefix):
					if message.content.lstrip(g_prefix).startswith(tuple(origin_commands)):  # Do not change the tuple() or I will decapitate your ass.
						await client.process_commands(message)
						return
					non_origin_commands = [cmd[:-4] for cmd in os.listdir("help_texts/specific_help")]
					non_origin_commands.remove("help")
					if message.content.lstrip(g_prefix).startswith(non_origin_commands):
						if message.channel.id == 843834879736283156:
							await message.reply(
								f"This Goldbot commands has been disabled in this server. {random.choices(('~~But you can always add me to your server with this link wink wink <https://discord.com/api/oauth2/authorize?client_id=573680244213678081&permissions=8&scope=bot>~~', ''), (1, 10))[0]}")
							return
						else:
							await message.reply("This Goldbot command has been disabled in this server.")
							return
			else:
				await client.process_commands(message)
				return
	else:
		await client.process_commands(message)


def embed_template(ctx, title=None, description=None, footer="", add_def_footer=True, image: str = "", icon: str = ""):
	embed = discord.Embed(description=description, color=random.randint(0, 0xffffff))
	if icon != "":
		embed.set_author(name=title, icon_url=icon)
	else:
		embed.set_author(name=title)
	if footer:
		if add_def_footer:
			embed.set_footer(
				text=f"{footer}\nTo see more information about a specific command, type {ctx.prefix}help <command>.\nGøldbot was created by Golder06#7041.",
				icon_url="https://i.imgur.com/ZgG8oJn.png")
		else:
			embed.set_footer(
				text=footer, icon_url="https://i.imgur.com/ZgG8oJn.png")
	embed.set_thumbnail(url="https://i.imgur.com/8bOl5gU.png")
	if image != "":
		embed.set_image(url=image)
	return embed


@client.command(name="help")
async def _help(ctx, command=None):
	if isnt_in_origin_server(ctx) or is_origin_mod(ctx):
		mod_commands = ("ban", "clear", "kick", "pin", "unban")
		if command is None:
			title = "Commands"
			with open("help_texts/general_help.txt", "r", encoding='utf-8') as file:
				help_text = file.read()
			if ctx.author.guild_permissions.administrator:
				with open("help_texts/mod_help.txt", "r", encoding='utf-8') as file:
					help_text += file.read()
			if is_in_origin_server(ctx):
				with open("help_texts/origin_help.txt", "r", encoding='utf-8') as file:
					origin_help = file.read().split('\n\n')[0]
					help_text += f"\n\n**Origins Commands:**\n{origin_help}"
			footer = "\n<>=Necessary, []=optional."
		else:
			command = command.lower()
			if command in mod_commands:
				if ctx.author.guild_permissions.administrator:
					title = command.capitalize()
					with open(f"help_texts/specific_help/{command}.txt", encoding='utf-8') as file:
						help_text = file.read()
					footer = "\n<>=Necessary, []=optional."
				else:
					title = "Error!"
					help_text = f"You don't have permissions to use `{command}`"
					footer = ""
			else:
				try:
					title = command.capitalize()
					with open(f"help_texts/specific_help/{command}.txt", encoding='utf-8') as file:
						help_text = file.read()
					footer = "\n<>=Necessary, []=optional."
				except FileNotFoundError:
					title = "Error!"
					help_text = "Command not found."
					footer = ""
		embed = embed_template(ctx, title, help_text.format(prefix=ctx.prefix), footer, add_def_footer=True)
	else:
		title = "Commands"
		with open("help_texts/origin_help.txt", "r", encoding='utf-8') as file:
			help_text = file.read()
		footer = "\n<>=Necessary, []=optional.\nGøldbot was created by Golder06#7041."
		shameless_promotion = random.choices((
			'~~But you can always add me to your server with this link wink wink <https://discord.com/api/oauth2/authorize?client_id=573680244213678081&permissions=8&scope=bot>~~',
			''), (1, 10))[0]
		embed = embed_template(ctx, title, help_text.format(prefix=ctx.prefix, shameless_promotion=shameless_promotion),
							   footer, add_def_footer=False)
	await ctx.send(embed=embed)


@client.command()
async def prefix(ctx, new_prefix=None):
	if not check_if_self_hosted():
		if new_prefix is None:
			await ctx.send(f"Server's prefix currently set to `{ctx.prefix}`.")
		else:
			if ctx.author.guild_permissions.administrator:
				if new_prefix.lower() == "reset":
					parser.update(str(ctx.guild.id), parser.default)
					await ctx.send(f"Prefix reset back to `{parser.default}`!")
				else:
					parser.update(str(ctx.guild.id), new_prefix)
					await ctx.send(f"Prefix changed to `{new_prefix}`!")
			else:
				raise commands.MissingPermissions(missing_perms=('administrator',))


if __name__ == "__main__":
	for filename in os.listdir('./cogs'):
		if filename.endswith('.py'):
			client.load_extension(f'cogs.{filename[:-3]}')
	TOKEN = os.getenv("GOLD_TOKEN")
	if not TOKEN:
		TOKEN = input("Goldbot's Token: ")

	client.run(TOKEN)
