import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Buffett AI", layout="centered")

st.title("📈 Buffett AI – Analisi tecnica e fondamentale")
st.markdown("Analizza qualsiasi azienda (ITA o USA) con Buffett Score, grafici a 6 e 12 mesi, dividendi, FCF e notizie in tempo reale.")

ticker = st.text_input("Ticker azienda (es: ENI.MI, AAPL, UCG.MI)", value="AAPL")

def format_val(val):
    if val is None: return "N/A"
    if isinstance(val, (int, float)):
        abs_val = abs(val)
        if abs_val >= 1e9:
            return f"{val / 1e9:.2f}B"
        elif abs_val >= 1e6:
            return f"{val / 1e6:.2f}M"
        return f"{val:.2f}"
    return val

def colored_text(label, value, positive=True):
    if value == "N/A":
        return f"**{label}:** {value}"
    color = "green" if (value > 0 if positive else value < 0) else "red"
    return f"<span style='color:{color}'><strong>{label}: {format_val(value)}</strong></span>"

if ticker:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        name = info.get("longName", ticker)
        price = info.get("currentPrice", None)
        pe = info.get("trailingPE", None)
        roe = info.get("returnOnEquity", None)
        if roe: roe *= 100
        debt = info.get("debtToEquity", None)
        fcf = info.get("freeCashflow", None)
        dividend_yield = info.get("dividendYield", None)
        if dividend_yield: dividend_yield *= 100
        dividend_rate = info.get("dividendRate", None)

        st.subheader(f"📊 Fondamentali per {name}")
        st.markdown(colored_text("Prezzo attuale", price), unsafe_allow_html=True)
        st.markdown(colored_text("P/E", pe), unsafe_allow_html=True)
        st.markdown(colored_text("ROE (%)", roe), unsafe_allow_html=True)
        st.markdown(colored_text("Debito/Equity", debt, positive=False), unsafe_allow_html=True)
        st.markdown(colored_text("Free Cash Flow", fcf), unsafe_allow_html=True)
        st.markdown(colored_text("Dividendo %", dividend_yield), unsafe_allow_html=True)
        st.markdown(colored_text("Dividendo annuale", dividend_rate), unsafe_allow_html=True)

        score = 0
        if pe and 8 < pe < 25: score += 1
        if roe and roe > 15: score += 1
        if debt and debt < 100: score += 1
        if fcf and fcf > 0: score += 1

        st.metric("💡 Buffett Score", f"{score}/4")
        if score == 4:
            st.success("✅ BUY – Azienda eccellente")
        elif score >= 2:
            st.warning("⚠️ HOLD – Azienda solida ma migliorabile")
        else:
            st.error("❌ SELL – Non rispetta i criteri fondamentali")

        st.subheader("📈 Grafici di prezzo")
        for periodo in ["6mo", "1y"]:
            try:
                hist = stock.history(period=periodo)
                st.line_chart(hist["Close"], height=300)
            except:
                st.warning(f"Grafico non disponibile per {periodo}")

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

        for n in cerca_notizie(name):
            st.markdown(f"- {n}")

    except Exception as e:
        st.error(f"Errore: {e}")
