"""
stock_tracker.py — Multi-page: Stock Dashboard + Earnings Calendar
Setup:  pip install streamlit yfinance plotly pandas pytz yahoo_fin
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
    initial_sidebar_state="collapsed",
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
}

html, body, [class*="css"] {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif;
}

/* ════════════════════════════════════════
   SIDEBAR — fully hidden
   ════════════════════════════════════════ */
section[data-testid="stSidebar"],
button[data-testid="collapsedControl"] {
  display: none !important;
}

/* ════════════════════════════════════════
   TOP NAV TABS
   ════════════════════════════════════════ */
.top-nav {
  display: flex; align-items: center; gap: 0;
  background: #d6eaf8; border-radius: 12px;
  padding: 5px; margin-bottom: 20px;
  border: 1px solid #a9cce3;
  width: fit-content;
}
.top-nav a {
  font-family: 'IBM Plex Mono', monospace; font-size: 0.82rem; font-weight: 600;
  padding: 8px 22px; border-radius: 8px; cursor: pointer;
  text-decoration: none; letter-spacing: 0.03em;
  color: #3a6080; transition: background 0.15s, color 0.15s;
  border: 1px solid transparent;
}
.top-nav a.active {
  background: #1565a8; color: #fff;
  border-color: #0d47a1;
  box-shadow: 0 2px 8px rgba(21,101,168,0.25);
}
.top-nav a:not(.active):hover {
  background: #c2dcef; color: #1565a8;
}

/* Dropdown menu panel */
[data-baseweb="popover"] ul {
  background: #eaf4fc !important;
  border: 1px solid #7fb3d3 !important;
  border-radius: 8px !important;
}
[data-baseweb="popover"] li {
  background: #eaf4fc !important;
  color: #1a3a52 !important;
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 0.85rem !important;
}
[data-baseweb="popover"] li:hover,
[data-baseweb="popover"] li[aria-selected="true"] {
  background: #c2dcef !important;
  color: #0d2b3e !important;
}

/* ════════════════════════════════════════
   SHARED HEADER
   ════════════════════════════════════════ */
.dash-header { display: flex; align-items: center; gap: 16px; margin-bottom: 4px; }
.dash-title {
  font-family: 'IBM Plex Mono', monospace; font-size: 1.5rem;
  font-weight: 600; color: var(--muted); letter-spacing: -0.02em;
}
.dash-pill {
  font-size: 0.9rem; color: var(--accent);
  background: rgba(59,158,255,0.12); border: 1px solid rgba(59,158,255,0.25);
  border-radius: 20px; padding: 2px 10px;
  letter-spacing: 0.06em; text-transform: uppercase; font-weight: 500;
}
.dash-timestamp {
  font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem;
  color: var(--muted); margin-top: 4px; margin-bottom: 22px;
}

/* ════════════════════════════════════════
   STOCK DASHBOARD CARDS — pastel palette
   ════════════════════════════════════════ */
.card {
  background: #eaf4fc;
  border: 1px solid #a9cce3;
  border-radius: 14px; padding: 14px 16px 12px; margin-bottom: 2px;
}
.card-top-row { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
.card-ticker { font-family: 'IBM Plex Mono', monospace; font-size: 1.2rem; font-weight: 700; color: #1565a8; letter-spacing: 0.04em; }
.card-name   { font-size: 0.78rem; color: #3a6080; margin-top: 2px; font-weight: 400; }
.price-main  {
  font-family: 'IBM Plex Mono', monospace; font-size: 1.45rem;
  font-weight: 700; color: #0d2b3e; line-height: 1;
  margin-bottom: 6px; letter-spacing: -0.02em;
}
.change-row  { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 4px; }
.badge {
  font-family: 'IBM Plex Mono', monospace; font-size: 0.89rem; font-weight: 600;
  padding: 3px 9px; border-radius: 6px; display: inline-flex; align-items: center; gap: 4px;
}
.badge-label {
  font-family: 'Inter', sans-serif; font-size: 0.6rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.07em; opacity: 0.75; margin-right: 2px;
}
.badge-up   { color: #0a6640; background: rgba(31,217,122,0.18); border: 1px solid rgba(31,217,122,0.35); }
.badge-down { color: #a8001e; background: rgba(255,77,106,0.15); border: 1px solid rgba(255,77,106,0.3); }
.badge-flat { color: #3a6080; background: rgba(59,96,128,0.10); border: 1px solid rgba(59,96,128,0.2); }

.ah-block {
  display: flex; align-items: center; gap: 8px; margin-top: 6px;
  padding: 5px 9px; background: #ddeef8;
  border: 1px solid #a9cce3; border-radius: 8px; flex-wrap: wrap;
}
.ah-label {
  font-size: 0.62rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.09em; color: #7a5000; background: rgba(255,179,71,0.25);
  padding: 2px 7px; border-radius: 4px; white-space: nowrap;
}
.ah-price    { font-family: 'IBM Plex Mono', monospace; font-size: 0.85rem; font-weight: 600; color: #0d2b3e; }
.ah-chg-up   { font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; font-weight: 500; color: #0a6640; }
.ah-chg-down { font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; font-weight: 500; color: #a8001e; }
.ah-na       { font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; color: #5a7a90; }

.metrics-row {
  display: flex; gap: 0; margin-top: 10px;
  padding-top: 10px; border-top: 1px solid #a9cce3;
}
.metric-block { flex: 1; padding-right: 8px; }
.metric-block + .metric-block { padding-left: 8px; border-left: 1px solid #a9cce3; }
.metric-label {
  font-size: 0.55rem; font-weight: 700; color: #5a7a90;
  text-transform: uppercase; letter-spacing: 0.09em; margin-bottom: 3px;
}
.metric-value {
  font-family: 'IBM Plex Mono', monospace; font-size: 0.82rem;
  font-weight: 600; color: #1565a8;
}
.metric-value-sm {
  font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem;
  font-weight: 600; color: #1565a8; line-height: 1.3;
}
.metric-value-earnings-soon {
  font-family: 'IBM Plex Mono', monospace; font-size: 0.82rem;
  font-weight: 700; color: #fff;
  background: linear-gradient(135deg, #e65c00, #f9a825);
  padding: 2px 7px; border-radius: 5px;
  display: inline-block; line-height: 1.4;
  box-shadow: 0 1px 4px rgba(230,92,0,0.3);
}

.error-card {
  background: rgba(255,77,106,0.06); border: 1px solid rgba(255,77,106,0.22);
  border-radius: 14px; padding: 28px 20px; text-align: center;
}
.error-icon { font-size: 2rem; margin-bottom: 10px; }
.error-sym  { font-family: 'IBM Plex Mono', monospace; font-size: 1rem; font-weight: 600; color: var(--red); }
.error-name { font-size: 0.75rem; color: var(--muted); margin: 4px 0 10px; }
.error-msg  { font-size: 0.78rem; color: #ff8096; }

/* ════════════════════════════════════════
   EARNINGS CALENDAR
   ════════════════════════════════════════ */
.ec-nav-context {
  display: inline-block; font-size: 0.68rem; font-weight: 700;
  letter-spacing: 0.08em; text-transform: uppercase;
  padding: 3px 12px; border-radius: 20px; margin-bottom: 6px;
}
.ec-nav-context.current { color: var(--green); background: var(--green-bg); border: 1px solid rgba(31,217,122,0.25); }
.ec-nav-context.next    { color: var(--accent); background: rgba(59,158,255,0.12); border: 1px solid rgba(59,158,255,0.25); }
.ec-nav-context.other   { color: var(--text2); background: var(--surface); border: 1px solid var(--border2); }

.ec-nav-week-label {
  font-family: 'IBM Plex Mono', monospace; font-size: 1.0rem;
  font-weight: 600; color: var(--text); letter-spacing: 0.02em;
}
.ec-nav-range {
  font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem;
  color: var(--text2); margin-top: 3px;
}

.ec-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; margin-bottom: 10px; }
.ec-table th {
  font-family: 'Inter', sans-serif; font-size: 0.65rem; font-weight: 700;
  letter-spacing: 0.1em; text-transform: uppercase; color: var(--text2);
  padding: 10px 16px; border-bottom: 1px solid var(--border2);
  text-align: left; background: var(--surface2);
}
.ec-table th:first-child { border-radius: 10px 0 0 0; }
.ec-table th:last-child  { border-radius: 0 10px 0 0; text-align: right; }
.ec-table td { padding: 14px 16px; border-bottom: 1px solid var(--border); vertical-align: middle; }
.ec-table tr:last-child td { border-bottom: none; }
.ec-table tr:hover td { background: rgba(255,255,255,0.02); }

.ec-sym   { font-family: 'IBM Plex Mono', monospace; font-size: 1rem; font-weight: 600; color: var(--accent); }
.ec-name  { font-size: 0.78rem; color: var(--text2); margin-top: 2px; }
.ec-price { font-family: 'IBM Plex Mono', monospace; font-size: 0.95rem; font-weight: 500; color: var(--text); text-align: right; }
.ec-date-cell { text-align: right; }
.ec-date-pill {
  font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; font-weight: 500;
  padding: 4px 12px; border-radius: 6px; display: inline-block;
}
.ec-date-pill.today    { background: rgba(31,217,122,0.15); color: var(--green); border: 1px solid rgba(31,217,122,0.3); }
.ec-date-pill.tomorrow { background: rgba(255,179,71,0.15); color: var(--amber); border: 1px solid rgba(255,179,71,0.3); }
.ec-date-pill.upcoming { background: var(--surface2); color: var(--text2); border: 1px solid var(--border2); }

.ec-count-badge {
  display: inline-flex; align-items: center; gap: 6px; margin-bottom: 14px;
  font-size: 0.72rem; font-weight: 600; color: var(--accent);
  background: rgba(59,158,255,0.10); border: 1px solid rgba(59,158,255,0.2);
  border-radius: 20px; padding: 3px 12px;
}
.ec-empty {
  text-align: center; padding: 40px 20px; color: var(--muted);
  background: var(--surface); border: 1px dashed var(--border2);
  border-radius: 12px; margin-bottom: 10px;
}
.ec-empty-icon  { font-size: 2rem; margin-bottom: 8px; }
.ec-empty-title { font-size: 0.9rem; font-weight: 600; color: var(--text2); margin-bottom: 4px; }
.ec-empty-sub   { font-size: 0.78rem; color: var(--muted); }
.ec-etf-note {
  font-size: 0.72rem; color: var(--muted); margin-top: 18px;
  padding: 10px 16px; background: var(--surface2);
  border: 1px solid var(--border); border-radius: 8px;
  font-family: 'IBM Plex Mono', monospace;
}

/* ── Buttons ── */
.stButton > button {
  background: linear-gradient(135deg, #3b9eff, #7c3aed) !important;
  color: #fff !important; font-family: 'IBM Plex Mono', monospace !important;
  font-weight: 600 !important; font-size: 0.82rem !important;
  letter-spacing: 0.04em !important; border: none !important;
  border-radius: 8px !important; padding: 10px 24px !important; transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 24px !important; padding-bottom: 30px !important; padding-left: 2rem !important; padding-right: 2rem !important; max-width: 100% !important; }
hr { border-color: var(--border) !important; margin: 18px 0 22px !important; }
div[data-testid="stPlotlyChart"] { margin-top: -4px; margin-bottom: -4px; }
/* Tighten column gaps for 4-col layout */
div[data-testid="column"] { padding-left: 0.4rem !important; padding-right: 0.4rem !important; }
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
    "GOOG":  "Alphabet Inc.",
    "ORCL":  "Oracle Corporation",
    "SPY":   "SPDR S&P 500 ETF",
    "IAU":   "iShares Gold Trust",
    "RKLB":  "Rocket Lab Corp",
}
ETF_TICKERS = {"SOXX", "SPY", "IAU"}
NO_EARNINGS = ETF_TICKERS

CHART_UP_LINE   = "#1fd97a"
CHART_UP_FILL   = "rgba(31,217,122,0.07)"
CHART_DOWN_LINE = "#ff4d6a"
CHART_DOWN_FILL = "rgba(255,77,106,0.07)"
ET = pytz.timezone("America/New_York")


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def week_monday(ref: date) -> date:
    return ref - timedelta(days=ref.weekday())

def week_sunday(monday: date) -> date:
    return monday + timedelta(days=6)

def fmt_volume(v) -> str:
    if v is None: return "—"
    v = int(v)
    if v >= 1_000_000: return f"{v/1_000_000:.2f}M"
    if v >= 1_000:     return f"{v/1_000:.1f}K"
    return str(v)

def fmt_price(p) -> str:
    if p is None: return "—"
    return f"${float(p):,.2f}"

PST = pytz.timezone("America/Los_Angeles")
_CHART_START_HOUR = 6   # 6:00 AM PST
_CHART_END_HOUR   = 17  # 5:00 PM PST

def make_chart(df: pd.DataFrame, is_up: bool) -> go.Figure | None:
    """
    Renders a Plotly line chart from an already PST-clipped, cleaned DataFrame.
    Returns None only if the df is empty or Close is all-NaN.
    """
    if df is None or df.empty or "Close" not in df.columns:
        return None
    if df["Close"].dropna().empty:
        return None

    # ── Y-axis bounds: day low − 10%  /  day high + 20% ──────────────────────
    if "Low" in df.columns and "High" in df.columns:
        day_low  = float(pd.to_numeric(df["Low"],  errors="coerce").min())
        day_high = float(pd.to_numeric(df["High"], errors="coerce").max())
    else:
        day_low  = float(df["Close"].min())
        day_high = float(df["Close"].max())

    # Guard against bad Low/High values (e.g. pre-market bars with 0s)
    if not (day_low > 0 and day_high > 0 and day_high >= day_low):
        day_low  = float(df["Close"].min())
        day_high = float(df["Close"].max())

    y_min = day_low  * 0.90
    y_max = day_high * 1.20

    # ── X-axis: anchor to 06:00–17:00 on the date of the first bar ───────────
    ref_date = df.index[0].date()
    x_start  = PST.localize(datetime(ref_date.year, ref_date.month, ref_date.day, 6,  0, 0))
    x_end    = PST.localize(datetime(ref_date.year, ref_date.month, ref_date.day, 17, 0, 0))

    color = CHART_UP_LINE if is_up else CHART_DOWN_LINE
    fill  = CHART_UP_FILL if is_up else CHART_DOWN_FILL

    fig = go.Figure()
    # Invisible baseline at y_min so fill area doesn't drop to zero
    fig.add_trace(go.Scatter(
        x=df.index, y=[y_min] * len(df),
        mode="lines", line=dict(width=0, color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Close"],
        mode="lines",
        line=dict(color=color, width=2.0),
        fill="tonexty", fillcolor=fill,
        hovertemplate="<b>%{x|%H:%M PST}</b>  $%{y:,.2f}<extra></extra>",
        connectgaps=False,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(234,244,252,0)",
        margin=dict(l=0, r=4, t=4, b=0),
        height=130,
        xaxis=dict(
            range=[x_start, x_end],
            showgrid=False, zeroline=False, showline=False,
            tickfont=dict(family="IBM Plex Mono", size=8, color="#5a7a90"),
            tickformat="%H:%M", nticks=6,
        ),
        yaxis=dict(
            range=[y_min, y_max],
            showgrid=True, zeroline=False,
            gridcolor="rgba(90,120,144,0.15)",
            tickfont=dict(family="IBM Plex Mono", size=8, color="#5a7a90"),
            showline=False, tickprefix="$", side="right",
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#ddeef8", bordercolor="#a9cce3",
            font=dict(family="IBM Plex Mono", size=10, color="#0d2b3e"),
        ),
        showlegend=False,
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
#  DATA FETCHERS
# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════════
#  DATA FETCHERS
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=0, show_spinner=False)
def fetch_ticker_data(symbol: str, _cache_key: int):
    ticker = yf.Ticker(symbol)

    # ── Chart data: 15-min / 1D, prepost=True for pre+after-hours bars ────────
    chart_df      = None
    chart_err     = None
    try:
        raw = ticker.history(period="1d", interval="15m",
                             auto_adjust=True, prepost=True)
        if raw is None or raw.empty or "Close" not in raw.columns:
            chart_err = "history() returned no data"
        else:
            # Ensure tz-aware index
            if raw.index.tz is None:
                raw.index = raw.index.tz_localize("UTC")
            raw.index = raw.index.tz_convert(PST)

            # Clip to 06:00–17:00 PST
            raw = raw.between_time("06:00", "17:00")

            # Clean Close column
            raw["Close"] = pd.to_numeric(raw["Close"], errors="coerce")
            raw = raw[raw["Close"].notna()]
            raw = raw[~raw["Close"].isin([float("inf"), float("-inf")])]

            if raw.empty:
                chart_err = "No bars in 06:00–17:00 PST window after cleaning"
            else:
                chart_df = raw
    except Exception as exc:
        chart_err = str(exc)

    # ── Price / metadata: use fast info + fallback to chart_df ────────────────
    info = {}
    try:
        info = ticker.info or {}
    except Exception:
        pass

    # Derive current price
    current_price = info.get("currentPrice") or info.get("regularMarketPrice")
    if current_price is None and chart_df is not None and not chart_df.empty:
        current_price = float(chart_df["Close"].iloc[-1])
    if current_price is None:
        raise ValueError(f"No price data available for {symbol}.")
    current_price = float(current_price)
    prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
    if prev_close is None and chart_df is not None and not chart_df.empty:
        prev_close = float(chart_df["Open"].iloc[0])
    try:
        day_change_pct = (
            (current_price - float(prev_close)) / float(prev_close) * 100
            if prev_close and float(prev_close) != 0 else 0.0
        )
    except Exception:
        day_change_pct = 0.0

    ah_price = None; ah_change_pct = None
    try:
        raw_ah = info.get("postMarketPrice") or info.get("preMarketPrice")
        if raw_ah:
            ah_price = float(raw_ah)
            ah_change_pct = (ah_price - current_price) / current_price * 100
    except Exception:
        ah_price = None

    volume = info.get("regularMarketVolume") or info.get("volume")
    if volume is None and chart_df is not None and "Volume" in chart_df.columns:
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
                        earnings_date = pd.Timestamp(str(val)[:10]).strftime("%b-%d-%Y")
                elif isinstance(cal, pd.DataFrame) and not cal.empty:
                    if "Earnings Date" in cal.index:
                        val = cal.loc["Earnings Date"].iloc[0]
                        earnings_date = pd.Timestamp(str(val)[:10]).strftime("%b-%d-%Y")
        except Exception:
            earnings_date = "Unavailable"

    # 52-week range
    week52_low  = info.get("fiftyTwoWeekLow")
    week52_high = info.get("fiftyTwoWeekHigh")
    if week52_low and week52_high:
        week52_range = f"${float(week52_low):,.2f} – ${float(week52_high):,.2f}"
    else:
        week52_range = "—"

    # Price target (analyst mean target)
    target_raw = info.get("targetMeanPrice") or info.get("targetMedianPrice")
    price_target = f"${float(target_raw):,.2f}" if target_raw else "—"

    return {
        "chart_df": chart_df, "chart_err": chart_err,
        "price": current_price,
        "prev_close": prev_close, "day_change_pct": day_change_pct,
        "ah_price": ah_price, "ah_change_pct": ah_change_pct,
        "volume": volume, "earnings": earnings_date,
        "week52_range": week52_range, "price_target": price_target,
    }


@st.cache_data(ttl=0, show_spinner=False)
def fetch_week_earnings(start_str: str, end_str: str, _cache_key: int):
    """
    Fetches the earnings calendar for the given week using yahoo_fin.
    Falls back to yfinance per-ticker calendar if yahoo_fin fails.
    Returns (rows, error_msg).
    """
    import yahoo_fin.stock_info as si

    start_d = date.fromisoformat(start_str)
    end_d   = date.fromisoformat(end_str)
    equity_syms = {s for s in TICKERS if s not in NO_EARNINGS}

    bulk_hits: dict[str, date] = {}
    errors: list = []

    # ── yahoo_fin bulk call ────────────────────────────────────────────────────
    try:
        raw = si.get_earnings_calendar()
        if raw is not None and not raw.empty:
            df = raw.copy()
            # Normalize column names
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
            ticker_col = next(
                (c for c in df.columns if c in ("ticker", "symbol", "company")), None
            )
            date_col = next(
                (c for c in df.columns
                 if c in ("startdatetime", "earnings_date", "date", "report_date")
                 or ("date" in c)), None
            )
            if ticker_col and date_col:
                for _, row in df.iterrows():
                    sym = str(row[ticker_col]).upper().strip()
                    if sym in equity_syms:
                        try:
                            d = pd.Timestamp(row[date_col]).date()
                            if start_d <= d <= end_d:
                                if sym not in bulk_hits or d < bulk_hits[sym]:
                                    bulk_hits[sym] = d
                        except Exception:
                            pass
            else:
                errors.append(
                    f"yahoo_fin: could not identify ticker/date columns "
                    f"(found: {list(df.columns)})"
                )
    except Exception as exc:
        errors.append(f"yahoo_fin.get_earnings_calendar: {exc}")

    # ── Per-ticker yfinance fallback for any sym not found via yahoo_fin ───────
    for sym in equity_syms - set(bulk_hits.keys()):
        try:
            cal = yf.Ticker(sym).calendar
            if cal is None:
                continue
            dates_found = []
            if isinstance(cal, dict):
                ed = cal.get("Earnings Date")
                if ed:
                    for v in (ed if isinstance(ed, (list, tuple)) else [ed]):
                        try: dates_found.append(pd.Timestamp(v).date())
                        except Exception: pass
            elif isinstance(cal, pd.DataFrame) and not cal.empty:
                if "Earnings Date" in cal.index:
                    cell = cal.loc["Earnings Date"]
                    for v in (cell if hasattr(cell, "__iter__") else [cell.iloc[0]]):
                        try: dates_found.append(pd.Timestamp(v).date())
                        except Exception: pass
            matched = [d for d in dates_found if start_d <= d <= end_d]
            if matched:
                bulk_hits[sym] = sorted(matched)[0]
        except Exception as exc:
            errors.append(f"{sym}: {exc}")

    # ── Resolve prices & build rows ────────────────────────────────────────────
    rows = []
    for sym, earn_date in bulk_hits.items():
        price = None
        try:
            info  = yf.Ticker(sym).info or {}
            p     = info.get("currentPrice") or info.get("regularMarketPrice")
            price = float(p) if p else None
        except Exception:
            pass
        rows.append({"sym": sym, "name": TICKERS.get(sym, sym), "price": price, "date": earn_date})

    rows.sort(key=lambda r: r["date"])

    error_msg = None
    if not rows and errors:
        error_msg = "Could not retrieve earnings data: " + "; ".join(errors[:3])
    return rows, error_msg


# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now(pytz.timezone("America/Los_Angeles"))
if "cache_key" not in st.session_state:
    st.session_state.cache_key = 0
if "ec_week_offset" not in st.session_state:
    st.session_state.ec_week_offset = 0


# ══════════════════════════════════════════════════════════════════════════════
#  TOP NAV — replaces sidebar; uses query param for page state
# ══════════════════════════════════════════════════════════════════════════════
_qp   = st.query_params.get("page", "dashboard")
page  = "📅  Earnings Calendar" if _qp == "earnings" else "📊  Stock Dashboard"

_dash_cls     = "active" if page == "📊  Stock Dashboard"   else ""
_earn_cls     = "active" if page == "📅  Earnings Calendar" else ""

st.markdown(f"""
<div class="top-nav">
  <a href="?page=dashboard" class="{_dash_cls}">📊&nbsp; Stock Dashboard</a>
  <a href="?page=earnings"  class="{_earn_cls}">📅&nbsp; Earnings Calendar</a>
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
          <span class="dash-pill">Live · 12 Assets · PST</span>
        </div>""", unsafe_allow_html=True)
        st.markdown(
            f'<div class="dash-timestamp">Last refreshed &nbsp;·&nbsp; '
            f'{st.session_state.last_refresh.strftime("%b %d, %Y  %H:%M:%S PST")}</div>',
            unsafe_allow_html=True,
        )
    with btn_col:
        st.write("")
        if st.button("⟳  Refresh Data", key="dash_refresh"):
            fetch_ticker_data.clear()
            fetch_week_earnings.clear()
            st.session_state.last_refresh = datetime.now(pytz.timezone("America/Los_Angeles"))
            st.session_state.cache_key += 1
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    tickers_list = list(TICKERS.keys())
    for row_start in range(0, len(tickers_list), 4):
        row_syms = tickers_list[row_start : row_start + 4]
        cols = st.columns(4, gap="medium")
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

                price      = data["price"]
                prev_close = data["prev_close"]
                chg        = data["day_change_pct"]
                chg_dollar = (price - prev_close) if (price and prev_close) else 0.0
                is_up      = chg >= 0
                is_flat    = abs(chg) < 0.01
                badge_cls  = "badge-flat" if is_flat else ("badge-up" if is_up else "badge-down")
                chg_arrow  = "" if is_flat else ("▲" if is_up else "▼")
                dollar_str = f"${abs(chg_dollar):,.2f}"

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
                      {chg_arrow} {dollar_str} &nbsp;·&nbsp; {abs(chg):.2f}%
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

                chart_df  = data["chart_df"]
                chart_err = data.get("chart_err")
                fig = make_chart(chart_df, is_up) if chart_df is not None else None
                if fig is None:
                    err_detail = chart_err or "No bars in trading window"
                    st.markdown(f"""
                    <div style="height:90px; display:flex; flex-direction:column;
                                align-items:center; justify-content:center;
                                background:rgba(90,120,144,0.07);
                                border:1px dashed #a9cce3; border-radius:10px;
                                margin:6px 0; padding: 0 8px; text-align:center;">
                      <span style="font-size:1rem; margin-bottom:4px;">📊</span>
                      <span style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem;
                                   color:#5a7a90;">Chart unavailable</span>
                      <span style="font-family:'IBM Plex Mono',monospace; font-size:0.58rem;
                                   color:#8aabb0; margin-top:2px;">{err_detail}</span>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                        config={"displayModeBar": False},
                        key=f"chart_{sym}_{st.session_state.cache_key}",
                    )

                earnings_label = "N/A" if sym in ETF_TICKERS else data["earnings"]
                week52         = data["week52_range"]
                price_tgt      = "N/A" if sym in ETF_TICKERS else data["price_target"]

                # Determine if earnings is within 30 days → highlight
                earnings_cls = "metric-value"
                if earnings_label not in ("N/A", "Unavailable", "—") and sym not in ETF_TICKERS:
                    try:
                        earn_dt = datetime.strptime(earnings_label, "%b-%d-%Y").date()
                        days_away = (earn_dt - date.today()).days
                        if 0 <= days_away <= 30:
                            earnings_cls = "metric-value-earnings-soon"
                    except Exception:
                        pass

                st.markdown(f"""
                <div class="metrics-row">
                  <div class="metric-block">
                    <div class="metric-label">Volume</div>
                    <div class="metric-value">{fmt_volume(data['volume'])}</div>
                  </div>
                  <div class="metric-block">
                    <div class="metric-label">Next Earnings</div>
                    <div class="{earnings_cls}">{earnings_label}</div>
                  </div>
                  <div class="metric-block">
                    <div class="metric-label">52W Range</div>
                    <div class="metric-value metric-value-sm">{week52}</div>
                  </div>
                  <div class="metric-block">
                    <div class="metric-label">Price Target</div>
                    <div class="metric-value">{price_tgt}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

        st.write("")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: EARNINGS CALENDAR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📅  Earnings Calendar":

    today      = date.today()
    cur_monday = week_monday(today)

    # ── Header + Refresh ──────────────────────────────────────────────────────
    header_col, btn_col = st.columns([6, 1])
    with header_col:
        st.markdown("""
        <div class="dash-header">
          <span class="dash-title">EARNINGS CALENDAR</span>
          <span class="dash-pill">Market-Wide</span>
        </div>""", unsafe_allow_html=True)
        st.markdown(
            f'<div class="dash-timestamp">Last refreshed &nbsp;·&nbsp; '
            f'{st.session_state.last_refresh.strftime("%b %d, %Y  %H:%M:%S PST")}</div>',
            unsafe_allow_html=True,
        )
    with btn_col:
        st.write("")
        if st.button("⟳  Refresh Data", key="ec_refresh"):
            fetch_ticker_data.clear()
            fetch_week_earnings.clear()
            st.session_state.last_refresh = datetime.now(pytz.timezone("America/Los_Angeles"))
            st.session_state.cache_key   += 1
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Week Navigator ────────────────────────────────────────────────────────
    offset    = st.session_state.ec_week_offset
    wk_monday = cur_monday + timedelta(weeks=offset)
    wk_sunday = week_sunday(wk_monday)
    wk_start_str = wk_monday.strftime("%Y-%m-%d")
    wk_end_str   = wk_sunday.strftime("%Y-%m-%d")
    wk_range_str = f"{wk_monday.strftime('%b %d, %Y')} – {wk_sunday.strftime('%b %d, %Y')}"

    if offset == 0:
        ctx_cls, ctx_txt = "current", "Current Week"
    elif offset == 1:
        ctx_cls, ctx_txt = "next",    "Next Week"
    elif offset == -1:
        ctx_cls, ctx_txt = "other",   "Previous Week"
    else:
        ctx_cls = "other"
        ctx_txt = f"{'−' if offset < 0 else '+'}{abs(offset)} weeks from today"

    nav_l, nav_c, nav_r = st.columns([1, 10, 1])

    with nav_l:
        if st.button("◀", key="ec_prev", help="Previous week"):
            st.session_state.ec_week_offset -= 1
            st.rerun()

    with nav_c:
        st.markdown(f"""
        <div style="text-align:center; padding:6px 0;">
          <div><span class="ec-nav-context {ctx_cls}">{ctx_txt}</span></div>
          <div class="ec-nav-week-label">
            {wk_monday.strftime('%A, %b %d')} — {wk_sunday.strftime('%A, %b %d, %Y')}
          </div>
          <div class="ec-nav-range">
            Monday → Sunday &nbsp;·&nbsp; ISO Week #{wk_monday.isocalendar()[1]}
          </div>
        </div>""", unsafe_allow_html=True)

    with nav_r:
        if st.button("▶", key="ec_next", help="Next week"):
            st.session_state.ec_week_offset += 1
            st.rerun()

    st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)

    if offset != 0:
        jmp_col, _ = st.columns([2, 6])
        with jmp_col:
            if st.button("⏎  Jump to Current Week", key="ec_jump"):
                st.session_state.ec_week_offset = 0
                st.rerun()

    # ── Fetch ─────────────────────────────────────────────────────────────────
    with st.spinner(f"Fetching earnings for {wk_range_str}…"):
        try:
            week_rows, api_error = fetch_week_earnings(
                wk_start_str, wk_end_str, st.session_state.cache_key,
            )
        except Exception as exc:
            week_rows = []; api_error = str(exc)

    # ── Error ─────────────────────────────────────────────────────────────────
    if api_error and not week_rows:
        st.markdown(f"""
        <div class="ec-empty" style="border-color:rgba(255,77,106,0.35);">
          <div class="ec-empty-icon">⚠️</div>
          <div class="ec-empty-title" style="color:#ff8096;">Could not load earnings data</div>
          <div class="ec-empty-sub">{api_error}</div>
        </div>""", unsafe_allow_html=True)

    # ── Empty ─────────────────────────────────────────────────────────────────
    elif not week_rows:
        st.markdown(f"""
        <div class="ec-empty">
          <div class="ec-empty-icon">🗓️</div>
          <div class="ec-empty-title">No earnings scheduled for tracked tickers this week</div>
          <div class="ec-empty-sub">
            None of the {len(TICKERS) - len(NO_EARNINGS)} tracked equities report earnings
            during<br>{wk_range_str}.<br>Use ◀ ▶ to navigate to another week.
          </div>
        </div>""", unsafe_allow_html=True)

    # ── Table ─────────────────────────────────────────────────────────────────
    else:
        n = len(week_rows)
        st.markdown(
            f'<div class="ec-count-badge">📋 &nbsp;'
            f'{n} compan{"y" if n == 1 else "ies"} reporting this week</div>',
            unsafe_allow_html=True,
        )
        rows_html = ""
        for r in week_rows:
            d = r["date"]
            if d == today:
                pill_cls, day_str = "today",    "TODAY"
            elif d == today + timedelta(days=1):
                pill_cls, day_str = "tomorrow", "TOMORROW"
            else:
                pill_cls, day_str = "upcoming", d.strftime("%a, %b %d")
            rows_html += f"""
            <tr>
              <td>
                <div class="ec-sym">{r['sym']}</div>
                <div class="ec-name">{r['name']}</div>
              </td>
              <td class="ec-price">{fmt_price(r.get('price'))}</td>
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

    etf_list = ", ".join(sorted(NO_EARNINGS))
    st.markdown(
        f'<div class="ec-etf-note">ℹ️ &nbsp;ETFs & trusts excluded: {etf_list}</div>',
        unsafe_allow_html=True,
    )
    st.write("")
