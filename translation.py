from unidecode import unidecode


custom_mapping = {
    'χ': 'ch',  # Replace "kh" with "ch"
    'Θ': 'Th',  # Add custom mappings as needed
    'φ': 'Ph',
    # Add more mappings as needed
}

def translate(text):
    # Perform the initial transliteration using unidecode
    transliterated_text = unidecode(text.lower())
    
    # Apply custom mappings
    for greek_char, custom_value in custom_mapping.items():
        transliterated_text = transliterated_text.replace(unidecode(greek_char), custom_value)
    
    return transliterated_text

