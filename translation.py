from unidecode import unidecode

greek_text = "Καλημέρα κόσμε"
latin_text = unidecode(greek_text)
print(latin_text)