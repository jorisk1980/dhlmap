import streamlit as st
import pandas as pd
import easyocr
from PIL import Image
import numpy as np
import re

st.set_page_config(page_title="DHL Scanner", page_icon="🚚")
st.title("🚚 DHL Adres Scanner")

@st.cache_resource
def load_reader():
    # We voegen 'en' toe omdat DHL formulieren vaak Engelse termen bevatten
    return easyocr.Reader(['nl', 'en'])

reader = load_reader()

if 'lijst_data' not in st.session_state:
    st.session_state.lijst_data = pd.DataFrame(columns=['Gevonden Tekst'])

foto = st.camera_input("Maak een foto van het DHL vel")

if foto:
    with st.spinner('Bezig met lezen...'):
        img = Image.open(foto)
        img_np = np.array(img)
        
        # We lezen nu de tekst met lokatiegegevens
        result = reader.readtext(img_np, detail=0)
        
        if result:
            # We maken een simpele lijst van alles wat op een adres lijkt
            # We zoeken nu puur naar Postcodes (4 cijfers + 2 letters)
            # Dat is het ankerpunt van elk adres op jouw lijst
            pc_pattern = re.compile(r"\d{4}\s?[A-Z]{2}")
            
            gevonden_adressen = []
            for i, line in enumerate(result):
                if pc_pattern.search(line):
                    # Als we een postcode vinden, pakken we de tekst eromheen ook mee
                    context = ""
                    if i > 0: context += result[i-1] + " " # Vaak het adres
                    context += line # De postcode en vaak de plaats
                    gevonden_adressen.append({"Gevonden Tekst": context.strip()})
            
            if gevonden_adressen:
                nieuw_df = pd.DataFrame(gevonden_adressen)
                st.session_state.lijst_data = pd.concat([st.session_state.lijst_data, nieuw_df]).drop_duplicates().reset_index(drop=True)
                st.success(f"Er zijn {len(gevonden_adressen)} mogelijke adressen gevonden!")
            else:
                st.warning("Postcodes niet herkend. Probeer de camera dichterbij te houden.")
                st.write("Ruwe data voor diagnose:", result[:10]) # Laat zien wat hij wél ziet
        else:
            st.error("De scanner ziet helemaal geen tekst. Is de foto scherp?")

st.subheader("Gescande Data")
st.dataframe(st.session_state.lijst_data)

if st.button("Lijst wissen"):
    st.session_state.lijst_data = pd.DataFrame(columns=['Gevonden Tekst'])
    st.rerun()
