"""
stock_tracker.py — A clean, modern stock dashboard built with Streamlit + yfinance + Plotly.

Setup:
  pip install streamlit yfinance plotly pandas

Run:
  streamlit run stock_tracker.py
"""

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Import fonts */
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

  /* Root variables */
  :root {
    --bg:        #0d0f14;
    --surface:   #141720;
    --border:    #1f2435;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --accent:    #38bdf8;
    --green:     #22c55e;
    --red:       #ef4444;
    --orange:    #f97316;
  }

  /* Global resets */
  html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'IBM Plex Sans', sans-serif;
  }

  /* Header */
  .dash-header {
    display: flex;
    align-items: baseline;
    gap: 14px;
    margin-bottom: 6px;
  }
  .dash-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.55rem;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: -0.02em;
  }
  .dash-subtitle {
    font-size: 0.82rem;
    color: var(--muted);
    font-weight: 300;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }
  .dash-timestamp {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: var(--muted);
    margin-bottom: 20px;
  }

  /* Stock card */
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px 18px 14px 18px;
    margin-bottom: 4px;
    transition: border-color 0.2s;
  }
  .card:hover { border-color: #2d3752; }

  .card-ticker {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 0.04em;
  }
  .card-name {
    font-size: 0.72rem;
    color: var(--muted);
    margin-top: 1px;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .price-row {
    display: flex;
    align-items: baseline;
    gap: 10px;
    margin-bottom: 4px;
  }
  .price-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.45rem;
    font-weight: 600;
    color: var(--text);
  }
  .price-change-pos {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--green);
    background: rgba(34,197,94,0.10);
    padding: 2px 7px;
    border-radius: 4px;
  }
  .price-change-neg {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--red);
    background: rgba(239,68,68,0.10);
    padding: 2px 7px;
    border-radius: 4px;
  }

  /* Metrics row */
  .metrics-row {
    display: flex;
    gap: 24px;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid var(--border);
  }
  .metric-block {}
  .metric-label {
    font-size: 0.65rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 2px;
  }
  .metric-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    color: var(--text);
  }

  /* Error card */
  .error-card {
    background: rgba(239,68,68,0.07);
    border: 1px solid rgba(239,68,68,0.25);
    border-radius: 10px;
    padding: 24px 18px;
    text-align: center;
    color: var(--red);
    font-size: 0.82rem;
  }
  .error-icon { font-size: 1.6rem; margin-bottom: 8px; }

  /* Streamlit button overrides */
  .stButton > button {
    background: var(--accent) !important;
    color: #0d0f14 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 8px 22px !important;
    transition: opacity 0.15s !important;
  }
  .stButton > button:hover { opacity: 0.85 !important; }

  /* Hide streamlit default chrome */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 28px !important; padding-bottom: 28px !important; }

  /* Radio buttons → timeframe pills */
  div[data-testid="stHorizontalBlock"] div[role="radiogroup"] {
    flex-direction: row !important;
    gap: 6px;
  }
  div[role="radiogroup"] label {
    background: #1a1f2e !important;
    border: 1px solid var(--border) !important;
    border-radius: 5px !important;
    padding: 3px 12px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    color: var(--muted) !important;
    cursor: pointer !important;
  }
  div[role="radiogroup"] label[data-checked="true"],
  div[role="radiogroup"] label:has(input:checked) {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: rgba(56,189,248,0.08) !important;
  }

  /* Divider */
  hr { border-color: var(--border) !important; margin: 20px 0 !important; }
