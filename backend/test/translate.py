from googletrans import Translator

translator = Translator(raise_exception=True, service_urls=['translate.googleapis.com'])
print(translator.translate('हॅलो वर्ल्ड').text)

lang = translator.detect('কেমন আছো?')
print(lang.lang)
print(lang.confidence)