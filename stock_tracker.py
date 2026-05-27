"""
stock_tracker.py — Modern stock dashboard: Streamlit + yfinance + Plotly
Setup:  pip install streamlit yfinance plotly pandas
Run:    streamlit run stock_tracker.py
"""

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, date
import pytz

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Market Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --bg:        #0a0c10;
  --surface:   #111318;
  --surface2:  #181b24;
  --border:    #1e2332;
  --border2:   #252b3b;
  --text:      #f0f4ff;
  --text2:     #c8d0e0;
  --muted:     #38134a;
  --accent:    #3b9eff;
  --green:     #1fd97a;
  --green-bg:  rgba(31,217,122,0.12);
  --red:       #ff4d6a;
  --red-bg:    rgba(255,77,106,0.12);
  --amber:     #ffb347;
  --amber-bg:  rgba(255,179,71,0.10);
}

html, body, [class*="css"] {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif;
}

/* ── Header ── */
.dash-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 4px;
}
.dash-logo {
  width: 34px; height: 34px;
  background: linear-gradient(135deg, #3b9eff 0%, #7c3aed 100%);
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; line-height: 1;
}
.dash-title {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text);
  letter-spacing: -0.02em;
}
.dash-pill {
  font-size: 0.7rem;
  color: var(--accent);
  background: rgba(59,158,255,0.12);
  border: 1px solid rgba(59,158,255,0.25);
  border-radius: 20px;
  padding: 2px 10px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  font-weight: 500;
}
.dash-timestamp {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.72rem;
  color: var(--muted);
  margin-top: 4px;
  margin-bottom: 22px;
}

/* ── Card ── */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 18px 20px 16px;
  margin-bottom: 2px;
}

.card-top-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}
.card-ticker {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 1.45rem;
  font-weight: 600;
  color: var(--accent);
  letter-spacing: 0.04em;
}
.card-name {
  font-size: 1.08rem;
  color: var(--text2);
  margin-top: 3px;
  font-weight: 400;
}

/* ── Price block ── */
.price-main {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 1.7rem;
  font-weight: 600;
  color: var(--text);
  line-height: 1;
  margin-bottom: 8px;
  letter-spacing: -0.02em;
}
.change-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 4px;
}

/* Day change badge */
.badge {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.85rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.badge-label {
  font-family: 'Inter', sans-serif;
  font-size: 0.95rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  opacity: 0.8;
  margin-right: 2px;
}
.badge-up   { color: var(--green); background: var(--green-bg); }
.badge-down { color: var(--red);   background: var(--red-bg);   }
.badge-flat { color: var(--text2); background: var(--surface2); }

/* After-hours block */
.ah-block {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
  padding: 7px 10px;
  background: var(--surface2);
  border: 1px solid var(--border2);
  border-radius: 8px;
  flex-wrap: wrap;
}
.ah-label {
  font-size: 0.90rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  color: var(--amber);
  background: var(--amber-bg);
  padding: 2px 7px;
  border-radius: 4px;
  white-space: nowrap;
}
.ah-price {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--text);
}
.ah-chg-up   { font-family: 'IBM Plex Mono', monospace; font-size: 0.92rem; font-weight: 500; color: var(--green); }
.ah-chg-down { font-family: 'IBM Plex Mono', monospace; font-size: 0.92rem; font-weight: 500; color: var(--red); }
.ah-chg-flat { font-family: 'IBM Plex Mono', monospace; font-size: 0.92rem; font-weight: 500; color: var(--text2); }
.ah-na { font-family: 'IBM Plex Mono', monospace; font-size: 0.9rem; color: var(--muted); }

/* ── Metrics row ── */
.metrics-row {
  display: flex;
  gap: 0;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}
.metric-block {
  flex: 1;
  padding-right: 16px;
}
.metric-block + .metric-block {
  padding-left: 16px;
  border-left: 1px solid var(--border);
}
.metric-label {
  font-size: 1.08rem;
  font-weight: 600;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.09em;
  margin-bottom: 4px;
}
.metric-value {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 1.05rem;
  font-weight: 500;
  color: var(--text);
}

