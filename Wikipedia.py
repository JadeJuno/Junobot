import wikipedia

# search = input(">")
search = "Mercury (planet)"

try:
	result = wikipedia.page(search)
	print(result.title)
	print(result.url)
	# print(f"{result.content[:50]} (...)")
except wikipedia.exceptions.DisambiguationError as e:
	i = 1
	for option in e.options[:10]:
		print(f"{i} {option}")
		i += 1
		disamb_result = wikipedia.page(option)
		print(disamb_result.title)
		if disamb_result != "":
			print(disamb_result.url)
		else:
			print("**URL Not Found**")
		# print(f"{disamb_result.content[0:50]} (...)")
