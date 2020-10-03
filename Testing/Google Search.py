import googlesearch

for result in googlesearch.search("a", stop=10):
    print(result.title)
    print(result.description)
    print(result.link)
    print()
