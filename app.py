import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PSX Stock Screener",
    page_icon="📈",
    layout="wide",
)

st.markdown("""
<style>
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 16px 20px;
        border: 1px solid #e9ecef;
    }
    .up { color: #1a7f4b; font-weight: 600; }
    .down { color: #c0392b; font-weight: 600; }
    .stDataFrame { font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# ── Data layer ────────────────────────────────────────────────────────────────
# When running locally, replace get_stock_data() with real yfinance calls.
# Example:
#   import yfinance as yf
#   def get_live_price(ticker):
#       t = yf.Ticker(ticker + ".KA")
#       hist = t.history(period="1y")
#       return hist

PSX_STOCKS = {
    # ticker: (name, sector)
    "HBL":    ("Habib Bank Limited",          "Banking"),
    "UBL":    ("United Bank Limited",          "Banking"),
    "MCB":    ("MCB Bank",                     "Banking"),
    "BAFL":   ("Bank Al-Falah",                "Banking"),
    "ABL":    ("Allied Bank Limited",          "Banking"),
    "OGDC":   ("Oil & Gas Dev. Company",       "Energy"),
    "PPL":    ("Pakistan Petroleum",           "Energy"),
    "PSO":    ("Pakistan State Oil",           "Energy"),
    "SNGP":   ("Sui Northern Gas",             "Energy"),
    "ENGRO":  ("Engro Corporation",            "Fertilizer"),
    "FFBL":   ("Fauji Fertilizer Bin Qasim",   "Fertilizer"),
    "FFC":    ("Fauji Fertilizer Company",     "Fertilizer"),
    "LUCK":   ("Lucky Cement",                 "Cement"),
    "DGKC":   ("D.G. Khan Cement",             "Cement"),
    "MLCF":   ("Maple Leaf Cement",            "Cement"),
    "HUBC":   ("Hub Power Company",            "Power"),
    "KAPCO":  ("Kot Addu Power",               "Power"),
    "NESTLE": ("Nestlé Pakistan",              "FMCG"),
    "UNILEVER":("Unilever Pakistan",           "FMCG"),
    "TRG":    ("TRG Pakistan",                 "Technology"),
    "SYS":    ("Systems Limited",              "Technology"),
    "NETSOL": ("NetSol Technologies",          "Technology"),
    "PKGS":   ("Packages Limited",             "Packaging"),
    "COLG":   ("Colgate-Palmolive Pak",        "Consumer"),
    "SEARL":  ("The Searle Company",           "Pharma"),
}

@st.cache_data(ttl=300)
def load_all_stocks():
    """
    Generates realistic mock data. 
    Replace this function body with yfinance calls for live data.
    """
    random.seed(42)
    rows = []
    for ticker, (name, sector) in PSX_STOCKS.items():
        base = random.uniform(50, 1200)
        prev = base * random.uniform(0.92, 1.08)
        high52 = base * random.uniform(1.05, 1.60)
        low52  = base * random.uniform(0.50, 0.95)
        volume = random.randint(200_000, 8_000_000)
        avg_vol = volume * random.uniform(0.7, 1.4)
        eps     = random.uniform(2, 80)
        pe      = round(base / eps, 1) if eps > 0 else None
        div_yield = random.uniform(0, 8)
        mktcap  = base * random.randint(100_000_000, 2_000_000_000) / 1e9
        change  = ((base - prev) / prev) * 100

        rows.append({
            "Ticker":       ticker,
            "Name":         name,
            "Sector":       sector,
            "Price (PKR)":  round(base, 2),
            "Change %":     round(change, 2),
            "P/E Ratio":    pe,
            "EPS":          round(eps, 2),
            "Div Yield %":  round(div_yield, 2),
            "52W High":     round(high52, 2),
            "52W Low":      round(low52, 2),
            "Volume":       volume,
            "Avg Volume":   int(avg_vol),
            "Mkt Cap (B)":  round(mktcap, 2),
        })

    return pd.DataFrame(rows)


@st.cache_data(ttl=300)
def load_price_history(ticker):
    """Mock 1-year daily price history. Replace with yfinance for live data."""
    random.seed(hash(ticker) % 10000)
    dates = pd.date_range(end=datetime.today(), periods=252, freq="B")
    price = 500.0
    closes = []
    for _ in dates:
        price *= random.uniform(0.975, 1.025)
        closes.append(round(price, 2))
    df = pd.DataFrame({"Date": dates, "Close": closes})
    df["MA20"]  = df["Close"].rolling(20).mean().round(2)
    df["MA50"]  = df["Close"].rolling(50).mean().round(2)
    return df


# ── Header ────────────────────────────────────────────────────────────────────
st.title("PSX Stock Screener")
st.caption("Pakistan Stock Exchange · Data updates every 5 min · Built with Python + Streamlit")

df = load_all_stocks()

# ── KPI strip ─────────────────────────────────────────────────────────────────
gainers = (df["Change %"] > 0).sum()
losers  = (df["Change %"] < 0).sum()
avg_pe  = df["P/E Ratio"].dropna().mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Stocks tracked", len(df))
c2.metric("Gainers today", gainers, delta=f"{gainers} up")
c3.metric("Losers today",  losers,  delta=f"-{losers} down", delta_color="inverse")
c4.metric("Avg P/E (market)", f"{avg_pe:.1f}x")

st.divider()

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.header("Filters")

sectors = ["All"] + sorted(df["Sector"].unique().tolist())
sel_sector = st.sidebar.selectbox("Sector", sectors)

pe_max = st.sidebar.slider("Max P/E Ratio", 0, 60, 40)

price_min, price_max = st.sidebar.slider(
    "Price range (PKR)",
    int(df["Price (PKR)"].min()),
    int(df["Price (PKR)"].max()),
    (int(df["Price (PKR)"].min()), int(df["Price (PKR)"].max())),
)

min_div = st.sidebar.slider("Min Dividend Yield %", 0.0, 8.0, 0.0, step=0.5)

vol_spike = st.sidebar.checkbox("Volume spike only (>1.3× avg)", value=False)

sort_by = st.sidebar.selectbox(
    "Sort by",
    ["Change %", "P/E Ratio", "Div Yield %", "Mkt Cap (B)", "Volume"],
)
sort_asc = st.sidebar.checkbox("Ascending", value=False)

# ── Apply filters ─────────────────────────────────────────────────────────────
filtered = df.copy()

if sel_sector != "All":
    filtered = filtered[filtered["Sector"] == sel_sector]

filtered = filtered[filtered["P/E Ratio"].fillna(999) <= pe_max]
filtered = filtered[filtered["Price (PKR)"].between(price_min, price_max)]
filtered = filtered[filtered["Div Yield %"] >= min_div]

if vol_spike:
    filtered = filtered[filtered["Volume"] > filtered["Avg Volume"] * 1.3]

filtered = filtered.sort_values(sort_by, ascending=sort_asc).reset_index(drop=True)

# ── Results table ─────────────────────────────────────────────────────────────
st.subheader(f"{len(filtered)} stocks match your filters")

def color_change(val):
    color = "#1a7f4b" if val > 0 else "#c0392b" if val < 0 else "gray"
    return f"color: {color}; font-weight: 600"

display_cols = [
    "Ticker", "Name", "Sector", "Price (PKR)", "Change %",
    "P/E Ratio", "EPS", "Div Yield %", "Mkt Cap (B)", "Volume",
]

styled = (
    filtered[display_cols]
    .style
    .map(color_change, subset=["Change %"])
    .format({
        "Price (PKR)": "{:.2f}",
        "Change %":    "{:+.2f}%",
        "P/E Ratio":   lambda x: f"{x:.1f}x" if pd.notna(x) else "—",
        "EPS":         "{:.2f}",
        "Div Yield %": "{:.1f}%",
        "Mkt Cap (B)": "₨{:.1f}B",
        "Volume":      "{:,.0f}",
    })
)

st.dataframe(styled, use_container_width=True, height=420)

st.divider()

# ── Stock detail chart ────────────────────────────────────────────────────────
st.subheader("Stock detail")
tickers_list = filtered["Ticker"].tolist()
if tickers_list:
    sel_ticker = st.selectbox("Select a stock to inspect", tickers_list)

    hist = load_price_history(sel_ticker)
    row  = df[df["Ticker"] == sel_ticker].iloc[0]

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Price",      f"₨{row['Price (PKR)']:.2f}", f"{row['Change %']:+.2f}%")
    m2.metric("P/E Ratio",  f"{row['P/E Ratio']:.1f}x" if pd.notna(row['P/E Ratio']) else "—")
    m3.metric("EPS",        f"₨{row['EPS']:.2f}")
    m4.metric("Div Yield",  f"{row['Div Yield %']:.1f}%")
    m5.metric("52W Range",  f"₨{row['52W Low']:.0f} – ₨{row['52W High']:.0f}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist["Date"], y=hist["Close"],
        name="Price", line=dict(color="#185FA5", width=2),
        fill="tozeroy", fillcolor="rgba(24,95,165,0.07)"
    ))
    fig.add_trace(go.Scatter(
        x=hist["Date"], y=hist["MA20"],
        name="MA 20", line=dict(color="#EF9F27", width=1.5, dash="dot")
    ))
    fig.add_trace(go.Scatter(
        x=hist["Date"], y=hist["MA50"],
        name="MA 50", line=dict(color="#D85A30", width=1.5, dash="dash")
    ))
    fig.update_layout(
        title=f"{sel_ticker} — {row['Name']} (1 year)",
        xaxis_title="Date", yaxis_title="Price (PKR)",
        legend=dict(orientation="h", y=1.08),
        height=380,
        margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0")
    fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No stocks match the current filters.")

st.divider()

# ── Sector breakdown chart ────────────────────────────────────────────────────
st.subheader("Sector overview")

col_a, col_b = st.columns(2)

with col_a:
    sector_avg = (
        df.groupby("Sector")["Change %"]
        .mean()
        .reset_index()
        .sort_values("Change %")
    )
    colors = ["#c0392b" if x < 0 else "#1a7f4b" for x in sector_avg["Change %"]]
    fig2 = go.Figure(go.Bar(
        x=sector_avg["Change %"],
        y=sector_avg["Sector"],
        orientation="h",
        marker_color=colors,
        text=sector_avg["Change %"].apply(lambda x: f"{x:+.2f}%"),
        textposition="outside",
    ))
    fig2.update_layout(
        title="Avg daily change by sector",
        height=340, margin=dict(l=10, r=40, t=40, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig2, use_container_width=True)

with col_b:
    sector_cap = df.groupby("Sector")["Mkt Cap (B)"].sum().reset_index()
    fig3 = px.pie(
        sector_cap, values="Mkt Cap (B)", names="Sector",
        title="Market cap distribution",
        color_discrete_sequence=px.colors.qualitative.Set2,
        hole=0.4,
    )
    fig3.update_layout(height=340, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig3, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.caption(
    "⚠️ Currently showing mock data. "
    "To enable live data: install yfinance and replace `load_all_stocks()` "
    "and `load_price_history()` in app.py with yfinance calls using the `.KA` suffix."
)
