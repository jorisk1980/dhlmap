import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="DHL Adres Filter", page_icon="🚚")
st.title("🚚 DHL Adres Ontdubbeling")

if 'adressen_lijst' not in st.session_state:
    st.session_state.adressen_lijst = []

st.write("1. Maak een foto van je lijst met je normale camera-app.")
st.write("2. Gebruik **Google Lens** (of de 'tekst selecteren' functie in je galerij) om de tekst te kopiëren.")
st.write("3. Plak de tekst hieronder.")

plak_tekst = st.text_area("Plak hier de gekopieerde tekst van je vellen", height=200)

if st.button("Adressen Toevoegen"):
    # Zoek naar postcodes (4 cijfers, 2 letters) als ankerpunt
    pattern = re.compile(r"([A-Z0-9\s\-]+?\d+[A-Z\s\-]*)\s+(\d{4}\s?[A-Z]{2})")
    matches = pattern.findall(plak_tekst)
    
    nieuwe_teller = 0
    for match in matches:
        # We pakken de straat + huisnummer en de postcode
        schon_adres = f"{match[0].strip()} {match[1].strip()}".replace('\n', ' ')
        if schon_adres not in st.session_state.adressen_lijst:
            st.session_state.adressen_lijst.append(schon_adres)
            nieuwe_teller += 1
            
    st.success(f"Toegevoegd: {nieuwe_teller} nieuwe unieke adressen.")

# Resultaten tonen
if st.session_state.adressen_lijst:
    df = pd.DataFrame(st.session_state.adressen_lijst, columns=["Adres"])
    st.subheader(f"Totaal overzicht: {len(df)} unieke adressen")
    st.dataframe(df, use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV voor MyMaps", data=csv, file_name="dhl_mymaps.csv", mime='text/csv')

if st.button("Lijst wissen"):
    st.session_state.adressen_lijst = []
    st.rerun()
