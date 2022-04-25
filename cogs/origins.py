import io
import json
import os
import pathlib
import re
import shutil
import zipfile

import discord
from discord.ext import commands
from nbt import nbt

import nbt_lib
from botutilities import error_template


class Origins(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.command(
		aliases=('disable',),
		description="Generates a datapack that disables the origin with the specified ID.",
		extras={"example": "extraorigins inchling 9"}
	)
	async def unchoosable(self, ctx, namespace, name, pack_format=9):
		pattern = re.compile('[^a-z\d_.\-/]')
		if re.search(pattern, namespace) or re.search(pattern, name):
			await error_template(ctx, "Identifier has non [a-z0-9_.-] character in it (In layman's terms: *there's a character that isn't a lowercase leter, a number, an underscore, a hyphen or a period on the ID.*).")
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

		await ctx.send(f'"Disable {name.title()}" is ready.', file=discord.File(fp=f'{directory}.zip'))
		shutil.rmtree(directory)
		os.remove(f'{directory}.zip')

	@commands.command(
		description="Automatically takes a Structure NBT file into a Block Condition object.",
		extras={"example": ""}
	)
	async def structure(self, ctx: commands.Context, x: int = 0, y: int = 0, z: int = 0):
		center = (x, y, z)

		if len(ctx.message.attachments) == 0:
			await error_template(ctx, "No file was attached.")
			return
		file = await ctx.message.attachments[0].to_file()
		if not file.filename.endswith('.nbt'):
			await error_template(ctx, "Attached file is not an NBT file.")
			return

		center = center[:3]
		structure = nbt.NBTFile(fileobj=file.fp)

		size = [val.value for val in structure['size']]
		for size_val, center_coord in zip(size, center):
			if center_coord > size_val:
				await error_template(ctx, "The center's coordinates are outside of the scructure.")
				return

		condition = nbt_lib.main(center, structure)

		with io.StringIO() as f:
			json.dump(condition, f, indent='\t')
			f.seek(0)
			attachment = discord.File(f, filename=f"{file.filename}.json")
		await ctx.send("Done! Remember that the result is **not a power nor an entity condition, but a block condition!** You'll have to put this condition yourself on whatever ower you want.", file=attachment)


async def setup(bot):
	await bot.add_cog(Origins(bot), override=True)
