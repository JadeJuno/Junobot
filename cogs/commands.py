import asyncio
import os
import random
from datetime import datetime, timedelta

import discord
import googletrans
import wikipedia
from discord.ext import commands, tasks
from googletrans import Translator
from iso639 import languages

import bot
import googlesearch
from morsecode import MorseCode
from oxforddict import get_definition

status_list = ('My default prefix is g!.', "If I break, contact Golder06#7041.", 'To see my commands, type g!help.')

change_loop_interval = random.randint(1, 90)


def get_dict_key(dictionary, value):
	key_list = list(dictionary.keys())
	value_list = list(dictionary.values())
	for listed_value in value_list:
		if listed_value == value:
			return key_list[value_list.index(value)]
	return value


def get_emoji_list(emojis):
	return_list = list(emojis)
	for i in range(len(return_list)):
		for j in range(i + 1, len(return_list)):
			if return_list[i].name > return_list[j].name:
				return_list[i], return_list[j] = return_list[j], return_list[i]
	return return_list


class Commands(commands.Cog):
	def __init__(self, client):
		self.activity = None
		self.client = client
		self.log = None
		self.loop_interval = None
		self.morse = MorseCode()
		self.my_guild = None
		self.translator = Translator()
		self.lang_dict = googletrans.LANGUAGES
		self.emoji_list = None

	async def reaction_decision(self, ctx, check_str):
		check_message = await ctx.send(check_str)
		await check_message.add_reaction("\U00002705")
		await check_message.add_reaction("\U0000274c")

		def check(reaction_checked, reaction_user):
			user_check = reaction_user.id == ctx.author.id or reaction_user.guild_permissions.administrator and ctx.author.bot
			return user_check and reaction_checked.message == check_message and str(reaction_checked.emoji) in (
				"\U00002705", "\U0000274c")

		reaction, user = await self.client.wait_for('reaction_add', check=check)
		if str(reaction.emoji) == "\U00002705":
			return True
		elif str(reaction.emoji) == "\U0000274c":
			return False

	@tasks.loop(minutes=change_loop_interval)
	async def change_status_task(self):
		global change_loop_interval
		self.activity = random.choice(status_list)
		await self.client.change_presence(status=discord.Status.online, activity=discord.Game(self.activity))
		time_now = datetime.now()
		print(f'Status changed to "{self.activity}" ({time_now.strftime("%H:%M")}).')
		change_loop_interval = random.randint(1, 90)
		print(
			f"Next status change in {change_loop_interval} minutes ({(time_now + timedelta(minutes=change_loop_interval)).strftime('%H:%M')}).")

	@commands.Cog.listener()
	async def on_ready(self):
		self.log = self.client.get_channel(bot.config["log_channel"])
		self.my_guild = self.client.get_guild(bot.config["guild_id"])
		self.emoji_list = get_emoji_list(self.my_guild.emojis)
		print(f'Bot is ready.')
		print(f"bot created by Golder06#7041.")
		await self.log.send("Bot Started.")
		self.change_status_task.start()

	@commands.command(name='8ball')
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
			elif "love" in question.lower():  # :tr:
				prediction = random.choice(ball_predicts[-5:])
			else:
				prediction = random.choice(ball_predicts)
		else:
			prediction = "That's not a question..."
		await ctx.send(f'Question: {question}\nThe ***:8ball:BALL*** says: {prediction}')

	@commands.command()
	async def choose(self, ctx, *, options):
		divided_options = options.split(",")
		if len(divided_options) >= 2:
			for option in divided_options:
				if not option:
					divided_options.pop(option)
			await ctx.send(f'Gøldbot chooses: `{random.choice(divided_options).strip()}`.')
		else:
			await ctx.send(
				f'I can\'t just choose between {len(divided_options)} choice. *(to divide the choices you should put a comma between them)*.')

	@commands.command(aliases=("coinflip", "flipcoin"))
	async def flip(self, ctx):
		await ctx.send(f"-Flip!-\nIt landed on {random.choice(('heads', 'tails'))}!")

	@commands.command(aliases=("rolldice", "diceroll", "dice"))
	async def roll(self, ctx, faces=6.0):
		if random.choices((True, False), (100, 1))[0]:
			if type(faces) is float and faces != int(faces):
				await ctx.send(
					f"Error: You can't roll a die with a non-whole amout of faces, you {faces} dimensional being!")
				return
			if faces > 2:
				try:
					faces = int(faces)
				except ValueError:
					await ctx.send("Error: You can't roll a die with a non-numeric amount of faces...")
				result = random.randint(1, faces)
				if faces <= 6:
					emoji = self.emoji_list[result - 1]
				else:
					emoji = result
				await ctx.send(f"Rolled a d{faces}.\nIt landed on **{emoji}**!")
			elif faces == 2:
				await ctx.send(f"... A 2 sided die is a coin... Use the `{ctx.prefix}flip` command.")
			elif faces <= 1:
				await ctx.send("... You serious?")
		else:
			# This right here is why you don't allow me to code while sick =)
			with open('=).gif', 'rb') as f:
				img = discord.File(f)
			await ctx.send("Rick. \n~~haha get it it's a rickroll lmfaooooooo-~~", file=img)

	@roll.error
	async def roll_error(self, ctx, error):
		if isinstance(error, commands.BadArgument):
			await ctx.send("Error: You can't roll a die with a non-numeric amount of faces...")

	@commands.command()
	async def say(self, ctx, message, channel=None):
		if len(message.strip()) == 0:
			await ctx.send("Error: You can't send an empty message.")
			return
		if channel is None:
			channel = ctx.channel
		else:
			if channel.startswith("<#"):
				channel = self.client.get_channel(int(channel.strip("<>")[1:]))
			else:
				channel = discord.utils.get(ctx.guild.text_channels, name=channel)
		if channel is None:
			await ctx.send("Error: Channel doesn't exist.")
			return
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
		try:
			os.remove(".google-cookie")
		except FileNotFoundError:
			pass

	@commands.command(aliases=('definition',))
	async def dictionary(self, ctx, *, query):
		message = await ctx.send("Getting definition...")
		results = get_definition(query)
		if results != "404 Error":
			lex_entries = results["lexicalEntries"]
			entries = [lex_entry["entries"] for lex_entry in lex_entries]
			entries = [x for y in entries for x in y]
			senses = [entry["senses"] for entry in entries]
			senses = [x for y in senses for x in y]
			definitions = [definition['definitions'][0] for definition in senses]

			emb = bot.embed_template(ctx, title=f'Definition of "{query.title()}":',
									 description=f"{definitions[0].capitalize()}")

		else:
			emb = bot.embed_template(ctx, title="Error:", description=f'Definition for "{query.title()}" not found.')

		await message.edit(content="", embed=emb)

	@commands.check(bot.is_in_origin_server)
	@commands.command()
	async def escape(self, ctx, *, string=None):
		if string is not None:
			escaping = string.replace('"', '\\"')
			await ctx.send(f"Here's your escaped string:\n`{escaping}`")
			return
		elif ctx.message.reference and string is None:
			escaping = ctx.message.reference.resolved.content.replace('"', '\\"')
			await ctx.send(f"Here's your escaped string:\n`{escaping}`")
		else:
			await ctx.send("Error: No string to escape.")

	@commands.command(aliases=("googleit", "googlesearch", "search"))
	async def google(self, ctx, *, search_request):
		message = await ctx.send(f"Searching for `{search_request}`...")
		i = 1
		output_str = ""
		for url in googlesearch.search(search_request, stop=10):
			if i < 10:
				output_str += f"`{i}.`   **[{discord.utils.escape_markdown(url.title)}](<{url.link}>)**\n"
			else:
				output_str += f"`{i}.` **[{discord.utils.escape_markdown(url.title)}](<{url.link}>)**\n"
			i += 1
		if i == 1:
			output_str = "**No results found.**"
		embed = bot.embed_template(ctx, "Google", output_str[0:-1],
								   icon="https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/1200px-Google_%22G%22_Logo.svg.png")
		await message.edit(content=None, embed=embed)

	@commands.command(aliases=("detect", "language"))
	async def lang_detect(self, ctx, *, user_message):
		detected_lang = self.translator.detect(user_message).lang
		if isinstance(detected_lang, list):
			detected_lang = detected_lang[self.translator.detect(user_message).confidence.index(
				max(self.translator.detect(user_message).confidence))]
		await ctx.send(
			f'"{user_message}" is in {languages.get(alpha2=detected_lang).name} (Certainty: `{int(max(self.translator.detect(user_message).confidence) * 100)}%`).')

	@commands.command(name="morse", aliases=("morsecode",))
	async def morse_code(self, ctx, encrypt_decrypt, *, sentence):
		disc = encrypt_decrypt
		var = self.morse.check_letter(sentence.upper())
		if not var:
			await ctx.send("Error: Invalid character detected.")
			return
		code = f"{sentence} "
		error_message = f"Error: You tried to {disc} an already {disc}ed message or you entered an invalid character."
		if disc == "encrypt":
			try:
				code = code[0:-1]
				output = self.morse.encrypt(code.upper())
			except KeyError:
				output = error_message
			except Exception as e:
				print(e)
				return
		elif disc == "decrypt":
			code = code.replace('_', '-')
			try:
				output = self.morse.decrypt(code).lower()
			except ValueError:
				output = error_message
		else:
			output = "Error: Invalid discriminator."
		await ctx.send(output.capitalize())

	@commands.command()
	async def ping(self, ctx):
		await ctx.send(f':ping_pong: Pong! {self.client.latency * 1000:.0f}ms.')

	@commands.command()
	async def translate(self, ctx, translate_message, destination_language='en', source_language=None):
		destination_language = destination_language.lower()
		destination_language = get_dict_key(self.lang_dict, destination_language)
		if source_language is not None:
			source_language = source_language.lower()
			source_language = get_dict_key(self.lang_dict, source_language)
		else:
			source_language = self.translator.detect(translate_message).lang
			if isinstance(source_language, list):
				source_language = source_language[0]
		try:
			translated_text = self.translator.translate(translate_message, src=source_language,
														dest=destination_language).text.replace("`", "\`")
			await ctx.send(
				f'Translated from {self.lang_dict[source_language].capitalize()} to {self.lang_dict[destination_language].capitalize()}\n`{translated_text.capitalize()}`.')
		except ValueError:
			await ctx.send(f"Error: Invalid language.")

	@commands.command()
	async def wikipedia(self, ctx, *, search_request):
		message = await ctx.send(f"Searching for {search_request}")
		title = "Wikipedia"
		description = ""
		image = "https://i.imgur.com/7kT1Ydo.png"
		try:
			result = wikipedia.page(search_request)
			# update: didn't go that bad, but it wasn't "well lol"
			description = f"[{result.title}]({result.url})\n{result.summary[:300].strip()}..."
			image = result.images[0]
		except wikipedia.exceptions.DisambiguationError as e:
			i = 1
			for option in e.options[:9]:
				i += 1
				disamb_result = wikipedia.page(option, auto_suggest=False)
				if disamb_result.url != "":
					result_2 = f"[{disamb_result.title}]({disamb_result.url})"
				else:
					result_2 = f"{disamb_result} **URL Not Found**"
				description += f"`{i}`: {result_2}\n"
		except wikipedia.exceptions.PageError:
			description = "Page not found."
		embed = bot.embed_template(ctx, title, description, image=image, icon="https://i.imgur.com/FD1pauH.png")
		await message.edit(content=None, embed=embed)

	@commands.has_permissions(manage_messages=True)
	@commands.command()
	async def clear(self, ctx, amount: int):
		await ctx.message.delete()
		await ctx.channel.purge(limit=amount)
		clear_message = await ctx.send(f'Cleared {amount} messages.')
		await asyncio.sleep(2)
		await clear_message.delete()

	@commands.has_permissions(ban_members=True)
	@commands.command()
	async def ban(self, ctx, member: discord.Member, *, reason=None):
		if not member.guild_permissions.administrator:
			await member.ban(reason=reason)
			await ctx.send(f'{member} banned via `{ctx.prefix}ban` command. Reason: {reason}.')
		else:
			await ctx.send(f"Error: {member} is an admin and can't be banned by Goldbot.")

	@commands.has_permissions(kick_members=True)
	@commands.command()
	async def kick(self, ctx, member: discord.Member, *, reason=None):
		await member.kick(reason=reason)
		await ctx.send(f'{member} kicked via `{ctx.prefix}kick` command. Reason: {reason}.')

	@commands.has_permissions(manage_roles=True)
	@commands.command()
	async def mute(self, member: discord.Member, time="1m", *, reason=None):
		return

	@commands.has_permissions(manage_messages=True)
	@commands.command()
	async def pin(self, ctx):
		if ctx.message.reference:
			await ctx.message.reference.resolved.pin()
		else:
			messages = await ctx.history(limit=2).flatten()
			messages.remove(ctx.message)
			await messages[0].pin()

	@commands.command()
	async def invite(self, ctx):
		await ctx.send(
			"Here's the invite link for Goldbot:\nhttps://discord.com/api/oauth2/authorize?client_id=573680244213678081&permissions=8&scope=bot")

	@commands.command()
	async def binary(self, ctx, encode_decode: str, *, sentence):
		if encode_decode.lower() == "encode":
			s = ''.join(format(ord(i), '08b') for x, i in enumerate(sentence))
			bin_list = [s[i:i + 8] for i in range(0, len(s), 8)]
			output = ''
			for _bin in bin_list:
				output += f'{_bin} '
			output = output[:-1]
			await ctx.send(f"Here\'s your encoded string: \n`{output}`")
		elif encode_decode.lower() == 'decode':
			for char in sentence:
				if char not in ['0', '1', ' ']:
					await ctx.send("Please only use 1s and 0s.")
					return
			try:
				int(sentence)
			except ValueError:
				bin_list = sentence.split()
			else:
				bin_list = [sentence[i:i + 8] for i in range(0, len(sentence), 8)]

			output = ''
			for _bin in bin_list:
				output += chr(int(_bin, 2))
			await ctx.send(f"Here\'s your decoded binary code: \n`{output}`")
			return
		else:
			await ctx.send('ERROR: Invalid discriminator.')
			return

	@commands.has_permissions(ban_members=True)
	@commands.command()
	async def unban(self, ctx, *, member):
		banned_users = await ctx.guild.bans()
		member_name, member_discriminator = member.split('#')
		for ban_entry in banned_users:
			user = ban_entry.user
			if (user.name, user.discriminator) == (member_name, member_discriminator):
				await ctx.guild.unban(user)
				await ctx.send(f'Unbanned {user.mention}.')
				return
			await ctx.send(f'{user.mention} is not banned.')

	@commands.has_permissions(manage_nicknames=True)
	@commands.command(aliases=("rename",))
	async def nickname(self, ctx, *, nickname):
		await ctx.guild.me.edit(nick=nickname)
		await ctx.send(f'Successfully changed my nickname to "{nickname}"')

	@commands.check(bot.is_bot_owner)
	@commands.command()
	async def test(self, ctx):
		gold_emoji = self.emoji_list[0]
		print("TEST")
		embed = discord.Embed(title="Title", description=f"{gold_emoji}[Test Link](https://www.youtube.com)",
							  color=random.randint(0, 0xffffff), url="https://www.google.com/")
		embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
		embed.set_footer(text=f"*Requested by {ctx.author.name}.*", icon_url=ctx.author.avatar_url)
		embed.set_image(url="https://discordpy.readthedocs.io/en/latest/_images/snake.png")
		embed.set_thumbnail(url="https://i.imgur.com/8bOl5gU.png")
		embed.add_field(name="Field 1", value="value 1")
		embed.add_field(name="Field 2", value="value 2")
		embed.add_field(name="Field 3", value="value 3")
		await ctx.send(embed=embed)
		await ctx.send(f"`{bot.parser.__getitem__(str(ctx.guild.id))}`")

	@commands.check(bot.is_bot_owner)
	@commands.command(aliases=['autoerror'])
	async def auto_error(self, ctx):
		await ctx.send(f"{int('A')}")

	@commands.check(bot.is_origin_mod)
	@commands.command()
	async def format(self, ctx):
		if ctx.message.reference:
			if len(ctx.message.reference.resolved.embeds) == 0:
				await ctx.send(f"```\n{ctx.message.reference.resolved.content.replace('> ', '')}```")
			else:
				await ctx.send(f"```\n{ctx.message.reference.resolved.embeds[0].description.replace('> ', '')}```")

	@commands.check(bot.is_origin_mod)
	@commands.command()
	async def sleep(self, ctx):
		serious = self.client.get_emoji(821796259333537813)
		await ctx.send(f"Golder!! Go to sleep! {serious}")

	@commands.check(bot.is_in_origin_server)
	@commands.command()
	async def datapacks(self, ctx):
		await bot.tryreply(ctx,
						   'If you want to find datapacks with custom origins, balance changes, and recipes for the Orb of Origin to use, check out <#749571272635187342>.\n\nTo install a datapack, navigate to your world folder (found in `.minecraft/saves`) and drop the datapack as a ZIP file into the `datapacks` folder. The same process can be used on a server (the world folder would be on the root though), and if you are running a server. the datapack does *not* need to be installed by each user.\n\nWhen creating a single-player world, there is also a "Data Packs" button in the world creation screen. If you click this, you are able to drag datapacks directly into the Minecraft window to add them. Don\'t forget to move them from "available" to "selected" though. This allows you to install datapacks *before* a world is generated!\n\nIf you are looking for information on how to create datapacks yourself, type `!wiki` or `!tutorial` in <#843834879736283156>.')

	@commands.check(bot.is_in_origin_server)
	@commands.command(name="<#843834879736283156>", aliases=('commands',))
	async def ch_commands(self, ctx):
		if ctx.channel.id != 843834879736283156:
			serious = self.client.get_emoji(821796259333537813)
			try:
				await ctx.message.reference.resolved.reply(
					f"Please use your commands in <#843834879736283156>, so the other channels don't get messy! {serious}")
			except AttributeError:
				await ctx.send(
					f"Please use your commands in <#843834879736283156>, so the other channels don't get messy! {serious}")
		else:
			await ctx.reply("This message is already in <#843834879736283156>...")

	@commands.check(bot.is_in_origin_server)
	@commands.command(aliases=('tias', 'try-it-and-see', 'tryit', 'try-it'))
	async def tryitandsee(self, ctx):
		await bot.tryreply(ctx, "https://tryitands.ee")

	@commands.check(bot.is_in_origin_server)
	@commands.command(aliases=('rules',))
	async def rule(self, ctx, rule_index: int):
		if rule_index <= 0:
			await ctx.send(f'Error: Rule {rule_index} does not exist.')
			return
		rules = (
			"**Rule 1: Be nice to each other.**\nWe want this to be a welcoming place for everyone. Keep in mind that not everyone has the same knowledge, background and experience as you.",
			"**Rule 2: Keep it in English.**\nWe do not want to exclude others. But English is the language we all understand here, and the only language the moderator team can moderate. (This includes using the Latin alphabet as well, please don't use the Standard Galactic Alphabet or any other. :P)",
			"**Rule 3: Appropriate content.**\nThis is a server about the Origins mod for Fabric. Please keep talk about that. If you want to talk about something else, move to off-topic. However, even in that channel we feel like certain controversial and inappropriate topics are out of place. A non-exhaustive list of topics which do not belong on this server includes: politics, religion, violence, and sexual content. In the end though, it's the call of the moderator that is present to decide what is appropriate and what isn't.",
			"**Rule 4: Follow the Discord Terms of Service.**\nDiscord does not allow talking about illegally distributed software, such as cracked Minecraft clients. Therefore we don't help with or want you to talk about cracked (non-premium) Minecraft clients and servers.",
			"**Rule 5: Check <#740658667161911296> before asking.**\nMany questions have already been answered in the <#740658667161911296> channel. Because of the large amount of new members, it is very time consuming to answer the same questions over and over and again. Therefore we would appreciate it if you could check that channel first and see if you can find a solution to your problem there.",
			"**Rule 6: Don't spam the advertisement channels.**\nPlease only advertise your server in <#749228091708014635>, and your content in <#809807082895048764>, once every 7 days. Depending on the server activity, this frequency might change in the future.",
			"**Rule 7: No transactions.**\nPlease do not offer or accept money or other forms of compensation for working on data packs or other content on this Discord. This is not the platform for this kind of transaction, and we won't take responsibility. Thus, we want you to keep that stuff out of this community.",
			"**Rule 8: Keep stuff that happened in other servers in those servers (or DMs).**\nWe can't confirm whether what you're saying actually happened the way you say it did. We can only moderate what happens in this Discord. Therefore we'd like to ask you to not take arguments or public accusations to this server, if someone for example behaved badly on your own Discord or Minecraft server. Similarly, if someone is misbehaving to you in DMs, report them to the Discord staff. It is not our duty (nor are we able to) to sort out your personal arguments. However, we will reserve the right to remove a server from the advertisement channels if the content of those servers seems inappropriate to us.",
			"**Rule 9: No Begging**\nDatapacks, addons, etc. are not easy to make, I think that we can all agree on that. So please, do not beg or ask other people to make something for you or anyone else. You can always do your best to learn yourself and then you have the ability to make whatever you may like! All we ask is that you don't beg others to make anything for anyone. (However, giving ideas in channels such as <#798545973554315304> is not the same as this. Spamming your idea in this channel is still breaking this rule.)",
			"**Rule 10: Keep your profile clean.**\nWhile your profile picture and custom status are part of your online identity and we don't want to restrict that, they are inherently public and visible to all users on this server. Thus we will ask you to change your profile picture or status (or nickname) if they break the Discord ToS or Community Guidelines. If you didn't change it after 24 hours, we will kick you and report your profile to the Discord staff.",
			"**Rule 11: Don't spam / Respect discussion.**\nThe point of this server is to help people with the Origins mod, talk about and discuss the base mod and datapacks, distribute datapacks so others can enjoy them, discuss the design of Origins, or build a friendly community in off-topic. Please be respectful with regards to other people's ongoing discussions. That does not mean that you are not allowed to talk to others while a discussion is going on - but purposefully interrupting them is not okay, and general spamming behavior is not tolerated."
		)
		try:
			rule = rules[rule_index - 1]
		except IndexError:
			await ctx.send(f'Error: Rule {rule_index} does not exist.')
			return
		await bot.tryreply(ctx, rule)

	@rule.error
	async def rule_error(self, ctx, error):
		if isinstance(error, commands.BadArgument):
			await ctx.send("Error: the rule's index has to be a whole number.")

	@commands.check(bot.is_in_origin_server)
	@commands.command(aliases=("avd", "addonsvsdatapacks"))
	async def addonvsdatapack(self, ctx):
		output = """When discussing datapacks and addons, it is important, for the sake of specificity, to understand the difference:\n\n**Addons**\nAddons are actual minecraft mods written in Java inside a .jar file\nThese add new features to the game and, in this case, the Origins Mod\nAdditionally, these are put into the `.minecraft/mods` folder\n\n**Datapacks**\n\nDatapacks are content packs that use existing features within minecraft\nThese are commonly written in JSON and using MCFunction files inside a zip folder\nAdditionally, these are localized to a specific minecraft world in the `.minecraft/saves/{worldname}/datapacks` folder\n\nMost Origins are Datapacks and can be located in #datapacks. Otherwise the origin may be an addon and can be found on curseforge."""
		await bot.tryreply(ctx, output)

	@commands.check(bot.is_in_origin_server)
	@commands.command()
	async def channelonly(self, ctx, key=None):
		replies = {
			825449766384828476: "This channel is only for posting powers that can be used by other people. For discussion about the powers listed in this channel, please go to <#802622603008409600>. If you need help related to the powers listed in here, please go to <#810587422303584286> or <#839141964519178240>",
			798545973554315304: "This channel is only for posting ideas for an origin. For discussion about the origins listed in this channel, please go to <#802622603008409600> or make a thread.",
			813795300691017798: "This channel is for posting media of your Origins only! If you wanted to comment on a video you found interesting, then please do so in <#756024207883894814>, <#802622603008409600>, or by making a thread",
			734133482757816401: "This channel is only for posting suggestions for the Origins mod. If you want to suggest an idea for an origin, do so in <#798545973554315304>. If you wanna comment about a suggestion, create a thread for that.",
			826144339041976321: "This channel is only for posting suggestions for the wiki of the Origins mod. If you want to suggest ideas for the Origins mod, do so in <#734133482757816401>. If you want to suggest an idea for an origin, do so in <#798545973554315304>."}
		if key is not None and ctx.channel.id not in replies.keys():
			try:
				await bot.tryreply(ctx, replies[key])
			except KeyError:
				return
		else:
			try:
				await bot.tryreply(ctx, replies[ctx.channel.id])
			except KeyError:
				return

	@commands.check(bot.is_in_origin_server)
	@commands.command(aliases=("whitelisted", "whitelist"))
	async def whitelistedlinks(self, ctx):
		s = "\n".join(bot.whitelisted_links[:len(bot.whitelisted_links) // 2])
		if ctx.channel.id == 843834879736283156:
			await ctx.reply(f"Here are the links you can use in <#749571272635187342>: ```{s}```")
		else:
			try:
				await ctx.author.send(f"Here are the links you can use in <#749571272635187342>: ```{s}```")
			except discord.Forbidden:
				await ctx.reply(
					"Error: Due to the length of the list, it should be sent in DMs. So please enable DMs in this server or use this command in <#843834879736283156>.")

	@commands.check(bot.is_in_origin_server)
	@commands.command()
	async def wiki(self, ctx, *, search=None):
		if search is None:
			await bot.tryreply(ctx,
							   "The Origins wiki has most of the information you'll need to create your own datapacks: https://origins.readthedocs.io/en/latest/\n\nIt is recommended you'll check out the \"Helpful\" Links at the bottom of the wiki page. Especially the video tutorial by CandyCaneCazoo is likely going to help you out!")
		else:
			await bot.tryreply(ctx,
							   f"https://origins.readthedocs.io/en/latest/search.html?q={search.replace(' ', '+')}")

	@commands.check(bot.is_in_origin_server)
	@commands.command()
	async def transbee(self, ctx):
		await ctx.send(random.choice(("https://images-ext-2.discordapp.net/external/ak_l1cuKUfVU-MUEGo57iF5_ELEZKbHFkdKUmpW1dEE/https/media.discordapp.net/attachments/756024207883894814/887514851356835880/886660055439650897.png", "https://cdn.discordapp.com/emojis/899508099977719888.png")))


def setup(client):
	client.add_cog(Commands(client))
