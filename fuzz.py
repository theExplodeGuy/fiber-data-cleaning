import re
from thefuzz import fuzz

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