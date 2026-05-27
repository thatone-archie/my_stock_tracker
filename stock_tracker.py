"""
stock_tracker.py — Multi-page: Stock Dashboard + Earnings Calendar
Setup:  pip install streamlit yfinance plotly pandas pytz
Run:    streamlit run stock_tracker.py
"""

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, date, timedelta
import pytz

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Market Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Shared CSS ────────────────────────────────────────────────────────────────
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
  --muted:     #6d28d9;
  --accent:    #3b9eff;
  --green:     #1fd97a;
  --green-bg:  rgba(31,217,122,0.12);
  --red:       #ff4d6a;
  --red-bg:    rgba(255,77,106,0.12);
  --amber:     #ffb347;
  --amber-bg:  rgba(255,179,71,0.10);
  --purple:    #a78bfa;
  --purple-bg: rgba(167,139,250,0.10);
}

html, body, [class*="css"] {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif;
}

/* ════════════════════════════════════════
   SIDEBAR NAV
   ════════════════════════════════════════ */
section[data-testid="stSidebar"] {
  background: #0d0f15 !important;
  border-right: 1px solid var(--border) !important;
  min-width: 220px !important;
  max-width: 220px !important;
}
.nav-logo-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0 20px 0;
}
.nav-logo {
  width: 32px; height: 32px;
  background: linear-gradient(135deg, #3b9eff 0%, #7c3aed 100%);
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px;
}
.nav-brand {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text);
  letter-spacing: 0.02em;
}
.nav-divider {
  height: 1px;
  background: var(--border);
  margin: 6px 0 14px 0;
}
.nav-section-label {
  font-size: 0.6rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 8px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.84rem;
  font-weight: 500;
  color: var(--text2);
  margin-bottom: 3px;
  border: 1px solid transparent;
  transition: all 0.15s;
  text-decoration: none !important;
}
.nav-item:hover {
  background: var(--surface2);
  color: var(--text);
  border-color: var(--border2);
}
.nav-item.active {
  background: rgba(59,158,255,0.12);
  color: var(--accent);
  border-color: rgba(59,158,255,0.25);
}
.nav-icon { font-size: 1rem; width: 20px; text-align: center; }

/* ════════════════════════════════════════
   SHARED HEADER
   ════════════════════════════════════════ */
.dash-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 4px;
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

/* ════════════════════════════════════════
   STOCK DASHBOARD CARDS
   ════════════════════════════════════════ */
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
  font-size: 1.0rem;
  color: var(--text2);
  margin-top: 3px;
  font-weight: 400;
}
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
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  opacity: 0.75;
  margin-right: 2px;
}
.badge-up   { color: var(--green); background: var(--green-bg); }
.badge-down { color: var(--red);   background: var(--red-bg);   }
.badge-flat { color: var(--text2); background: var(--surface2); }

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
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  color: var(--amber);
  background: var(--amber-bg);
  padding: 2px 7px;
  border-radius: 4px;
  white-space: nowrap;
}
.ah-price { font-family: 'IBM Plex Mono', monospace; font-size: 0.92rem; font-weight: 600; color: var(--text); }
.ah-chg-up   { font-family: 'IBM Plex Mono', monospace; font-size: 0.82rem; font-weight: 500; color: var(--green); }
.ah-chg-down { font-family: 'IBM Plex Mono', monospace; font-size: 0.82rem; font-weight: 500; color: var(--red); }
.ah-na { font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; color: var(--muted); }

.metrics-row {
  display: flex;
  gap: 0;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}
.metric-block { flex: 1; padding-right: 16px; }
.metric-block + .metric-block { padding-left: 16px; border-left: 1px solid var(--border); }
.metric-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.09em;
  margin-bottom: 4px;
}
.metric-value {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--text);
}

