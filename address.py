import pandas as pd
from itertools import combinations
from unidecode import unidecode
import re
from translation import translate_clean

# Function to calculate normalized Hamming distance
def hamming_distance(str1, str2):

    # Pad the shorter string with spaces to make lengths equal
    max_len = max(len(str1), len(str2))
    str1 = str1.ljust(max_len)
    str2 = str2.ljust(max_len)
    
    # Calculate Hamming distance
    distance = sum(c1 != c2 for c1, c2 in zip(str1, str2))
    
    # Normalize the distance by dividing by the length of the strings
    normalized_distance = distance / max_len
    return normalized_distance

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
df['translated_address'] = df['address'].apply(translate_clean)

# Group by 'tk' and collect the 'address', 'translated_address', and 'aprt_no' combinations
grouped = df.groupby('tk')[['address', 'translated_address', 'aprt_no']].apply(lambda x: x.values.tolist()).reset_index(name='pairs')

# Create a list to store the results
results = []
total_duplicates = 0  # Counter for total duplicates
threshold = 0.05  # Hamming distance threshold for considering duplicates

# Iterate over the grouped DataFrame
for index, row in grouped.iterrows():
    tk = row['tk']
    address_aprt_pairs = row['pairs']  # List of [address, translated_address, aprt_no] pairs for the tk group
    
    # Create a dictionary to store duplicate details
    duplicate_details = {}
    
    # Compare all pairs of addresses within the same 'tk' group
    for (addr1, trans_addr1, aprt_no1), (addr2, trans_addr2, aprt_no2) in combinations(address_aprt_pairs, 2):
        # Calculate Hamming distance between translated addresses (ignoring numbers)
        distance = hamming_distance(trans_addr1, trans_addr2)
        
        # Check if the distance is below the threshold and aprt_no matches
        if distance < threshold and aprt_no1 == aprt_no2:
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
            
            total_duplicates += 1  # Increment total duplicates
    
    # Append the results to the list
    if duplicate_details:
        results.append({
            'tk': tk,
            'duplicates': duplicate_details
        })

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