</style>
""", unsafe_allow_html=True)


# ── Constants ─────────────────────────────────────────────────────────────────
TICKERS = {
    "TSLA":  "Tesla, Inc.",
    "META":  "Meta Platforms",
    "MU":    "Micron Technology",
    "WDC":   "Western Digital",
    "NVMI":  "Nova Ltd",
    "MRVL":  "Marvell Technology",
    "SOXX":  "iShares Semiconductor ETF",
    "SPY":   "SPDR S&P 500 ETF",
    "IAU":   "iShares Gold Trust",
    "RKLB":  "Rocket Lab Corp",
}

ETF_TICKERS = {"SOXX", "SPY", "IAU"}

CHART_COLOR_UP   = "#38bdf8"
CHART_COLOR_DOWN = "#ef4444"
CHART_FILL_UP    = "rgba(56,189,248,0.08)"
CHART_FILL_DOWN  = "rgba(239,68,68,0.08)"


# ── Data helpers ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=0, show_spinner=False)
def fetch_ticker_data(symbol: str):
    """
    Fetch price history, current price, change %, volume, and next earnings.
    Returns a dict or raises on failure.
    """
    ticker = yf.Ticker(symbol)

    # 5-day 30-min data (covers both 1D and 5D views)
    hist_5d = ticker.history(period="5d", interval="30m", auto_adjust=True)
    hist_1d = ticker.history(period="1d", interval="5m",  auto_adjust=True)

    if hist_5d.empty:
        raise ValueError(f"No price data returned for {symbol}")

    info = {}
    try:
        info = ticker.info or {}
    except Exception:
        pass

    # Current price
    current_price = info.get("currentPrice") or info.get("regularMarketPrice")
    if current_price is None and not hist_5d.empty:
        current_price = float(hist_5d["Close"].iloc[-1])

    # Change % (vs previous close)
    prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
    if prev_close is None and len(hist_5d) > 1:
        prev_close = float(hist_5d["Close"].iloc[-2])
    change_pct = ((current_price - prev_close) / prev_close * 100) if prev_close else 0.0

    # Volume
    volume = info.get("regularMarketVolume") or info.get("volume")
    if volume is None and not hist_5d.empty:
        volume = int(hist_5d["Volume"].iloc[-1]) if "Volume" in hist_5d.columns else 0

    # Next earnings date
    earnings_date = "N/A"
    if symbol not in ETF_TICKERS:
        try:
            cal = ticker.calendar
            if cal is not None:
                if isinstance(cal, dict):
                    ed = cal.get("Earnings Date")
                    if ed:
                        if isinstance(ed, (list, tuple)) and len(ed) > 0:
                            earnings_date = str(ed[0])[:10]
                        else:
                            earnings_date = str(ed)[:10]
                elif isinstance(cal, pd.DataFrame) and not cal.empty:
                    if "Earnings Date" in cal.index:
                        val = cal.loc["Earnings Date"].iloc[0]
                        earnings_date = str(val)[:10]
        except Exception:
            earnings_date = "Unavailable"

    return {
        "hist_1d":      hist_1d,
        "hist_5d":      hist_5d,
        "price":        current_price,
        "change_pct":   change_pct,
        "volume":       volume,
        "earnings":     earnings_date,
    }


def fmt_volume(v) -> str:
    if v is None:
        return "—"
    v = int(v)
    if v >= 1_000_000:
        return f"{v/1_000_000:.2f}M"
    if v >= 1_000:
        return f"{v/1_000:.1f}K"
    return str(v)


def fmt_price(p) -> str:
    if p is None:
        return "—"
    return f"${float(p):,.2f}"


def make_chart(df: pd.DataFrame, ticker: str, up: bool) -> go.Figure:
    color = CHART_COLOR_UP if up else CHART_COLOR_DOWN
    fill  = CHART_FILL_UP  if up else CHART_FILL_DOWN

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["Close"],
        mode="lines",
        line=dict(color=color, width=1.8, shape="spline"),
        fill="tozeroy",
        fillcolor=fill,
        hovertemplate="<b>%{x|%b %d %H:%M}</b><br>$%{y:,.2f}<extra></extra>",
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=4, b=0),
        height=160,
        xaxis=dict(
            showgrid=False, zeroline=False,
            showticklabels=False, showline=False,
        ),
        yaxis=dict(
            showgrid=True, zeroline=False,
            gridcolor="rgba(255,255,255,0.04)",
            tickfont=dict(family="IBM Plex Mono", size=9, color="#64748b"),
            showline=False, tickprefix="$",
            side="right",
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#1a1f2e", bordercolor="#2d3752",
            font=dict(family="IBM Plex Mono", size=11, color="#e2e8f0"),
        ),
        showlegend=False,
    )
    return fig


# ── App state ─────────────────────────────────────────────────────────────────

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()
if "cache_key" not in st.session_state:
    st.session_state.cache_key = 0

# Persist timeframe selections per ticker
for sym in TICKERS:
    if f"tf_{sym}" not in st.session_state:
        st.session_state[f"tf_{sym}"] = "1D"


# ── Header ────────────────────────────────────────────────────────────────────
header_col, btn_col = st.columns([5, 1])

with header_col:
    st.markdown("""
    <div class="dash-header">
      <span class="dash-title">MARKET TRACKER</span>
      <span class="dash-subtitle">Live Quotes · 10 Assets</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(
        f'<div class="dash-timestamp">Last refreshed: '
        f'{st.session_state.last_refresh.strftime("%b %d, %Y · %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )

with btn_col:
    st.write("")  # vertical spacer
    if st.button("⟳  Refresh Data"):
        fetch_ticker_data.clear()
        st.session_state.last_refresh = datetime.now()
        st.session_state.cache_key += 1
        st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)


