import pandas as pd
from itertools import combinations
from unidecode import unidecode
import re
from fuzz import custom_score
from translation import translate_clean


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