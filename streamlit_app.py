# ==========================================================
# WEOS - World Economic Operating System
# ĐOẠN 001
# ==========================================================

import os
import json
import math
import time
import random
import sqlite3
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import yfinance as yf

from bs4 import BeautifulSoup

# ==========================================================
# STREAMLIT CONFIG
# ==========================================================

st.set_page_config(
    page_title="WEOS",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# APP INFO
# ==========================================================

APP_NAME = "WEOS"
APP_VERSION = "0.0.1"
AUTHOR = "Duy"

# ==========================================================
# SESSION STATE
# ==========================================================

if "startup_time" not in st.session_state:
    st.session_state.startup_time = datetime.now()

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "logs" not in st.session_state:
    st.session_state.logs = []

if "gold_price" not in st.session_state:
    st.session_state.gold_price = None

if "dxy_price" not in st.session_state:
    st.session_state.dxy_price = None

if "news" not in st.session_state:
    st.session_state.news = []

if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

if "database_ready" not in st.session_state:
    st.session_state.database_ready = False

# ==========================================================
# CONSTANTS
# ==========================================================

GOLD_SYMBOL = "GC=F"
SILVER_SYMBOL = "SI=F"
DXY_SYMBOL = "DX-Y.NYB"
SP500_SYMBOL = "^GSPC"
NASDAQ_SYMBOL = "^IXIC"

REQUEST_TIMEOUT = 15

# ==========================================================
# DATABASE
# ==========================================================

DB_NAME = "weos.db"

connection = sqlite3.connect(
    DB_NAME,
    check_same_thread=False
)

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS system_logs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT,
    level TEXT,
    message TEXT
)
""")

connection.commit()

st.session_state.database_ready = True

# ==========================================================
# LOG FUNCTION
# ==========================================================

def write_log(level: str, message: str):

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO system_logs(time,level,message)
        VALUES(?,?,?)
        """,
        (
            now,
            level,
            message
        )
    )

    connection.commit()

    st.session_state.logs.append(
        {
            "time": now,
            "level": level,
            "message": message
        }
    )

# ==========================================================
# FORMAT FUNCTIONS
# ==========================================================

def format_price(value):

    if value is None:
        return "--"

    return f"{value:,.2f}"


def format_percent(value):

    return f"{value:.2f} %"


def current_time():

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==========================================================
# STARTUP LOG
# ==========================================================

write_log(
    "INFO",
    "WEOS started."
)

# ==========================================================
# HEADER
# ==========================================================

st.title("🌍 WEOS")

st.caption(
    f"{APP_NAME}  |  Version {APP_VERSION}"
)

st.divider()

# ==========================================================
# WEOS
# ĐOẠN 002
# ==========================================================

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.title("🌍 WEOS")

    st.caption("World Economic Operating System")

    st.divider()

    page = st.radio(
        "Điều hướng",
        [
            "Dashboard",
            "Gold",
            "Macro",
            "News",
            "Forex",
            "Crypto",
            "Stocks",
            "Economic Calendar",
            "AI Analysis",
            "Database",
            "Settings"
        ]
    )

    st.session_state.page = page

    st.divider()

    auto_refresh = st.checkbox(
        "Tự động làm mới",
        value=False
    )

    refresh_seconds = st.slider(
        "Chu kỳ (giây)",
        5,
        300,
        30
    )

    st.divider()

    st.markdown("### Hệ thống")

    st.write("Khởi động:")
    st.success(
        st.session_state.startup_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    st.write("Database")

    if st.session_state.database_ready:
        st.success("Đã kết nối")
    else:
        st.error("Chưa kết nối")

    st.divider()

    st.markdown("### Watchlist")

    if len(st.session_state.watchlist) == 0:

        st.info("Chưa có dữ liệu")

    else:

        for item in st.session_state.watchlist:
            st.write(item)

# ==========================================================
# MAIN HEADER
# ==========================================================

left, right = st.columns([4, 1])

with left:

    st.header(st.session_state.page)

with right:

    st.metric(
        "Thời gian",
        current_time()
    )

st.divider()

# ==========================================================
# DASHBOARD
# ==========================================================

if st.session_state.page == "Dashboard":

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Gold",
            "--",
            "-"
        )

    with c2:

        st.metric(
            "DXY",
            "--",
            "-"
        )

    with c3:

        st.metric(
            "S&P500",
            "--",
            "-"
        )

    with c4:

        st.metric(
            "NASDAQ",
            "--",
            "-"
        )

    st.divider()

    st.subheader("Tổng quan")

    st.info(
        "WEOS đang khởi tạo dữ liệu thị trường..."
    )

    st.write("Các module sẽ được kích hoạt theo từng giai đoạn.")

