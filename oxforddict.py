import os

import requests


def get_definition(word):
	url = f'https://od-api.oxforddictionaries.com:443/api/v2/entries/en-gb/{word.lower()}?strictMatch=false&fields=definitions'
	r = requests.get(url, headers={'app_id': os.getenv("DICT_ID"), 'app_key': os.getenv("DICT_TOKEN")})
	# print(r.text)
	if r.status_code == 404:
		return "404 Error"
	else:
		return r.json()["results"][0]


if __name__ == "__main__":
	foo = get_definition("Book")
	print(type(foo))
	print(foo)
