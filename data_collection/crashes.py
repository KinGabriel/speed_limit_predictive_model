import pandas as pd

# Load datasets
main_df = pd.read_csv("main dataset.csv")
crashes_df = pd.read_csv("city_total_crashes.csv")

# Normalize casing and spacing for reliable matching
main_df['city'] = main_df['city'].astype(str).str.strip().str.lower()
crashes_df['city'] = crashes_df['city'].astype(str).str.strip().str.lower()

# Create a mapping dictionary from crash data
crash_map = dict(zip(crashes_df['city'], crashes_df['city_total_crashes']))

# Add the new column using the mapping
main_df['city_total_crashes'] = main_df['city'].map(crash_map)

# Save back to the same main dataset file
main_df.to_csv("main dataset.csv", index=False)

# Optionally print out cities that didn't match
unmatched = [city for city in crashes_df['city'] if city not in set(main_df['city'])]
if unmatched:
    print("Cities in crash dataset not found in main dataset:")
    for city in unmatched:
        print("-", city)
else:
    print("All crash data successfully matched.")

