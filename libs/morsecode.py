# Dictionary representing the morse code chart
MORSE_CODE_DICT = {
	'A': '.-',
	'B': '-...',
	'C': '-.-.',
	'D': '-..',
	'E': '.',
	'F': '..-.',
	'G': '--.',
	'H': '....',
	'I': '..',
	'J': '.---',
	'K': '-.-',
	'L': '.-..',
	'M': '--',
	'N': '-.',
	'O': '---',
	'P': '.--.',
	'Q': '--.-',
	'R': '.-.',
	'S': '...',
	'T': '-',
	'U': '..-',
	'V': '...-',
	'W': '.--',
	'X': '-..-',
	'Y': '-.--',
	'Z': '--..',
	'1': '.----',
	'2': '..---',
	'3': '...--',
	'4': '....-',
	'5': '.....',
	'6': '-....',
	'7': '--...',
	'8': '---..',
	'9': '----.',
	'0': '-----',
	', ': '--..--',
	'.': '.-.-.-',
	'?': '..--..',
	'/': '-..-.',
	'-': '-....-',
	'(': '-.--.',
	')': '-.--.-',
	',': '--..--'
}
LETTERS_DICT = {v: k for k, v in MORSE_CODE_DICT.items()}
letters = MORSE_CODE_DICT.keys()
morse_letters = MORSE_CODE_DICT.values()


def check_letter(message: str) -> bool:
	i = False
	for letter in message:
		for key in letters:
			if letter == key:
				i = True
		for value in morse_letters:
			if letter == value:
				i = True
	return i


def encrypt(message: str) -> str:
	message = message.upper()

	my_cipher = ''
	for myletter in message:
		if myletter != ' ':
			my_cipher += MORSE_CODE_DICT[myletter] + ' '
		else:
			my_cipher += '/ '
	return my_cipher


# This function is used to decrypt Morse code to English
def decrypt(message: str) -> str:
	message = message.strip()
	output = ''

	words = [word.split(' ') for word in message.split(' / ')]

	for word in words:
		for letter in word:
			output += LETTERS_DICT[letter]
		output += ' '

	return output.strip()


def main():
	my_message = '"'
	output = encrypt(my_message.upper())
	print(output)
	my_message = ".... . .-.. .-.. --- --..-- / - .... .. ... / .. ... / -- --- .-. ... . / -.-. --- -.. . "
	output = decrypt(my_message)
	print(output)


# Executes the main function
if __name__ == '__main__':
	main()
