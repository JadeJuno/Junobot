from googletrans import Translator

translator = Translator()

translate_this = input(">")
print(translator.translate(translate_this).text)
print(translator.detect(translate_this).lang)
