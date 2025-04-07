from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time

# === CONFIG ===
driver_path = r"C:\\programmi\\chromedriver\\chromedriver.exe"
options = Options()
options.add_argument("--window-size=1920,1080")
# options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(driver_path), options=options)

all_data = []
page = 0

while True:
    url = f"https://datacvr.virk.dk/soegeresultater?sideIndex={page}&enhedstype=virksomhed&kommune=851&branchekode=561110&size=1000"
    print(f"🔎 Scraping pagina {page}")
    driver.get(url)
    time.sleep(5)

    # Estrai tutti i blocchi delle aziende
    rows = driver.find_elements(By.CSS_SELECTOR, 'div[data-cy="soegeresultater-tabel"] > div.row')

    if not rows:
        print("❌ Nessun dato trovato. Fine scraping.")
        break

    for row in rows:
        try:
            name = row.find_element(By.CSS_SELECTOR, ".bold.value").text.strip()

            text = row.text.strip()
            lines = text.split("\n")

            # Estrai indirizzo, CVR, status, company type
            address_lines = []
            cvr = status = form = ""

            for line in lines:
                if "CVR-nummer:" in line:
                    cvr = line.replace("CVR-nummer:", "").strip()
                elif "Status:" in line:
                    status = line.replace("Status:", "").strip()
                elif "Virksomhedsform:" in line:
                    form = line.replace("Virksomhedsform:", "").strip()
                elif line.strip() != name:
                    address_lines.append(line.strip())

            address_lines = list(dict.fromkeys(address_lines))  # rimuove duplicati preservando ordine
            address = ", ".join(address_lines)

            print(f"✔️ {name} | {address} | {cvr} | {status} | {form}")

            all_data.append({
                "Name": name,
                "Address": address,
                "CVR": cvr,
                "Status": status,
                "Company Type": form
            })

        except Exception as e:
            print("⚠️ Errore durante parsing:", e)
            continue




    page += 1
    time.sleep(1)

driver.quit()

# Salva in CSV
df = pd.DataFrame(all_data)
df.to_csv("aziende_scraped_da_dom.csv", index=False)
print(f"✅ Salvate {len(df)} aziende in 'aziende_scraped_da_dom.csv'")