# ==========================================================
# PAGE PLACEHOLDER
# ==========================================================

elif st.session_state.page == "Gold":

    st.header("Gold")

elif st.session_state.page == "Macro":

    st.header("Macro")

elif st.session_state.page == "News":

    st.header("News")

elif st.session_state.page == "Forex":

    st.header("Forex")

elif st.session_state.page == "Crypto":

    st.header("Crypto")

elif st.session_state.page == "Stocks":

    st.header("Stocks")

elif st.session_state.page == "Economic Calendar":

    st.header("Economic Calendar")

elif st.session_state.page == "AI Analysis":

    st.header("AI Analysis")

elif st.session_state.page == "Database":

    st.header("Database")

elif st.session_state.page == "Settings":

    st.header("Settings")
```
# ==========================================================
# WEOS
# ĐOẠN 003
# ==========================================================

# ==========================================================
# MARKET DATA
# ==========================================================

@st.cache_data(ttl=30)
def get_yfinance_price(symbol):

    try:

        ticker = yf.Ticker(symbol)

        history = ticker.history(period="2d")

        if history.empty:
            return None

        latest = float(history["Close"].iloc[-1])

        previous = float(history["Close"].iloc[-2])

        change = latest - previous

        percent = (change / previous) * 100

        return {
            "price": latest,
            "change": change,
            "percent": percent
        }

    except Exception:

        return None


# ==========================================================
# LOAD MARKET
# ==========================================================

gold_data = get_yfinance_price(GOLD_SYMBOL)

dxy_data = get_yfinance_price(DXY_SYMBOL)

sp500_data = get_yfinance_price(SP500_SYMBOL)

nasdaq_data = get_yfinance_price(NASDAQ_SYMBOL)

# ==========================================================
# SAVE SESSION
# ==========================================================

if gold_data:

    st.session_state.gold_price = gold_data["price"]

if dxy_data:

    st.session_state.dxy_price = dxy_data["price"]

# ==========================================================
# SMALL UTILITIES
# ==========================================================

def metric_value(data):

    if data is None:

        return "--"

    return format_price(data["price"])


def metric_delta(data):

    if data is None:

        return "--"

    return f'{data["change"]:+.2f} ({data["percent"]:+.2f}%)'


# ==========================================================
# SYSTEM STATUS
# ==========================================================

market_loaded = True

if gold_data is None:
    market_loaded = False

if dxy_data is None:
    market_loaded = False

# ==========================================================
# HEADER STATUS
# ==========================================================

status_left, status_right = st.columns([3, 1])

with status_left:

    if market_loaded:

        st.success("Dữ liệu thị trường đã tải.")

    else:

        st.warning("Một số dữ liệu chưa tải được.")

with status_right:

    st.write(current_time())

st.divider()
```

# ==========================================================
# WEOS
# ĐOẠN 004
# ==========================================================

# ==========================================================
# DASHBOARD REALTIME METRICS
# ==========================================================

if st.session_state.page == "Dashboard":

    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:

        st.metric(
            label="🥇 Gold",
            value=metric_value(gold_data),
            delta=metric_delta(gold_data)
        )

    with metric2:

        st.metric(
            label="💵 DXY",
            value=metric_value(dxy_data),
            delta=metric_delta(dxy_data)
        )

    with metric3:

        st.metric(
            label="📈 S&P 500",
            value=metric_value(sp500_data),
            delta=metric_delta(sp500_data)
        )

    with metric4:

        st.metric(
            label="💻 NASDAQ",
            value=metric_value(nasdaq_data),
            delta=metric_delta(nasdaq_data)
        )

    st.divider()

    left, right = st.columns([3, 2])

    # ======================================================
    # SYSTEM INFORMATION
    # ======================================================

    with left:

        st.subheader("WEOS Status")

        info = pd.DataFrame(
            {
                "Item": [
                    "Application",
                    "Version",
                    "Current Page",
                    "Database",
                    "Market Data",
                    "Startup"
                ],
                "Value": [
                    APP_NAME,
                    APP_VERSION,
                    st.session_state.page,
                    "Connected"
                    if st.session_state.database_ready
                    else "Disconnected",
                    "Loaded"
                    if market_loaded
                    else "Loading",
                    st.session_state.startup_time.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                ]
            }
        )

        st.dataframe(
            info,
            use_container_width=True,
            hide_index=True
        )

    # ======================================================
    # WATCHLIST
    # ======================================================

    with right:

        st.subheader("Watchlist")

        if len(st.session_state.watchlist) == 0:

            st.info("Danh sách đang trống.")

        else:

            watch_df = pd.DataFrame(
                st.session_state.watchlist
            )

            st.dataframe(
                watch_df,
                use_container_width=True,
                hide_index=True
            )

    st.divider()

    st.subheader("System Log")

    if len(st.session_state.logs) == 0:

        st.warning("Không có log.")

    else:

        log_df = pd.DataFrame(
            st.session_state.logs
        )

        st.dataframe(
            log_df,
            use_container_width=True,
            hide_index=True
        )

    st.divider()
