import os
import re

import googlesearch
import oxford
import wikipedia
from discord.ext import commands
from discord.utils import escape_markdown

from libs import botutils, urban


class Information(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.oxford = oxford.AsyncClient(os.getenv('DICT_ID'), os.getenv('DICT_TOKEN'))
		botutils.log("Information Cog ready!")

	@commands.command(
		aliases=('definition', 'define'),
		description='Get the definition of a word.',
		extras={
			'example': 'auric'
		}
	)
	async def dictionary(self, ctx: commands.Context, *, query: str):
		error_embed = await botutils.error_template(ctx, f'Definition for "{query.title()}" not found.', send=False)

		message = await ctx.send("Getting definition...")
		try:
			definitions = await self.oxford.define(query)
			emb = botutils.embed_template(
				title=f'Definition of "{query.title()}":', description=definitions[0].capitalize(),
				footer='Powered by Oxford Dictionary'
			)
		except oxford.Exceptions.WordNotFoundException:
			emb = error_embed

		await message.edit(content=None, embed=emb)

	@commands.command(
		aliases=("googleit", "googlesearch", "search"),
		description="Make a quick Google Search from Discord because you're too lazy to open your browser.",
		extras={
			"signature": "<Query>",
			"example":   'How to perform a Google Search from Discord'
		}
	)
	async def google(self, ctx: commands.Context, *, search_request: str):
		message = await ctx.send(f"Searching for `{search_request}`...")
		async with ctx.typing():
			results = []
			search_results = googlesearch.search(search_request, advanced=True)
			for i, result in enumerate(search_results, start=1):
				if i <= 10:
					results.append(f"`{i}.`\t**[{escape_markdown(result.title)}](<{result.url}>)**")

			output_str = '\n'.join(results)
			if not output_str:
				output_str = "**No results found.**"
			embed = botutils.embed_template("Google", output_str,
			                                icon="https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/1200px-Google_%22G%22_Logo.svg.png")
		await message.edit(content=None, embed=embed)
		try:
			os.remove(".google-cookie")
		except FileNotFoundError:
			pass

	@commands.command(
		description="Searches a Wikipedia page with your search request.",
		extras={
			'example': 'gold'
		}
	)
	async def wikipedia(self, ctx: commands.Context, *, search_request: str):
		message = await ctx.send(f"Searching for {search_request}")
		async with ctx.typing():
			description = ""
			image = "https://i.imgur.com/7kT1Ydo.png"

			try:
				result = wikipedia.page(search_request)
				description = f"**[{result.title}]({result.url})**\n{result.summary[:300].strip()}..."

				try:
					image = result.images[0]
				except IndexError:
					pass

			except wikipedia.exceptions.DisambiguationError as e:
				image = None
				i = 1
				for option in e.options:
					try:
						disamb_result = wikipedia.page(option)
						if disamb_result.url != "":
							result = f"[{disamb_result.title}]({disamb_result.url})"
						else:
							result = f"~~{disamb_result}~~ **URL Not Found**"

					except wikipedia.exceptions.PageError:
						continue
					except wikipedia.exceptions.DisambiguationError:
						continue
					description += f"`{i}`: {result}\n"
					if i >= 10:
						break
					i += 1
			except wikipedia.exceptions.PageError:
				description = "Page not found."
			embed = botutils.embed_template("Wikipedia", description, image=image,
			                                icon="https://i.imgur.com/FD1pauH.png")
		await message.edit(content=None, embed=embed)

	@commands.command(
		description="Makes a search on Urban Dictionary.",
		aliases=("urbandictionary",),
		extras={
			"example": "Noob"
		}
	)
	async def urban(self, ctx: commands.Context, *, query: str):
		pattern = re.compile("\[(.*?)]")
		async with ctx.typing():
			urban_definition = urban.define(query)
			try:
				urban_definition = urban_definition[0]
			except IndexError:
				await botutils.error_template(ctx, f'No definition found for "{query}"')
				return

			definition = urban_definition.definition.split(" ")
			if len(definition) > 70:
				definition = " ".join(definition[:70]) + " (...)"
			else:
				definition = " ".join(definition)

			example = urban_definition.example.split(" ")
			if len(example) > 70:
				example = " ".join(example[:70]) + " (...)"
			else:
				example = " ".join(example)

			hypertexts = re.findall(pattern, definition)
			hypertexts.extend(re.findall(pattern, example))
			hypertexts = {text: urban.define(text)[0].permalink for text in hypertexts}

			# Adds hypertexts to the definition and example strings. I.E. "[Text](http://notarealurldonotclick.hi)"
			definition = re.sub(pattern, lambda x: f"{x.group()}({hypertexts[x.group(1)]})", definition)
			example = re.sub(pattern, lambda x: f"{x.group()}({hypertexts[x.group(1)]})", example)

			embed = botutils.embed_template(title=f'Definition for "{urban_definition.word}"',
			                                description=f"{definition}\n",
			                                footer="Powered by Urban Dictionary")
			if example:
				embed.add_field(name="Example:", value=f">>> {example}", inline=False)

			embed.url = urban_definition.permalink

		await ctx.send(embed=embed)


async def setup(bot):
	await bot.add_cog(Information(bot), override=True)
