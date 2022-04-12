import discord
import googletrans
import wikipedia
from discord.ext import commands
from googletrans import Translator
from iso639 import languages

import botutilities
import googlesearch
from oxforddict import get_definition


class Information(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.translator = Translator()
		self.lang_dict = googletrans.LANGUAGES

	async def cog_load(self):
		print("Information Cog ready!")

	@staticmethod
	def get_dict_key(dictionary, value):
		key_list = list(dictionary.keys())
		value_list = list(dictionary.values())
		for listed_value in value_list:
			if listed_value == value:
				return key_list[value_list.index(value)]
		return value

	@commands.command(
		aliases=('definition', 'define'),
		description='G',
		extras={
			'example': 'auric'
		}
	)
	async def dictionary(self, ctx, *, query):
		error_embed = botutilities.error_template(ctx, f'Definition for "{query.title()}" not found.', send=False)
		message = await ctx.send("Getting definition...")
		results = get_definition(query)
		if results != "404 Error":
			lex_entries = results["lexicalEntries"]
			try:
				entries = [lex_entry["entries"] for lex_entry in lex_entries]
			except KeyError:
				emb = error_embed
			else:
				entries = [x for y in entries for x in y]
				senses = [entry["senses"] for entry in entries]
				senses = [x for y in senses for x in y]
				definitions = [definition['definitions'][0] for definition in senses]

				emb = botutilities.embed_template(
					title=f'Definition of "{query.title()}":',
					description=f"{definitions[0].capitalize()}",
					footer='Powered by Oxford Dictionary'
				)
		else:
			emb = error_embed

		await message.edit(content="", embed=emb)

	@commands.command(
		aliases=("googleit", "googlesearch", "search"),
		description="Make a quick Google Search from Discord because you're too lazy to open your browser.",
		extras={
			"signature": "<search>",
			"example": 'How to perform a Google Search from Discord'
		}
	)
	async def google(self, ctx, *, search_request):
		message = await ctx.send(f"Searching for `{search_request}`...")
		async with ctx.typing():
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
			embed = botutilities.embed_template("Google", output_str[0:-1],
												icon="https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/1200px-Google_%22G%22_Logo.svg.png")
		return await message.edit(content=None, embed=embed)

	@commands.command(
		name="language",
		aliases=("detect",),
		description='Detects the language of a quoted sentence.',
		extras={
			"example": "Hola, mi nombre es Gøldbot y soy español"
		}
	)
	async def lang_detect(self, ctx, *, sentence):
		detected_lang = self.translator.detect(sentence).lang
		if isinstance(detected_lang, list):
			detected_lang = detected_lang[self.translator.detect(sentence).confidence.index(
				max(self.translator.detect(sentence).confidence))]
		await ctx.send(
			f'"{sentence}" is in {languages.get(alpha2=detected_lang).name} (Certainty: `{int(max(self.translator.detect(sentence).confidence) * 100)}%`).')

	@commands.command(
		description='Translates a sentence surrounded by quotation marks.',
		extras={
			'signature': '"<Sentence>" [Destination Language] [Source Language]',
			'example': '"Hola, ¿como estás?" japanese spanish'
		}
	)
	async def translate(self, ctx, translate_message, destination_language='en', source_language=None):
		destination_language = destination_language.lower()
		destination_language = self.get_dict_key(self.lang_dict, destination_language)
		if source_language is not None:
			source_language = source_language.lower()
			source_language = self.get_dict_key(self.lang_dict, source_language)
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
			await botutilities.error_template(ctx, "Invalid language.")

	@commands.command(
		description="Searches a Wikipedia page with your search request.",
		extras={
			'example': 'gold'
		}
	)
	async def wikipedia(self, ctx, *, search_request):
		message = await ctx.send(f"Searching for {search_request}")
		async with ctx.typing():
			title = "Wikipedia"
			description = ""
			image = "https://i.imgur.com/7kT1Ydo.png"
			try:
				result = wikipedia.page(search_request)
				# update: didn't go that bad, but it wasn't "well lol"
				# Future Golder here: WTF does this comment mean????
				description = f"[{result.title}]({result.url})\n{result.summary[:300].strip()}..."
				try:
					image = result.images[0]
				except IndexError:
					pass
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
			embed = botutilities.embed_template(title, description, image=image,
												icon="https://i.imgur.com/FD1pauH.png")
		await message.edit(content=None, embed=embed)


async def setup(bot):
	await bot.add_cog(Information(bot), override=True)