.error-card {
  background: rgba(255,77,106,0.06);
  border: 1px solid rgba(255,77,106,0.22);
  border-radius: 14px;
  padding: 28px 20px;
  text-align: center;
}
.error-icon { font-size: 2rem; margin-bottom: 10px; }
.error-sym  { font-family: 'IBM Plex Mono', monospace; font-size: 1rem; font-weight: 600; color: var(--red); }
.error-name { font-size: 0.75rem; color: var(--muted); margin: 4px 0 10px; }
.error-msg  { font-size: 0.78rem; color: #ff8096; }

/* ════════════════════════════════════════
   EARNINGS CALENDAR
   ════════════════════════════════════════ */
.ec-filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}
.ec-week-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.78rem;
  color: var(--muted);
  letter-spacing: 0.06em;
}

/* Earnings table */
.ec-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}
.ec-table th {
  font-family: 'Inter', sans-serif;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted);
  padding: 10px 16px;
  border-bottom: 1px solid var(--border2);
  text-align: left;
  background: var(--surface2);
}
.ec-table th:first-child { border-radius: 10px 0 0 0; }
.ec-table th:last-child  { border-radius: 0 10px 0 0; text-align: right; }
.ec-table td {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  vertical-align: middle;
}
.ec-table tr:last-child td { border-bottom: none; }
.ec-table tr:hover td { background: rgba(255,255,255,0.02); }

.ec-sym  { font-family: 'IBM Plex Mono', monospace; font-size: 1rem; font-weight: 600; color: var(--accent); }
.ec-name { font-size: 0.78rem; color: var(--text2); margin-top: 2px; }
.ec-price {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--text);
  text-align: right;
}
.ec-date-cell { text-align: right; }
.ec-date-pill {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.78rem;
  font-weight: 500;
  padding: 4px 12px;
  border-radius: 6px;
  display: inline-block;
}
.ec-date-pill.today    { background: rgba(59,158,255,0.18); color: var(--accent); border: 1px solid rgba(59,158,255,0.35); }
.ec-date-pill.upcoming { background: var(--surface2); color: var(--text2); border: 1px solid var(--border2); }
.ec-date-pill.na       { background: transparent; color: var(--muted); border: 1px solid var(--border); font-style: italic; }

/* No-earnings card */
.ec-na-card {
  background: var(--surface2);
  border: 1px solid var(--border2);
  border-radius: 14px;
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 3px;
}
.ec-na-icon  { font-size: 1.4rem; }
.ec-na-sym   { font-family: 'IBM Plex Mono', monospace; font-size: 0.95rem; font-weight: 600; color: var(--muted); }
.ec-na-name  { font-size: 0.75rem; color: var(--muted); margin-top: 2px; }
.ec-na-badge {
  margin-left: auto;
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color: var(--muted);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 3px 10px;
}

/* Empty state */
.ec-empty {
  text-align: center;
  padding: 60px 20px;
  color: var(--muted);
}
.ec-empty-icon { font-size: 2.5rem; margin-bottom: 12px; }
.ec-empty-title { font-size: 1rem; font-weight: 600; color: var(--text2); margin-bottom: 6px; }
.ec-empty-sub   { font-size: 0.8rem; color: var(--muted); }

/* Section header above table */
.ec-section-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  margin-top: 8px;
}
.ec-section-title {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text2);
  letter-spacing: 0.04em;
}
.ec-section-count {
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--accent);
  background: rgba(59,158,255,0.12);
  border: 1px solid rgba(59,158,255,0.2);
  border-radius: 20px;
  padding: 1px 8px;
}
.ec-na-section-title {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.78rem;
  color: var(--muted);
  margin: 20px 0 10px;
  letter-spacing: 0.04em;
}

/* ── Shared chrome ── */
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

/* Sidebar radio as nav */
div[data-testid="stSidebar"] .stRadio > label { display: none !important; }
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
  gap: 4px !important;
  flex-direction: column !important;
}
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  padding: 9px 12px !important;
  border-radius: 8px !important;
  font-size: 0.84rem !important;
  font-weight: 500 !important;
  color: var(--text2) !important;
  background: transparent !important;
  border: 1px solid transparent !important;
  cursor: pointer !important;
  transition: all 0.15s !important;
  width: 100% !important;
}
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
  background: var(--surface2) !important;
  color: var(--text) !important;
  border-color: var(--border2) !important;
}
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
  background: rgba(59,158,255,0.12) !important;
  color: var(--accent) !important;
  border-color: rgba(59,158,255,0.25) !important;
}
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label > div:first-child {
  display: none !important;
}

