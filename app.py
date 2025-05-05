
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import time

st.set_page_config(page_title="Buffett AI App", layout="centered")

st.title("📈 Buffett AI – Analizza qualsiasi azienda")
st.markdown("Scrivi il simbolo (ticker) di qualsiasi azienda, italiana o internazionale, per ricevere un'analisi completa con Buffett Score, grafico e notizie.")

# Input ticker
ticker = st.text_input("Inserisci il ticker dell'azienda (es: AAPL, TSLA, ENI.MI, UCG.MI)", value="AAPL")

if ticker:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Estrai dati fondamentali
        name = info.get("longName", ticker)
        price = info.get("currentPrice", "N/A")
        pe = info.get("trailingPE", None)
        roe = info.get("returnOnEquity", None)
        if roe: roe = roe * 100
        debt = info.get("debtToEquity", None)
        fcf = info.get("freeCashflow", None)

        # Calcolo Buffett Score
        score = 0
        if pe and 8 < pe < 25: score += 1
        if roe and roe > 15: score += 1
        if debt and debt < 100: score += 1
        if fcf and fcf > 0: score += 1

        st.subheader(f"📊 Dati fondamentali per {name}")
        st.write(f"**Prezzo attuale:** {price} €")
        st.write(f"**P/E:** {pe if pe else 'N/A'}")
        st.write(f"**ROE (%):** {roe if roe else 'N/A'}")
        st.write(f"**Debito/Equity:** {debt if debt else 'N/A'}")
        st.write(f"**Free Cash Flow:** {fcf if fcf else 'N/A'}")

        st.metric("💡 Buffett Score", f"{score}/4")
        if score == 4:
            st.success("✅ CONSIGLIO: BUY – Azienda eccellente")
        elif score >= 2:
            st.warning("⚠️ CONSIGLIO: HOLD – Azienda solida ma migliorabile")
        else:
            st.error("❌ CONSIGLIO: SELL – Non rispetta i criteri fondamentali")

        # Grafico prezzo
        st.subheader("📈 Andamento del prezzo (ultimi 6 mesi)")
        hist = stock.history(period="6mo")
        if not hist.empty:
            st.line_chart(hist["Close"])
        else:
            st.write("Grafico non disponibile.")

        # Notizie da Google News
        st.subheader("📰 Notizie recenti")
        def cerca_notizie(nome):
            try:
                query = nome.replace(" ", "+") + "+site:ansa.it+OR+site:ilsole24ore.com"
                url = f"https://www.google.com/search?q={query}&tbm=nws"
                headers = {"User-Agent": "Mozilla/5.0"}
                res = requests.get(url, headers=headers)
                soup = BeautifulSoup(res.text, "html.parser")
                articoli = soup.find_all("div", class_="BVG0Nb", limit=5)
                return [a.get_text() for a in articoli if a.get_text()]
            except:
                return []

        notizie = cerca_notizie(name)
        if notizie:
            for titolo in notizie:
                st.write("•", titolo)
        else:
            st.write("Nessuna notizia trovata.")
        time.sleep(1)

    except Exception as e:
        st.error(f"Errore durante l'analisi: {e}")
