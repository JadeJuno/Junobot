import difflib
import discord
import json
import prefix
import random
import time
import wikipedia
from discord.ext import commands, tasks
from googlesearch import search
from googletrans import Translator
from morsecode import MorseCode


status_list = ['Default prefix is "g!"', "If something's wrong with the bot, contact Gølder06#7041", 'To see my commands, type "g!help"'] # ["End my suffering.", 'Hekoru killed me.']

lang_dict = {'af': 'afrikaans', 'sq': 'albanian', 'am': 'amharic', 'ar': 'arabic', 'hy': 'armenian', 'az': 'azerbaijani', 'eu': 'basque', 'be': 'belarusian', 'bn': 'bengali', 'bs': 'bosnian', 'bg': 'bulgarian', 'ca': 'catalan', 'ceb': 'cebuano', 'ny': 'chichewa', 'zh-cn': 'chinese (simplified)', 'zh-tw': 'chinese (traditional)', 'co': 'corsican', 'hr': 'croatian', 'cs': 'czech', 'da': 'danish', 'nl': 'dutch', 'en': 'english', 'eo': 'esperanto', 'et': 'estonian', 'tl': 'filipino', 'fi': 'finnish', 'fr': 'french', 'fy': 'frisian', 'gl': 'galician', 'ka': 'georgian', 'de': 'german', 'el': 'greek', 'gu': 'gujarati', 'ht': 'haitian creole', 'ha': 'hausa', 'haw': 'hawaiian', 'iw': 'hebrew', 'hi': 'hindi', 'hmn': 'hmong', 'hu': 'hungarian', 'is': 'icelandic', 'ig': 'igbo', 'id': 'indonesian', 'ga': 'irish', 'it': 'italian', 'ja': 'japanese', 'jw': 'javanese', 'kn': 'kannada', 'kk': 'kazakh', 'km': 'khmer', 'ko': 'korean', 'ku': 'kurdish (kurmanji)', 'ky': 'kyrgyz', 'lo': 'lao', 'la': 'latin', 'lv': 'latvian', 'lt': 'lithuanian', 'lb': 'luxembourgish', 'mk': 'macedonian', 'mg': 'malagasy', 'ms': 'malay', 'ml': 'malayalam', 'mt': 'maltese', 'mi': 'maori', 'mr': 'marathi', 'mn': 'mongolian', 'my': 'myanmar (burmese)', 'ne': 'nepali', 'no': 'norwegian', 'ps': 'pashto', 'fa': 'persian', 'pl': 'polish', 'pt': 'portuguese', 'pa': 'punjabi', 'ro': 'romanian', 'ru': 'russian', 'sm': 'samoan', 'gd': 'scots gaelic', 'sr': 'serbian', 'st': 'sesotho', 'sn': 'shona', 'sd': 'sindhi', 'si': 'sinhala', 'sk': 'slovak', 'sl': 'slovenian', 'so': 'somali', 'es': 'spanish', 'su': 'sundanese', 'sw': 'swahili', 'sv': 'swedish', 'tg': 'tajik', 'ta': 'tamil', 'te': 'telugu', 'th': 'thai', 'tr': 'turkish', 'uk': 'ukrainian', 'ur': 'urdu', 'uz': 'uzbek', 'vi': 'vietnamese', 'cy': 'welsh', 'xh': 'xhosa', 'yi': 'yiddish', 'yo': 'yoruba', 'zu': 'zulu', 'he': 'Hebrew'}

command_list = ["8ball", "choose", "flip", "coinflip", "flipcoin", "roll", "rolldie", "dieroll", "say", "help", "google", "googleit", "googlesearch", "language", "detect", "morsecode", "morse", "ping", "translate", "wikipedia", "ban", "clear", "kick", "prefix", "unban", ""]

change_loop_interval = random.randint(1, 60)

abbrev_lang_list = list(lang_dict.keys())
full_lang_list = list(lang_dict.values())

def get_dict_key(dictionary, value):
	key_list = list(dictionary.keys())
	value_list = list(dictionary.values())
	for listed_value in value_list:
		if listed_value == value:
			return key_list[value_list.index(value)]
	return value


