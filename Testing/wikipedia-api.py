import wikipediaapi

wiki_wiki = wikipediaapi.Wikipedia('en')
while True:
	search_request = input(">")
	page_search = wiki_wiki.page(search_request)

	print(page_search.fullurl)
	print(page_search.canonicalurl)
	print(page_search)
	print(type(page_search))
	summary = "Page - Summary: {0}".format(page_search.summary[0:len(search_request)+60])
	print(summary)
