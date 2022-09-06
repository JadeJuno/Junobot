import io
import json
import os
import pathlib
import re
import shutil
import zipfile
from gzip import BadGzipFile

import discord
from discord.ext import commands
from nbt import nbt

import botutils
from nbt_lib import nbt_to_condition


class Origins(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		botutils.log("Origins Cog Ready!")

	@commands.command(
		aliases=('disable',),
		description="Generates a datapack that disables the origin with the specified ID.",
		extras={"example": "extraorigins inchling 9"}
	)
	async def unchoosable(self, ctx, namespace, name, pack_format=10):
		pattern = re.compile('[^a-z\d_.\-/]')
		if re.search(pattern, namespace) or re.search(pattern, name):
			await botutils.error_template(ctx, "Identifier has non `[a-z0-9_.-]` character in it (In layman's terms: there's a character that isn't a lowercase letter, a number, an underscore, a hyphen or a period on the ID.).")
			return
		filename = f"Disable_{name.title()}"
		unchoosable_obj = {
			"unchoosable": True,
			"loading_priority": 2147483647
		}
		directory = f'datapacks/{filename}'
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

		await ctx.send(f'"{filename}" is ready.', file=discord.File(fp=f'{directory}.zip'))
		shutil.rmtree(directory)
		os.remove(f'{directory}.zip')

	@commands.command(
		description="Automatically turns a Structure NBT file into a Block Condition object.\n\nThe 'Center' argument is the coordinates of the center of the block condition in the structure. I recommend using the [NBT Viewer](https://marketplace.visualstudio.com/items?itemName=Misodee.vscode-nbt) extension for Visual Studio Code to visualize that more easily.",
		extras={"example": "5 4 5", "signature": "[Center=0 0 0]"}
	)
	async def structure(self, ctx: commands.Context, file: discord.Attachment, x: int = 0, y: int = 0, z: int = 0):
		valid_nbt = True
		center = (x, y, z)

		file = await file.to_file()
		if not file.filename.endswith('.nbt'):
			valid_nbt = False

		center = center[:3]
		try:
			structure = nbt.NBTFile(fileobj=file.fp)
		except BadGzipFile:
			valid_nbt = False
		else:
			if 'size' not in structure:
				valid_nbt = False

		if not valid_nbt:
			await botutils.error_template(ctx, "Attached file is not an NBT file.")
			return

		size = [val.value for val in structure['size']]
		for size_val, center_coord in zip(size, center):
			if center_coord > size_val:
				await botutils.error_template(ctx, "The center's coordinates are outside of the structure.")
				return

		condition = nbt_to_condition(center, structure)

		with io.StringIO(json.dumps(condition, indent='\t')) as f:
			attachment = discord.File(f, filename=f"{file.filename}.json")
		await ctx.send("Done! Remember that the result is **not a power nor an entity condition, but a block condition!** You'll have to put this condition yourself on whatever power you want.", file=attachment)


async def setup(bot):
	await bot.add_cog(Origins(bot), override=True)
