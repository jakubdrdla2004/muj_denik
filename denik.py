import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime

# Nastavení širšího rozložení, ať se lístečky vejdou vedle sebe
st.set_page_config(page_title="Můj deníček", page_icon="📌", layout="centered")

# --- VIZUÁLNÍ STYLY (Design nástěnky a lístečků) ---
st.markdown("""
<style>
/* Pozadí aplikace - jemná nástěnka */
.stApp {
    background-color: #f4eee8;
}
/* Vzhled textových polí jako žluté lístečky (Post-it) */
.stTextArea textarea {
    background-color: #fdfd96;
    color: #2b2b2b;
    border-radius: 2px;
    box-shadow: 3px 3px 10px rgba(0,0,0,0.1);
    border: none !important;
    padding: 15px;
    font-size: 16px;
    min-height: 120px;
}
/* Reakce lístečku při psaní */
.stTextArea textarea:focus {
    box-shadow: 5px 5px 15px rgba(0,0,0,0.2) !important;
    background-color: #fffbc4;
}
/* Změna písma u popisků (otázek) */
.stTextArea p, .stRadio p {
    font-weight: bold !important;
    color: #4a4a4a !important;
    font-size: 15px !important;
}
/* Rámeček pro emotikony */
div.row-widget.stRadio > div {
    background-color: #fdfd96;
    padding: 15px;
    border-radius: 2px;
    box-shadow: 3px 3px 10px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

st.title("Můj dnešní den 📌")

# --- 1. PŘIPOJENÍ K TABULCE ---
# Funkce cache zajistí, že se připojení naváže jen jednou a neztěžuje se telefon
@st.cache_resource
def init_connection():
    key_dict = json.loads(st.secrets["google_json_key"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(key_dict, scopes=scopes)
    return gspread.authorize(credentials)

try:
    gc = init_connection()
    sheet = gc.open("Muj_Denik_Data").sheet1
except Exception as e:
    st.error("Nepodařilo se připojit k tabulce. Zkontrolujte tajný klíč.")
    st.stop()

# --- 2. LOGIKA UKLÁDÁNÍ A NAČÍTÁNÍ (AUTOSAVE) ---
today_str = datetime.today().strftime("%d.%m.%Y")

# Tato funkce se spustí skrytě pokaždé, když kliknete mimo textové pole
def autosave():
    new_row = [
        today_str,
        st.session_state.radost_mne,
        st.session_state.radost_ostatnim,
        st.session_state.vdecnost,
        st.session_state.progress,
        st.session_state.modlitba,
        st.session_state.overall
    ]
    try:
        # Uložení (přepsání) aktuálního řádku pro dnešek
        sheet.update(values=[new_row], range_name=f"A{st.session_state.row_index}:G{st.session_state.row_index}")
        st.toast("Záznam úspěšně uložen! 📌", icon="✅")
    except Exception as e:
        st.toast("Chyba při ukládání, zkuste to znovu.", icon="❌")

# Zjištění, zda už máme dnešek načtený v paměti telefonu
if "initialized_date" not in st.session_state or st.session_state.initialized_date != today_str:
    dates = sheet.col_values(1) # Přečte všechny datumy z prvního sloupce
    
    if today_str in dates:
        # Záznam pro dnešek už existuje, načteme z něj rozepsaná data
        st.session_state.row_index = dates.index(today_str) + 1
        row_data = sheet.row_values(st.session_state.row_index)
        row_data += [""] * (7 - len(row_data)) # Ochrana, pokud jsou na konci prázdné buňky
    else:
        # Je nový den! Vytvoříme prázdný řádek
        st.session_state.row_index = len(dates) + 1
        row_data = [today_str, "", "", "", "", "", "☀️"]
        sheet.append_row(row_data)
    
    # Uložení dat do paměti aplikace
    st.session_state.radost_mne = row_data[1]
    st.session_state.radost_ostatnim = row_data[2]
    st.session_state.vdecnost = row_data[3]
    st.session_state.progress = row_data[4]
    st.session_state.modlitba = row_data[5]
    st.session_state.overall = row_data[6] if row_data[6] in ["☀️", "☁️"] else "☀️"
    
    st.session_state.initialized_date = today_str

# --- 3. VYKRESLENÍ NÁSTĚNKY ---
st.write(f"**Lístečky pro den:** {today_str}")

# Rozdělení obrazovky na dva sloupce pro efekt nástěnky
col1, col2 = st.columns(2)

# Všimněte si, že každé pole má 'key' odpovídající paměti a povel 'on_change=autosave'
with col1:
    st.text_area("Čím jsem si dnes udělal radost?", key="radost_mne", on_change=autosave)
    st.text_area("Co jsem dnes udělal pro ostatní?", key="radost_ostatnim", on_change=autosave)
    st.text_area("Za co jsem dnes vděčný?", key="vdecnost", on_change=autosave)

with col2:
    st.text_area("Jaký jsem udělal pokrok ve škole?", key="progress", on_change=autosave)
    st.text_area("Jak jsem dnešní den prožil s Bohem?", key="modlitba", on_change=autosave)
    st.radio("Jaký mám ze sebe dnes pocit?", ["☀️", "☁️"], horizontal=True, key="overall", on_change=autosave)