/* Selectbox (week filter) */
div[data-testid="stSelectbox"] > div > div {
  background: var(--surface2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 8px !important;
  color: var(--text) !important;
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 0.82rem !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 28px !important; padding-bottom: 30px !important; }
hr { border-color: var(--border) !important; margin: 18px 0 22px !important; }
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
ETF_TICKERS   = {"SOXX", "SPY", "IAU"}
NO_EARNINGS   = ETF_TICKERS  # expand if needed

CHART_UP_LINE   = "#1fd97a"
CHART_UP_FILL   = "rgba(31,217,122,0.07)"
CHART_DOWN_LINE = "#ff4d6a"
CHART_DOWN_FILL = "rgba(255,77,106,0.07)"
ET = pytz.timezone("America/New_York")


# ══════════════════════════════════════════════════════════════════════════════
#  DATA FETCHERS
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=0, show_spinner=False)
def fetch_ticker_data(symbol: str, _cache_key: int):
    ticker = yf.Ticker(symbol)

    hist = ticker.history(period="2d", interval="1h", auto_adjust=True, prepost=False)
    if hist.empty:
        raise ValueError(f"No intraday data returned for {symbol}.")

    today_et = datetime.now(ET).date()
    if hist.index.tz is None:
        hist.index = hist.index.tz_localize("UTC")
    hist_et = hist.copy()
    hist_et.index = hist_et.index.tz_convert(ET)
    today_bars = hist_et[hist_et.index.date == today_et]
    if today_bars.empty:
        latest_date = hist_et.index.date[-1]
        today_bars = hist_et[hist_et.index.date == latest_date]
    chart_df = today_bars if not today_bars.empty else hist_et

    info = {}
    try:
        info = ticker.info or {}
    except Exception:
        pass

    current_price = (
        info.get("currentPrice") or info.get("regularMarketPrice")
        or float(chart_df["Close"].iloc[-1])
    )
    prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
    if prev_close is None and not chart_df.empty:
        prev_close = float(chart_df["Open"].iloc[0])
    day_change_pct = (
        (current_price - prev_close) / prev_close * 100
        if prev_close and prev_close != 0 else 0.0
    )

    ah_price = None; ah_change_pct = None
    try:
        raw_ah = info.get("postMarketPrice") or info.get("preMarketPrice")
        if raw_ah:
            ah_price = float(raw_ah)
            ah_change_pct = (ah_price - current_price) / current_price * 100
    except Exception:
        ah_price = None

    volume = info.get("regularMarketVolume") or info.get("volume")
    if volume is None and "Volume" in chart_df.columns:
        volume = int(chart_df["Volume"].sum())

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
        "chart_df": chart_df, "price": current_price,
        "prev_close": prev_close, "day_change_pct": day_change_pct,
        "ah_price": ah_price, "ah_change_pct": ah_change_pct,
        "volume": volume, "earnings": earnings_date,
    }


