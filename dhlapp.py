import streamlit as st
import pandas as pd
import easyocr
from PIL import Image
import numpy as np
import re

st.set_page_config(page_title="DHL Adres Scanner", layout="wide")
st.title("🚚 DHL Multi-Scan Tool")

@st.cache_resource
def load_reader():
    return easyocr.Reader(['nl'])

reader = load_reader()

if 'adressen_lijst' not in st.session_state:
    st.session_state.adressen_lijst = []

st.info("Tip: Maak foto's van DICHTBIJ. Het geeft niet als het vel er maar half op staat. De app verzamelt alles.")

foto = st.camera_input("Scan een deel van het vel")

if foto:
    with st.spinner('Tekst herkennen...'):
        img = Image.open(foto)
        # Optimalisatie: Maak afbeelding zwart-wit voor betere OCR
        img = img.convert('L') 
        img_np = np.array(img)
        
        result = reader.readtext(img_np, detail=0)
        tekst_blok = " ".join(result)
        
        # We zoeken naar de combinatie: Straat + Huisnummer + Postcode
        # Dit patroon is flexibeler voor leesfouten
        pattern = re.compile(r"([A-Z\s\-]+?\d+[A-Z\s\-]*)\s+(\d{4}\s?[A-Z]{2})")
        matches = pattern.findall(tekst_blok)
        
        for match in matches:
            adres = f"{match[0].strip()} {match[1].strip()}"
            if adres not in st.session_state.adressen_lijst:
                st.session_state.adressen_lijst.append(adres)
        
        st.success(f"Totaal aantal unieke adressen verzameld: {len(st.session_state.adressen_lijst)}")

# Weergave van de resultaten
if st.session_state.adressen_lijst:
    df = pd.DataFrame(st.session_state.adressen_lijst, columns=["Adres & Postcode"])
    st.dataframe(df, use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV voor MyMaps", data=csv, file_name="dhl_mymaps.csv", mime='text/csv')

if st.button("Lijst wissen"):
    st.session_state.adressen_lijst = []
    st.rerun()
