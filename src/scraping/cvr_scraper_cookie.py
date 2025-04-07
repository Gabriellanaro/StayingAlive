
import requests
import pandas as pd
import time

url = "https://datacvr.virk.dk/gateway/soeg/fritekst"

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Referer": "https://datacvr.virk.dk/soegeresultater?branchekode=561110&region=29190623",
    "Origin": "https://datacvr.virk.dk",
    "Accept": "application/json, text/plain, */*",
    "X-Requested-With": "XMLHttpRequest"
}

cookies = {
    "S9SESSIONID": "848EDB9011529E3D3BDFA41C492FEEFE",
}

def get_companies_page(page_index):
    payload = {
        "fritekstCommand": {
            "soegOrd": "",
            "sideIndex": str(page_index),
            "enhedstype": "",
            "kommune": [],
            "region": ["29190623"],
            "antalAnsatte": [],
            "branchekode": "561110",
            "ophoersdatoFra": "",
            "ophoersdatoTil": "",
            "personrolle": [],
            "size": 100,
            "sortering": "",
            "startdatoFra": "",
            "startdatoTil": "",
            "virksomhedsform": [],
            "virksomhedsmarkering": [],
            "virksomhedsstatus": []
        }
    }

    response = requests.post(url, headers=headers, cookies=cookies, json=payload)
    if response.status_code == 200:
        return response.json().get("enheder", [])
    else:
        print(f"❌ Errore {response.status_code}")
        return []

all_companies = []
page = 0

while True:
    print(f"🔄 Pagina {page}")
    companies = get_companies_page(page)
    if not companies:
        break
    all_companies.extend(companies)
    page += 1
    time.sleep(1)

df = pd.DataFrame(all_companies)
df.to_csv("aziende_ristoranti_copenhagen.csv", index=False)
print(f"✅ Salvate {len(df)} aziende in 'aziende_ristoranti_copenhagen.csv'")
