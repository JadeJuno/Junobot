from googlesearch import *
import requests
from bs4 import BeautifulSoup
"""
url = "http://www.amazon.in/s/ref=nb_sb_noss_1?url=search-alias%3Daps&field-keywords=python"
source_code = requests.get(url)
plain_text = source_code.content
soup = BeautifulSoup(plain_text, "lxml")
links = soup.findAll('a', {'class': 'a-link-normal s-access-detail-page a-text-normal'})
prin(len(links))
for link in links:
	title = link.get('title')
	print(title)
"""

browse = input(">")
for html in search(browse, stop=10):
	print(html)
