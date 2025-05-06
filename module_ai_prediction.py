
import streamlit as st
import yfinance as yf
import pandas as pd

st.subheader("🤖 Previsione direzione prezzo (prossimi 5 giorni)")

def predici_direzione(ticker):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1mo")
        if data.empty or len(data) < 10:
            return "📉 Dati insufficienti per previsione"

        # Calcolo media mobile e direzione recente
        data["MA5"] = data["Close"].rolling(window=5).mean()
        ultimo_prezzo = data["Close"].iloc[-1]
        media_recente = data["MA5"].iloc[-1]

        direzione = "📈 Probabile salita" if ultimo_prezzo > media_recente else "📉 Probabile discesa"
        confidenza = abs((ultimo_prezzo - media_recente) / media_recente) * 100

        return f"{direzione} con confidenza stimata del {confidenza:.1f}%"
    except Exception as e:
        return f"Errore previsione: {e}"

ticker = st.session_state.get("ticker_ai", st.text_input("Ticker per previsione AI", value="AAPL"))
st.session_state["ticker_ai"] = ticker

if ticker:
    risultato = predici_direzione(ticker)
    st.info(risultato)
