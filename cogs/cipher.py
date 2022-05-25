import re

from discord.ext import commands

import botutils
import morsecode


class Ciphering(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		botutils.log("Ciphering Cog ready!")

	@commands.command(
		name="morse",
		aliases=("morsecode",),
		description="Encrypts a sentence to morse code or decrypts it to English.",
		extras={
			'signature': '<Encrypt/Decrypt> <Sentence>',
			'example': "decrypt .... . .-.. .-.. --- --..-- / - .... .. ... / .. ... / -- --- .-. ... . / -.-. --- -.. ."
		}
	)
	async def morse_code(self, ctx, encrypt_decrypt: typing.Annotated[str, lambda s: s.lower()], *, sentence: typing.Annotated[str, lambda s: s.upper()]):
		if encrypt_decrypt not in ('encrypt', 'decrypt'):
			await botutils.error_template(ctx, "The argument 'Encrypt/Decrypt', as its name suggests, can only take 'encrypt' or 'decrypt'.")
			return
		if not morsecode.check_letter(sentence):
			await botutils.error_template(ctx, "Invalid character detected.")
			return

		sentence += " "
		if encrypt_decrypt == "encrypt":
			try:
				sentence = sentence[:-1]
				output = morsecode.encrypt(sentence).capitalize()
				await ctx.send(f"Here's your encrypted message: {output}")
			except KeyError:
				await botutils.error_template(ctx, "Your message has a character that isn't translatable to International Morse Code.")
				return

		else:
			sentence = sentence.replace('_', '-')
			try:
				output = morsecode.decrypt(sentence).capitalize()
				await ctx.send(f"Here's your decrypted Morse: {output}")
			except ValueError:
				await botutils.error_template(ctx, f"You tried to decrypt normal text as Morse Code.\n*(If you believe this error message is wrong, please send a bug report to my creator via `{ctx.clean_prefix}report`.)*")
				return

	# Long-ass example :weary:
	@commands.command(
		description="Converts text to a binary string and viceversa",
		extras={
			'signature': '<Encode/Decode> <Sentence>',
			'example': 'decode 01001000 01101001 00101100 00100000 01001001 00100111 01101101 00100000 01000111 11111000 01101100 01100100 01100010 01101111 01110100 00100000 01100001 01101110 01100100 00100000 01001001 00100111 01101101 00100000 01110011 01100101 01101110 01110100 01101001 01100101 01101110 01110100 00100000 00111101 00101001',
			'encode_decode': 'Encode/Decode'
		}
	)
	async def binary(self, ctx, encode_decode: typing.Annotated[str, lambda s: s.lower()], *, sentence):
		if encode_decode not in ('encode', 'decode'):
			await botutils.error_template(ctx, "The argument 'Encode/Decode', as its name suggests, can only take 'encode' or 'decode'.")
			return

		if encode_decode == "encode":
			s = ''.join(format(ord(i), '08b') for x, i in enumerate(sentence))
			bin_list = [s[i:i + 8] for i in range(0, len(s), 8)]
			output = ' '.join(bin_list)
			await ctx.send(f"Here's your encoded string: \n`{output}`")

		elif encode_decode == 'decode':
			if re.search("[^01 ]", sentence):
				await ctx.send("Please only use 1s and 0s.")
				return

			try:
				int(sentence)
			except ValueError:
				bin_list = sentence.split()
			else:
				bin_list = [sentence[i:i+8] for i in range(len(sentence), 8)]
			for _bin in bin_list:
				if len(_bin) < 8:
					await botutils.error_template(ctx, "Unknown Error... If you can fix this mess, please contact my creator at Golder06#7041, or make a Pull Request at <https://github.com/Golder06/Goldbot>")
					return
			bin_list = [chr(int(_bin, 2)) for _bin in bin_list]

			output = ''.join(bin_list)
			await ctx.send(f"Here's your decoded binary code: \n`{output}`")


async def setup(bot: commands.Bot):
	await bot.add_cog(Ciphering(bot), override=True)
