def get_key(val, dictt): 
    for key, value in dictt.items(): 
         if val == value: 
             return key 

def translate_bad():
	if True:
		print(f"user_message={user_message}")
		translate_list = user_message.split('"')
		print(f"translate_list={translate_list}")
		translate_list.pop(0)
		print(f"translate_list={translate_list}")
		_user_message = translate_list[0]
		print(f"_user_message={_user_message}")
		translate_list.pop(0)
		print(f"translate_list={translate_list}")
		translate_list = translate_list[0].lstrip().split(" ")
		print(f"translate_list={translate_list}")
		translate_to_language = translate_list[0]
		print(f"translate_to_language={translate_to_language}")
		
		try:
			source_language = translate_list[1]
		except IndexError:
			source_language = None
		
		print(f"source_language={source_language}")
		
		discriminator_a = None
		discriminator_b = None
		for lang in abbrev_lang_list:
			if translate_to_language == lang:
				discriminator_a = "abbreviated"
				break
			else:
				for _lang in full_lang_list:
					if translate_to_language == _lang:
						discriminator_a = "full"
						break
		print(discriminator_a)
		if source_language is not None:
			for lang in abbrev_lang_list:
				if source_language == lang:
					discriminator_b = "abbreviated"
					break
				else:
					for _lang in full_lang_list:
						if source_language == _lang:
							discriminator_b = "full"
							break
			print(discriminator_b)
			
		if discriminator_b is None or discriminator_a is None:
			ctx.send("Something went wrong.")
		
		if source_language is not None:
			if discriminator_b == "abbreviated":
				if translate_to_language is not None:
					if discriminator_a == "abbreviated":
						await ctx.send(f'Translated from {lang_dict[source_language]} to {lang_dict[translate_to_language]}:\n`"{self.translator.translate(_user_message, src=source_language, dest=translate_to_language).text}"`')
					elif discriminator_a == "full":
						await ctx.send(f'Translated from {source_language} to {translate_to_language}:\n`"{self.translator.translate(_user_message, src=source_language, dest=lang_dict[translate_to_language]).text}"`')
				else:
					await ctx.send(f'Translated from {lang_dict[source_language]} to english:\n`"{self.translator.translate(_user_message, src=source_language, dest="en").text}"`')
			elif discriminator_b == "full":
				if translate_to_language is not None:
					if discriminator_a == "abbreviated":
						await ctx.send(f'Translated from {source_language} to {lang_dict[translate_to_language]}:\n`"{self.translator.translate(_user_message, src=lang_dict[source_language], dest=translate_to_language).text}"`')
					elif discriminator_a == "full":
						await ctx.send(f'Translated from {source_language} to {translate_to_language}:\n`"{self.translator.translate(_user_message, src=lang_dict[source_language], dest=lang_dict[translate_to_language]).text}"`')
				else:
					await ctx.send(f'Translated from {source_language} to english:\n`"{self.translator.translate(_user_message, src=lang_dict[source_language], dest="en").text}"`')
		else:
			await ctx.send(f'Translated from {lang_dict[self.translator.detect(_user_message).lang]} to english:\n`"{self.translator.translate(_user_message).text}"`')

def translate_good(ctx, translate_message, destination_language = 'en', source_language = None):
	if True:
		for lang in full_lang_list:
			if lang == destination_language:
				destination_language = abbrev_lang_list[full_lang_list.index(destination_language)]

		if source_language is not None:
			for lang in full_lang_list:
				if lang == source_language:
					source_language = abbrev_lang_list[full_lang_list.index(source_language)]
		if source_language is None:
			source_language = self.translator.detect(translate_message).lang

		translated_text = self.translator.translate(translate_message, src=source_language, dest=).text
		await ctx.send(f'Translated from {lang_dict[source_language]} to {lang_dict[destination_language]}\n`"{translated_text}"`')
