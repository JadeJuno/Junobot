import random

import discord
import googletrans
from discord.ext import commands
from googletrans import Translator

import bot
from config import parse_config

config = parse_config("./config.toml")


def is_in_command(ctx):
	return ctx.channel.id == 843834879736283156 or ctx.author.id in config["origins_mods"]


class Commands(commands.Cog):
	def __init__(self, client):
		self.activity = None
		self.client = client
		self.log = None
		self.loop_interval = None
		self.my_guild = None
		self.translator = Translator()
		self.lang_dict = googletrans.LANGUAGES
		self.emoji_list = None

	@commands.check(bot.is_origin_mod)
	@commands.command()
	async def sleep(self, ctx):
		serious = self.client.get_emoji(821796259333537813)
		await ctx.send(f"Golder!! Go to sleep! {serious}")

	@commands.check(bot.is_in_origin_server)
	@commands.command()
	async def datapacks(self, ctx):
		await bot.tryreply(ctx,
						   'If you want to find datapacks with custom origins.py, balance changes, and recipes for the Orb of Origin to use, check out <#749571272635187342>.\n\nTo install a datapack, navigate to your world folder (found in `.minecraft/saves`) and drop the datapack as a ZIP file into the `datapacks` folder. The same process can be used on a server (the world folder would be on the root though), and if you are running a server. the datapack does *not* need to be installed by each user.\n\nWhen creating a single-player world, there is also a "Data Packs" button in the world creation screen. If you click this, you are able to drag datapacks directly into the Minecraft window to add them. Don\'t forget to move them from "available" to "selected" though. This allows you to install datapacks *before* a world is generated!\n\nIf you are looking for information on how to create datapacks yourself, type `!wiki` or `!tutorial` in <#843834879736283156>.')

	@commands.check(bot.is_in_origin_server)
	@commands.command(name="<#843834879736283156>", aliases=('commands',))
	async def ch_commands(self, ctx):
		if ctx.channel.id != 843834879736283156:
			serious = self.client.get_emoji(821796259333537813)
			await bot.tryreply(ctx,
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
	@commands.command(aliases=("ideasonly", "mediaonly", "suggestionsonly", "suggestiononly", "powersonly"))
	async def channelonly(self, ctx):
		replies = {
			825449766384828476: "This channel is only for posting powers that can be used by other people. For discussion about the powers listed in this channel, please go to <#802622603008409600>. If you need help related to the powers listed in here, please go to <#810587422303584286> by making a thread.",
			798545973554315304: "This channel is only for posting ideas for an origin. For discussion about the origins.py listed in this channel, please go to <#802622603008409600> or make a thread.",
			813795300691017798: "This channel is for posting media of your Origins only! If you wanted to comment on a video you found interesting, then please do so in <#756024207883894814>, <#802622603008409600>, or by making a thread.",
			734133482757816401: "This channel is only for posting suggestions for the Origins mod. If you want to suggest an idea for an origin, do so in <#798545973554315304>. If you wanna comment about a suggestion, create a thread for that.",
			826144339041976321: "This channel is only for posting suggestions for the wiki of the Origins mod. If you want to suggest ideas for the Origins mod, do so in <#734133482757816401>, and if you wanna comment about a suggestion, create a thread for that."}

		await bot.tryreply(ctx, replies[ctx.channel.id])

		"""
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
		"""

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
		await ctx.send(random.choice((
									 "https://images-ext-2.discordapp.net/external/ak_l1cuKUfVU-MUEGo57iF5_ELEZKbHFkdKUmpW1dEE/https/media.discordapp.net/attachments/756024207883894814/887514851356835880/886660055439650897.png",
									 "https://cdn.discordapp.com/emojis/899508099977719888.png")))

	@commands.check(bot.is_in_origin_server)
	@commands.command(aliases=('tag',))
	async def tags(self, ctx, _type):
		match _type.lower():
			case ('entity types' | 'entity_types' | 'entity type' | 'entity_type'):
				await bot.tryreply(ctx, 'An entity type tag is a JSON file used for grouping entities. It\'s stored inside the `data/<namespace>/tags/entity_types` folder, where `<namespace>` is the folder you\'re using to store your advancements, functions, loot tables, powers, origins, etc.\n\nHere\'s an example of an entity type tag, named `undead.json`, stored inside the `data/example/tags/entity_types` folder:\n```json\n{\n    "values": [\n        "minecraft:drowned",\n        "minecraft:zombie",\n        "minecraft:husk",\n        "minecraft:zombie_villager",\n        "minecraft:skeleton",\n        "minecraft:stray",\n        "minecraft:wither",\n        "minecraft:phantom",\n        "minecraft:skeleton_horse",\n        "minecraft:zombified_piglin",\n        "minecraft:drowned"\n    ]\n}\n```\n\nYou can then reference the `example:undead` entity type tag inside an entity condition, like `origins:in_tag` or the `type` target selector argument, like so:\nexecute as @e[type = #example:undead] ...\n```json\n"entity_condition": {\n    "type": "origins:in_tag",\n    "tag": "example:undead"\n}\n```', reply=True)
			case ('block' | 'blocks'):
				await ctx.send()

def setup(client):
	client.add_cog(Commands(client))
