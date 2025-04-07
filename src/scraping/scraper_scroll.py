
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

driver_path = r"C:\\programmi\\chromedriver\\chromedriver.exe"

options = Options()
# options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_argument("--log-level=3")

driver = webdriver.Chrome(service=Service(driver_path), options=options)

all_companies = []
page = 0

while True:
    url = f"https://datacvr.virk.dk/soegeresultater?region=29190623&branchekode=561110&size=1000&sideIndex={page}"
    print(f"Scraping pagina {page}")
    driver.get(url)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    blocks = soup.find_all("div", class_="search-result")
    print(f"Trovati {len(blocks)} risultati nella pagina {page}")

    for block in blocks:
        try:
            name = block.find("h3").get_text(strip=True)
            address = block.find("div", class_="address").get_text(strip=True)
            cvr_label = block.find(text="CVR-nummer:")
            cvr = cvr_label.find_next().get_text(strip=True) if cvr_label else ""
            status_label = block.find(text="Status:")
            status = status_label.find_next().get_text(strip=True) if status_label else ""
            form_label = block.find(text="Virksomhedsform:")
            form = form_label.find_next().get_text(strip=True) if form_label else ""

            all_companies.append({
                "Name": name,
                "Address": address,
                "CVR": cvr,
                "Status": status,
                "Company Type": form
            })
        except Exception as e:
            print("Errore parsing blocco:", e)

    page += 1
    time.sleep(1)

driver.quit()

df = pd.DataFrame(all_companies)
df.to_csv("aziende_copenhagen.csv", index=False)
print(f"✅ Salvati {len(df)} risultati in 'aziende_copenhagen.csv'")
