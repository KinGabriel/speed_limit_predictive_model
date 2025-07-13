import pandas as pd

# Load CSV
df = pd.read_csv("roads_characteristics.csv")

# Define urban cities
urban_cities = {
    "Quezon City", "Davao", "Cebu", "Baguio", "Dagupan", "Santiago", "SJDM",
    "Antipolo", "Puerto Princesa", "Naga", "Bacolod", "Tacloban", "Zamboanga", "CDO",
    "GenSan", "Butuan", "Cotabato"
}

# Total population for all cities
total_population_dict = {
    "Quezon City": 2960048, "Davao": 1776949, "Cebu": 964169, "Baguio": 366358,
    "Iloilo": 457626, "Bacolod": 600783, "Zamboanga": 977234, "Naga": 209170,
    "Dagupan": 174302, "Dasma": 703141, "Antipolo": 887399, "CDO": 728402,
    "San Carlos": 205424, "Tacloban": 251881, "Ormoc": 230998, "Butuan": 372910,
    "Gingoog": 136698, "Marawi": 201785, "GenSan": 679588, "Puerto Princesa": 307079,
    "Sorsogon": 182237, "Tabuk": 121033, "Santiago": 148580, "Ilagan": 158218,
    "Samal": 116771, "Sindangan": 103952, "Bayugan": 109499, "Palimbang": 92828,
    "Cotabato": 325079, "SJDM": 651813, "Barili": 80715, "Tarlac": 385398,
    "Naujan": 109587
}

# Urban population
urban_population_dict = {
    "Quezon City": 2960048, "Davao": 1631785, "Cebu": 908195, "Baguio": 236926,
    "Iloilo": 365018, "Bacolod": 589209, "Zamboanga": 869929, "Naga": 197330,
    "Dagupan": 589447, "Dasma": 589447, "Antipolo": 886309, "CDO": 697611,
    "San Carlos": 61621, "Tacloban": 140953, "Ormoc": 108833, "Butuan": 255281,
    "Gingoog": 43179, "Marawi": 33657, "GenSan": 33657, "Puerto Princesa": 33657,
    "Sorsogon": 182237, "Tabuk": 121033, "Santiago": 148580, "Ilagan": 158218,
    "Samal": 36377, "Sindangan": 2737, "Bayugan": 42562, "Palimbang": 14090,
    "Cotabato": 307790, "SJDM": 307790, "Barili": 5081, "Tarlac": 280216,
    "Naujan": 4880
}

# Calculate rural population as total - urban
rural_population_dict = {
    city: total_population_dict[city] - urban_population_dict.get(city, 0)
    for city in total_population_dict
}

# Set is_urban based on the list
df["is_urban"] = df["city"].apply(lambda x: 1 if x.strip() in urban_cities else 0)
# Map populations
df["total_population"] = df["city"].map(total_population_dict)
df["urban_population"] = df["city"].map(urban_population_dict).fillna(0).astype(int)
df["rural_population"] = df["city"].map(rural_population_dict).fillna(0).astype(int)



# Save to csv
df.to_csv("roads_with_features_with_urban.csv", index=False)
print("Done adding")
