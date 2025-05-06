
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# ⚙️ Configurazione iniziale
st.set_page_config(page_title="Buffett AI Enterprise", layout="wide")

# 🎨 Logo e tema
logo_url = "https://cdn.pixabay.com/photo/2017/08/10/07/32/stock-2619124_1280.jpg"
st.image(logo_url, use_container_width=True)

tema_scuro = st.toggle("🌗 Tema scuro", value=False)
if tema_scuro:
    st.markdown('<style>body, .stApp {background-color: #1e1e1e; color: white;}</style>', unsafe_allow_html=True)

st.title("💼 Buffett AI – Enterprise Edition")

menu = st.sidebar.selectbox("📊 Seleziona sezione", [
    "Dashboard", "Analisi singola azienda"
])

# Dashboard
if menu == "Dashboard":
    st.subheader("📈 Panoramica Mercati Principali")

    indices = {
        "FTSE MIB (Italia)": "^FTSEMIB.MI",
        "NASDAQ 100 (USA)": "^NDX",
        "S&P 500 (USA)": "^GSPC",
        "DAX (Germania)": "^GDAXI"
    }

    col1, col2 = st.columns(2)
    for i, (nome, symbol) in enumerate(indices.items()):
        try:
            data = yf.Ticker(symbol).history(period="5d")
            if not data.empty and "Close" in data.columns:
                last_close = data["Close"].iloc[-1]
                first_close = data["Close"].iloc[0]
                delta = last_close - first_close
                pct = (delta / first_close) * 100
                val = f"{last_close:.2f}"
                dlt = f"{pct:+.2f}%"
            else:
                val = "N/D"
                dlt = "N/D"
        except:
            val = "N/D"
            dlt = "N/D"

        if i % 2 == 0:
            col1.metric(label=nome, value=val, delta=dlt)
        else:
            col2.metric(label=nome, value=val, delta=dlt)

    st.markdown("---")
    st.markdown("📰 Ultime notizie economiche globali")
    try:
        url = "https://news.google.com/rss/search?q=borsa+economia+site:reuters.com+OR+site:bloomberg.com&hl=it&gl=IT&ceid=IT:it"
        res = requests.get(url)
        soup = BeautifulSoup(res.content, features="xml")
        items = soup.findAll("item")[:5]
        for item in items:
            st.markdown(f"- {item.title.text}")
    except:
        st.warning("⚠️ Impossibile caricare le notizie globali.")

# Placeholder per altre sezioni
elif menu == "Analisi singola azienda":
    st.subheader("🚧 Analisi singola azienda in costruzione")
