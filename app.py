
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import requests
st.set_page_config(page_title="Buffett AI", layout="centered")
from bs4 import BeautifulSoup

# 🎨 Branding e Tema UI

st.markdown("""<style>
h1 {
    text-align: center;
}
</style>""", unsafe_allow_html=True)

# LOGO IMMAGINE MODERNA
logo_url = "https://cdn.pixabay.com/photo/2017/08/10/07/32/stock-2619124_1280.jpg"
st.image(logo_url, width=300, caption="Buffett AI – Market Analyzer", use_container_width=False)

# Toggle Tema Chiaro / Scuro
tema_scuro = st.toggle("🌗 Attiva tema scuro", value=False)

if tema_scuro:
    st.markdown(
        '''
        <style>
        body, .stApp {
            background-color: #1e1e1e;
            color: white;
        }
        </style>
        ''',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        '''
        <style>
        body, .stApp {
            background-color: white;
            color: black;
        }
        </style>
        ''',
        unsafe_allow_html=True
    )


st.title("📈 Buffett AI – Analisi tecnica, fondamentale e predittiva")

st.markdown("Analizza qualsiasi azienda (ITA o USA) con Buffett Score, grafici a 6 e 12 mesi, AI trend, dividendi, FCF e notizie in tempo reale.")

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

def predici_direzione(ticker):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1mo")
        if data.empty or len(data) < 10:
            return "📉 Dati insufficienti per previsione"
        data["MA5"] = data["Close"].rolling(window=5).mean()
        ultimo_prezzo = data["Close"].iloc[-1]
        media_recente = data["MA5"].iloc[-1]
        direzione = "📈 Probabile salita" if ultimo_prezzo > media_recente else "📉 Probabile discesa"
        confidenza = abs((ultimo_prezzo - media_recente) / media_recente) * 100
        return f"{direzione} con confidenza stimata del {confidenza:.1f}%"
    except Exception as e:
        return f"Errore previsione: {e}"

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

        # Grafici + alert
        st.subheader("📈 Grafici e Alert Prezzo")
        for periodo in [("6 mesi", "6mo"), ("12 mesi", "1y")]:
            nome, yf_period = periodo
            try:
                hist = stock.history(period=yf_period)
                st.line_chart(hist["Close"], height=300)
                if not hist.empty and price:
                    media = hist["Close"].mean()
                    diff = (price - media) / media * 100
                    if diff < -10:
                        st.success(f"🟢 [{nome}] Prezzo sottovalutato del {abs(diff):.1f}% rispetto alla media")
                    elif diff > 10:
                        st.error(f"🔴 [{nome}] Prezzo sopravvalutato del {abs(diff):.1f}% rispetto alla media")
                    else:
                        st.info(f"🟡 [{nome}] Prezzo nella norma (±10%) rispetto alla media")
            except:
                st.warning(f"⚠️ Grafico o dati non disponibili per {nome}")

        # Modulo AI predittivo
        st.subheader("🤖 AI: previsione prossimi 5 giorni")
        risultato = predici_direzione(ticker)
        st.info(risultato)

        # Notizie
        st.subheader("📰 Notizie recenti da fonti italiane")
        news = get_news(name)
        if news:
            for n in news:
                st.markdown(f"- {n}")
        else:
            st.write("Nessuna notizia trovata.")

    except Exception as e:
        st.error(f"Errore: {e}")


# 🔽 MODULI FUTURI - Placeholder per estensioni
# 📤 Export PDF report (in sviluppo)
# def export_to_pdf(data): pass  # TODO: implementa generazione PDF

# 📊 Export Excel (in sviluppo)
# def export_to_excel(data): pass  # TODO: salvataggio in xlsx

# 🔍 Filtri avanzati (es. per settore, score minimo)
# def filtra_aziende(df): pass  # TODO: UI per filtro score/settore

# 💼 Simulatore portafoglio (in sviluppo)
# def simula_portafoglio(aziende): pass  # TODO: simulazione e performance

# 🎨 Logo, branding personalizzato
# TODO: inserisci logo aziendale, tema colore, layout personalizzato