# ── Grid ──────────────────────────────────────────────────────────────────────
tickers_list = list(TICKERS.keys())
COLS = 2  # cards per row

for row_start in range(0, len(tickers_list), COLS):
    row_tickers = tickers_list[row_start : row_start + COLS]
    cols = st.columns(COLS, gap="medium")

    for col, sym in zip(cols, row_tickers):
        with col:
            # ── Fetch data ────────────────────────────────────────────────
            try:
                data = fetch_ticker_data(sym)
                error = None
            except Exception as e:
                data = None
                error = str(e)

            # ── Error state ───────────────────────────────────────────────
            if error or data is None:
                st.markdown(f"""
                <div class="error-card">
                  <div class="error-icon">⚠</div>
                  <strong>{sym}</strong> — {TICKERS[sym]}<br><br>
                  Unable to load data.<br>
                  <small style="color:#94a3b8">{error or 'Unknown error'}</small>
                </div>
                """, unsafe_allow_html=True)
                continue

            # ── Price & change ────────────────────────────────────────────
            price      = data["price"]
            chg        = data["change_pct"]
            is_up      = chg >= 0
            chg_class  = "price-change-pos" if is_up else "price-change-neg"
            chg_symbol = "▲" if is_up else "▼"

            st.markdown(f"""
            <div class="card">
              <div class="card-ticker">{sym}</div>
              <div class="card-name">{TICKERS[sym]}</div>
              <div class="price-row">
                <span class="price-value">{fmt_price(price)}</span>
                <span class="{chg_class}">{chg_symbol} {abs(chg):.2f}%</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Timeframe selector ─────────────────────────────────────────
            tf_key = f"tf_{sym}"
            tf = st.radio(
                label="",
                options=["1D", "5D"],
                index=0 if st.session_state[tf_key] == "1D" else 1,
                horizontal=True,
                key=f"radio_{sym}_{st.session_state.cache_key}",
                label_visibility="collapsed",
            )
            st.session_state[tf_key] = tf

            # ── Chart ──────────────────────────────────────────────────────
            hist = data["hist_1d"] if tf == "1D" else data["hist_5d"]

            if hist is None or hist.empty:
                st.caption("No chart data available for this period.")
            else:
                fig = make_chart(hist, sym, is_up)
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False},
                    key=f"chart_{sym}_{tf}_{st.session_state.cache_key}",
                )

            # ── Metrics ────────────────────────────────────────────────────
            earnings_label = "Not Applicable" if sym in ETF_TICKERS else data["earnings"]

            st.markdown(f"""
            <div class="metrics-row">
              <div class="metric-block">
                <div class="metric-label">Daily Volume</div>
                <div class="metric-value">{fmt_volume(data['volume'])}</div>
              </div>
              <div class="metric-block">
                <div class="metric-label">Next Earnings</div>
                <div class="metric-value">{earnings_label}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.write("")  # row spacing
