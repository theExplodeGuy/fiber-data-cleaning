import pandas as pd

df = pd.read_excel('data.xlsx')
unique_values = df['tk'].unique()
count = df['tk'].value_counts().get(unique_values[1], 0)
print(unique_values[0])
print(count)
