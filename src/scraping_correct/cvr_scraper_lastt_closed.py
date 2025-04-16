from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
import csv
import os

# === CONFIG ===
driver_path = r"C:\\programmi\\chromedriver\\chromedriver.exe"
options = Options()
options.add_argument("--window-size=1920,1080")
# options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(driver_path), options=options)

branchekodes = [
    #561110,
    #561190,
    563010,
    # 563020,
]

for branchekode in branchekodes:
    page = 0
    csv_file_path = f"scraped_companies_{branchekode}_notactive.csv"
    header = ["Name", "Address", "P-nummer", "Status", "Company Type", "Startdate", "Enddate"]
    pnummer_seen = set()

    # Se il file esiste, leggi i P-nummer già presenti
    file_exists = os.path.exists(csv_file_path)
    if file_exists:
        with open(csv_file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pnummer_seen.add(row["P-nummer"])
    else:
        # Crea il file e scrivi header
        with open(csv_file_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()

    while True:
        url = f"https://datacvr.virk.dk/soegeresultater?sideIndex={page}&enhedstype=produktionsenhed&virksomhedsstatus=ophoerte&region=29190623&branchekode={branchekode}" #&virksomhedsstatus=ophoerte
        print(f"🔎 Scraping pagina {page}")
        driver.get(url)
        time.sleep(2)

        rows = driver.find_elements(By.CSS_SELECTOR, 'div[data-cy="soegeresultater-tabel"] > div.row')

        if not rows:
            print("❌ Nessun dato trovato. Fine scraping.")
            break

        for row in rows:
            try:
                name = row.find_element(By.CSS_SELECTOR, "span.bold.value").text.strip()

                address_block = row.find_element(By.CSS_SELECTOR, "div.col-12.col-lg-4")
                address_lines = address_block.text.strip().split("\n")[-2:]
                address = ", ".join(address_lines)

                pnummer = row.find_element(By.XPATH, './/div[div[text()="P-nummer:"]]/div[2]').text.strip()

                # Se già salvato, salta
                if pnummer in pnummer_seen:
                    continue
                pnummer_seen.add(pnummer)

                status = row.find_element(By.XPATH, './/div[div[text()="Status:"]]/div[2]').text.strip()
                form = row.find_element(By.XPATH, './/div[div[text()="Virksomhedsform:"]]/div[2]').text.strip()

                link_elem = row.find_element(By.CSS_SELECTOR, 'div[data-cy="vis-mere"] a')
                link = link_elem.get_attribute("href")

                # Vai al dettaglio
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(link)
                time.sleep(3)

                # Estrai date
                startdato = ""
                ophoersdato = ""

                try:
                    startdato_element = driver.find_element(
                        By.XPATH, '//div[(strong[text()="Startdato"] or span[text()="Startdato"])]/following-sibling::div'
                    )
                    startdato = startdato_element.text.strip()
                except:
                    startdato = ""

                try:
                    ophoersdato_element = driver.find_element(
                        By.XPATH, '//div[(strong[text()="Ophørsdato"] or span[text()="Ophørsdato"])]/following-sibling::div'
                    )
                    ophoersdato = ophoersdato_element.text.strip()
                except:
                    ophoersdato = ""

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                # Scrivi riga su CSV
                with open(csv_file_path, "a", newline='', encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=header)
                    writer.writerow({
                        "Name": name,
                        "Address": address,
                        "P-nummer": pnummer,
                        "Status": status,
                        "Company Type": form,
                        "Startdate": startdato,
                        "Enddate": ophoersdato
                    })

                print(f"✔️ {name} | {startdato} → {ophoersdato}")

            except Exception as e:
                print("⚠️ Errore durante parsing:", e)
                continue

        page += 1
        time.sleep(1)

driver.quit()
print("🏁 Fine scraping.")
