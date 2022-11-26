"""
Created on May 5, 2017

@author: anthony
"""
import math
import re
from collections import deque
from threading import Thread
from time import sleep

import urllib2
from bs4 import BeautifulSoup


class GoogleSearch:
	USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/ 58.0.3029.81 Safari/537.36"
	SEARCH_URL = "https://google.com/search"
	RESULT_SELECTOR = ".srg h3.r a"
	TOTAL_SELECTOR = "#resultStats"
	RESULTS_PER_PAGE = 10
	DEFAULT_HEADERS = [
		('User-Agent', USER_AGENT),
		("Accept-Language", "en-US,en;q=0.5"),
	]

	def search(self, _query, num_results=10, prefetch_pages=True, prefetch_threads=10, language="en"):
		search_results = []
		pages = int(math.ceil(num_results / float(GoogleSearch.RESULTS_PER_PAGE)))
		fetcher_threads = deque([])
		total = None
		for i in range(pages):
			start = i * GoogleSearch.RESULTS_PER_PAGE
			opener = urllib2.build_opener()
			opener.addheaders = GoogleSearch.DEFAULT_HEADERS
			with opener.open(GoogleSearch.SEARCH_URL + "?q=" + urllib2.quote(_query) + "&hl=" + language + (
				"" if start == 0 else ("&start=" + str(start)))) as _response:
				soup = BeautifulSoup(_response.read(), "lxml")
			if total is None:
				total_text = soup.select(GoogleSearch.TOTAL_SELECTOR)[0].children.next().encode('utf-8')
				total = long(re.sub("[',. ]", "", re.search("(([0-9]+[',. ])*[0-9]+)", total_text).group(1)))
			results = self.parse_results(soup.select(GoogleSearch.RESULT_SELECTOR))
			if len(search_results) + len(results) > num_results:
				del results[num_results - len(search_results):]
			search_results += results
			if prefetch_pages:
				for _result in results:
					while True:
						running = 0
						for thread in fetcher_threads:
							if thread.is_alive():
								running += 1
						if running < prefetch_threads:
							break
						sleep(1)
					fetcher_thread = Thread(target=result.get_text)
					fetcher_thread.start()
					fetcher_threads.append(fetcher_thread)
		for thread in fetcher_threads:
			thread.join()
		return SearchResponse(search_results, total)

	@staticmethod
	def parse_results(results):
		search_results = []
		for _result in results:
			url = _result["href"]
			title = _result.text
			search_results.append(SearchResult(title, url))
		return search_results


class SearchResponse:
	def __init__(self, results, total):
		self.results = results
		self.total = total


class SearchResult:
	def __init__(self, title, url):
		self.title = title
		self.url = url
		self.__text = None
		self.__markup = None

	def get_text(self):
		if self.__text is None:
			soup = BeautifulSoup(self.get_markup(), "lxml")
			for junk in soup(["script", "style"]):
				junk.extract()
				self.__text = soup.get_text()
		return self.__text

	def get_markup(self):
		if self.__markup is None:
			opener = urllib2.build_opener()
			opener.addheaders = GoogleSearch.DEFAULT_HEADERS
			_response = opener.open(self.url)
			self.__markup = _response.read()
		return self.__markup

	def __str__(self):
		return str(self.__dict__)

	def __unicode__(self):
		return unicode(self.__str__())

	def __repr__(self):
		return self.__str__()


if __name__ == "__main__":
	import sys

	search = GoogleSearch()
	i = 1
	query = " ".join(sys.argv[1:])
	if len(query) == 0:
		query = "python"
	count = 10
	print("Fetching first " + str(count) + " results for \"" + query + "\"...")
	response = search.search(query, count)
	print("TOTAL: " + str(response.total) + " RESULTS")
	for result in response.results:
		print("RESULT #" + str(i) + ": " + (
			result._SearchResult__text if result._SearchResult__text is not None else "[None]") + "\n\n")
		i += 1