/* ── Error card ── */
.error-card {
  background: rgba(255,77,106,0.06);
  border: 1px solid rgba(255,77,106,0.22);
  border-radius: 14px;
  padding: 28px 20px;
  text-align: center;
}
.error-icon  { font-size: 2rem; margin-bottom: 10px; }
.error-sym   { font-family: 'IBM Plex Mono', monospace; font-size: 1rem; font-weight: 600; color: var(--red); }
.error-name  { font-size: 0.75rem; color: var(--muted); margin: 4px 0 10px; }
.error-msg   { font-size: 0.78rem; color: #ff8096; }

/* ── Refresh button ── */
.stButton > button {
  background: linear-gradient(135deg, #3b9eff, #7c3aed) !important;
  color: #fff !important;
  font-family: 'IBM Plex Mono', monospace !important;
  font-weight: 600 !important;
  font-size: 0.82rem !important;
  letter-spacing: 0.04em !important;
  border: none !important;
  border-radius: 8px !important;
  padding: 10px 24px !important;
  transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* ── Streamlit chrome cleanup ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 30px !important; padding-bottom: 30px !important; }
hr { border-color: var(--border) !important; margin: 18px 0 22px !important; }

/* ── Chart container spacing ── */
div[data-testid="stPlotlyChart"] { margin-top: -6px; margin-bottom: -6px; }
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

CHART_UP_LINE   = "#1fd97a"
CHART_UP_FILL   = "rgba(31,217,122,0.07)"
CHART_DOWN_LINE = "#ff4d6a"
CHART_DOWN_FILL = "rgba(255,77,106,0.07)"
ET = pytz.timezone("America/New_York")


# ── Data fetching ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=0, show_spinner=False)
def fetch_ticker_data(symbol: str, _cache_key: int):
    """
    Fetch 1-day 1h chart data, price info, after-hours, volume, earnings.
    _cache_key is intentionally unused — changing it busts the cache on refresh.
    """
    ticker = yf.Ticker(symbol)

    # ── 1-Day chart: 1h bars, last 2 trading days so we always have today's open
    hist = ticker.history(period="2d", interval="1h", auto_adjust=True, prepost=False)
    if hist.empty:
        raise ValueError(f"No intraday data returned for {symbol}.")

    # Keep only today's regular-hours bars (9:30–16:00 ET)
    today_et = datetime.now(ET).date()
    if hist.index.tz is None:
        hist.index = hist.index.tz_localize("UTC")
    hist_et = hist.copy()
    hist_et.index = hist_et.index.tz_convert(ET)
    today_bars = hist_et[hist_et.index.date == today_et]

    # Fall back to most recent available day if today has no bars yet
    if today_bars.empty:
        latest_date = hist_et.index.date[-1]
        today_bars = hist_et[hist_et.index.date == latest_date]

    chart_df = today_bars if not today_bars.empty else hist_et

    # ── Fundamentals
    info = {}
    try:
        info = ticker.info or {}
    except Exception:
        pass

    # Current / regular-market price
    current_price = (
        info.get("currentPrice")
        or info.get("regularMarketPrice")
        or float(chart_df["Close"].iloc[-1])
    )

    # Previous close (for day-change %)
    prev_close = (
        info.get("previousClose")
        or info.get("regularMarketPreviousClose")
    )
    if prev_close is None and not chart_df.empty:
        # Use first bar's open as proxy
        prev_close = float(chart_df["Open"].iloc[0])

    day_change_pct = (
        (current_price - prev_close) / prev_close * 100
        if prev_close and prev_close != 0 else 0.0
    )

    # ── After-hours price & change
    ah_price      = None
    ah_change_pct = None
    try:
        ah_price = (
            info.get("postMarketPrice")
            or info.get("preMarketPrice")
        )
        if ah_price:
            ah_price = float(ah_price)
            ah_change_pct = (ah_price - current_price) / current_price * 100
    except Exception:
        ah_price = None

    # ── Volume
    volume = info.get("regularMarketVolume") or info.get("volume")
    if volume is None and "Volume" in chart_df.columns:
        volume = int(chart_df["Volume"].sum())

    # ── Next earnings
    earnings_date = "N/A"
    if symbol not in ETF_TICKERS:
        try:
            cal = ticker.calendar
            if cal is not None:
                if isinstance(cal, dict):
                    ed = cal.get("Earnings Date")
                    if ed:
                        val = ed[0] if isinstance(ed, (list, tuple)) else ed
                        earnings_date = str(val)[:10]
                elif isinstance(cal, pd.DataFrame) and not cal.empty:
                    if "Earnings Date" in cal.index:
                        val = cal.loc["Earnings Date"].iloc[0]
                        earnings_date = str(val)[:10]
        except Exception:
            earnings_date = "Unavailable"

    return {
        "chart_df":      chart_df,
        "price":         current_price,
        "prev_close":    prev_close,
        "day_change_pct": day_change_pct,
        "ah_price":      ah_price,
        "ah_change_pct": ah_change_pct,
        "volume":        volume,
        "earnings":      earnings_date,
    }


# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_volume(v) -> str:
    if v is None: return "—"
    v = int(v)
    if v >= 1_000_000: return f"{v/1_000_000:.2f}M"
    if v >= 1_000:     return f"{v/1_000:.1f}K"
    return str(v)

def fmt_price(p) -> str:
    if p is None: return "—"
    return f"${float(p):,.2f}"

def make_chart(df: pd.DataFrame, is_up: bool) -> go.Figure:
    color = CHART_UP_LINE if is_up else CHART_DOWN_LINE
    fill  = CHART_UP_FILL if is_up else CHART_DOWN_FILL

    # Reference line at previous close to show gain/loss visually
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["Close"],
        mode="lines",
        line=dict(color=color, width=2.2),
        fill="tozeroy",
        fillcolor=fill,
        hovertemplate="<b>%{x|%H:%M}</b>  $%{y:,.2f}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=4, t=6, b=0),
        height=170,
        xaxis=dict(
            showgrid=False, zeroline=False, showline=False,
            tickfont=dict(family="IBM Plex Mono", size=9, color="#5a6480"),
            tickformat="%H:%M",
            nticks=6,
        ),
        yaxis=dict(
            showgrid=True, zeroline=False,
            gridcolor="rgba(255,255,255,0.04)",
            tickfont=dict(family="IBM Plex Mono", size=9, color="#5a6480"),
            showline=False,
            tickprefix="$",
            side="right",
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#1a1f2e", bordercolor="#252b3b",
            font=dict(family="IBM Plex Mono", size=11, color="#f0f4ff"),
        ),
        showlegend=False,
    )
    return fig


# ── Session state ─────────────────────────────────────────────────────────────
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()
if "cache_key" not in st.session_state:
    st.session_state.cache_key = 0


# ── Header ────────────────────────────────────────────────────────────────────
header_col, btn_col = st.columns([6, 1])

with header_col:
    st.markdown("""
    <div class="dash-header">
      <div class="dash-logo">📈</div>
      <span class="dash-title">MARKET TRACKER</span>
      <span class="dash-pill">Live · 10 Assets</span>
    </div>""", unsafe_allow_html=True)
    st.markdown(
        f'<div class="dash-timestamp">'
        f'Last refreshed &nbsp;·&nbsp; '
        f'{st.session_state.last_refresh.strftime("%b %d, %Y  %H:%M:%S")}'
        f'</div>',
        unsafe_allow_html=True,
    )

with btn_col:
    st.write("")
    if st.button("⟳  Refresh Data"):
        fetch_ticker_data.clear()
        st.session_state.last_refresh = datetime.now()
        st.session_state.cache_key += 1
        st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)


