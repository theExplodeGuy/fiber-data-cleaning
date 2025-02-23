from unidecode import unidecode
import re

# Custom mapping for transliteration
custom_mapping = {
    'χ': 'ch',  # Replace "kh" with "ch"
    'Θ': 'th',  # Add custom mappings as needed
    'φ': 'ph',
    # Add more mappings as needed
}

# Function to clean the text
def clean(text):
    punctuation = ["αρ.", "μπλοκ", "block" "/", ".", ",", "*", "(", ")", "&", "#", "@", "!"]
    text = text.strip()
    for punc in punctuation:
        text = text.replace(punc, "")
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    return text

# Function to translate and clean the text
def translate_clean(text):
    # Perform the initial transliteration using unidecode
    transliterated_text = unidecode(text.lower())
    transliterated_text = clean(transliterated_text)
    
    # Apply custom mappings
    for greek_char, custom_value in custom_mapping.items():
        transliterated_text = transliterated_text.replace(unidecode(greek_char), custom_value)

    return transliterated_text