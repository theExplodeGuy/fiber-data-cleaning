import pandas as pd
from collections import Counter
from unidecode import unidecode
from translation import translate_clean

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

# Iterate over the grouped DataFrame
for index, row in grouped.iterrows():
    tk = row['tk']
    address_aprt_pairs = row['pairs']  # List of [address, translated_address, aprt_no] pairs for the tk group
    
    # Count the occurrences of each [translated_address, aprt_no] pair
    pair_counts = Counter((pair[1], pair[2]) for pair in address_aprt_pairs)  # Use translated_address and aprt_no for counting
    
    # Filter out pairs that occur more than once (duplicates)
    duplicates = {pair: count for pair, count in pair_counts.items() if count > 1}
    
    # Append the results to the list
    if duplicates:
        # Create a dictionary to store duplicate details
        duplicate_details = {}
        for pair, count in duplicates.items():
            translated_address, aprt_no = pair
            # Find all original addresses that match the duplicate pair
            original_addresses = [p[0] for p in address_aprt_pairs if (p[1], p[2]) == pair]
            duplicate_details[pair] = {
                'count': count,
                'original_addresses': original_addresses
            }
        
        results.append({
            'tk': tk,
            'duplicates': duplicate_details
        })

# Print the results
c = 0
for result in results:
    tk = result['tk']
    duplicates = result['duplicates']
    
    print(f"tk: {tk}")
    print("Duplicates found:")
    for pair, details in duplicates.items():
        translated_address, aprt_no = pair
        count = details['count']
        original_addresses = details['original_addresses']
        c += count-1

        print(f"  Translated Address: {translated_address}, aprt_no: {aprt_no} - Count: {count}")
        print("  Original Addresses:")
        for address in original_addresses:
            print(f"    - {address}")
    print("-" * 50)  # Separator for readability
print("total duol: ", c)
