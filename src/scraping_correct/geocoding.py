import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import os

# === CONFIG ===
input_file = "scraped_companies_combined_clean.csv"
output_file = "restaurants_geocoded_simple.csv"

# === CARICA IL FILE ORIGINALE ===
df = pd.read_csv(input_file)

# Funzione per semplificare l'indirizzo
def simplify_address(row):
    addr = str(row["Address"])
    addr = addr.split(",")[0].strip()  # prende solo la parte prima della prima virgola
    return f"{addr}, Denmark"

# Aggiungi colonne coordinate se mancano
if "latitude" not in df.columns:
    df["latitude"] = None
if "longitude" not in df.columns:
    df["longitude"] = None

# Carica gli indirizzi già geocodificati
already_done = set()
if os.path.exists(output_file):
    df_existing = pd.read_csv(output_file)
    already_done = set(df_existing["Address"].dropna().unique())
    print(f"Riprendendo da {len(already_done)} già completati")

# Filtra solo quelli da fare
df_to_process = df[~df["Address"].isin(already_done)].copy()
print(f"Da geocodificare: {len(df_to_process)}")

# Geocoder OpenStreetMap
geolocator = Nominatim(user_agent="stayin_alive_simple_geocoder")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.5)

# Salvataggio progressivo
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
                print(f"❌ {full_address} → non trovato")
        except Exception as e:
            print(f"⚠️ Errore su {full_address}: {e}")
            continue

        # Salva riga in append
        pd.DataFrame([row]).to_csv(f_out, index=False, header=header_written)
        header_written = False
