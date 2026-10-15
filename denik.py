import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime

st.set_page_config(page_title="Můj deník", page_icon="🌱")
st.title("Na cestě za lepším já 🌱")

# 1. Připojení k Google Tabulce
try:
    # Aplikace si bezpečně načte tajný klíč z tzv. "Secrets" na serveru
    key_dict = json.loads(st.secrets["google_json_key"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(key_dict, scopes=scopes)
    gc = gspread.authorize(credentials)
    
    # Otevření tabulky (ZDE ZKONTROLUJTE, ŽE SE NÁZEV SHODUJE S VAŠÍ TABULKOU)
    sheet = gc.open("Muj_Denik_Data").sheet1
except Exception as e:
    st.error("Nepodařilo se připojit k tabulce. Zkontrolujte nastavení klíče.")
    st.stop()

# 2. Formulář pro váš deník
datum = st.date_input("Datum", datetime.today())
radost_mne = st.text_area("Co mi dnes udělalo radost?")
radost_ostatnim = st.text_area("Komu jsem udělal radost já?")
zlepseni = st.text_area("Co bych zítra mohl udělat o kousek lépe?")

# 3. Tlačítko pro odeslání dat
if st.button("Uložit záznam"):
    if radost_mne or radost_ostatnim or zlepseni:
        # Převedeme datum na český formát textu
        datum_str = datum.strftime("%d.%m.%Y")
        
        try:
            # Příkaz append_row přidá data na první volný řádek odspodu
            sheet.append_row([datum_str, radost_mne, radost_ostatnim, zlepseni])
            st.success("Záznam byl úspěšně uložen do vaší tabulky! 🌟")
        except Exception as e:
            st.error(f"Při ukládání nastala chyba: {e}")
    else:
        st.warning("Vyplňte alespoň jedno pole, než záznam uložíte.")