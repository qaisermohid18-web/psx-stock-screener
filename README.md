# PSX Stock Screener

A stock screener for the Pakistan Stock Exchange (PSX) built with Python and Streamlit.

## Features
- Screen 25 major PSX stocks across 9 sectors
- Filter by sector, P/E ratio, price range, dividend yield, volume spike
- Interactive price chart with 20-day and 50-day moving averages
- Sector performance bar chart and market cap breakdown
- Sortable results table

## Setup

```bash
# 1. Clone / download this folder
# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

The app opens at http://localhost:8501

## Enabling live data

The app currently uses realistic mock data. To switch to live PSX prices:

1. The `load_all_stocks()` function in `app.py` has a comment showing the yfinance pattern.
2. PSX tickers on Yahoo Finance use the `.KA` suffix — e.g. `HBL.KA`, `OGDC.KA`.
3. Replace the mock data generation with:

```python
import yfinance as yf

def get_live_data(ticker):
    t = yf.Ticker(ticker + ".KA")
    hist = t.history(period="1y")
    info = t.info
    return hist, info
```

## Deploying to Streamlit Cloud (free)

1. Push this folder to a GitHub repo
2. Go to share.streamlit.io
3. Connect your repo and set `app.py` as the entry point
4. Deploy — you get a public shareable link

## Tech stack
- **Streamlit** — dashboard UI
- **Pandas** — data manipulation and filtering
- **Plotly** — interactive charts
- **yfinance** — live market data (when enabled)

## CV description (copy this)
> Built a PSX stock screener in Python covering 25+ equities across 9 sectors. Features include real-time filtering by P/E ratio, dividend yield, and volume spikes, with interactive price charts and moving average overlays. Deployed on Streamlit Cloud.
