import pandas as pd

df = pd.read_excel('data.xlsx')
unique_values = df['tk'].unique()

print(unique_values)
