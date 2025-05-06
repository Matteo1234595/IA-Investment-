
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
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
    "Dashboard", "Analisi singola azienda", "Filtri aziende", 
    "Portafoglio simulato", "Esporta dati", "Impostazioni"
])

# 🔧 Funzioni utili
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
    if value == "N/A": return f"**{label}:** {value}"
    color = "green" if (value > 0 if positive else value < 0) else "red"
    return f"<span style='color:{color}'><strong>{label}: {format_val(value)}</strong></span>"

def get_news(company):
    try:
        url = f"https://news.google.com/rss/search?q={company}+borsa+site:ansa.it+OR+site:ilsole24ore.com&hl=it&gl=IT&ceid=IT:it"
        res = requests.get(url)
        soup = BeautifulSoup(res.content, features="xml")
        items = soup.findAll("item")[:5]
        news = [item.title.text for item in items]
        return news
    except:
        return []

def analizza_titolo(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    name = info.get("longName", ticker)
    price = info.get("currentPrice", None)
    pe = info.get("trailingPE", None)
    roe = info.get("returnOnEquity", None)
    if roe: roe *= 100
    debt = info.get("debtToEquity", None)
    fcf = info.get("freeCashflow", None)
    dy = info.get("dividendYield", None)
    if dy: dy *= 100
    dr = info.get("dividendRate", None)

    st.subheader(f"📊 Dati fondamentali per {name}")
    st.markdown(colored_text("Prezzo attuale", price), unsafe_allow_html=True)
    st.markdown(colored_text("P/E", pe), unsafe_allow_html=True)
    st.markdown(colored_text("ROE (%)", roe), unsafe_allow_html=True)
    st.markdown(colored_text("Debito/Equity", debt, positive=False), unsafe_allow_html=True)
    st.markdown(colored_text("Free Cash Flow", fcf), unsafe_allow_html=True)
    st.markdown(colored_text("Dividendo %", dy), unsafe_allow_html=True)
    st.markdown(colored_text("Dividendo annuale", dr), unsafe_allow_html=True)

    score = 0
    if pe and 8 < pe < 25: score += 1
    if roe and roe > 15: score += 1
    if debt and debt < 100: score += 1
    if fcf and fcf > 0: score += 1
    st.metric("Buffett Score", f"{score}/4")

    st.subheader("📈 Andamento e media")
    for periodo in [("6 mesi", "6mo"), ("12 mesi", "1y")]:
        nome, yf_period = periodo
        hist = stock.history(period=yf_period)
        if not hist.empty and price:
            st.line_chart(hist["Close"])
            media = hist["Close"].mean()
            diff = (price - media) / media * 100
            if diff < -10:
                st.success(f"🟢 [{nome}] Prezzo sottovalutato del {abs(diff):.1f}% rispetto alla media")
            elif diff > 10:
                st.error(f"🔴 [{nome}] Prezzo sopravvalutato del {abs(diff):.1f}% rispetto alla media")
            else:
                st.info(f"🟡 [{nome}] Prezzo nella norma (±10%) rispetto alla media")

    st.subheader("🤖 AI: previsione prossimi 5 giorni")
    data = stock.history(period="1mo")
    if not data.empty and len(data) >= 10:
        data["MA5"] = data["Close"].rolling(window=5).mean()
        ultimo_prezzo = data["Close"].iloc[-1]
        media_recente = data["MA5"].iloc[-1]
        direzione = "📈 Probabile salita" if ultimo_prezzo > media_recente else "📉 Probabile discesa"
        confidenza = abs((ultimo_prezzo - media_recente) / media_recente) * 100
        st.info(f"{direzione} con confidenza stimata del {confidenza:.1f}%")
    else:
        st.warning("Dati insufficienti per la previsione AI.")

    st.subheader("📰 Notizie recenti")
    news = get_news(name)
    for n in news: st.markdown(f"- {n}")

# ✅ Sezioni dell'app
if menu == "Dashboard":
    st.subheader("📈 Panoramica di mercato")
    st.write("🚧 In sviluppo: indici principali, sentiment, novità settore")
elif menu == "Analisi singola azienda":
    ticker = st.text_input("Inserisci ticker azienda (es: ENI.MI, AAPL)", value="AAPL")
    if ticker: analizza_titolo(ticker)
elif menu == "Filtri aziende":
    st.subheader("🔍 Filtri (score, settore, paese)")
    st.write("🚧 In sviluppo: filtro multiplo su aziende italiane e USA")
elif menu == "Portafoglio simulato":
    st.subheader("💼 Crea il tuo portafoglio")
    st.write("🚧 In sviluppo: scegli più titoli, visualizza performance attese")
elif menu == "Esporta dati":
    st.subheader("📤 Esporta i tuoi risultati")
    st.write("🚧 PDF e Excel export in arrivo")
elif menu == "Impostazioni":
    st.subheader("⚙️ Impostazioni app")
    st.write("Lingua, tema, logo personalizzato – in sviluppo")
