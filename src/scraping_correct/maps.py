from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time

# === CONFIG ===
# driver_path = r"C:\\programmi\\chromedriver\\chromedriver.exe"
driver_path = (
    r"C:\Users\Dell\Desktop\Adv. Business Analytics\chromedriver-win64\chromedriver.exe"
)
options = Options()
options.add_argument("--window-size=1920,1080")
# options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(driver_path), options=options)

# === DATI DI INPUT ===
csv_path = r"C:\Users\Dell\OneDrive - Danmarks Tekniske Universitet\Git Hub\StayingAlive\src\scraping_correct\scraped_companies_561110_active.csv"
df_input = pd.read_csv(csv_path)
restaurant_data = df_input.to_dict(orient="records")


all_data = []

# === LOOP SUI RISTORANTI ===
for entry in restaurant_data:
    name = entry["Name"]
    address = entry["Address"]

    try:
        print(f"🔎 Cercando: {name} @ {address}")
        query = f"{name} {address}".replace(" ", "+")
        linkmaps = f"https://www.google.com/maps/search/{query}"
        print(f"🔗 Link: {linkmaps}")
        driver.get(linkmaps)
        time.sleep(1)

        # Estrai dati principali
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
            reviews = reviews_elem.strip("()")  # prende (148) e restituisce 148
            # print(reviews)
        except:
            reviews = ""

        try:
            price_level = driver.find_element(By.CSS_SELECTOR, 'div.DfOCNb.fontBodyMedium > div').text.split('\n')[0]
            # print(price_level)
        except:
            price_level = ""

        try:
            # Locate all outer divs with the class "KNfEk aUjao"
            outer_divs = driver.find_elements(By.CSS_SELECTOR, "div.KNfEk.aUjao")

            # Extract the text from the specific span inside each div
            tags = []
            for div in outer_divs:
                try:
                    tag = div.find_element(
                        By.CSS_SELECTOR, "div.tXNTee span.uEubGf.fontBodyMedium"
                    ).text
                    tags.append(tag)
                except:
                    continue  # Skip if the specific span is not found in this div

            # Join all tags into a single string, separated by commas
            tags = ", ".join(tags)
            print(tags)
        except:
            tags = ""

        print(f"✔️{title}***⭐{rating}***🗨️{reviews}***💰{price_level}***🏷️{tags}")

        all_data.append({
            "Input Name": name,
            "Input Address": address,
            "Title": title,
            "Rating": rating,
            "Reviews": reviews,
            "Price Level": price_level,
            "Tags": tags
        })

    except Exception as e:
        print("⚠️ Errore durante scraping:", e)
        continue


# === FINE ===
driver.quit()

# Salva in CSV
df = pd.DataFrame(all_data)
df.to_csv("maps_data_scraped.csv", index=False)
print(f"✅ Salvati {len(df)} ristoranti in 'maps_data_scraped.csv'")
