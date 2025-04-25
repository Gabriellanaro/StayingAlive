import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import os

# === CONFIGURATION ===
input_file = "scraped_companies_combined_clean.csv"
output_file = "restaurants_geocoded_simple.csv"

# === LOAD ORIGINAL DATA ===
df = pd.read_csv(input_file)

# Function to simplify the address before geocoding
def simplify_address(row):
    addr = str(row["Address"])
    addr = addr.split(",")[0].strip()  # only keep the part before the first comma
    return f"{addr}, Denmark"

# Add coordinate columns if they don't exist
if "latitude" not in df.columns:
    df["latitude"] = None
if "longitude" not in df.columns:
    df["longitude"] = None

# Load already geocoded addresses to avoid duplicates
already_done = set()
if os.path.exists(output_file):
    df_existing = pd.read_csv(output_file)
    already_done = set(df_existing["Address"].dropna().unique())
    print(f"Resuming from {len(already_done)} already completed addresses.")

# Filter rows that still need geocoding
df_to_process = df[~df["Address"].isin(already_done)].copy()
print(f"Addresses to geocode: {len(df_to_process)}")

# Initialize OpenStreetMap geocoder with delay to respect rate limits
geolocator = Nominatim(user_agent="stayin_alive_simple_geocoder")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.5)

# Progressive saving to CSV (append mode)
with open(output_file, "a", encoding="utf-8", newline="") as f_out:
    header_written = os.stat(output_file).st_size == 0
    for i, row in df_to_process.iterrows():
        full_address = simplify_address(row)
        try:
            location = geocode(full_address)
            if location:
                row["latitude"] = location.latitude
                row["longitude"] = location.longitude
                print(f"✔️ {full_address} → ({location.latitude}, {location.longitude})")
            else:
                print(f"❌ {full_address} → not found")
        except Exception as e:
            print(f"⚠️ Error on {full_address}: {e}")
            continue

        # Append row to output CSV
        pd.DataFrame([row]).to_csv(f_out, index=False, header=header_written)
        header_written = False
