import streamlit as st
import pandas as pd
import easyocr
from PIL import Image
import numpy as np

st.set_page_config(page_title="DHL naar MyMaps", page_icon="🚚")

st.title("🚚 DHL Adres Scanner")
st.write("Maak foto's van je vellen. Dubbele adressen worden automatisch verwijderd.")

# Initialiseer de OCR reader
reader = easyocr.Reader(['nl'])

if 'lijst_data' not in st.session_state:
    st.session_state.lijst_data = pd.DataFrame(columns=['Stop', 'Ontvanger', 'Ontvanger Adres', 'Plaats'])

# Camera input
foto = st.camera_input("Scan een DHL vel")

if foto:
    with st.spinner('Adresgegevens herkennen...'):
        img = Image.open(foto)
        # Hier komt de logica die de kolommen 'Stop', 'Ontvanger', 'Adres' en 'Plaats' uit de foto haalt
        # Voor nu simuleren we de extractie (OCR logica is uitgebreid)
        nieuwe_data = pd.DataFrame([
            {"Stop": "17", "Ontvanger": "TIMESAVERS", "Ontvanger Adres": "FRUITLAAN 20-30", "Plaats": "GOES"}
        ])
        
        # Toevoegen en ontdubbelen
        st.session_state.lijst_data = pd.concat([st.session_state.lijst_data, nieuwe_data]).drop_duplicates(subset=['Ontvanger Adres', 'Plaats'])
        st.success(f"Totaal aantal unieke adressen: {len(st.session_state.lijst_data)}")

st.dataframe(st.session_state.lijst_data)

if not st.session_state.lijst_data.empty:
    csv = st.session_state.lijst_data.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV voor MyMaps", data=csv, file_name="mymaps_export.csv", mime='text/csv')

if st.button("Lijst leegmaken"):
    st.session_state.lijst_data = pd.DataFrame(columns=['Stop', 'Ontvanger', 'Ontvanger Adres', 'Plaats'])
    st.rerun()
