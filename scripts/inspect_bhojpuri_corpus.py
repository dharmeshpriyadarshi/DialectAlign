
import pandas as pd

DATA_PATH = "data/external/bhojpuri_corpus/BhojpuriCorpus.parquet"

df = pd.read_parquet(DATA_PATH)

print("\n--- SHORT TEXT RECORDS (1-3 WORDS) ---")
short_records = df[df["text"].str.split().str.len() <= 3]
print("Count:", len(short_records))
print(short_records[["source", "text"]].head(10).to_string(index=False))

print("\n--- EXTREMELY LONG RECORDS (>1000 WORDS) ---")
long_records = df[df["text"].str.split().str.len() > 1000]
print("Count:", len(long_records))
print(long_records[["source", "text"]].head(5).to_string(index=False))

print("\n--- FISH_FOOD SOURCE INSPECTION ---")
fish_food = df[df["source"] == "fish_food"]
print("Total records:", len(fish_food))
print("Licence distribution:")
print(fish_food["license"].value_counts())
print("\nSample records:")
for text in fish_food["text"].sample(
    min(10, len(fish_food)), random_state=42
):
    print("-", text[:250])

print("\n--- INITIAL CIVIC VOCABULARY SEARCH ---")

civic_terms = [
    "सड़क", "रस्ता", "गाँव", "गाँव के",
    "पानी", "नल", "बिजली", "बिजुली",
    "कचरा", "नाला", "नाली", "अस्पताल",
    "विद्यालय", "स्कूल", "सरकार", "पंचायत"
]

for term in civic_terms:
    matches = df["text"].str.contains(
        term, regex=False, na=False
    )
    print(f"{term}: {matches.sum()} records")
