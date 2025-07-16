import pandas as pd

# Load both datasets
main_df = pd.read_csv("main dataset.csv")
cities_df = pd.read_csv("Cities_and_Towns_With_Population_and_Classification.csv")

# Ensure consistent casing for matching
cities_df['Location'] = cities_df['Location'].str.strip().str.lower()
main_df['city'] = main_df['city'].str.strip().str.lower()

# Create mapping dictionaries
population_map = dict(zip(cities_df['Location'], cities_df['Total']))
classification_map = dict(zip(cities_df['Location'], cities_df['Classification']))

# Update the main dataset
main_df['population'] = main_df['city'].map(population_map)
main_df['classification'] = main_df['city'].map(classification_map)

# Save updated file back to same name
main_df.to_csv("main dataset.csv", index=False)