@st.cache_data(ttl=0, show_spinner=False)
def fetch_earnings_calendar_range(start_str: str, end_str: str, _cache_key: int) -> pd.DataFrame:
    """
    Fetch earnings calendar for a date range using yf.get_earnings_calendar().
    Returns a DataFrame (may be empty on error or no data).
    """
    try:
        df = yf.get_earnings_calendar(start=start_str, end=end_str)
        if df is None:
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=0, show_spinner=False)
def fetch_earnings_data(symbol: str, _cache_key: int):
    """
    Returns dict with:
      price        – current price (float or None)
      dates        – list of date objects (may be empty)
      is_na        – True when ticker has no earnings (ETF / gold trust)
      error        – error string if fetch failed, else None
    """
    if symbol in NO_EARNINGS:
        return {"price": None, "dates": [], "is_na": True, "error": None}

    try:
        ticker = yf.Ticker(symbol)

        # Current price (fast path via info)
        price = None
        try:
            info  = ticker.info or {}
            price = info.get("currentPrice") or info.get("regularMarketPrice")
            if price:
                price = float(price)
        except Exception:
            pass

        # Earnings dates via get_earnings_dates (returns a DataFrame indexed by date)
        dates = []
        try:
            raw = ticker.get_earnings_dates(limit=8)   # up to 8 upcoming/past
            if raw is not None and not raw.empty:
                # Index is a DatetimeTZDtype; convert to plain dates
                for ts in raw.index:
                    try:
                        d = ts.date() if hasattr(ts, "date") else pd.Timestamp(ts).date()
                        if d >= date.today():          # keep only future dates
                            dates.append(d)
                    except Exception:
                        pass
                dates = sorted(set(dates))
        except Exception:
            pass

        # Fallback: ticker.calendar
        if not dates:
            try:
                cal = ticker.calendar
                if cal is not None:
                    if isinstance(cal, dict):
                        ed = cal.get("Earnings Date")
                        if ed:
                            vals = ed if isinstance(ed, (list, tuple)) else [ed]
                            for v in vals:
                                try:
                                    d = pd.Timestamp(v).date()
                                    if d >= date.today():
                                        dates.append(d)
                                except Exception:
                                    pass
                    elif isinstance(cal, pd.DataFrame) and not cal.empty:
                        if "Earnings Date" in cal.index:
                            v = cal.loc["Earnings Date"].iloc[0]
                            try:
                                d = pd.Timestamp(v).date()
                                if d >= date.today():
                                    dates.append(d)
                            except Exception:
                                pass
                dates = sorted(set(dates))
            except Exception:
                pass

        return {"price": price, "dates": dates, "is_na": False, "error": None}

    except Exception as e:
        return {"price": None, "dates": [], "is_na": False, "error": str(e)}


# ── Shared helpers ─────────────────────────────────────────────────────────────
def fmt_volume(v) -> str:
    if v is None: return "—"
    v = int(v)
    if v >= 1_000_000: return f"{v/1_000_000:.2f}M"
    if v >= 1_000:     return f"{v/1_000:.1f}K"
    return str(v)

def fmt_price(p) -> str:
    if p is None: return "—"
    return f"${float(p):,.2f}"

def week_bounds(offset_weeks: int = 0):
    """Return (monday, sunday) for the current week + offset_weeks."""
    today = date.today()
    monday = today - timedelta(days=today.weekday()) + timedelta(weeks=offset_weeks)
    sunday = monday + timedelta(days=6)
    return monday, sunday

