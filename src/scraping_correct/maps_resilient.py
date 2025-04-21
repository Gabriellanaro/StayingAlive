
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
import csv
import os

# === CONFIG ===
driver_path = r"C:\Program Files\chromedriver\chromedriver.exe"
options = Options()
options.add_argument("--window-size=1920,1080")
# options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(driver_path), options=options)

# === INPUT & OUTPUT PATH ===
csv_input_path = r"C:\Users\Admin\Documents\HCAI\ADVANCED_BUSINESS_ANALYTICS\StayingAlive\StayingAlive\src\scraping_correct\scraped_companies_563020_notactive.csv"
csv_output_path = r"C:\Users\Admin\Documents\HCAI\ADVANCED_BUSINESS_ANALYTICS\StayingAlive\StayingAlive\src\scraping_correct\maps_data_scraped.csv"

# Carica input
df_input = pd.read_csv(csv_input_path)
restaurant_data = df_input.to_dict(orient="records")

# Carica già salvati (se esiste il file output)
saved_entries = set()
header = ["Input Name", "Input Address", "Title", "Rating", "Reviews", "Price Level", "Tags"]

if os.path.exists(csv_output_path):
    with open(csv_output_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["Input Name"], row["Input Address"])
            saved_entries.add(key)
else:
    with open(csv_output_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()

# === LOOP SUI RISTORANTI ===
for entry in restaurant_data:
    name = entry["Name"]
    address = entry["Address"]
    key = (name, address)

    if key in saved_entries:
        continue

    try:
        print(f"🔎 Cercando: {name} @ {address}")
        query = f"{name} {address}".replace(" ", "+")
        linkmaps = f"https://www.google.com/maps/search/{query}"
        print(f"🔗 Link: {linkmaps}")
        driver.get(linkmaps)
        time.sleep(2)

        try:
            title = driver.find_element(By.CSS_SELECTOR, 'h1.DUwDvf').text
            print(title)
        except:
            title = ""

        try:
            rating = driver.find_element(By.CSS_SELECTOR, 'div.F7nice > span span[aria-hidden="true"]').text
            print(rating)
        except:
            rating = ""

        try:
            reviews_elem = driver.find_element(By.CSS_SELECTOR, 'div.F7nice > span span[aria-label$="recensioni"]').text
            reviews = reviews_elem.strip("()")
            print(reviews)
        except:
            reviews = ""

        try:
            price_level = driver.find_element(By.CSS_SELECTOR, 'div.DfOCNb.fontBodyMedium > div').text.split('\n')[0]
            print(price_level)
        except:
            price_level = ""

        try:
            outer_divs = driver.find_elements(By.CSS_SELECTOR, "div.KNfEk.aUjao")
            tags = []
            for div in outer_divs:
                try:
                    tag = div.find_element(By.CSS_SELECTOR, "div.tXNTee span.uEubGf.fontBodyMedium").text
                    tags.append(tag)
                except:
                    continue
            tags = ", ".join(tags)
            print(tags)
        except:
            tags = ""

        # Scrivi immediatamente su CSV
        with open(csv_output_path, "a", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writerow({
                "Input Name": name,
                "Input Address": address,
                "Title": title,
                "Rating": rating,
                "Reviews": reviews,
                "Price Level": price_level,
                "Tags": tags
            })

        print(f"✔️ Salvato: {title}")

    except Exception as e:
        print("⚠️ Errore durante scraping:", e)
        continue

driver.quit()
print("🏁 Fine scraping.")
