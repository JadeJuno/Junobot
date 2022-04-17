import json
import os
import pathlib
import re
import shutil
import zipfile

import discord
from discord.ext import commands


class Origins(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.command()
	async def unchoosable(self, ctx, namespace, name, pack_format=8):
		pattern = re.compile('[^a-z0-9_.\-/]')
		if re.search(pattern, namespace) or re.search(pattern, name):
			await ctx.send(
				"Error: Identifier has non [a-z0-9_.-] character in it (In layman's terms: *there's a character that isn't a lowercase leter, a number, an underscore, a hyphen or a period on the ID.*).")
			return
		unchoosable_obj = {
			"unchoosable": True,
			"loading_priority": 2147483647
		}
		directory = f'datapacks/Disable_{name.title()}'
		os.makedirs(f'{directory}/data/{namespace}/origins/')
		with open(f'{directory}/data/{namespace}/origins/{name}.json', 'w') as f:
			json.dump(unchoosable_obj, f, indent='\t')
		with open(f'{directory}/pack.mcmeta', 'w') as metadata:
			meta_obj = {
				"pack": {
					"pack_format": pack_format,
					"description": f"Disables {name.title()}."
				}
			}
			json.dump(meta_obj, metadata, indent='\t')

		with pathlib.Path(directory) as root:
			with zipfile.ZipFile(f'{directory}.zip', 'w') as z:
				for child in root.rglob('*'):
					z.write(child, arcname=str(child).replace(directory, ''))

		await ctx.send(f'"Unchoosable_{name.title()}" is ready.', file=discord.File(fp=f'{directory}.zip'))
		shutil.rmtree(directory)
		os.remove(f'{directory}.zip')


async def setup(bot):
	await bot.add_cog(Origins(bot), override=True)
