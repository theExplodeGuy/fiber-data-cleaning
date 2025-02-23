import pandas as pd
from itertools import combinations
from unidecode import unidecode
import re
from thefuzz import fuzz

# Custom mapping for transliteration
custom_mapping = {
    'χ': 'ch',  # Replace "kh" with "ch"
    'Θ': 'th',  # Add custom mappings as needed
    'φ': 'ph',
    # Add more mappings as needed
}

# Function to clean the text
def clean(text):
    punctuation = ["Αρ.", "/", ".", ",", "*", "(", ")", "&", "#", "@", "!"]
    text = text.strip()
    for punc in punctuation:
        text = text.replace(punc, "")
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    return text

# Function to translate and clean the text
def translate_clean(text):
    transliterated_text = clean(text)
    # Perform the initial transliteration using unidecode
    transliterated_text = unidecode(transliterated_text.lower())
    
    # Apply custom mappings
    for greek_char, custom_value in custom_mapping.items():
        transliterated_text = transliterated_text.replace(unidecode(greek_char), custom_value)

    return transliterated_text

# Function to calculate a custom similarity score
def custom_score(s1, s2, num_weight=1.5, text_weight=1):
    # If the strings are exactly identical, return 100 immediately.
    if s1 == s2:
        return 100

    # Extract numeric tokens from both strings.
    nums1 = re.findall(r'\d+', s1)
    nums2 = re.findall(r'\d+', s2)
    
    # Remove numeric tokens from the strings to isolate the text.
    s1_text = re.sub(r'\d+', '', s1).strip()
    s2_text = re.sub(r'\d+', '', s2).strip()
    
    # Compute similarity for the text parts.
    text_score = fuzz.token_sort_ratio(s1_text, s2_text)
    
    # Compute similarity for the numeric parts.
    if nums1 and nums2:
        num1 = " ".join(nums1)
        num2 = " ".join(nums2)
        num_score = fuzz.token_sort_ratio(num1, num2)
    else:
        # If one or both strings lack numbers, consider the numeric similarity as 0.
        num_score = 0

    # Combine the scores using a weighted average.
    combined_score = (num_weight * num_score + text_weight * text_score) / (num_weight + text_weight)
    return combined_score

# Read the excel file
try:
    df = pd.read_excel('data.xlsx')
except FileNotFoundError:
    print("Error: The file 'data.xlsx' was not found.")
    exit()

# Check if the required columns exist
if not all(col in df.columns for col in ['tk', 'address', 'aprt_no', 'id']):
    print("Error: The required columns 'tk', 'address', and 'aprt_no' are not in the DataFrame.")
    exit()

# Clean and translate the 'address' column
df['translated_address'] = df['address'].apply(translate_clean)

# Group by 'tk' and collect the 'address', 'translated_address', and 'aprt_no' combinations
grouped = df.groupby('tk')[['id', 'address', 'translated_address', 'aprt_no']].apply(lambda x: x.values.tolist()).reset_index(name='pairs')

# Create a list to store the results
results = []
total_duplicates = 0  # Counter for total duplicates
threshold = 92  # Similarity threshold for considering duplicates
duplicate_rows = []

# Iterate over the grouped DataFrame
for index, row in grouped.iterrows():
    tk = row['tk']
    address_aprt_pairs = row['pairs']  # List of [address, translated_address, aprt_no] pairs for the tk group
    
    # Create a dictionary to store duplicate details
    duplicate_details = {}
    
    # Compare all pairs of addresses within the same 'tk' group
    for (id1, addr1, trans_addr1, aprt_no1), (id2, addr2, trans_addr2, aprt_no2) in combinations(address_aprt_pairs, 2):
        # Calculate similarity score between translated addresses
        similarity = custom_score(trans_addr1, trans_addr2)
        
        # Check if the similarity is above the threshold and aprt_no matches
        if similarity > threshold and aprt_no1 == aprt_no2:
            # Use the translated address and aprt_no as the key
            key = (trans_addr1, aprt_no1)
            
            # Add the original addresses to the duplicate details
            if key not in duplicate_details:
                duplicate_details[key] = {
                    'count': 1,  # Start with 1 (first occurrence)
                    'original_addresses': [addr1, addr2]
                }
            else:
                duplicate_details[key]['count'] += 1
                duplicate_details[key]['original_addresses'].append(addr2)
            
            # Add the duplicate rows to the list for the CSV file
            duplicate_rows.append({'id':id1, 'address': addr1, 'aprt_no': aprt_no1, 'tk': tk})
            duplicate_rows.append({'id':id2, 'address': addr2, 'aprt_no': aprt_no2, 'tk': tk})
            
            total_duplicates += 1  # Increment total duplicates
    
    # Append the results to the list
    if duplicate_details:
        results.append({
            'tk': tk,
            'duplicates': duplicate_details
        })

# Save the duplicate rows to a CSV file
duplicates_df = pd.DataFrame(duplicate_rows)
duplicates_df.drop_duplicates(inplace=True)  # Remove duplicate rows (if any)
duplicates_df.to_csv('duplicates.csv', index=False, columns=['address', 'aprt_no', 'tk'])

# Print the results
for result in results:
    tk = result['tk']
    duplicates = result['duplicates']
    
    print(f"tk: {tk}")
    print("Duplicates found:")
    for key, details in duplicates.items():
        translated_address, aprt_no = key
        count = details['count']
        original_addresses = details['original_addresses']
        
        print(f"  Translated Address: {translated_address}, aprt_no: {aprt_no} - Count: {count}")
        print("  Original Addresses:")
        for address in original_addresses:
            print(f"    - {address}")
    print("-" * 50)  # Separator for readability

# Print the total number of duplicates
print(f"Total duplicates across all 'tk' groups: {total_duplicates}")