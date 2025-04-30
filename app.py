import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# Set up the page
st.set_page_config(page_title="Nifty Support & Resistance Tracker", layout="wide")

# Top 20 Nifty 50 Stocks
TOP_20_NIFTY50_SYMBOLS = [
    "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TCS.NS",
    "ITC.NS", "LT.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS",
    "BHARTIARTL.NS", "HINDUNILVR.NS", "BAJFINANCE.NS", "ASIANPAINT.NS",
    "MARUTI.NS", "HCLTECH.NS", "SUNPHARMA.NS", "NTPC.NS", "TITAN.NS",
    "ULTRACEMCO.NS"
]

# Header
st.title("📈 Nifty 50 - Support & Resistance Dashboard")
st.markdown("_Live view of S/R levels, sorted by breakout potential._")

# Sidebar filters
with st.sidebar:
    st.header("⚙️ Settings")
    selected_columns = st.multiselect(
        "Select Columns to Display",
        options=[
            "Stock", "LTP", "Points to Next Resistance", "Pivot",
            "Resistance 1 (R1)", "Resistance 2 (R2)", "Resistance 3 (R3)",
            "Support 1 (S1)", "Support 2 (S2)", "Support 3 (S3)", "Breakout"
        ],
        default=["Stock", "LTP", "Points to Next Resistance", "Resistance 1 (R1)", "Support 1 (S1)", "Breakout"]
    )
    refresh = st.button("🔄 Refresh Now")

@st.cache_data(ttl=60)
def fetch_support_resistance(symbols):
    results = []
    for symbol in symbols:
        try:
            df = yf.download(symbol, period="5d", interval="1d", progress=False)
            st.text(f"Fetching {symbol}...")
            st.text(df.tail(2))

            if df.shape[0] < 2:
                continue
            
            high = float(df['High'].iloc[-2])
            low = float(df['Low'].iloc[-2])
            close = float(df['Close'].iloc[-2])
            ltp = float(df['Close'].iloc[-1])

            pivot = (high + low + close) / 3
            r1 = 2 * pivot - low
            r2 = pivot + (high - low)
            r3 = high + 2 * (pivot - low)
            s1 = 2 * pivot - high
            s2 = pivot - (high - low)
            s3 = low - 2 * (high - pivot)
            breakout = "🔺 Yes" if ltp > r1 else "🔹 No"

            points_to_r = next((round(r - ltp, 2) for r in [r1, r2, r3] if r > ltp), "✅ Above R3")

            results.append({
                "Stock": symbol.replace(".NS", ""),
                "LTP": round(ltp, 2),
                "Points to Next Resistance": points_to_r,
                "Pivot": round(pivot, 2),
                "Resistance 1 (R1)": round(r1, 2),
                "Resistance 2 (R2)": round(r2, 2),
                "Resistance 3 (R3)": round(r3, 2),
                "Support 1 (S1)": round(s1, 2),
                "Support 2 (S2)": round(s2, 2),
                "Support 3 (S3)": round(s3, 2),
                "Breakout": breakout
            })
        except Exception as e:
            st.warning(f"⚠️ Error fetching {symbol}: {e}")
    return pd.DataFrame(results)

if refresh:
    with st.spinner("📡 Fetching latest stock data..."):
        df = fetch_support_resistance(TOP_20_NIFTY50_SYMBOLS)
        if df.empty:
            st.error("No data fetched.")
        else:
            # Sort by points to next resistance
            def sort_key(val):
                try:
                    return float(val)
                except:
                    return float('inf')

            df['__sort__'] = df['Points to Next Resistance'].apply(sort_key)
            df = df.sort_values('__sort__').drop(columns="__sort__")

            st.success(f"✅ Updated at {datetime.now().strftime('%H:%M:%S')}")
            st.dataframe(df[selected_columns], use_container_width=True)

            # Export option
            csv = df[selected_columns].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name="nifty_s_r_levels.csv",
                mime="text/csv"
            )
else:
    st.info("Click **🔄 Refresh Now** to fetch live data.")

