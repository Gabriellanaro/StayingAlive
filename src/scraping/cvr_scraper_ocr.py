import time
import pytesseract
from PIL import Image
import pandas as pd
import cv2
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# === CONFIGURAZIONE ===
CHROMEDRIVER_PATH = r"C:\\programmi\\chromedriver\\chromedriver.exe"  # <- Modifica se necessario
TESSERACT_PATH = r"C:\\programmi\\Tesseract-OCR\\tesseract-ocr-w64-setup-5.5.0.20241111"  # <- Modifica se necessario

# === SETUP BROWSER ===
options = Options()
options.add_argument("--window-size=1920,1080")
# options.add_argument("--headless")  # attivalo se vuoi browser invisibile

driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)

# === APERTURA PAGINA E SCREENSHOT ===
url = "https://datacvr.virk.dk/soegeresultater?branchekode=561110&region=29190623"
driver.get(url)
time.sleep(5)  # attesa per caricamento contenuti

# Screenshot della finestra visibile
screenshot_path = "screenshot.png"
driver.save_screenshot(screenshot_path)
driver.quit()

# === OCR CON TESSERACT ===
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Carica l'immagine
image = cv2.imread(screenshot_path)

# Preprocessing: grigio + soglia
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

# Salva immagine processata (opzionale)
cv2.imwrite("screenshot_processed.png", gray)

# Estrai testo con OCR
text = pytesseract.image_to_string(gray, lang="eng")

# Salva testo grezzo in CSV (una riga per linea)
lines = [line.strip() for line in text.split("\n") if line.strip()]
df = pd.DataFrame(lines, columns=["Estratto OCR"])
df.to_csv("ocr_aziende.csv", index=False)

print("✅ OCR completato. File salvato in 'ocr_aziende.csv'")