# ── Grid ──────────────────────────────────────────────────────────────────────
tickers_list = list(TICKERS.keys())
COLS = 2

for row_start in range(0, len(tickers_list), COLS):
    row_syms = tickers_list[row_start : row_start + COLS]
    cols = st.columns(COLS, gap="large")

    for col, sym in zip(cols, row_syms):
        with col:
            # ── Fetch ─────────────────────────────────────────────────────
            try:
                data  = fetch_ticker_data(sym, st.session_state.cache_key)
                error = None
            except Exception as e:
                data  = None
                error = str(e)

            # ── Error state ────────────────────────────────────────────────
            if error or data is None:
                st.markdown(f"""
                <div class="error-card">
                  <div class="error-icon">⚠️</div>
                  <div class="error-sym">{sym}</div>
                  <div class="error-name">{TICKERS[sym]}</div>
                  <div class="error-msg">Unable to load data.<br>
                    <small style="color:#7a8099">{error or 'Unknown error'}</small>
                  </div>
                </div>""", unsafe_allow_html=True)
                continue

            # ── Derived values ─────────────────────────────────────────────
            price   = data["price"]
            chg     = data["day_change_pct"]
            is_up   = chg >= 0
            is_flat = abs(chg) < 0.01

            badge_cls = "badge-flat" if is_flat else ("badge-up" if is_up else "badge-down")
            chg_arrow = "" if is_flat else ("▲" if is_up else "▼")

            # ── Card header ────────────────────────────────────────────────
            st.markdown(f"""
            <div class="card">
              <div class="card-top-row">
                <div>
                  <div class="card-ticker">{sym}</div>
                  <div class="card-name">{TICKERS[sym]}</div>
                </div>
              </div>

              <div class="price-main">{fmt_price(price)}</div>

              <div class="change-row">
                <span class="badge {badge_cls}">
                  <span class="badge-label">Day</span>
                  {chg_arrow} {abs(chg):.2f}%
                </span>
              </div>
            </div>""", unsafe_allow_html=True)

            # ── After-hours block ──────────────────────────────────────────
            ah_price = data["ah_price"]
            ah_chg   = data["ah_change_pct"]

            if ah_price is not None and ah_chg is not None:
                ah_is_up   = ah_chg >= 0
                ah_arrow   = "▲" if ah_is_up else "▼"
                ah_cls     = "ah-chg-up" if ah_is_up else "ah-chg-down"
                st.markdown(f"""
                <div class="ah-block">
                  <span class="ah-label">After Hours</span>
                  <span class="ah-price">{fmt_price(ah_price)}</span>
                  <span class="{ah_cls}">{ah_arrow} {abs(ah_chg):.2f}%</span>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="ah-block">
                  <span class="ah-label">After Hours</span>
                  <span class="ah-na">Not available outside trading hours</span>
                </div>""", unsafe_allow_html=True)

            # ── Chart ──────────────────────────────────────────────────────
            chart_df = data["chart_df"]
            if chart_df is None or chart_df.empty:
                st.caption("No intraday data available.")
            else:
                fig = make_chart(chart_df, is_up)
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False},
                    key=f"chart_{sym}_{st.session_state.cache_key}",
                )

            # ── Metrics ────────────────────────────────────────────────────
            earnings_label = (
                "Not Applicable" if sym in ETF_TICKERS else data["earnings"]
            )
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
            </div>""", unsafe_allow_html=True)

    st.write("")  # row gap
