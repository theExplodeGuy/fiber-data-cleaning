import pandas as pd
from collections import Counter
from unidecode import unidecode

# Custom mapping for transliteration
custom_mapping = {
    'χ': 'ch',  # Replace "kh" with "ch"
    'Θ': 'Th',  # Add custom mappings as needed
    'φ': 'Ph',
    # Add more mappings as needed
}

# Function to clean the text
def clean(text):
    punctuation = ["/", ".", ",", "*", "(", ")", "&", "#", "@", "!"]
    text = text.strip()
    for punc in punctuation:
        text = text.replace(punc, "")
    return text

# Function to translate the text
def translate(text):
    # Perform the initial transliteration using unidecode
    transliterated_text = unidecode(text.lower())
    
    # Apply custom mappings
    for greek_char, custom_value in custom_mapping.items():
        transliterated_text = transliterated_text.replace(unidecode(greek_char), custom_value)
    
    return transliterated_text

# Read the excel file
try:
    df = pd.read_excel('data.xlsx')
except FileNotFoundError:
    print("Error: The file 'data.xlsx' was not found.")
    exit()

# Check if the required columns exist
if not all(col in df.columns for col in ['tk', 'address', 'aprt_no']):
    print("Error: The required columns 'tk', 'address', and 'aprt_no' are not in the DataFrame.")
    exit()

# Clean and translate the 'address' column
df['translated_address'] = df['address'].apply(clean).apply(translate)

# Group by 'tk' and collect the 'translated_address' and 'aprt_no' combinations
grouped = df.groupby('tk')[['translated_address', 'aprt_no']].apply(lambda x: x.values.tolist()).reset_index()

# Create a list to store the results
results = []

# Iterate over the grouped DataFrame
for index, row in grouped.iterrows():
    tk = row['tk']
    address_aprt_pairs = row[1]  # List of [translated_address, aprt_no] pairs for the tk group
    
    # Count the occurrences of each [translated_address, aprt_no] pair
    pair_counts = Counter(tuple(pair) for pair in address_aprt_pairs)
    
    # Filter out pairs that occur more than once (duplicates)
    duplicates = {pair: count for pair, count in pair_counts.items() if count > 1}
    
    # Append the results to the list
    if duplicates:
        results.append({
            'tk': tk,
            'duplicates': duplicates
        })

# Print the results
for result in results:
    tk = result['tk']
    duplicates = result['duplicates']
    
    print(f"tk: {tk}")
    print("Duplicates found (translated_address, aprt_no):")
    for pair, count in duplicates.items():
        translated_address, aprt_no = pair
        print(f"  Translated Address: {translated_address}, aprt_no: {aprt_no} - Count: {count}")
    print("-" * 50)  # Separator for readability