```

# ==========================================================
# WEOS
# ĐOẠN 005
# ==========================================================

# ==========================================================
# GOLD PAGE
# ==========================================================

if st.session_state.page == "Gold":

    st.title("🥇 Gold Market")

    if gold_data is None:

        st.error("Không thể tải dữ liệu Gold.")

    else:

        price = gold_data["price"]
        change = gold_data["change"]
        percent = gold_data["percent"]

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "Current Price",
                format_price(price),
                f"{change:+.2f}"
            )

        with c2:

            st.metric(
                "Change %",
                format_percent(percent)
            )

        with c3:

            trend = "Bullish"

            if change < 0:
                trend = "Bearish"

            st.metric(
                "Trend",
                trend
            )

        st.divider()

        history = yf.download(
            GOLD_SYMBOL,
            period="3mo",
            interval="1d",
            progress=False
        )

        if not history.empty:

            fig = go.Figure()

            fig.add_trace(

                go.Candlestick(

                    x=history.index,

                    open=history["Open"],

                    high=history["High"],

                    low=history["Low"],

                    close=history["Close"],

                    name="Gold"
                )

            )

            fig.update_layout(

                height=650,

                xaxis_title="Date",

                yaxis_title="Price",

                template="plotly_white"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.divider()

        st.subheader("Market Summary")

        if change > 0:

            st.success(
                "Giá vàng hiện đang tăng so với phiên trước."
            )

        elif change < 0:

            st.error(
                "Giá vàng hiện đang giảm so với phiên trước."
            )

        else:

            st.info(
                "Giá vàng gần như không thay đổi."
            )

        st.write(
            f"Current Price : {format_price(price)}"
        )

        st.write(
            f"Daily Change : {change:.2f}"
        )

        st.write(
            f"Percentage : {percent:.2f}%"
        )

        st.divider()

# ==========================================================
# WEOS
# ĐOẠN 006
# ==========================================================

# ==========================================================
# DXY PAGE
# ==========================================================

if st.session_state.page == "Forex":

    st.title("💵 US Dollar Index (DXY)")

    if dxy_data is None:

        st.error("Không thể tải dữ liệu DXY.")

    else:

        price = dxy_data["price"]
        change = dxy_data["change"]
        percent = dxy_data["percent"]

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "Current DXY",
                format_price(price),
                f"{change:+.2f}"
            )

        with c2:

            st.metric(
                "Change %",
                format_percent(percent)
            )

        with c3:

            if change > 0:
                trend = "USD Strong"

            elif change < 0:
                trend = "USD Weak"

            else:
                trend = "Neutral"

            st.metric(
                "Trend",
                trend
            )

        st.divider()

        history = yf.download(
            DXY_SYMBOL,
            period="3mo",
            interval="1d",
            progress=False
        )

        if not history.empty:

            fig = go.Figure()

            fig.add_trace(

                go.Scatter(

                    x=history.index,

                    y=history["Close"],

                    mode="lines",

                    name="DXY"

                )

            )

            fig.update_layout(

                height=650,

                template="plotly_white",

                xaxis_title="Date",

                yaxis_title="Index"

            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.divider()

        st.subheader("Gold Relationship")

        if change > 0:

            st.warning(
                """
                DXY đang tăng.

                Thông thường điều này gây áp lực giảm
                lên giá vàng, tuy nhiên cần kết hợp
                với lợi suất trái phiếu và dữ liệu kinh tế.
                """
            )

        elif change < 0:

            st.success(
                """
                DXY đang giảm.

                Đây thường là điều kiện hỗ trợ
                cho giá vàng nếu các yếu tố khác
                không thay đổi.
                """
            )

        else:

            st.info(
                "DXY hiện gần như đi ngang."
            )

        st.divider()

# ==========================================================
# QUICK MARKET TABLE
# ==========================================================

market_table = pd.DataFrame(
    [
        {
            "Market": "Gold",
            "Price": metric_value(gold_data),
            "Change": metric_delta(gold_data)
        },
        {
            "Market": "DXY",
            "Price": metric_value(dxy_data),
            "Change": metric_delta(dxy_data)
        },
        {
            "Market": "S&P500",
            "Price": metric_value(sp500_data),
            "Change": metric_delta(sp500_data)
        },
        {
            "Market": "NASDAQ",
            "Price": metric_value(nasdaq_data),
            "Change": metric_delta(nasdaq_data)
        }
    ]
)

# ==========================================================
# WEOS
# ĐOẠN 007
# ==========================================================

# ==========================================================
# MARKET OVERVIEW
# ==========================================================

if st.session_state.page == "Macro":

    st.title("🌍 Global Market Overview")

    st.dataframe(
        market_table,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("Market Interpretation")

    if gold_data and dxy_data:

        gold_up = gold_data["change"] > 0
        dxy_up = dxy_data["change"] > 0

        if gold_up and not dxy_up:

            st.success(
                """
                Gold ↑
                DXY ↓

                Đây là trạng thái khá tích cực đối với vàng.
                USD suy yếu tạo điều kiện để kim loại quý tăng giá.
                """
            )

        elif (not gold_up) and dxy_up:

            st.error(
                """
                Gold ↓
                DXY ↑

                Đây là trạng thái thường xuyên xuất hiện
                khi dòng tiền chuyển sang USD.
                """
            )

        elif gold_up and dxy_up:

            st.warning(
                """
                Gold ↑
                DXY ↑

                Hai thị trường cùng tăng.
                Điều này thường cho thấy còn có
                yếu tố khác tác động như:
                - Địa chính trị
                - Lợi suất trái phiếu
                - Kỳ vọng FED
                """
            )

        else:

            st.info(
                """
                Gold ↓
                DXY ↓

                Hai thị trường cùng suy yếu.
                Cần quan sát thêm dòng tiền
                và dữ liệu kinh tế.
                """
            )

    st.divider()

    st.subheader("Market Health")

    score = 0

    if gold_data:

        if gold_data["change"] > 0:
            score += 25

    if dxy_data:

        if dxy_data["change"] < 0:
            score += 25

    if sp500_data:

        if sp500_data["change"] > 0:
            score += 25

    if nasdaq_data:

        if nasdaq_data["change"] > 0:
            score += 25

    st.progress(score / 100)

    st.write(f"Market Score : {score}/100")

    st.divider()

# ==========================================================
# WATCHLIST FUNCTIONS
# ==========================================================

def add_watchlist(name, symbol):

    st.session_state.watchlist.append(
        {
            "Name": name,
            "Symbol": symbol
        }
    )

def clear_watchlist():

    st.session_state.watchlist.clear()

# ==========================================================
# WATCHLIST PAGE
# ==========================================================

if st.session_state.page == "Settings":

    st.title("⚙ Settings")

    st.subheader("Watchlist")

    col1, col2 = st.columns(2)

    with col1:

        if st.button("Add Gold"):

            add_watchlist(
                "Gold",
                GOLD_SYMBOL
            )

        if st.button("Add DXY"):

            add_watchlist(
                "DXY",
                DXY_SYMBOL
            )

    with col2:

        if st.button("Clear Watchlist"):

            clear_watchlist()

    st.divider()

    st.subheader("Current Watchlist")

    if len(st.session_state.watchlist) == 0:

        st.info("Watchlist trống.")

    else:

        st.dataframe(
            pd.DataFrame(
                st.session_state.watchlist
            ),
            use_container_width=True,
            hide_index=True
        )

    st.divider()

# ==========================================================
# WEOS
# ĐOẠN 008
# ==========================================================

# ==========================================================
# NEWS FUNCTIONS
# ==========================================================

@st.cache_data(ttl=300)
def load_finance_news():

    url = "https://finance.yahoo.com"

    articles = []

    try:

        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        titles = soup.find_all("h3")

        for item in titles[:20]:

            text = item.get_text(strip=True)

            if len(text) > 10:

                articles.append(text)

        return articles

    except Exception:

        return []


# ==========================================================
# LOAD NEWS
# ==========================================================

news_data = load_finance_news()

if len(news_data) > 0:

    st.session_state.news = news_data


# ==========================================================
# NEWS PAGE
# ==========================================================

if st.session_state.page == "News":

    st.title("📰 Financial News")

    if len(st.session_state.news) == 0:

        st.warning(
            "Không tải được dữ liệu tin tức."
        )

    else:

        st.success(
            f"Tìm thấy {len(st.session_state.news)} tin."
        )

        st.divider()

        for index, title in enumerate(
            st.session_state.news,
            start=1
        ):

            st.markdown(
                f"**{index}. {title}**"
            )

            st.divider()

# ==========================================================
# MARKET SUMMARY CARD
# ==========================================================

st.sidebar.markdown("---")

st.sidebar.subheader("Market Summary")

if gold_data:

    st.sidebar.write(
        f"🥇 Gold : {metric_value(gold_data)}"
    )

if dxy_data:

    st.sidebar.write(
        f"💵 DXY : {metric_value(dxy_data)}"
    )

if sp500_data:

    st.sidebar.write(
        f"📈 S&P500 : {metric_value(sp500_data)}"
    )

if nasdaq_data:

    st.sidebar.write(
        f"💻 NASDAQ : {metric_value(nasdaq_data)}"
    )

st.sidebar.markdown("---")

st.sidebar.caption(
    f"Last Update : {current_time()}"
)

# ==========================================================
# FOOTER
# ==========================================================

st.divider()

footer_left, footer_center, footer_right = st.columns(3)

with footer_left:

    st.caption(f"{APP_NAME}")

with footer_center:

    st.caption(f"Version {APP_VERSION}")

with footer_right:

    st.caption(current_time())

# ==========================================================
# WEOS
# ĐOẠN 009
# ==========================================================

# ==========================================================
# ECONOMIC CALENDAR
# ==========================================================

calendar_events = [

    {
        "Time": "15:30",
        "Country": "🇺🇸 USA",
        "Event": "CPI",
        "Impact": "High"
    },
    {
        "Time": "15:30",
        "Country": "🇺🇸 USA",
        "Event": "PPI",
        "Impact": "High"
    },
    {
        "Time": "21:00",
        "Country": "🇺🇸 USA",
        "Event": "FOMC",
        "Impact": "High"
    },
    {
        "Time": "21:00",
        "Country": "🇺🇸 USA",
        "Event": "Interest Rate",
        "Impact": "High"
    },
    {
        "Time": "15:30",
        "Country": "🇺🇸 USA",
        "Event": "NFP",
        "Impact": "High"
    },
    {
        "Time": "15:30",
        "Country": "🇺🇸 USA",
        "Event": "Unemployment Rate",
        "Impact": "High"
    },
    {
        "Time": "15:30",
        "Country": "🇺🇸 USA",
        "Event": "Retail Sales",
        "Impact": "Medium"
    },
    {
        "Time": "15:30",
        "Country": "🇺🇸 USA",
        "Event": "GDP",
        "Impact": "High"
    }

]

# ==========================================================
# CALENDAR PAGE
# ==========================================================

if st.session_state.page == "Economic Calendar":

    st.title("📅 Economic Calendar")

    calendar_df = pd.DataFrame(
        calendar_events
    )

    st.dataframe(
        calendar_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("High Impact Events")

    for event in calendar_events:

        if event["Impact"] == "High":

            st.warning(
                f'{event["Time"]}  |  {event["Country"]}  |  {event["Event"]}'
            )

# ==========================================================
# MARKET CLOCK
# ==========================================================

st.sidebar.subheader("Market Clock")

utc_now = datetime.utcnow()

st.sidebar.write(
    "UTC :",
    utc_now.strftime("%H:%M:%S")
)

ny_time = utc_now - timedelta(hours=4)

st.sidebar.write(
    "New York :",
    ny_time.strftime("%H:%M:%S")
)

london_time = utc_now + timedelta(hours=1)

st.sidebar.write(
    "London :",
    london_time.strftime("%H:%M:%S")
)

tokyo_time = utc_now + timedelta(hours=9)

st.sidebar.write(
    "Tokyo :",
    tokyo_time.strftime("%H:%M:%S")
)

# ==========================================================
# SYSTEM STATISTICS
# ==========================================================

st.sidebar.markdown("---")

st.sidebar.subheader("Statistics")

st.sidebar.write(
    f"Logs : {len(st.session_state.logs)}"
)

st.sidebar.write(
    f"News : {len(st.session_state.news)}"
)

st.sidebar.write(
    f"Watchlist : {len(st.session_state.watchlist)}"
)

st.sidebar.write(
    f"Database : {DB_NAME}"
)

st.sidebar.markdown("---")

# ==========================================================
# WEOS
# ĐOẠN 010
# ==========================================================

# ==========================================================
# AI MARKET ANALYSIS
# ==========================================================

def generate_market_analysis():

    report = []

    if gold_data:

        if gold_data["change"] > 0:

            report.append(
                "• Gold đang trong trạng thái tăng giá."
            )

        elif gold_data["change"] < 0:

            report.append(
                "• Gold đang trong trạng thái giảm giá."
            )

        else:

            report.append(
                "• Gold đang đi ngang."
            )

    if dxy_data:

        if dxy_data["change"] > 0:

            report.append(
                "• Đồng USD đang mạnh lên."
            )

        elif dxy_data["change"] < 0:

            report.append(
                "• Đồng USD đang suy yếu."
            )

        else:

            report.append(
                "• Đồng USD đang ổn định."
            )

    if sp500_data:

        if sp500_data["change"] > 0:

            report.append(
                "• Chứng khoán Mỹ đang tích cực."
            )

        else:

            report.append(
                "• Chứng khoán Mỹ đang chịu áp lực."
            )

    if gold_data and dxy_data:

        if gold_data["change"] > 0 and dxy_data["change"] < 0:

            report.append(
                "• Mô hình Gold ↑ + DXY ↓ đang hỗ trợ xu hướng tăng."
            )

        elif gold_data["change"] < 0 and dxy_data["change"] > 0:

            report.append(
                "• Mô hình Gold ↓ + DXY ↑ gây áp lực giảm lên vàng."
            )

    return report

# ==========================================================
# AI PAGE
# ==========================================================

if st.session_state.page == "AI Analysis":

    st.title("🤖 WEOS AI")

    st.success(
        "Phân tích tự động"
    )

    st.divider()

    analysis = generate_market_analysis()

    if len(analysis) == 0:

        st.warning(
            "Không có dữ liệu."
        )

    else:

        for item in analysis:

            st.write(item)

    st.divider()

    st.subheader("Market Sentiment")

    sentiment = 50

    if gold_data:

        if gold_data["change"] > 0:
            sentiment += 10
        else:
            sentiment -= 10

    if dxy_data:

        if dxy_data["change"] < 0:
            sentiment += 10
        else:
            sentiment -= 10

    if sp500_data:

        if sp500_data["change"] > 0:
            sentiment += 10

    sentiment = max(0, min(sentiment, 100))

    st.progress(sentiment / 100)

    st.metric(
        "Bullish Score",
        f"{sentiment}/100"
    )

    st.divider()

# ==========================================================
# EXPORT LOG
# ==========================================================

def export_logs():

    return pd.DataFrame(
        st.session_state.logs
    )

# ==========================================================
# DOWNLOAD
# ==========================================================

if len(st.session_state.logs) > 0:

    csv = export_logs().to_csv(
        index=False
    )

    st.sidebar.download_button(

        "📄 Export Logs",

        data=csv,

        file_name="weos_logs.csv",

        mime="text/csv"

    )

# ==========================================================
# WEOS
# ĐOẠN 011
# ==========================================================

# ==========================================================
# DATABASE PAGE
# ==========================================================

if st.session_state.page == "Database":

    st.title("🗄 Database")

    st.success("SQLite Database Connected")

    st.divider()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM system_logs
        """
    )

    total_logs = cursor.fetchone()[0]

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Database",
            DB_NAME
        )

    with col2:

        st.metric(
            "System Logs",
            total_logs
        )

    st.divider()

    cursor.execute(
        """
        SELECT
            id,
            time,
            level,
            message
        FROM system_logs
        ORDER BY id DESC
        LIMIT 100
        """
    )

    rows = cursor.fetchall()

    if len(rows) > 0:

        df = pd.DataFrame(
            rows,
            columns=[
                "ID",
                "Time",
                "Level",
                "Message"
            ]
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("Database trống.")

    st.divider()

# ==========================================================
# SYSTEM INFORMATION
# ==========================================================

def get_system_information():

    return {

        "Application": APP_NAME,

        "Version": APP_VERSION,

        "Database": DB_NAME,

        "Python": os.sys.version.split()[0],

        "Startup": st.session_state.startup_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "Current Time": current_time()

    }

# ==========================================================
# SETTINGS PAGE
# ==========================================================

if st.session_state.page == "Settings":

    st.subheader("System Information")

    system_info = get_system_information()

    info_df = pd.DataFrame(

        {

            "Item": list(system_info.keys()),

            "Value": list(system_info.values())

        }

    )

    st.dataframe(

        info_df,

        use_container_width=True,

        hide_index=True

    )

    st.divider()

    st.subheader("Memory")

    st.write(
        f"Session Logs : {len(st.session_state.logs)}"
    )

    st.write(
        f"News Loaded : {len(st.session_state.news)}"
    )

    st.write(
        f"Watchlist : {len(st.session_state.watchlist)}"
    )

    st.write(
        f"Database Ready : {st.session_state.database_ready}"
    )

    st.divider()

# ==========================================================
# END OF CHUNK 011
# ==========================================================

# ==========================================================
# WEOS
# ĐOẠN 012
# ==========================================================

# ==========================================================
# MARKET SENTIMENT ENGINE
# ==========================================================

def calculate_market_sentiment():

    score = 50

    detail = []

    if gold_data:

        if gold_data["change"] > 0:

            score += 10
            detail.append("Gold tăng (+10)")

        else:

            score -= 10
            detail.append("Gold giảm (-10)")

    if dxy_data:

        if dxy_data["change"] < 0:

            score += 10
            detail.append("DXY giảm (+10)")

        else:

            score -= 10
            detail.append("DXY tăng (-10)")

    if sp500_data:

        if sp500_data["change"] > 0:

            score += 10
            detail.append("S&P500 tăng (+10)")

        else:

            score -= 5
            detail.append("S&P500 giảm (-5)")

    if nasdaq_data:

        if nasdaq_data["change"] > 0:

            score += 10
            detail.append("NASDAQ tăng (+10)")

        else:

            score -= 5
            detail.append("NASDAQ giảm (-5)")

    score = max(0, min(score, 100))

    return score, detail

# ==========================================================
# MARKET HEALTH PAGE
# ==========================================================

if st.session_state.page == "Macro":

    st.subheader("Market Sentiment Engine")

    score, detail = calculate_market_sentiment()

    st.progress(score / 100)

    st.metric(
        "Overall Score",
        f"{score}/100"
    )

    st.divider()

    for item in detail:

        st.write("•", item)

    st.divider()

    if score >= 80:

        st.success(
            "Thị trường đang rất tích cực."
        )

    elif score >= 60:

        st.info(
            "Xu hướng đang nghiêng về tích cực."
        )

    elif score >= 40:

        st.warning(
            "Thị trường đang cân bằng."
        )

    else:

        st.error(
            "Thị trường đang khá tiêu cực."
        )

# ==========================================================
# PERFORMANCE MONITOR
# ==========================================================

def calculate_uptime():

    delta = datetime.now() - st.session_state.startup_time

    return str(delta).split(".")[0]

# ==========================================================
# SIDEBAR PERFORMANCE
# ==========================================================

st.sidebar.subheader("Performance")

st.sidebar.write(
    "Uptime"
)

st.sidebar.success(
    calculate_uptime()
)

st.sidebar.write(
    "Python"
)

st.sidebar.info(
    os.sys.version.split()[0]
)

st.sidebar.write(
    "Session Logs"
)

st.sidebar.info(
    len(st.session_state.logs)
)

st.sidebar.write(
    "Watchlist"
)

st.sidebar.info(
    len(st.session_state.watchlist)
)

st.sidebar.write(
    "News"
)

st.sidebar.info(
    len(st.session_state.news)
)

st.sidebar.divider()

# ==========================================================
# RANDOM MARKET QUOTE
# ==========================================================

quotes = [

    "Trend is your friend.",

    "Risk comes first.",

    "Protect capital.",

    "Patience beats emotion.",

    "Follow probability, not hope.",

    "Discipline creates consistency.",

    "Trade the market, not your ego.",

    "Never fight the trend.",

    "Manage risk before profit.",

    "Cash is also a position."

]

st.sidebar.subheader("Market Quote")

st.sidebar.success(
    random.choice(quotes)
)

# ==========================================================
# END OF CHUNK 012
# ==========================================================

# ==========================================================
# WEOS
# ĐOẠN 013
# ==========================================================

# ==========================================================
# PRICE ALERT SYSTEM
# ==========================================================

if "alerts" not in st.session_state:

    st.session_state.alerts = []

def add_price_alert(symbol, price):

    st.session_state.alerts.append(

        {
            "symbol": symbol,
            "price": float(price),
            "created": current_time(),
            "triggered": False
        }

    )

# ==========================================================
# ALERT PAGE
# ==========================================================

if st.session_state.page == "Alerts":

    st.title("🔔 Price Alerts")

    st.subheader("Create Alert")

    col1, col2 = st.columns(2)

    with col1:

        symbol = st.selectbox(

            "Symbol",

            [

                "Gold",

                "DXY",

                "S&P500",

                "NASDAQ"

            ]

        )

    with col2:

        target_price = st.number_input(

            "Target Price",

            value=0.0,

            step=1.0

        )

    if st.button("Add Alert"):

        add_price_alert(

            symbol,

            target_price

        )

        st.success("Alert Added.")

    st.divider()

    if len(st.session_state.alerts) == 0:

        st.info("No Alerts.")

    else:

        df = pd.DataFrame(

            st.session_state.alerts

        )

        st.dataframe(

            df,

            use_container_width=True,

            hide_index=True

        )

# ==========================================================
# ALERT ENGINE
# ==========================================================

def check_alerts():

    market = {

        "Gold": gold_data,

        "DXY": dxy_data,

        "S&P500": sp500_data,

        "NASDAQ": nasdaq_data

    }

    for alert in st.session_state.alerts:

        if alert["triggered"]:

            continue

        symbol = alert["symbol"]

        if symbol not in market:

            continue

        data = market[symbol]

        if not data:

            continue

        current = data["price"]

        target = alert["price"]

        if current >= target:

            alert["triggered"] = True

            log(

                "INFO",

                f"{symbol} reached {target}"

            )

            st.toast(

                f"🔔 {symbol} reached {target}"

            )

check_alerts()

# ==========================================================
# SIDEBAR ALERT SUMMARY
# ==========================================================

st.sidebar.subheader("Alerts")

total_alerts = len(

    st.session_state.alerts

)

triggered = len(

    [

        x

        for x in st.session_state.alerts

        if x["triggered"]

    ]

)

st.sidebar.metric(

    "Total",

    total_alerts

)

st.sidebar.metric(

    "Triggered",

    triggered

)

st.sidebar.divider()

# ==========================================================
# END OF CHUNK 013
# ==========================================================

# ==========================================================
# WEOS
# ĐOẠN 014
# ==========================================================

# ==========================================================
# FAVORITE SYMBOLS
# ==========================================================

if "favorites" not in st.session_state:

    st.session_state.favorites = [

        "Gold",

        "DXY"

    ]

# ==========================================================
# FAVORITES PAGE
# ==========================================================

if st.session_state.page == "Favorites":

    st.title("⭐ Favorite Markets")

    markets = [

        "Gold",

        "DXY",

        "S&P500",

        "NASDAQ"

    ]

    selected = st.multiselect(

        "Favorite Symbols",

        markets,

        default=st.session_state.favorites

    )

    st.session_state.favorites = selected

    st.divider()

    market_map = {

        "Gold": gold_data,

        "DXY": dxy_data,

        "S&P500": sp500_data,

        "NASDAQ": nasdaq_data

    }

    for symbol in st.session_state.favorites:

        data = market_map.get(symbol)

        if not data:

            continue

        col1, col2, col3 = st.columns(3)

        with col1:

            st.write(symbol)

        with col2:

            st.metric(

                "Price",

                format_price(

                    data["price"]

                )

            )

        with col3:

            st.metric(

                "Change",

                format_percent(

                    data["change"]

                )

            )

        st.divider()

# ==========================================================
# WATCHLIST FILTER
# ==========================================================

def search_watchlist(keyword):

    keyword = keyword.lower()

    result = []

    for item in st.session_state.watchlist:

        if keyword in item.lower():

            result.append(item)

    return result

# ==========================================================
# WATCHLIST SEARCH PAGE
# ==========================================================

if st.session_state.page == "Watchlist":

    st.subheader("Search")

    keyword = st.text_input(

        "Search Symbol"

    )

    if keyword:

        result = search_watchlist(

            keyword

        )

        if len(result) == 0:

            st.warning(

                "No Result."

            )

        else:

            for item in result:

                st.success(item)

# ==========================================================
# QUICK ACTIONS
# ==========================================================

st.sidebar.subheader("Quick Actions")

if st.sidebar.button("Refresh Data"):

    st.cache_data.clear()

    st.toast("Data refreshed.")

if st.sidebar.button("Clear Logs"):

    st.session_state.logs.clear()

    st.toast("Logs cleared.")

if st.sidebar.button("Clear Alerts"):

    st.session_state.alerts.clear()

    st.toast("Alerts cleared.")

if st.sidebar.button("Clear Watchlist"):

    st.session_state.watchlist.clear()

    st.toast("Watchlist cleared.")

st.sidebar.divider()

# ==========================================================
# STATUS PANEL
# ==========================================================

status = "ONLINE"

if not gold_data:

    status = "LIMITED"

st.sidebar.subheader("WEOS Status")

st.sidebar.success(status)

st.sidebar.caption(

    f"Updated {current_time()}"

)

# ==========================================================
# END OF CHUNK 014
# ==========================================================
