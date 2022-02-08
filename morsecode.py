# Dictionary representing the morse code chart
MORSE_CODE_DICT = {'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
				   'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
				   'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
				   'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
				   '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----', ', ': '--..--', '.': '.-.-.-',
				   '?': '..--..', '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-', ',': '--..--'}
letters = MORSE_CODE_DICT.keys()
morse_letters = MORSE_CODE_DICT.values()


class MorseCode:
	@staticmethod
	def check_letter(message):
		i = False
		for letter in message:
			for key in letters:
				if letter == key:
					i = True
			for value in morse_letters:
				if letter == value:
					i = True
		return i

	@staticmethod
	def encrypt(message):
		my_cipher = ''
		for myletter in message:
			if myletter != ' ':
				my_cipher += MORSE_CODE_DICT[myletter] + ' '
			else:
				my_cipher += '/ '
		return my_cipher

	# This function is used to decrypt
	# Morse code to English
	@staticmethod
	def decrypt(message):
		i = None
		decipher = ''
		mycitext = ''
		for myletter in message:
			# checks for space
			if myletter != ' ':
				if myletter == "/":
					decipher += ' '
					i = True
				else:
					mycitext += myletter
					i = False
			elif myletter == " " and i is not True:
				decipher += list(MORSE_CODE_DICT.keys())[list(MORSE_CODE_DICT.values()).index(mycitext)]
				mycitext = ''
				i = False
		return decipher


morse = MorseCode()


def main():
	my_message = '"'
	output = morse.encrypt(my_message.upper())
	print(output)
	my_message = ".... . .-.. .-.. --- --..-- / - .... .. ... / .. ... / -- --- .-. ... . / -.-. --- -.. . "
	output = morse.decrypt(my_message)
	print(output)


# Executes the main function
if __name__ == '__main__':
	main()
