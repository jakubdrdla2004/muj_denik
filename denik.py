import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime

# Nastavení širšího rozložení
st.set_page_config(page_title="Můj deníček", page_icon="📌", layout="centered")

# --- VIZUÁLNÍ STYLY ---
st.markdown("""
<style>
/* Pozadí aplikace */
.stApp {
    background-color: #f4eee8;
}
/* Vzhled textových polí (Dnešní lístečky) */
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
/* Efekt při psaní */
.stTextArea textarea:focus {
    box-shadow: 5px 5px 15px rgba(0,0,0,0.2) !important;
    background-color: #fffbc4;
}
/* Vzhled starších lístečků (Historie - nelze editovat) */
.stTextArea textarea:disabled {
    background-color: #f9f9a5;
    color: #4a4a4a;
}
/* Změna písma u popisků */
.stTextArea p, .stRadio p, .stSelectbox p {
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

st.title("Můj deníček 📌")

# --- 1. PŘIPOJENÍ K TABULCE ---
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

# --- 2. ROZDĚLENÍ NA ZÁLOŽKY ---
tab1, tab2 = st.tabs(["📝 Dnešní den", "🕰️ Historie záznamů"])

# ==========================================
# ZÁLOŽKA 1: DNEŠNÍ DEN (S možností psaní)
# ==========================================
with tab1:
    today_str = datetime.today().strftime("%d.%m.%Y")

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
            sheet.update(values=[new_row], range_name=f"A{st.session_state.row_index}:G{st.session_state.row_index}")
            st.toast("Záznam úspěšně uložen! 📌", icon="✅")
        except Exception as e:
            st.toast("Chyba při ukládání, zkuste to znovu.", icon="❌")

    if "initialized_date" not in st.session_state or st.session_state.initialized_date != today_str:
        dates = sheet.col_values(1)
        
        if today_str in dates:
            st.session_state.row_index = dates.index(today_str) + 1
            row_data = sheet.row_values(st.session_state.row_index)
            row_data += [""] * (7 - len(row_data))
        else:
            st.session_state.row_index = len(dates) + 1
            row_data = [today_str, "", "", "", "", "", "☀️"]
            sheet.append_row(row_data)
        
        st.session_state.radost_mne = row_data[1]
        st.session_state.radost_ostatnim = row_data[2]
        st.session_state.vdecnost = row_data[3]
        st.session_state.progress = row_data[4]
        st.session_state.modlitba = row_data[5]
        st.session_state.overall = row_data[6] if row_data[6] in ["☀️", "☁️"] else "☀️"
        st.session_state.initialized_date = today_str

    st.write(f"**Lístečky pro den:** {today_str}")

    col1, col2 = st.columns(2)
    with col1:
        st.text_area("Čím jsem si dnes udělal radost?", key="radost_mne", on_change=autosave)
        st.text_area("Co jsem dnes udělal pro ostatní?", key="radost_ostatnim", on_change=autosave)
        st.text_area("Za co jsem dnes vděčný?", key="vdecnost", on_change=autosave)

    with col2:
        st.text_area("Jaký jsem udělal pokrok ve škole?", key="progress", on_change=autosave)
        st.text_area("Jak jsem dnešní den prožil s Bohem?", key="modlitba", on_change=autosave)
        st.radio("Jaký mám ze sebe dnes pocit?", ["☀️", "☁️"], horizontal=True, key="overall", on_change=autosave)


# ==========================================
# ZÁLOŽKA 2: HISTORIE (Pouze pro čtení)
# ==========================================
with tab2:
    st.write("**Nahlédněte do svých starších záznamů**")
    
    # Stáhneme všechna data z tabulky (včetně starých dnů)
    vsechna_data = sheet.get_all_values()
    
    # Vytvoříme seznam dnů (vynecháme první řádek, pokud je to hlavička "Datum")
    dostupne_dny = [radek[0] for radek in vsechna_data if len(radek) > 0 and radek[0] != "Datum"]
    
    # Otočíme seznam, abychom v menu viděli nejnovější dny jako první
    dostupne_dny.reverse()
    
    if dostupne_dny:
        vybrany_den = st.selectbox("Vyberte den z historie:", dostupne_dny)
        
        # Najdeme data pro vybraný den
        for radek in vsechna_data:
            if len(radek) > 0 and radek[0] == vybrany_den:
                # Doplníme prázdné buňky, pokud by jich bylo méně než 7
                radek += [""] * (7 - len(radek))
                
                st.write("---")
                h_col1, h_col2 = st.columns(2)
                
                # Parametr 'disabled=True' uzamkne pole, aby se nedalo upravovat
                with h_col1:
                    st.text_area("Čím jsem si dnes udělal radost?", value=radek[1], disabled=True, key="h1")
                    st.text_area("Co jsem dnes udělal pro ostatní?", value=radek[2], disabled=True, key="h2")
                    st.text_area("Za co jsem dnes vděčný?", value=radek[3], disabled=True, key="h3")
                
                with h_col2:
                    st.text_area("Jaký jsem udělal pokrok ve škole?", value=radek[4], disabled=True, key="h4")
                    st.text_area("Jak jsem dnešní den prožil s Bohem?", value=radek[5], disabled=True, key="h5")
                    st.text_area("Jaký mám ze sebe dnes pocit?", value=radek[6], disabled=True, key="h6")
                
                break
    else:
        st.info("Zatím tu nejsou žádné záznamy.")