def is_bot_owner(ctx):
	return ctx.author.id == 498606108836102164 or ctx.author == 503657339258273812

class Commands(commands.Cog):

	def __init__(self, client):
		self.activity = random.choice(status_list)
		self.client = client
		self.log = None
		self.loop_interval = None
		self.morse = MorseCode()
		self.owner = None
		self.translator = Translator()

	@tasks.loop(minutes=change_loop_interval)
	async def change_status_task(self):
		global change_loop_interval
		self.activity = random.choice(status_list)
		await self.client.change_presence(activity=discord.Game(self.activity))
		print(f'Status changed to "{self.activity}"')
		change_loop_interval = random.randint(15, 60)
		print(f"Next status change in {change_loop_interval} minutes.")

	@commands.Cog.listener()
	async def on_ready(self):
		self.log = self.client.get_channel(751555878385221705)
		self.owner = self.client.get_user(498606108836102164)
		await self.client.change_presence(status=discord.Status.online, activity=discord.Game(self.activity))
		print(f'Bot is ready with status "{self.activity}"')
		print(f"bot created by {self.owner.name}")
		self.log = self.client.get_channel(751555878385221705)
		self.change_status_task.start()
		await self.log.send("Bot Started.")
	
	@commands.Cog.listener()
	async def on_command(self, ctx):
		my_guild = self.client.get_guild(574480926189420555)
		if ctx.message.channel.guild != my_guild:
			await self.log.send(f"{ctx.message.channel.guild.name}:\n{ctx.message.author}: {ctx.message.content}")
			print(f"{ctx.message.channel.guild.name}:\n{ctx.message.author}: {ctx.message.content}")

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		if isinstance(error, commands.CommandNotFound):
			command = ctx.message.content.lstrip(ctx.prefix).split(" ")
			command = command[0]
			for com in command_list:
				similarity = difflib.SequenceMatcher(None, command, com).ratio()
				if similarity >= 0.6:
					await ctx.send(f"That command doesn't exist. Did you mean `{ctx.prefix}{com}`?")
		elif isinstance(error, commands.CheckFailure):
			await ctx.send("You don't have permissions to use that command.")
		elif isinstance(error, commands.MissingRequiredArgument):
			await ctx.send(f"Missing argument! `{error.param.name}`")

	@commands.command(aliases=['8ball'])
	async def _8ball(self, ctx, *, question):
		ball_responses = ["It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.", "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.", "All signs point to yes.", "Reply hazy, try again.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful."]
		await ctx.send(f'Question: {question}\n:8ball: Answer: {random.choice(ball_responses)}')

	@commands.command()
	async def choose(self, ctx, *, options):
		divided_options = options.split(",")
		if len(divided_options) >= 2:
			for option in divided_options:
				if option == False:
					divided_options.pop(option)
			await ctx.send(f'Gøldbot chooses: `{random.choice(divided_options).strip()}`')
		else:
			await ctx.send('I can\'t just choose between one choice. *(to divide the choices you can put a comma between them)*')

	@commands.command(aliases=["coinflip", "flipcoin"])
	async def flip(self, ctx):
		await ctx.send(f"-Flip!-\nIt landed on {random.choice(['heads', 'tails'])}!")

	@commands.command(aliases=["rolldie", "dieroll"])
	async def roll(self, ctx, faces=6):
		if faces > 2:
			try:
				faces = int(faces)
			except ValueError:
				await ctx.send("Error: You can't roll a die with a non-number amount of faces...")
			await ctx.send(f"Rolled a d{faces}.\nIt landed on `{random.randint(1, faces)}`!")
		elif faces == 2:
			await ctx.send(f"... A 2 sided die is a coin... Use the {ctx.prefix}flip command.")
		elif faces <= 1:
			await ctx.send("... You serious?")

	@commands.command()
	async def say(self, ctx, *, user_message):
		await discord.Message.delete(ctx.message, delay=0)
		await ctx.send(user_message)
		
	@commands.command()
	async def alias(self, ctx, command=None):
		alias_command_list = ["language", "morse", "morsecode", "detect", "google", "googleit", "googlesearch", "dieroll", "roll", "rolldie", "coinflip", "flip", "flipcoin"]
		title = ""
		i = None
		value = random.randint(0, 0xffffff)
		
		if command is None:
			title = "Commands"
			with open("Help/Aliases/General.txt") as f:
				alias_text = f.read()
		else:
			for com in alias_command_list:
				if com == command:
					i = True
					break
			if i == True:
				title = command.capitalize()
				with open(f"Help/Aliases/{command}.txt") as f:
					alias_text = f.read()
			else:
				title = "Error"
				alias_text = "Command alias not found"

		embed = discord.Embed(description=alias_text)
		embed.set_author(name=title)
		embed.set_footer(text=f"\nGøldbot was created by {self.owner.name}.", icon_url="https://i.imgur.com/ZgG8oJn.png")
		embed.colour = value
		await ctx.send(embed=embed)
	
	@commands.command(aliases=["googleit", "googlesearch"])
	async def google(self, ctx, *, search_request):
		message = await ctx.send(f"Searching for `{search_request}`")
		output_str = "**No results found.**"
		i = 1
		for url in search(search_request, stop=10):
			output_str = ""
			if i == 10:
				output_str += f"`{i}.` {url}"
			else:
				output_str += f"`{i}.` {url}\n"
			i += 1
		value = random.randint(0, 0xffffff)
		embed = discord.Embed(description=output_str, color=value)
		embed.set_author(name="Google", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/1200px-Google_%22G%22_Logo.svg.png")
		embed.set_thumbnail(url="https://i.imgur.com/8bOl5gU.png")
		embed.set_footer(text=f"Gøldbot was created by {self.owner.name}", icon_url="https://i.imgur.com/ZgG8oJn.png")
		await message.edit(content=None, embed=embed)

	@commands.command(aliases=["detect", "language"])
	async def lang_detect(self, ctx, *, user_message):
		await ctx.send(f'`{user_message}` is in {lang_dict[self.translator.detect(user_message).lang].capitalize()} (certainty: `{int(self.translator.detect(user_message).confidence*100)}%`)')
	
	@commands.command(aliases=["langlist", "languagelist"])
	async def language_list(self, ctx):
		message = await ctx.send("The language list is quite long, so proceed with caution.")
		time.sleep(2)
		output = ""
		for lang in lang_dict:
			output += f"**{lang_dict[lang]}** *({lang})*\n"
		value = random.randint(0, 0xffffff)
		embed = discord.Embed(description=output, color=value)
		embed.set_author(name="Language List:")
		embed.set_footer(text=f"Gøldbot was created by {self.owner.name}", icon_url="https://i.imgur.com/ZgG8oJn.png")
		await message.edit(content=None, embed=embed)
	
	@commands.command(aliases=["morsecode", "morse"])
	async def morse_code(self, ctx, encrypt_decrypt, *, sentence):
		disc = encrypt_decrypt
		var = self.morse.check_letter(sentence.upper())
		if var == False:
			await ctx.send("Error: Invalid character detected.")
			return
		code = f"{sentence} "
		output = ""
		error_message = f"Error: You tried to {disc} an already {disc}ed message or you entered an invalid character."
		if disc == "encrypt":
			try:
				code = code[0:-1]
				output = self.morse.encrypt(code.upper())
			except KeyError:
				output = error_message
			except Exception as e:
				print(e)
		elif disc == "decrypt":
			try:
				output = self.morse.decrypt(code).lower()
			except ValueError:
				output = error_message
		else:
			output = "Error: Invalid discriminator."
		await ctx.send(output.capitalize())

	@commands.command()
	async def ping(self, ctx):
		await ctx.send(f':ping_pong: Pong!{round(self.client.latency * 1000)}ms.')

	@commands.command()
	async def translate(self, ctx, translate_message, destination_language='en', source_language=None):
		try:
			destination_language = destination_language.lower()
			destination_language = get_dict_key(lang_dict, destination_language)
			if source_language is not None:
				source_language = source_language.lower()
				source_language = get_dict_key(lang_dict, source_language)
			else:
				source_language = self.translator.detect(translate_message).lang
			translated_text = self.translator.translate(translate_message, src=source_language, dest=destination_language).text
			try:
				await ctx.send(f'Translated from {lang_dict[source_language]} to {lang_dict[destination_language]}\n`{translated_text}`.')
			except ValueError:
				await ctx.send(f"Invalid language. You can use the full English name of the language or it's abbreviation *(type `{ctx.prefix}languagelist` for more information)*.")
		except Exception as e:
			await ctx.send(f"An exception has ocurred: {e}")

	@commands.command(aliases=["translatemess"])
	async def translate_mess(self, ctx, translate_message, translate_times:int =5):
		first_time = time.time()
		message = await ctx.send(f"Translating the message {translate_times} times. This might take a while...")
		try:
			translated_message = translate_message
			initial_lang = self.translator.detect(translated_message).lang
			old_rand_lang = initial_lang
			for i in range(translate_times):
				rand_lang = random.choice(abbrev_lang_list)
				translated_message = self.translator.translate(translated_message, src=self.translator.detect(translated_message).lang, dest=rand_lang).text
				# print(f'{i+1}: "{translated_message}" from {old_rand_lang} to {rand_lang}')
				old_rand_lang = rand_lang
			translated_message = self.translator.translate(translated_message, dest=initial_lang).text
			elapsed_time = int((time.time()-first_time)*100)
			elapsed_time = elapsed_time/100
			await message.edit(content=f'"{translated_message}" (Translated {translate_times} times in {elapsed_time} seconds).')
		except Exception as e:
			await message.edit(content=f"ERROR: `{e}`")
	
	@commands.command()
	async def wikipedia(self, ctx):
		await ctx.send("**\**WIP****")

	@commands.has_permissions(manage_messages=True)
	@commands.command()
	async def clear(self, ctx, amount: int):
		await ctx.message.delete()
		await ctx.channel.purge(limit=amount)
		clear_message = await ctx.send(f'Cleared {amount} messages.')
		time.sleep(2)
		await clear_message.delete()

	@commands.has_permissions(kick_members=True)
	@commands.command()
	async def kick(self, ctx, member: discord.Member, *, reason=None):
		await member.kick(reason=reason)
		await ctx.send(f'{member} kicked via {ctx.prefix}kick. Reason: {reason}')

	@commands.has_permissions(ban_members=True)
	@commands.command()
	async def ban(self, ctx, member: discord.Member, *, reason=None):
		await member.ban(reason=reason)
		await ctx.send(f'{member} banned via {ctx.prefix}ban command. Reason: {reason}')
	
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
			await ctx.send(f'{user.mention} is not banned')

	@commands.command()
	async def test(self, ctx):
		gold_emoji = self.client.get_emoji(751859382349856838)
		print("TEST")
		value = random.randint(0, 0xffffff)
		embed = discord.Embed(title="Title", description=f"{gold_emoji}[Test Link](https://www.youtube.com)", color=value, url="https://www.google.com/")
		embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
		embed.set_footer(text=f"*Requested by {ctx.author.name}*", icon_url=ctx.author.avatar_url)
		embed.set_image(url="https://discordpy.readthedocs.io/en/latest/_images/snake.png")
		embed.set_thumbnail(url="https://i.imgur.com/8bOl5gU.png")
		embed.add_field(name="Field 1", value="value 1")
		embed.add_field(name="Field 2", value="value 2")
		embed.add_field(name="Field 3", value="value 3")
		await ctx.send(embed=embed)
		if ctx.author.guild_permissions.administrator == True:
			await ctx.send("You have administrator permissions.")
		try:
			await ctx.send(f"{0/0}")
		except Exception as e:
			error = e
			await ctx.send(f"An exception has ocurred: {e}")

	@commands.command()
	async def trans_test(self, ctx):
		trans_str = "The World is the strongest Stand!"
		length = len(abbrev_lang_list)
		proof = ""
		i = 0
		for lang in abbrev_lang_list:
			try:
				i += 1
				proof += f"{self.translator.translate(trans_str, dest=lang).text}\n"
				print(f"{self.translator.translate(trans_str, dest=lang).text} {lang} ({i}/{length})")
			except exception as e:
				print(f"Error: {e}")
		await ctx.send(f"{i}/{length}")


def setup(client):
	client.add_cog(Commands(client))