def make_chart(df: pd.DataFrame, is_up: bool) -> go.Figure:
    color = CHART_UP_LINE if is_up else CHART_DOWN_LINE
    fill  = CHART_UP_FILL if is_up else CHART_DOWN_FILL
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Close"],
        mode="lines",
        line=dict(color=color, width=2.2),
        fill="tozeroy", fillcolor=fill,
        hovertemplate="<b>%{x|%H:%M}</b>  $%{y:,.2f}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=4, t=6, b=0), height=170,
        xaxis=dict(showgrid=False, zeroline=False, showline=False,
                   tickfont=dict(family="IBM Plex Mono", size=9, color="#5a6480"),
                   tickformat="%H:%M", nticks=6),
        yaxis=dict(showgrid=True, zeroline=False, gridcolor="rgba(255,255,255,0.04)",
                   tickfont=dict(family="IBM Plex Mono", size=9, color="#5a6480"),
                   showline=False, tickprefix="$", side="right"),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#1a1f2e", bordercolor="#252b3b",
                        font=dict(family="IBM Plex Mono", size=11, color="#f0f4ff")),
        showlegend=False,
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()
if "cache_key" not in st.session_state:
    st.session_state.cache_key = 0


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR NAVIGATION
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="nav-logo-row">
      <div class="nav-logo">📈</div>
      <span class="nav-brand">MARKET TRACKER</span>
    </div>
    <div class="nav-divider"></div>
    <div class="nav-section-label">Navigation</div>
    """, unsafe_allow_html=True)

    page = st.radio(
        label="nav",
        options=["📊  Stock Dashboard", "📅  Earnings Calendar"],
        label_visibility="collapsed",
    )
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="nav-divider"></div>
    <div style="font-size:0.65rem; color:#3a4060; text-align:center; margin-top:10px;">
      Data via yfinance · US markets
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: STOCK DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊  Stock Dashboard":

    header_col, btn_col = st.columns([6, 1])
    with header_col:
        st.markdown("""
        <div class="dash-header">
          <span class="dash-title">STOCK DASHBOARD</span>
          <span class="dash-pill">Live · 10 Assets</span>
        </div>""", unsafe_allow_html=True)
        st.markdown(
            f'<div class="dash-timestamp">Last refreshed &nbsp;·&nbsp; '
            f'{st.session_state.last_refresh.strftime("%b %d, %Y  %H:%M:%S")}</div>',
            unsafe_allow_html=True,
        )
    with btn_col:
        st.write("")
        if st.button("⟳  Refresh Data", key="dash_refresh"):
            fetch_ticker_data.clear()
            fetch_earnings_data.clear()
            st.session_state.last_refresh = datetime.now()
            st.session_state.cache_key += 1
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    tickers_list = list(TICKERS.keys())
    COLS = 2
    for row_start in range(0, len(tickers_list), COLS):
        row_syms = tickers_list[row_start : row_start + COLS]
        cols = st.columns(COLS, gap="large")
        for col, sym in zip(cols, row_syms):
            with col:
                try:
                    data  = fetch_ticker_data(sym, st.session_state.cache_key)
                    error = None
                except Exception as e:
                    data = None; error = str(e)

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

                price   = data["price"]
                chg     = data["day_change_pct"]
                is_up   = chg >= 0
                is_flat = abs(chg) < 0.01
                badge_cls = "badge-flat" if is_flat else ("badge-up" if is_up else "badge-down")
                chg_arrow = "" if is_flat else ("▲" if is_up else "▼")

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

                ah_price = data["ah_price"]; ah_chg = data["ah_change_pct"]
                if ah_price is not None and ah_chg is not None:
                    ah_arrow = "▲" if ah_chg >= 0 else "▼"
                    ah_cls   = "ah-chg-up" if ah_chg >= 0 else "ah-chg-down"
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

                chart_df = data["chart_df"]
                if chart_df is None or chart_df.empty:
                    st.caption("No intraday data available.")
                else:
                    st.plotly_chart(
                        make_chart(chart_df, is_up),
                        use_container_width=True,
                        config={"displayModeBar": False},
                        key=f"chart_{sym}_{st.session_state.cache_key}",
                    )

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
                </div>""", unsafe_allow_html=True)

        st.write("")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: EARNINGS CALENDAR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📅  Earnings Calendar":

    # ── Header
    header_col, btn_col = st.columns([6, 1])
    with header_col:
        st.markdown("""
        <div class="dash-header">
          <span class="dash-title">EARNINGS CALENDAR</span>
          <span class="dash-pill">10 Tickers</span>
        </div>""", unsafe_allow_html=True)
        st.markdown(
            f'<div class="dash-timestamp">Last refreshed &nbsp;·&nbsp; '
            f'{st.session_state.last_refresh.strftime("%b %d, %Y  %H:%M:%S")}</div>',
            unsafe_allow_html=True,
        )
    with btn_col:
        st.write("")
        if st.button("⟳  Refresh Data", key="ec_refresh"):
            fetch_ticker_data.clear()
            fetch_earnings_data.clear()
            fetch_earnings_calendar_range.clear()
            st.session_state.last_refresh = datetime.now()
            st.session_state.cache_key += 1
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Month selector ─────────────────────────────────────────────────────────
    today = date.today()

    # Build list of selectable months: current month + next 2
    month_options = []
    for delta in range(3):
        y = today.year + (today.month - 1 + delta) // 12
        m = (today.month - 1 + delta) % 12 + 1
        month_options.append(date(y, m, 1))

    month_labels = [d.strftime("%B %Y") for d in month_options]

    filter_col, _, _ = st.columns([2, 3, 3])
    with filter_col:
        selected_month_label = st.selectbox(
            "Select month",
            options=month_labels,
            label_visibility="collapsed",
            key="ec_month",
        )

    selected_month_start = month_options[month_labels.index(selected_month_label)]

    # Compute last day of selected month
    if selected_month_start.month == 12:
        month_end = date(selected_month_start.year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(selected_month_start.year, selected_month_start.month + 1, 1) - timedelta(days=1)

    # ── Compute week buckets for the selected month ────────────────────────────
    def get_week_buckets(month_start: date, month_end: date):
        """
        Returns a list of (label, mon, sun) tuples for each Mon–Sun week
        that overlaps the given month. Labels: 'Current Week', 'Next Week',
        or 'Week of MMM DD'.
        """
        # Find the Monday on or before month_start
        cursor = month_start - timedelta(days=month_start.weekday())
        buckets = []
        current_mon, _ = week_bounds(0)
        next_mon, _    = week_bounds(1)
        while cursor <= month_end:
            wk_sun = cursor + timedelta(days=6)
            if cursor == current_mon:
                label = "Current Week"
            elif cursor == next_mon:
                label = "Next Week"
            else:
                label = f"Week of {cursor.strftime('%b %d')}"
            buckets.append((label, cursor, wk_sun))
            cursor += timedelta(weeks=1)
        return buckets

    week_buckets = get_week_buckets(selected_month_start, month_end)

    # ── Fetch earnings calendar for the full month in one call ─────────────────
    with st.spinner("Fetching earnings calendar…"):
        cal_df = fetch_earnings_calendar_range(
            selected_month_start.strftime("%Y-%m-%d"),
            month_end.strftime("%Y-%m-%d"),
            st.session_state.cache_key,
        )

    # Normalise the calendar DataFrame into a simple lookup:
    # { ticker_symbol -> [date, ...] }
    TRACKED = set(TICKERS.keys()) - NO_EARNINGS

    def parse_calendar_df(df: pd.DataFrame) -> dict:
        """
        Parse yf.get_earnings_calendar() output into {ticker: [date, ...]}.
        The DataFrame columns vary by yfinance version; we handle common shapes.
        """
        result: dict = {}
        if df is None or df.empty:
            return result
        try:
            # Detect ticker column
            ticker_col = None
            for col in ("ticker", "Ticker", "symbol", "Symbol"):
                if col in df.columns:
                    ticker_col = col
                    break
            # Detect date column
            date_col = None
            for col in ("startdatetime", "startDateTime", "date", "Date",
                        "Earnings Date", "earningsDate"):
                if col in df.columns:
                    date_col = col
                    break

            if ticker_col is None or date_col is None:
                # Try index as ticker, first date column fallback
                if df.index.name and df.index.name.lower() in ("ticker", "symbol"):
                    df = df.reset_index()
                    ticker_col = df.columns[0]
                if date_col is None and not df.empty:
                    date_col = df.columns[1] if len(df.columns) > 1 else None

            if ticker_col is None or date_col is None:
                return result

            for _, row in df.iterrows():
                sym = str(row[ticker_col]).strip().upper()
                if sym not in TRACKED:
                    continue
                try:
                    d = pd.Timestamp(row[date_col]).date()
                    result.setdefault(sym, [])
                    result[sym].append(d)
                except Exception:
                    pass
        except Exception:
            pass
        # Sort each ticker's dates
        for sym in result:
            result[sym] = sorted(set(result[sym]))
        return result

    cal_lookup = parse_calendar_df(cal_df)

    # ── Fetch current prices for tracked tickers (re-use existing cache) ───────
    price_lookup: dict = {}
    for sym in TRACKED:
        try:
            data = fetch_earnings_data(sym, st.session_state.cache_key)
            if data and data.get("price"):
                price_lookup[sym] = data["price"]
        except Exception:
            pass

    # Also check tickers found in calendar but not in price_lookup
    for sym in cal_lookup:
        if sym not in price_lookup:
            try:
                info = yf.Ticker(sym).info or {}
                p = info.get("currentPrice") or info.get("regularMarketPrice")
                if p:
                    price_lookup[sym] = float(p)
            except Exception:
                pass

    # ── Render week-by-week ────────────────────────────────────────────────────
    any_results = False

    for wk_label, wk_mon, wk_sun in week_buckets:
        # Gather all tracked tickers with an earnings date in this week
        week_rows = []
        for sym, name in TICKERS.items():
            if sym in NO_EARNINGS:
                continue
            sym_dates = cal_lookup.get(sym, [])
            matched = [d for d in sym_dates if wk_mon <= d <= wk_sun]
            if matched:
                week_rows.append({
                    "sym":   sym,
                    "name":  name,
                    "price": price_lookup.get(sym),
                    "date":  matched[0],
                })

        week_rows.sort(key=lambda r: r["date"])
        wk_range_label = f"{wk_mon.strftime('%b %d')} – {wk_sun.strftime('%b %d, %Y')}"

        if not week_rows:
            # Show a compact empty-state row for weeks with no data
            st.markdown(f"""
            <div class="ec-section-head" style="margin-top:18px">
              <span class="ec-section-title">{wk_label.upper()}</span>
              <span style="font-size:0.7rem;color:var(--muted);font-family:'IBM Plex Mono',monospace">
                {wk_range_label}
              </span>
            </div>
            <div class="ec-empty" style="padding:20px 0 24px 0">
              <div class="ec-empty-icon" style="font-size:1.6rem;margin-bottom:6px">🗓️</div>
              <div class="ec-empty-title" style="font-size:0.85rem">
                No earnings scheduled for this week
              </div>
              <div class="ec-empty-sub">
                None of the tracked tickers report during {wk_range_label}.
              </div>
            </div>""", unsafe_allow_html=True)
            continue

        any_results = True

        st.markdown(f"""
        <div class="ec-section-head" style="margin-top:18px">
          <span class="ec-section-title">{wk_label.upper()}</span>
          <span class="ec-section-count">{len(week_rows)} ticker{'s' if len(week_rows)!=1 else ''}</span>
          <span style="font-size:0.7rem;color:var(--muted);font-family:'IBM Plex Mono',monospace;margin-left:4px">
            · {wk_range_label}
          </span>
        </div>""", unsafe_allow_html=True)

        rows_html = ""
        for r in week_rows:
            d        = r["date"]
            is_today = (d == today)
            is_tmrw  = (d == today + timedelta(days=1))
            pill_cls = "today" if is_today else "upcoming"
            day_str  = ("TODAY" if is_today
                        else ("TOMORROW" if is_tmrw
                              else d.strftime("%a, %b %d")))
            rows_html += f"""
            <tr>
              <td>
                <div class="ec-sym">{r['sym']}</div>
                <div class="ec-name">{r['name']}</div>
              </td>
              <td class="ec-price">{fmt_price(r['price'])}</td>
              <td class="ec-date-cell">
                <span class="ec-date-pill {pill_cls}">{day_str}</span>
              </td>
            </tr>"""

        st.markdown(f"""
        <table class="ec-table">
          <thead>
            <tr>
              <th>Ticker / Company</th>
              <th style="text-align:right">Current Price</th>
              <th style="text-align:right">Earnings Date</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>""", unsafe_allow_html=True)

    # ── If the entire calendar returned no data at all ─────────────────────────
    if cal_df.empty and not any_results:
        st.markdown(f"""
        <div class="ec-empty">
          <div class="ec-empty-icon">📭</div>
          <div class="ec-empty-title">No earnings data available for {selected_month_label}</div>
          <div class="ec-empty-sub">
            The earnings calendar returned no results for this period.<br>
            Try a different month or refresh to retry.
          </div>
        </div>""", unsafe_allow_html=True)

    st.write("")

    # ── ETFs / no-earnings (always shown, compact) ─────────────────────────────
    na_rows = [{"sym": s, "name": n} for s, n in TICKERS.items() if s in NO_EARNINGS]
    if na_rows:
        with st.expander(
            f"🚫  {len(na_rows)} ticker(s) don't report earnings (ETFs / Trusts)",
            expanded=False,
        ):
            for r in na_rows:
                st.markdown(f"""
                <div class="ec-na-card">
                  <span class="ec-na-icon">📦</span>
                  <div>
                    <div class="ec-na-sym">{r['sym']}</div>
                    <div class="ec-na-name">{r['name']}</div>
                  </div>
                  <span class="ec-na-badge">Not Applicable</span>
                </div>""", unsafe_allow_html=True)
