"""import wikipedia

# search = input(">")
search = "Mercury"

try:
	result = wikipedia.page(search)
	print(result.title)
	print(result.url)
	print(f"{result.content[0:50]} (...)")
except wikipedia.exceptions.DisambiguationError as e:
	i = 1
	for option in e.options[0:10]:
		print(f"{i} {option}")
		i += 1
		disamb_result = wikipedia.page(option)
		print(disamb_result.title)
		print(disamb_result.url)
		# print(f"{disamb_result.content[0:50]} (...)")


import pywikibot

site = pywikibot.Site('en', 'wikipedia')
page = pywikibot.Page(site, 'Wikipedia:Sandbox')
print(page)
"""

# This thing doesn't work yet...
