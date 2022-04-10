import re

from discord.ext import commands

import morsecode


class Ciphering(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def cog_load(self):
		print("Ciphering Cog ready!")

	@commands.command(
		name="morse",
		aliases=("morsecode",),
		description="Encrypts a sentence to morse code or decrypts it to English.",
		extras={
			'signature': '<encrypt/decrypt> <sentence>',
			'example': "decrypt .... . .-.. .-.. --- --..-- / - .... .. ... / .. ... / -- --- .-. ... . / -.-. --- -.. ."
		}
	)
	async def morse_code(self, ctx, encrypt_decrypt, *, sentence):
		var = morsecode.check_letter(sentence.upper())
		if not var:
			await ctx.send("Error: Invalid character detected.")
			return
		sentence += " "
		error_message = f"Error: You tried to {encrypt_decrypt} an already {encrypt_decrypt}ed message or you entered an invalid character."
		if encrypt_decrypt == "encrypt":
			try:
				sentence = sentence[0:-1]
				output = morsecode.encrypt(sentence.upper())
			except KeyError:
				output = error_message
			except Exception as e:
				print(e)
				return
		elif encrypt_decrypt == "decrypt":
			sentence = sentence.replace('_', '-')
			try:
				output = morsecode.decrypt(sentence).lower()
			except ValueError:
				output = error_message
		else:
			output = "Error: Invalid discriminator."
		await ctx.send(output.capitalize())

	# Long-ass example :weary:
	@commands.command(
		description="Converts text to binary code and viceversa",
		extras={
			'signature': '<encode/decode> <sentence>',
			'example': "decode 01001000 01101001 00101100 00100000 01001001 00100111 01101101 00100000 01000111 11111000 01101100 01100100 01100010 01101111 01110100 00100000 01100001 01101110 01100100 00100000 01001001 00100111 01101101 00100000 01110011 01100101 01101110 01110100 01101001 01100101 01101110 01110100 00100000 00111101 00101001"
		}
	)
	async def binary(self, ctx, encode_decode: str, *, sentence):
		if encode_decode.lower() == "encode":
			s = ''.join(format(ord(i), '08b') for x, i in enumerate(sentence))
			bin_list = [s[i:i + 8] for i in range(0, len(s), 8)]
			output = ''
			for _bin in bin_list:
				output += f'{_bin} '
			output = output[:-1]
			await ctx.send(f"Here's your encoded string: \n`{output}`")
		elif encode_decode.lower() == 'decode':
			if re.search("[^01 ]", sentence):
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
			await ctx.send(f"Here's your decoded binary code: \n`{output}`")
			return
		else:
			await ctx.send('ERROR: Invalid discriminator.')
			return


async def setup(bot: commands.Bot):
	await bot.add_cog(Ciphering(bot), override=True)
