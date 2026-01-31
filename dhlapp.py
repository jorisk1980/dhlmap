import streamlit as st
import pandas as pd
import easyocr
from PIL import Image
import numpy as np
import re

st.set_page_config(page_title="DHL Scanner", page_icon="🚚")
st.title("🚚 DHL Adres Scanner")

# Start de reader (wordt één keer geladen)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['nl'])

reader = load_reader()

if 'lijst_data' not in st.session_state:
    st.session_state.lijst_data = pd.DataFrame(columns=['Ontvanger', 'Adres', 'Plaats'])

foto = st.camera_input("Maak een foto van het DHL vel")

if foto:
    with st.spinner('De hele lijst scannen... dit duurt even...'):
        img = Image.open(foto)
        img_np = np.array(img)
        
        # Lees alle tekst op het blad
        result = reader.readtext(img_np, detail=0)
        volledige_tekst = " ".join(result)

        # We zoeken naar patronen: Postcode (4 cijfers, 2 letters) + Plaats
        # Dit is de meest betrouwbare manier om adressen te vinden op deze lijst
        pattern = r"([A-Z0-9\s\-]{3,})\s+([A-Z\s]+(?:\d+[\-\w]*))\s+(\d{4}\s?[A-Z]{2})\s+([A-Z\s]{2,})"
        matches = re.findall(pattern, volledige_tekst)

        nieuwe_rijen = []
        for match in matches:
            naam, straat, pc, stad = match
            nieuwe_rijen.append({
                "Ontvanger": naam.strip(),
                "Adres": f"{straat.strip()} {pc.strip()}",
                "Plaats": stad.strip()
            })
        
        if nieuwe_rijen:
            nieuw_df = pd.DataFrame(nieuwe_rijen)
            # Voeg toe aan bestaande lijst en ontdubbel direct
            st.session_state.lijst_data = pd.concat([st.session_state.lijst_data, nieuw_df]).drop_duplicates(subset=['Adres', 'Plaats']).reset_index(drop=True)
            st.success(f"Gevonden op dit vel: {len(nieuwe_rijen)} adressen.")
        else:
            st.warning("Geen adressen herkend. Probeer de foto iets dichterbij of met meer licht te maken.")

st.subheader("Gescande Adressen")
st.dataframe(st.session_state.lijst_data)

if not st.session_state.lijst_data.empty:
    csv = st.session_state.lijst_data.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV voor MyMaps", data=csv, file_name="mymaps_dhl.csv", mime='text/csv')

if st.button("Lijst wissen"):
    st.session_state.lijst_data = pd.DataFrame(columns=['Ontvanger', 'Adres', 'Plaats'])
    st.rerun()
