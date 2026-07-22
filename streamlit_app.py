# ==========================================================
# WEOS
# ĐOẠN 001
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import sqlite3
import json
import random
import time
import os

from datetime import datetime
from datetime import timedelta

from bs4 import BeautifulSoup

# ==========================================================
# APPLICATION INFORMATION
# ==========================================================

APP_NAME = "WEOS"

APP_VERSION = "2.0.0"

DB_NAME = "weos.db"

REQUEST_TIMEOUT = 10

# ==========================================================
# STREAMLIT CONFIG
# ==========================================================

st.set_page_config(

    page_title=APP_NAME,

    page_icon="🌍",

    layout="wide",

    initial_sidebar_state="expanded"

)

# ==========================================================
# APPLICATION TITLE
# ==========================================================

st.title("🌍 WEOS")

st.caption(

    "World Economic Operating System"

)

# ==========================================================
# DATABASE
# ==========================================================

connection = sqlite3.connect(

    DB_NAME,

    check_same_thread=False

)

cursor = connection.cursor()

cursor.execute(

    """
    CREATE TABLE IF NOT EXISTS system_logs(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        time TEXT,

        level TEXT,

        message TEXT

    )
    """

)

connection.commit()

# ==========================================================
# SESSION STATE
# ==========================================================

if "startup_time" not in st.session_state:

    st.session_state.startup_time = datetime.now()

if "page" not in st.session_state:

    st.session_state.page = "Dashboard"

if "logs" not in st.session_state:

    st.session_state.logs = []

if "news" not in st.session_state:

    st.session_state.news = []

if "watchlist" not in st.session_state:

    st.session_state.watchlist = []

if "database_ready" not in st.session_state:

    st.session_state.database_ready = True

# ==========================================================
# KẾT THÚC ĐOẠN 001
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 002
# ==========================================================

# ==========================================================
# LOGGING SYSTEM
# ==========================================================

def current_time():

    return datetime.now().strftime(

        "%Y-%m-%d %H:%M:%S"

    )

def log(

    level,

    message

):

    record = {

        "time": current_time(),

        "level": level,

        "message": message

    }

    st.session_state.logs.append(

        record

    )

    cursor.execute(

        """
        INSERT INTO system_logs
        (
            time,
            level,
            message
        )
        VALUES
        (
            ?,
            ?,
            ?
        )
        """,

        (

            record["time"],

            record["level"],

            record["message"]

        )

    )

    connection.commit()

# ==========================================================
# FORMAT FUNCTIONS
# ==========================================================

def format_price(

    value

):

    try:

        return f"{value:,.2f}"

    except Exception:

        return "-"

def format_percent(

    value

):

    try:

        return f"{value:.2f}%"

    except Exception:

        return "-"

def metric_value(

    data

):

    if data is None:

        return "-"

    return format_price(

        data["price"]

    )

# ==========================================================
# STARTUP LOG
# ==========================================================

if len(

    st.session_state.logs

) == 0:

    log(

        "INFO",

        "WEOS started successfully."

    )

# ==========================================================
# KẾT THÚC ĐOẠN 002
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 003
# ==========================================================

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.title(

    "🌍 WEOS"

)

pages = [

    "Dashboard",

    "Gold",

    "Forex",

    "Macro",

    "News",

    "Watchlist",

    "Settings"

]

st.session_state.page = st.sidebar.radio(

    "Navigation",

    pages,

    index=pages.index(

        st.session_state.page

    )

)

st.sidebar.divider()

# ==========================================================
# MARKET SYMBOLS
# ==========================================================

MARKET_SYMBOLS = {

    "Gold": "GC=F",

    "DXY": "DX-Y.NYB",

    "S&P500": "^GSPC",

    "NASDAQ": "^IXIC",

    "USDJPY": "JPY=X",

    "EURUSD": "EURUSD=X",

    "GBPUSD": "GBPUSD=X"

}

# ==========================================================
# MARKET DATA FUNCTION
# ==========================================================

@st.cache_data(

    ttl=60

)

def load_market_data(

    symbol

):

    try:

        ticker = yf.Ticker(

            symbol

        )

        history = ticker.history(

            period="2d"

        )

        if history.empty:

            return None

        close = history["Close"]

        price = float(

            close.iloc[-1]

        )

        previous = float(

            close.iloc[-2]

        )

        change = (

            (price - previous)

            / previous

        ) * 100

        return {

            "price": price,

            "change": change

        }

    except Exception:

        return None

# ==========================================================
# KẾT THÚC ĐOẠN 003
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 004
# ==========================================================

# ==========================================================
# LOAD MARKET DATA
# ==========================================================

gold_data = load_market_data(

    MARKET_SYMBOLS["Gold"]

)

dxy_data = load_market_data(

    MARKET_SYMBOLS["DXY"]

)

sp500_data = load_market_data(

    MARKET_SYMBOLS["S&P500"]

)

nasdaq_data = load_market_data(

    MARKET_SYMBOLS["NASDAQ"]

)

eurusd_data = load_market_data(

    MARKET_SYMBOLS["EURUSD"]

)

gbpusd_data = load_market_data(

    MARKET_SYMBOLS["GBPUSD"]

)

usdjpy_data = load_market_data(

    MARKET_SYMBOLS["USDJPY"]

)

# ==========================================================
# DASHBOARD PAGE
# ==========================================================

if st.session_state.page == "Dashboard":

    st.header(

        "📊 Dashboard"

    )

    col1, col2, col3, col4 = st.columns(

        4

    )

    with col1:

        if gold_data:

            st.metric(

                "Gold",

                format_price(

                    gold_data["price"]

                ),

                format_percent(

                    gold_data["change"]

                )

            )

    with col2:

        if dxy_data:

            st.metric(

                "DXY",

                format_price(

                    dxy_data["price"]

                ),

                format_percent(

                    dxy_data["change"]

                )

            )

    with col3:

        if sp500_data:

            st.metric(

                "S&P500",

                format_price(

                    sp500_data["price"]

                ),

                format_percent(

                    sp500_data["change"]

                )

            )

    with col4:

        if nasdaq_data:

            st.metric(

                "NASDAQ",

                format_price(

                    nasdaq_data["price"]

                ),

                format_percent(

                    nasdaq_data["change"]

                )

            )

# ==========================================================
# KẾT THÚC ĐOẠN 004
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 005
# ==========================================================

# ==========================================================
# GOLD PAGE
# ==========================================================

if st.session_state.page == "Gold":

    st.header(

        "🥇 Gold"

    )

    if gold_data is None:

        st.error(

            "Không thể tải dữ liệu Gold."

        )

    else:

        col1, col2 = st.columns(

            2

        )

        with col1:

            st.metric(

                "Current Price",

                format_price(

                    gold_data["price"]

                )

            )

        with col2:

            st.metric(

                "Daily Change",

                format_percent(

                    gold_data["change"]

                )

            )

        st.divider()

        if gold_data["change"] > 0:

            st.success(

                "Xu hướng hôm nay: Tăng"

            )

        elif gold_data["change"] < 0:

            st.error(

                "Xu hướng hôm nay: Giảm"

            )

        else:

            st.warning(

                "Xu hướng hôm nay: Đi ngang"

            )

# ==========================================================
# FOREX PAGE
# ==========================================================

if st.session_state.page == "Forex":

    st.header(

        "💱 Forex"

    )

    forex_table = []

    forex_market = {

        "EUR/USD": eurusd_data,

        "GBP/USD": gbpusd_data,

        "USD/JPY": usdjpy_data,

        "DXY": dxy_data

    }

    for symbol, data in forex_market.items():

        if data is None:

            continue

        forex_table.append(

            {

                "Symbol": symbol,

                "Price": round(

                    data["price"],

                    5

                ),

                "Change %": round(

                    data["change"],

                    2

                )

            }

        )

# ==========================================================
# KẾT THÚC ĐOẠN 005
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 006
# ==========================================================

    if len(forex_table) == 0:

        st.warning(

            "Không có dữ liệu Forex."

        )

    else:

        forex_df = pd.DataFrame(

            forex_table

        )

        st.dataframe(

            forex_df,

            use_container_width=True,

            hide_index=True

        )

# ==========================================================
# MACRO PAGE
# ==========================================================

if st.session_state.page == "Macro":

    st.header(

        "🌍 Global Macro"

    )

    macro_data = [

        {

            "Indicator": "Gold",

            "Value": format_price(

                gold_data["price"]

            ) if gold_data else "-",

            "Change": format_percent(

                gold_data["change"]

            ) if gold_data else "-"

        },

        {

            "Indicator": "DXY",

            "Value": format_price(

                dxy_data["price"]

            ) if dxy_data else "-",

            "Change": format_percent(

                dxy_data["change"]

            ) if dxy_data else "-"

        },

        {

            "Indicator": "S&P500",

            "Value": format_price(

                sp500_data["price"]

            ) if sp500_data else "-",

            "Change": format_percent(

                sp500_data["change"]

            ) if sp500_data else "-"

        },

        {

            "Indicator": "NASDAQ",

            "Value": format_price(

                nasdaq_data["price"]

            ) if nasdaq_data else "-",

            "Change": format_percent(

                nasdaq_data["change"]

            ) if nasdaq_data else "-"

        }

    ]

    st.dataframe(

        pd.DataFrame(

            macro_data

        ),

        use_container_width=True,

        hide_index=True

    )

# ==========================================================
# KẾT THÚC ĐOẠN 006
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 007
# ==========================================================

# ==========================================================
# WATCHLIST PAGE
# ==========================================================

if st.session_state.page == "Watchlist":

    st.header(

        "⭐ Watchlist"

    )

    symbol_input = st.text_input(

        "Nhập mã sản phẩm hoặc thị trường",

        placeholder="Ví dụ: XAUUSD"

    )

    col1, col2 = st.columns(

        2

    )

    with col1:

        if st.button(

            "➕ Thêm"

        ):

            symbol = symbol_input.strip().upper()

            if symbol != "":

                if symbol not in st.session_state.watchlist:

                    st.session_state.watchlist.append(

                        symbol

                    )

                    log(

                        "INFO",

                        f"Add watchlist: {symbol}"

                    )

                    st.success(

                        f"Đã thêm {symbol}"

                    )

                else:

                    st.warning(

                        "Đã tồn tại."

                    )

            else:

                st.error(

                    "Không được để trống."

                )

    with col2:

        if st.button(

            "🗑 Xóa tất cả"

        ):

            st.session_state.watchlist.clear()

            log(

                "INFO",

                "Clear watchlist"

            )

            st.success(

                "Đã xóa toàn bộ Watchlist."

            )

# ==========================================================
# WATCHLIST TABLE
# ==========================================================

    if len(

        st.session_state.watchlist

    ) == 0:

        st.info(

            "Watchlist đang trống."

        )

    else:

        watchlist_df = pd.DataFrame(

            {

                "Symbol":

                st.session_state.watchlist

            }

        )

        st.dataframe(

            watchlist_df,

            use_container_width=True,

            hide_index=True

        )

# ==========================================================
# KẾT THÚC ĐOẠN 007
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 008
# ==========================================================

# ==========================================================
# NEWS FUNCTIONS
# ==========================================================

@st.cache_data(

    ttl=300

)

def load_gold_news():

    url = (

        "https://feeds.finance.yahoo.com/rss/2.0/headline"

        "?s=GC=F"

        "&region=US"

        "&lang=en-US"

    )

    try:

        response = requests.get(

            url,

            timeout=REQUEST_TIMEOUT

        )

        soup = BeautifulSoup(

            response.content,

            "xml"

        )

        items = soup.find_all(

            "item"

        )

        news = []

        for item in items[:20]:

            news.append(

                {

                    "title": item.title.text,

                    "link": item.link.text,

                    "date": item.pubDate.text

                }

            )

        return news

    except Exception:

        return []

# ==========================================================
# NEWS PAGE
# ==========================================================

if st.session_state.page == "News":

    st.header(

        "📰 Gold News"

    )

    news_data = load_gold_news()

    if len(

        news_data

    ) == 0:

        st.warning(

            "Không tải được tin tức."

        )

    else:

        for article in news_data:

            with st.container():

                st.subheader(

                    article["title"]

                )

                st.caption(

                    article["date"]

                )

                st.write(

                    article["link"]

                )

                st.divider()

# ==========================================================
# KẾT THÚC ĐOẠN 008
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 009
# ==========================================================

# ==========================================================
# SETTINGS PAGE
# ==========================================================

if st.session_state.page == "Settings":

    st.header(

        "⚙️ Settings"

    )

    refresh_time = st.slider(

        "Refresh Interval (seconds)",

        min_value=10,

        max_value=300,

        value=60,

        step=10

    )

    show_logs = st.checkbox(

        "Hiển thị System Logs",

        value=True

    )

    show_database = st.checkbox(

        "Hiển thị Database Status",

        value=True

    )

    st.divider()

    st.write(

        f"Application: {APP_NAME}"

    )

    st.write(

        f"Version: {APP_VERSION}"

    )

    st.write(

        f"Refresh: {refresh_time} seconds"

    )

    if show_database:

        st.success(

            "SQLite Database Connected"

        )

# ==========================================================
# LOG VIEWER
# ==========================================================

    if show_logs:

        st.subheader(

            "System Logs"

        )

        if len(

            st.session_state.logs

        ) == 0:

            st.info(

                "No logs."

            )

        else:

            log_df = pd.DataFrame(

                st.session_state.logs

            )

            st.dataframe(

                log_df,

                use_container_width=True,

                hide_index=True

            )

# ==========================================================
# FOOTER
# ==========================================================

st.sidebar.divider()

st.sidebar.caption(

    f"{APP_NAME} {APP_VERSION}"

)

# ==========================================================
# KẾT THÚC ĐOẠN 009
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 010
# ==========================================================

# ==========================================================
# SYSTEM INFORMATION
# ==========================================================

def get_system_information():

    return {

        "Application": APP_NAME,

        "Version": APP_VERSION,

        "Database": DB_NAME,

        "Startup Time": str(

            st.session_state.startup_time

        ),

        "Current Time": current_time(),

        "Watchlist Items": len(

            st.session_state.watchlist

        ),

        "News Cached": len(

            st.session_state.news

        ),

        "Log Records": len(

            st.session_state.logs

        )

    }

# ==========================================================
# SIDEBAR STATUS
# ==========================================================

st.sidebar.subheader(

    "System Status"

)

system_info = get_system_information()

st.sidebar.write(

    f"🟢 Version: {system_info['Version']}"

)

st.sidebar.write(

    f"📦 Logs: {system_info['Log Records']}"

)

st.sidebar.write(

    f"⭐ Watchlist: {system_info['Watchlist Items']}"

)

st.sidebar.write(

    f"📰 News Cache: {system_info['News Cached']}"

)

# ==========================================================
# SETTINGS - SYSTEM INFO
# ==========================================================

if st.session_state.page == "Settings":

    st.divider()

    st.subheader(

        "System Information"

    )

    info_df = pd.DataFrame(

        [

            {

                "Property": key,

                "Value": value

            }

            for key, value in system_info.items()

        ]

    )

    st.dataframe(

        info_df,

        use_container_width=True,

        hide_index=True

    )

# ==========================================================
# KẾT THÚC ĐOẠN 010
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 011
# ==========================================================

# ==========================================================
# MARKET CHART FUNCTIONS
# ==========================================================

@st.cache_data(

    ttl=120

)

def load_price_history(

    symbol,

    period="1mo",

    interval="1d"

):

    try:

        ticker = yf.Ticker(

            symbol

        )

        history = ticker.history(

            period=period,

            interval=interval

        )

        return history

    except Exception:

        return pd.DataFrame()

# ==========================================================
# GOLD CHART
# ==========================================================

if st.session_state.page == "Gold":

    history = load_price_history(

        MARKET_SYMBOLS["Gold"]

    )

    if not history.empty:

        st.subheader(

            "Gold Price Chart"

        )

        chart_data = history[

            ["Close"]

        ].rename(

            columns={

                "Close": "Gold"

            }

        )

        st.line_chart(

            chart_data,

            use_container_width=True

        )

# ==========================================================
# FOREX CHART
# ==========================================================

if st.session_state.page == "Forex":

    eurusd_history = load_price_history(

        MARKET_SYMBOLS["EURUSD"]

    )

    if not eurusd_history.empty:

        st.subheader(

            "EUR/USD Chart"

        )

        st.line_chart(

            eurusd_history[

                ["Close"]

            ],

            use_container_width=True

        )

# ==========================================================
# KẾT THÚC ĐOẠN 011
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 012
# ==========================================================

# ==========================================================
# MULTI MARKET CHARTS
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "Market Overview"

    )

    chart_option = st.selectbox(

        "Select Market",

        [

            "Gold",

            "DXY",

            "S&P500",

            "NASDAQ"

        ]

    )

    chart_symbol = MARKET_SYMBOLS[

        chart_option

    ]

    dashboard_history = load_price_history(

        chart_symbol

    )

    if dashboard_history.empty:

        st.warning(

            "Không có dữ liệu biểu đồ."

        )

    else:

        st.line_chart(

            dashboard_history[

                ["Close"]

            ],

            use_container_width=True

        )

# ==========================================================
# MARKET SNAPSHOT
# ==========================================================

market_snapshot = []

for market_name, market_symbol in MARKET_SYMBOLS.items():

    market_data = load_market_data(

        market_symbol

    )

    if market_data is None:

        continue

    market_snapshot.append(

        {

            "Market": market_name,

            "Price": round(

                market_data["price"],

                4

            ),

            "Change %": round(

                market_data["change"],

                2

            )

        }

    )

# ==========================================================
# DASHBOARD TABLE
# ==========================================================

if st.session_state.page == "Dashboard":

    st.subheader(

        "Live Market Snapshot"

    )

    snapshot_df = pd.DataFrame(

        market_snapshot

    )

    st.dataframe(

        snapshot_df,

        use_container_width=True,

        hide_index=True

    )

# ==========================================================
# KẾT THÚC ĐOẠN 012
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 013
# ==========================================================

# ==========================================================
# ECONOMIC CALENDAR
# ==========================================================

@st.cache_data(

    ttl=600

)

def load_economic_calendar():

    events = [

        {

            "Time": "12:30 UTC",

            "Event": "US CPI",

            "Impact": "High"

        },

        {

            "Time": "12:30 UTC",

            "Event": "US PPI",

            "Impact": "High"

        },

        {

            "Time": "18:00 UTC",

            "Event": "FOMC Meeting",

            "Impact": "High"

        },

        {

            "Time": "12:30 UTC",

            "Event": "Non Farm Payroll",

            "Impact": "High"

        },

        {

            "Time": "14:00 UTC",

            "Event": "Consumer Confidence",

            "Impact": "Medium"

        },

        {

            "Time": "14:00 UTC",

            "Event": "ISM Manufacturing PMI",

            "Impact": "Medium"

        },

        {

            "Time": "14:00 UTC",

            "Event": "Retail Sales",

            "Impact": "High"

        }

    ]

    return pd.DataFrame(

        events

    )

# ==========================================================
# MACRO PAGE
# ==========================================================

if st.session_state.page == "Macro":

    st.divider()

    st.subheader(

        "Economic Calendar"

    )

    calendar_df = load_economic_calendar()

    st.dataframe(

        calendar_df,

        use_container_width=True,

        hide_index=True

    )

# ==========================================================
# KẾT THÚC ĐOẠN 013
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 014
# ==========================================================

# ==========================================================
# MARKET SENTIMENT
# ==========================================================

def calculate_market_sentiment():

    score = 0

    details = []

    if gold_data is not None:

        if gold_data["change"] > 0:

            score += 1

            details.append(

                "Gold tăng"

            )

        else:

            score -= 1

            details.append(

                "Gold giảm"

            )

    if dxy_data is not None:

        if dxy_data["change"] > 0:

            score -= 1

            details.append(

                "DXY tăng"

            )

        else:

            score += 1

            details.append(

                "DXY giảm"

            )

    if sp500_data is not None:

        if sp500_data["change"] > 0:

            score += 1

            details.append(

                "S&P500 tăng"

            )

        else:

            score -= 1

            details.append(

                "S&P500 giảm"

            )

    if score >= 2:

        sentiment = "Bullish"

    elif score <= -2:

        sentiment = "Bearish"

    else:

        sentiment = "Neutral"

    return sentiment, details

# ==========================================================
# DASHBOARD SENTIMENT
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "Market Sentiment"

    )

    sentiment, sentiment_detail = calculate_market_sentiment()

    st.metric(

        "Current Sentiment",

        sentiment

    )

    for item in sentiment_detail:

        st.write(

            "•",

            item

        )

# ==========================================================
# KẾT THÚC ĐOẠN 014
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 015
# ==========================================================

# ==========================================================
# FEAR & GREED INDEX
# ==========================================================

def calculate_fear_greed():

    score = 50

    if gold_data is not None:

        if gold_data["change"] > 1:

            score += 10

        elif gold_data["change"] < -1:

            score -= 10

    if dxy_data is not None:

        if dxy_data["change"] > 0.5:

            score -= 10

        elif dxy_data["change"] < -0.5:

            score += 10

    if sp500_data is not None:

        if sp500_data["change"] > 1:

            score += 15

        elif sp500_data["change"] < -1:

            score -= 15

    score = max(

        0,

        min(

            score,

            100

        )

    )

    return score

# ==========================================================
# DASHBOARD FEAR & GREED
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "Fear & Greed"

    )

    fg_score = calculate_fear_greed()

    st.progress(

        fg_score / 100

    )

    st.metric(

        "Index",

        fg_score

    )

    if fg_score >= 75:

        st.success(

            "Extreme Greed"

        )

    elif fg_score >= 55:

        st.info(

            "Greed"

        )

    elif fg_score >= 45:

        st.warning(

            "Neutral"

        )

    elif fg_score >= 25:

        st.warning(

            "Fear"

        )

    else:

        st.error(

            "Extreme Fear"

        )

# ==========================================================
# KẾT THÚC ĐOẠN 015
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 016
# ==========================================================

# ==========================================================
# GOLD SIGNAL ENGINE
# ==========================================================

def generate_gold_signal():

    score = 0

    reasons = []

    if gold_data is not None:

        if gold_data["change"] > 0:

            score += 1

            reasons.append(

                "Gold đang tăng."

            )

        else:

            score -= 1

            reasons.append(

                "Gold đang giảm."

            )

    if dxy_data is not None:

        if dxy_data["change"] < 0:

            score += 1

            reasons.append(

                "DXY suy yếu."

            )

        else:

            score -= 1

            reasons.append(

                "DXY mạnh lên."

            )

    if sp500_data is not None:

        if sp500_data["change"] < 0:

            score += 1

            reasons.append(

                "Chứng khoán Mỹ suy yếu."

            )

        else:

            reasons.append(

                "Chứng khoán Mỹ tích cực."

            )

    if score >= 2:

        signal = "BUY"

    elif score <= -2:

        signal = "SELL"

    else:

        signal = "WAIT"

    return signal, reasons

# ==========================================================
# GOLD SIGNAL PAGE
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "Trading Signal"

    )

    signal, signal_reason = generate_gold_signal()

    if signal == "BUY":

        st.success(

            "BUY"

        )

    elif signal == "SELL":

        st.error(

            "SELL"

        )

    else:

        st.warning(

            "WAIT"

        )

    for reason in signal_reason:

        st.write(

            "•",

            reason

        )

# ==========================================================
# KẾT THÚC ĐOẠN 016
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 017
# ==========================================================

# ==========================================================
# GOLD TREND ANALYZER
# ==========================================================

def analyze_gold_trend():

    history = load_price_history(

        MARKET_SYMBOLS["Gold"],

        period="3mo"

    )

    if history.empty:

        return None

    history["MA20"] = history[

        "Close"

    ].rolling(

        20

    ).mean()

    history["MA50"] = history[

        "Close"

    ].rolling(

        50

    ).mean()

    latest_close = float(

        history["Close"].iloc[-1]

    )

    latest_ma20 = float(

        history["MA20"].iloc[-1]

    )

    latest_ma50 = float(

        history["MA50"].iloc[-1]

    )

    if latest_close > latest_ma20 > latest_ma50:

        trend = "Strong Uptrend"

    elif latest_close > latest_ma20:

        trend = "Uptrend"

    elif latest_close < latest_ma20 < latest_ma50:

        trend = "Strong Downtrend"

    elif latest_close < latest_ma20:

        trend = "Downtrend"

    else:

        trend = "Sideway"

    return {

        "trend": trend,

        "close": latest_close,

        "ma20": latest_ma20,

        "ma50": latest_ma50

    }

# ==========================================================
# GOLD TREND PAGE
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "Trend Analysis"

    )

    trend_data = analyze_gold_trend()

    if trend_data is None:

        st.warning(

            "Không thể phân tích xu hướng."

        )

    else:

        st.metric(

            "Trend",

            trend_data["trend"]

        )

        col1, col2, col3 = st.columns(

            3

        )

        with col1:

            st.metric(

                "Close",

                format_price(

                    trend_data["close"]

                )

            )

        with col2:

            st.metric(

                "MA20",

                format_price(

                    trend_data["ma20"]

                )

            )

        with col3:

            st.metric(

                "MA50",

                format_price(

                    trend_data["ma50"]

                )

            )

# ==========================================================
# KẾT THÚC ĐOẠN 017
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 018
# ==========================================================

# ==========================================================
# SUPPORT & RESISTANCE
# ==========================================================

def calculate_support_resistance():

    history = load_price_history(

        MARKET_SYMBOLS["Gold"],

        period="3mo"

    )

    if history.empty:

        return None

    resistance = float(

        history["High"].max()

    )

    support = float(

        history["Low"].min()

    )

    latest = float(

        history["Close"].iloc[-1]

    )

    distance_support = (

        latest - support

    )

    distance_resistance = (

        resistance - latest

    )

    return {

        "support": support,

        "resistance": resistance,

        "price": latest,

        "distance_support": distance_support,

        "distance_resistance": distance_resistance

    }

# ==========================================================
# GOLD SUPPORT / RESISTANCE
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "Support & Resistance"

    )

    sr = calculate_support_resistance()

    if sr is None:

        st.warning(

            "Không có dữ liệu."

        )

    else:

        col1, col2, col3 = st.columns(

            3

        )

        with col1:

            st.metric(

                "Support",

                format_price(

                    sr["support"]

                )

            )

        with col2:

            st.metric(

                "Current",

                format_price(

                    sr["price"]

                )

            )

        with col3:

            st.metric(

                "Resistance",

                format_price(

                    sr["resistance"]

                )

            )

        st.write(

            f"Distance to Support: {format_price(sr['distance_support'])}"

        )

        st.write(

            f"Distance to Resistance: {format_price(sr['distance_resistance'])}"

        )

# ==========================================================
# KẾT THÚC ĐOẠN 018
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 019
# ==========================================================

# ==========================================================
# VOLATILITY ANALYZER
# ==========================================================

def calculate_volatility():

    history = load_price_history(

        MARKET_SYMBOLS["Gold"],

        period="1mo"

    )

    if history.empty:

        return None

    history["Range"] = (

        history["High"]

        - history["Low"]

    )

    average_range = float(

        history["Range"].mean()

    )

    max_range = float(

        history["Range"].max()

    )

    min_range = float(

        history["Range"].min()

    )

    latest_range = float(

        history["Range"].iloc[-1]

    )

    return {

        "average": average_range,

        "maximum": max_range,

        "minimum": min_range,

        "latest": latest_range

    }

# ==========================================================
# GOLD VOLATILITY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "Market Volatility"

    )

    volatility = calculate_volatility()

    if volatility is None:

        st.warning(

            "Không thể tính biến động."

        )

    else:

        col1, col2 = st.columns(

            2

        )

        with col1:

            st.metric(

                "Today's Range",

                format_price(

                    volatility["latest"]

                )

            )

            st.metric(

                "Average Range",

                format_price(

                    volatility["average"]

                )

            )

        with col2:

            st.metric(

                "Maximum Range",

                format_price(

                    volatility["maximum"]

                )

            )

            st.metric(

                "Minimum Range",

                format_price(

                    volatility["minimum"]

                )

            )

# ==========================================================
# KẾT THÚC ĐOẠN 019
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 020
# ==========================================================

# ==========================================================
# VOLUME ANALYZER
# ==========================================================

def analyze_volume():

    history = load_price_history(

        MARKET_SYMBOLS["Gold"],

        period="3mo"

    )

    if history.empty:

        return None

    if "Volume" not in history.columns:

        return None

    average_volume = float(

        history["Volume"].mean()

    )

    latest_volume = float(

        history["Volume"].iloc[-1]

    )

    ratio = latest_volume / average_volume

    if ratio >= 1.5:

        status = "Very High"

    elif ratio >= 1.1:

        status = "High"

    elif ratio >= 0.8:

        status = "Normal"

    else:

        status = "Low"

    return {

        "latest": latest_volume,

        "average": average_volume,

        "ratio": ratio,

        "status": status

    }

# ==========================================================
# GOLD VOLUME
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "Volume Analysis"

    )

    volume = analyze_volume()

    if volume is None:

        st.info(

            "Nguồn dữ liệu hiện tại không hỗ trợ Volume."

        )

    else:

        col1, col2, col3 = st.columns(

            3

        )

        with col1:

            st.metric(

                "Latest Volume",

                format_price(

                    volume["latest"]

                )

            )

        with col2:

            st.metric(

                "Average Volume",

                format_price(

                    volume["average"]

                )

            )

        with col3:

            st.metric(

                "Status",

                volume["status"]

            )

        st.progress(

            min(

                volume["ratio"],

                2.0

            ) / 2.0

        )

# ==========================================================
# KẾT THÚC ĐOẠN 020
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 021
# ==========================================================

# ==========================================================
# RSI CALCULATOR
# ==========================================================

def calculate_rsi(

    period=14

):

    history = load_price_history(

        MARKET_SYMBOLS["Gold"],

        period="6mo"

    )

    if history.empty:

        return None

    delta = history[

        "Close"

    ].diff()

    gain = delta.where(

        delta > 0,

        0

    )

    loss = -delta.where(

        delta < 0,

        0

    )

    average_gain = gain.rolling(

        period

    ).mean()

    average_loss = loss.rolling(

        period

    ).mean()

    rs = average_gain / average_loss

    rsi = 100 - (

        100 / (

            1 + rs

        )

    )

    latest = float(

        rsi.iloc[-1]

    )

    if latest >= 70:

        signal = "Overbought"

    elif latest <= 30:

        signal = "Oversold"

    else:

        signal = "Neutral"

    return {

        "rsi": latest,

        "signal": signal

    }

# ==========================================================
# GOLD RSI
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "RSI Indicator"

    )

    rsi_data = calculate_rsi()

    if rsi_data is None:

        st.warning(

            "Không thể tính RSI."

        )

    else:

        st.metric(

            "RSI (14)",

            round(

                rsi_data["rsi"],

                2

            )

        )

        st.write(

            "Signal:",

            rsi_data["signal"]

        )

# ==========================================================
# KẾT THÚC ĐOẠN 021
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 022
# ==========================================================

# ==========================================================
# MACD CALCULATOR
# ==========================================================

def calculate_macd():

    history = load_price_history(

        MARKET_SYMBOLS["Gold"],

        period="6mo"

    )

    if history.empty:

        return None

    close = history[

        "Close"

    ]

    ema12 = close.ewm(

        span=12,

        adjust=False

    ).mean()

    ema26 = close.ewm(

        span=26,

        adjust=False

    ).mean()

    macd = ema12 - ema26

    signal = macd.ewm(

        span=9,

        adjust=False

    ).mean()

    histogram = macd - signal

    return {

        "macd": float(

            macd.iloc[-1]

        ),

        "signal": float(

            signal.iloc[-1]

        ),

        "histogram": float(

            histogram.iloc[-1]

        )

    }

# ==========================================================
# GOLD MACD
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "MACD Indicator"

    )

    macd_data = calculate_macd()

    if macd_data is None:

        st.warning(

            "Không thể tính MACD."

        )

    else:

        col1, col2, col3 = st.columns(

            3

        )

        with col1:

            st.metric(

                "MACD",

                round(

                    macd_data["macd"],

                    4

                )

            )

        with col2:

            st.metric(

                "Signal",

                round(

                    macd_data["signal"],

                    4

                )

            )

        with col3:

            st.metric(

                "Histogram",

                round(

                    macd_data["histogram"],

                    4

                )

            )

# ==========================================================
# KẾT THÚC ĐOẠN 022
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 023
# ==========================================================

# ==========================================================
# BOLLINGER BANDS
# ==========================================================

def calculate_bollinger_bands(

    period=20,

    std_multiplier=2

):

    history = load_price_history(

        MARKET_SYMBOLS["Gold"],

        period="6mo"

    )

    if history.empty:

        return None

    close = history[

        "Close"

    ]

    middle = close.rolling(

        period

    ).mean()

    deviation = close.rolling(

        period

    ).std()

    upper = middle + (

        deviation

        * std_multiplier

    )

    lower = middle - (

        deviation

        * std_multiplier

    )

    latest_price = float(

        close.iloc[-1]

    )

    latest_upper = float(

        upper.iloc[-1]

    )

    latest_middle = float(

        middle.iloc[-1]

    )

    latest_lower = float(

        lower.iloc[-1]

    )

    if latest_price > latest_upper:

        signal = "Breakout Above"

    elif latest_price < latest_lower:

        signal = "Breakout Below"

    else:

        signal = "Inside Bands"

    return {

        "upper": latest_upper,

        "middle": latest_middle,

        "lower": latest_lower,

        "price": latest_price,

        "signal": signal

    }

# ==========================================================
# GOLD BOLLINGER BANDS
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "Bollinger Bands"

    )

    bb = calculate_bollinger_bands()

    if bb is None:

        st.warning(

            "Không thể tính Bollinger Bands."

        )

    else:

        col1, col2, col3 = st.columns(

            3

        )

        with col1:

            st.metric(

                "Upper",

                format_price(

                    bb["upper"]

                )

            )

        with col2:

            st.metric(

                "Middle",

                format_price(

                    bb["middle"]

                )

            )

        with col3:

            st.metric(

                "Lower",

                format_price(

                    bb["lower"]

                )

            )

        st.write(

            "Signal:",

            bb["signal"]

        )

# ==========================================================
# KẾT THÚC ĐOẠN 023
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 024
# ==========================================================

# ==========================================================
# ATR CALCULATOR
# ==========================================================

def calculate_atr(

    period=14

):

    history = load_price_history(

        MARKET_SYMBOLS["Gold"],

        period="6mo"

    )

    if history.empty:

        return None

    high = history[

        "High"

    ]

    low = history[

        "Low"

    ]

    close = history[

        "Close"

    ]

    previous_close = close.shift(

        1

    )

    tr = pd.concat(

        [

            high - low,

            (high - previous_close).abs(),

            (low - previous_close).abs()

        ],

        axis=1

    ).max(

        axis=1

    )

    atr = tr.rolling(

        period

    ).mean()

    latest = float(

        atr.iloc[-1]

    )

    return latest

# ==========================================================
# GOLD ATR
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "Average True Range"

    )

    atr_value = calculate_atr()

    if atr_value is None:

        st.warning(

            "Không thể tính ATR."

        )

    else:

        st.metric(

            "ATR (14)",

            format_price(

                atr_value

            )

        )

        if atr_value >= 40:

            st.error(

                "Biến động rất mạnh."

            )

        elif atr_value >= 25:

            st.warning(

                "Biến động cao."

            )

        elif atr_value >= 10:

            st.info(

                "Biến động trung bình."

            )

        else:

            st.success(

                "Biến động thấp."

            )

# ==========================================================
# KẾT THÚC ĐOẠN 024
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 025
# ==========================================================

# ==========================================================
# STOCHASTIC OSCILLATOR
# ==========================================================

def calculate_stochastic(

    period=14,

    smooth=3

):

    history = load_price_history(

        MARKET_SYMBOLS["Gold"],

        period="6mo"

    )

    if history.empty:

        return None

    lowest_low = history[

        "Low"

    ].rolling(

        period

    ).min()

    highest_high = history[

        "High"

    ].rolling(

        period

    ).max()

    k = (

        (

            history["Close"]

            - lowest_low

        )

        /

        (

            highest_high

            - lowest_low

        )

    ) * 100

    d = k.rolling(

        smooth

    ).mean()

    latest_k = float(

        k.iloc[-1]

    )

    latest_d = float(

        d.iloc[-1]

    )

    if latest_k >= 80:

        signal = "Overbought"

    elif latest_k <= 20:

        signal = "Oversold"

    else:

        signal = "Neutral"

    return {

        "k": latest_k,

        "d": latest_d,

        "signal": signal

    }

# ==========================================================
# GOLD STOCHASTIC
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "Stochastic Oscillator"

    )

    stochastic = calculate_stochastic()

    if stochastic is None:

        st.warning(

            "Không thể tính Stochastic."

        )

    else:

        col1, col2 = st.columns(

            2

        )

        with col1:

            st.metric(

                "%K",

                round(

                    stochastic["k"],

                    2

                )

            )

        with col2:

            st.metric(

                "%D",

                round(

                    stochastic["d"],

                    2

                )

            )

        st.write(

            "Signal:",

            stochastic["signal"]

        )

# ==========================================================
# KẾT THÚC ĐOẠN 025
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 026
# ==========================================================

# ==========================================================
# EMA ANALYZER
# ==========================================================

def calculate_ema_signal():

    history = load_price_history(

        MARKET_SYMBOLS["Gold"],

        period="6mo"

    )

    if history.empty:

        return None

    close = history[

        "Close"

    ]

    ema20 = close.ewm(

        span=20,

        adjust=False

    ).mean()

    ema50 = close.ewm(

        span=50,

        adjust=False

    ).mean()

    ema200 = close.ewm(

        span=200,

        adjust=False

    ).mean()

    latest_price = float(

        close.iloc[-1]

    )

    latest_ema20 = float(

        ema20.iloc[-1]

    )

    latest_ema50 = float(

        ema50.iloc[-1]

    )

    latest_ema200 = float(

        ema200.iloc[-1]

    )

    if latest_price > latest_ema20 > latest_ema50 > latest_ema200:

        signal = "Strong Bullish"

    elif latest_price < latest_ema20 < latest_ema50 < latest_ema200:

        signal = "Strong Bearish"

    else:

        signal = "Neutral"

    return {

        "ema20": latest_ema20,

        "ema50": latest_ema50,

        "ema200": latest_ema200,

        "signal": signal

    }

# ==========================================================
# GOLD EMA
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "EMA Analysis"

    )

    ema_data = calculate_ema_signal()

    if ema_data is None:

        st.warning(

            "Không thể tính EMA."

        )

    else:

        col1, col2, col3 = st.columns(

            3

        )

        with col1:

            st.metric(

                "EMA20",

                format_price(

                    ema_data["ema20"]

                )

            )

        with col2:

            st.metric(

                "EMA50",

                format_price(

                    ema_data["ema50"]

                )

            )

        with col3:

            st.metric(

                "EMA200",

                format_price(

                    ema_data["ema200"]

                )

            )

        st.write(

            "Signal:",

            ema_data["signal"]

        )

# ==========================================================
# KẾT THÚC ĐOẠN 026
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 027
# ==========================================================

# ==========================================================
# TREND STRENGTH ANALYZER
# ==========================================================

def calculate_trend_strength():

    history = load_price_history(

        MARKET_SYMBOLS["Gold"],

        period="6mo"

    )

    if history.empty:

        return None

    close = history["Close"]

    change = (

        close.iloc[-1]

        -

        close.iloc[-20]

    )

    percentage = (

        change

        /

        close.iloc[-20]

    ) * 100

    if percentage >= 5:

        strength = "Very Strong Uptrend"

    elif percentage >= 2:

        strength = "Strong Uptrend"

    elif percentage > 0:

        strength = "Weak Uptrend"

    elif percentage <= -5:

        strength = "Very Strong Downtrend"

    elif percentage <= -2:

        strength = "Strong Downtrend"

    elif percentage < 0:

        strength = "Weak Downtrend"

    else:

        strength = "Sideway"

    return {

        "change": float(change),

        "percentage": float(percentage),

        "strength": strength

    }

# ==========================================================
# GOLD TREND STRENGTH
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "Trend Strength"

    )

    trend_strength = calculate_trend_strength()

    if trend_strength is None:

        st.warning(

            "Không thể phân tích trend."

        )

    else:

        col1, col2 = st.columns(

            2

        )

        with col1:

            st.metric(

                "20 Day Change",

                format_percent(

                    trend_strength["percentage"]

                )

            )

        with col2:

            st.metric(

                "Strength",

                trend_strength["strength"]

            )

# ==========================================================
# KẾT THÚC ĐOẠN 027
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 028
# ==========================================================

# ==========================================================
# MARKET CORRELATION ANALYZER
# ==========================================================

def calculate_market_correlation():

    data = {}

    symbols = {

        "Gold": MARKET_SYMBOLS["Gold"],

        "DXY": MARKET_SYMBOLS["DXY"],

        "S&P500": MARKET_SYMBOLS["S&P500"],

        "NASDAQ": MARKET_SYMBOLS["NASDAQ"]

    }

    for name, symbol in symbols.items():

        history = load_price_history(

            symbol,

            period="6mo"

        )

        if not history.empty:

            data[name] = history["Close"]

    if len(data) < 2:

        return None

    price_df = pd.DataFrame(

        data

    )

    correlation = price_df.corr()

    return correlation

# ==========================================================
# CORRELATION PAGE
# ==========================================================

if st.session_state.page == "Macro":

    st.divider()

    st.subheader(

        "Market Correlation"

    )

    correlation = calculate_market_correlation()

    if correlation is None:

        st.warning(

            "Không đủ dữ liệu."

        )

    else:

        st.dataframe(

            correlation,

            use_container_width=True

        )

# ==========================================================
# DXY ANALYSIS
# ==========================================================

def analyze_dxy():

    history = load_price_history(

        MARKET_SYMBOLS["DXY"],

        period="6mo"

    )

    if history.empty:

        return None

    close = history["Close"]

    change = (

        close.iloc[-1]

        -

        close.iloc[-20]

    )

    percent = (

        change

        /

        close.iloc[-20]

    ) * 100

    if percent > 2:

        trend = "USD Strong"

    elif percent < -2:

        trend = "USD Weak"

    else:

        trend = "USD Neutral"

    return {

        "change": percent,

        "trend": trend

    }

# ==========================================================
# DXY PAGE
# ==========================================================

if st.session_state.page == "Forex":

    st.divider()

    st.subheader(

        "DXY Analysis"

    )

    dxy_analysis = analyze_dxy()

    if dxy_analysis:

        st.metric(

            "6 Month Change",

            format_percent(

                dxy_analysis["change"]

            )

        )

        st.info(

            dxy_analysis["trend"]

        )

# ==========================================================
# KẾT THÚC ĐOẠN 028
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 029
# ==========================================================

# ==========================================================
# MARKET RISK ANALYZER
# ==========================================================

def calculate_market_risk():

    risk_score = 50

    reasons = []

    if gold_data:

        if abs(gold_data["change"]) > 2:

            risk_score += 15

            reasons.append(

                "Gold biến động mạnh."

            )

        else:

            risk_score -= 5

            reasons.append(

                "Gold ổn định."

            )

    if dxy_data:

        if abs(dxy_data["change"]) > 1:

            risk_score += 15

            reasons.append(

                "USD biến động cao."

            )

        else:

            risk_score -= 5

            reasons.append(

                "USD ổn định."

            )

    if sp500_data:

        if sp500_data["change"] < -1:

            risk_score += 20

            reasons.append(

                "Chứng khoán giảm mạnh."

            )

        elif sp500_data["change"] > 1:

            risk_score -= 5

            reasons.append(

                "Thị trường tích cực."

            )

    risk_score = max(

        0,

        min(

            risk_score,

            100

        )

    )

    if risk_score >= 80:

        level = "High Risk"

    elif risk_score >= 60:

        level = "Medium Risk"

    else:

        level = "Low Risk"

    return {

        "score": risk_score,

        "level": level,

        "reasons": reasons

    }

# ==========================================================
# RISK PAGE
# ==========================================================

if st.session_state.page == "Macro":

    st.divider()

    st.subheader(

        "Market Risk"

    )

    risk = calculate_market_risk()

    st.progress(

        risk["score"] / 100

    )

    st.metric(

        "Risk Score",

        f'{risk["score"]}/100'

    )

    st.info(

        risk["level"]

    )

    for reason in risk["reasons"]:

        st.write(

            "•",

            reason

        )

# ==========================================================
# KẾT THÚC ĐOẠN 029
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 030
# ==========================================================

# ==========================================================
# AI MARKET SUMMARY
# ==========================================================

def generate_ai_summary():

    summary = []

    if gold_data:

        if gold_data["change"] > 0:

            summary.append(

                "Gold đang có lực mua."

            )

        elif gold_data["change"] < 0:

            summary.append(

                "Gold đang chịu áp lực bán."

            )

        else:

            summary.append(

                "Gold đang cân bằng."

            )

    if dxy_data:

        if dxy_data["change"] > 0:

            summary.append(

                "USD đang mạnh lên."

            )

        elif dxy_data["change"] < 0:

            summary.append(

                "USD đang suy yếu."

            )

        else:

            summary.append(

                "USD đi ngang."

            )

    if sp500_data:

        if sp500_data["change"] > 0:

            summary.append(

                "Tâm lý rủi ro tích cực."

            )

        else:

            summary.append(

                "Tâm lý thị trường thận trọng."

            )

    return summary

# ==========================================================
# AI ANALYSIS PAGE
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🤖 AI Market Summary"

    )

    ai_summary = generate_ai_summary()

    for item in ai_summary:

        st.write(

            "•",

            item

        )

# ==========================================================
# MARKET OPEN HOURS
# ==========================================================

def market_session():

    hour = datetime.utcnow().hour

    if 0 <= hour < 7:

        return "Asia Session"

    elif 7 <= hour < 13:

        return "London Session"

    elif 13 <= hour < 21:

        return "New York Session"

    else:

        return "Market Transition"

# ==========================================================
# SESSION DISPLAY
# ==========================================================

st.sidebar.divider()

st.sidebar.subheader(

    "Market Session"

)

st.sidebar.info(

    market_session()

)

# ==========================================================
# KẾT THÚC ĐOẠN 030
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 031
# ==========================================================

# ==========================================================
# TRADING SESSION ANALYZER
# ==========================================================

def analyze_trading_session():

    hour = datetime.utcnow().hour

    if 0 <= hour < 8:

        return {

            "session": "Asia",

            "volatility": "Medium"

        }

    elif 8 <= hour < 16:

        return {

            "session": "London",

            "volatility": "High"

        }

    elif 16 <= hour < 24:

        return {

            "session": "New York",

            "volatility": "Very High"

        }

    return {

        "session": "Unknown",

        "volatility": "Low"

    }

# ==========================================================
# SESSION PANEL
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "⏰ Trading Session"

    )

    session_data = analyze_trading_session()

    col1, col2 = st.columns(

        2

    )

    with col1:

        st.metric(

            "Current Session",

            session_data["session"]

        )

    with col2:

        st.metric(

            "Expected Volatility",

            session_data["volatility"]

        )

# ==========================================================
# MARKET CONDITION ENGINE
# ==========================================================

def market_condition():

    score = 0

    if gold_data:

        if gold_data["change"] > 0:

            score += 1

        else:

            score -= 1

    if dxy_data:

        if dxy_data["change"] < 0:

            score += 1

        else:

            score -= 1

    if sp500_data:

        if sp500_data["change"] > 0:

            score += 1

        else:

            score -= 1

    if score >= 2:

        return "Bullish Environment"

    elif score <= -2:

        return "Bearish Environment"

    return "Mixed Environment"

# ==========================================================
# CONDITION DISPLAY
# ==========================================================

st.sidebar.subheader(

    "Market Condition"

)

st.sidebar.success(

    market_condition()

)

# ==========================================================
# KẾT THÚC ĐOẠN 031
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 032
# ==========================================================

# ==========================================================
# MARKET ALERT SYSTEM
# ==========================================================

if "alerts" not in st.session_state:

    st.session_state.alerts = []


def add_alert(

    symbol,

    target,

    condition

):

    alert = {

        "symbol": symbol,

        "target": target,

        "condition": condition,

        "created": current_time(),

        "active": True

    }

    st.session_state.alerts.append(

        alert

    )

    log(

        "INFO",

        f"Created alert {symbol}"

    )


# ==========================================================
# ALERT PAGE
# ==========================================================

if st.session_state.page == "Settings":

    st.divider()

    st.subheader(

        "🔔 Price Alert"

    )

    alert_symbol = st.selectbox(

        "Symbol",

        list(

            MARKET_SYMBOLS.keys()

        ),

        key="alert_symbol"

    )

    alert_price = st.number_input(

        "Target Price",

        value=0.0,

        key="alert_price"

    )

    alert_condition = st.selectbox(

        "Condition",

        [

            "Above",

            "Below"

        ],

        key="alert_condition"

    )

    if st.button(

        "Create Alert"

    ):

        add_alert(

            alert_symbol,

            alert_price,

            alert_condition

        )

        st.success(

            "Alert created"

        )


# ==========================================================
# ALERT CHECK ENGINE
# ==========================================================

def check_alerts():

    triggered = []

    market_data = {

        "Gold": gold_data,

        "DXY": dxy_data,

        "S&P500": sp500_data,

        "NASDAQ": nasdaq_data

    }

    for alert in st.session_state.alerts:

        if not alert["active"]:

            continue

        data = market_data.get(

            alert["symbol"]

        )

        if data is None:

            continue

        price = data["price"]

        if alert["condition"] == "Above":

            if price >= alert["target"]:

                triggered.append(

                    alert

                )

        if alert["condition"] == "Below":

            if price <= alert["target"]:

                triggered.append(

                    alert

                )

    return triggered


# ==========================================================
# ALERT STATUS
# ==========================================================

active_alerts = check_alerts()

if len(active_alerts) > 0:

    for alert in active_alerts:

        st.toast(

            f'{alert["symbol"]} reached target'

        )


# ==========================================================
# KẾT THÚC ĐOẠN 032
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 033
# ==========================================================

# ==========================================================
# PORTFOLIO TRACKER
# ==========================================================

if "portfolio" not in st.session_state:

    st.session_state.portfolio = []


def add_position(

    symbol,

    amount,

    entry_price

):

    position = {

        "symbol": symbol,

        "amount": amount,

        "entry_price": entry_price,

        "time": current_time()

    }

    st.session_state.portfolio.append(

        position

    )

    log(

        "INFO",

        f"Added position {symbol}"

    )


# ==========================================================
# PORTFOLIO PAGE
# ==========================================================

if st.session_state.page == "Settings":

    st.divider()

    st.subheader(

        "💼 Portfolio"

    )

    portfolio_symbol = st.selectbox(

        "Market",

        list(

            MARKET_SYMBOLS.keys()

        ),

        key="portfolio_symbol"

    )

    portfolio_amount = st.number_input(

        "Amount",

        min_value=0.0,

        value=0.01,

        step=0.01,

        key="portfolio_amount"

    )

    portfolio_entry = st.number_input(

        "Entry Price",

        min_value=0.0,

        value=0.0,

        key="portfolio_entry"

    )


    if st.button(

        "Add Position"

    ):

        add_position(

            portfolio_symbol,

            portfolio_amount,

            portfolio_entry

        )

        st.success(

            "Position added"

        )


# ==========================================================
# PORTFOLIO CALCULATOR
# ==========================================================

def calculate_portfolio():

    result = []

    market = {

        "Gold": gold_data,

        "DXY": dxy_data,

        "S&P500": sp500_data,

        "NASDAQ": nasdaq_data

    }

    for item in st.session_state.portfolio:

        current = market.get(

            item["symbol"]

        )

        if current is None:

            continue

        pnl = (

            current["price"]

            -

            item["entry_price"]

        ) * item["amount"]

        result.append(

            {

                "Symbol": item["symbol"],

                "Amount": item["amount"],

                "Entry": item["entry_price"],

                "Current": current["price"],

                "PnL": round(

                    pnl,

                    2

                )

            }

        )

    return pd.DataFrame(

        result

    )


# ==========================================================
# PORTFOLIO DISPLAY
# ==========================================================

if st.session_state.page == "Settings":

    if len(

        st.session_state.portfolio

    ) > 0:

        st.subheader(

            "Current Positions"

        )

        st.dataframe(

            calculate_portfolio(),

            use_container_width=True,

            hide_index=True

        )


# ==========================================================
# KẾT THÚC ĐOẠN 033
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 034
# ==========================================================

# ==========================================================
# TRADING JOURNAL
# ==========================================================

if "journal" not in st.session_state:

    st.session_state.journal = []


def add_trade_record(

    symbol,

    direction,

    entry,

    exit_price,

    volume,

    note

):

    profit = (

        exit_price - entry

    ) * volume

    if direction == "SELL":

        profit = (

            entry - exit_price

        ) * volume

    trade = {

        "Time": current_time(),

        "Symbol": symbol,

        "Direction": direction,

        "Entry": entry,

        "Exit": exit_price,

        "Volume": volume,

        "Profit": round(

            profit,

            2

        ),

        "Note": note

    }

    st.session_state.journal.append(

        trade

    )

    log(

        "INFO",

        f"Trade saved {symbol}"

    )


# ==========================================================
# JOURNAL PAGE
# ==========================================================

if st.session_state.page == "Settings":

    st.divider()

    st.subheader(

        "📒 Trading Journal"

    )

    journal_symbol = st.selectbox(

        "Symbol",

        list(

            MARKET_SYMBOLS.keys()

        ),

        key="journal_symbol"

    )

    journal_direction = st.selectbox(

        "Direction",

        [

            "BUY",

            "SELL"

        ],

        key="journal_direction"

    )

    journal_entry = st.number_input(

        "Entry",

        value=0.0,

        key="journal_entry"

    )

    journal_exit = st.number_input(

        "Exit",

        value=0.0,

        key="journal_exit"

    )

    journal_volume = st.number_input(

        "Volume",

        value=0.01,

        step=0.01,

        key="journal_volume"

    )

    journal_note = st.text_input(

        "Note",

        key="journal_note"

    )


    if st.button(

        "Save Trade"

    ):

        add_trade_record(

            journal_symbol,

            journal_direction,

            journal_entry,

            journal_exit,

            journal_volume,

            journal_note

        )

        st.success(

            "Trade saved"

        )


# ==========================================================
# JOURNAL DISPLAY
# ==========================================================

if st.session_state.page == "Settings":

    if len(

        st.session_state.journal

    ) > 0:

        st.subheader(

            "Trade History"

        )

        journal_df = pd.DataFrame(

            st.session_state.journal

        )

        st.dataframe(

            journal_df,

            use_container_width=True,

            hide_index=True

        )


# ==========================================================
# KẾT THÚC ĐOẠN 034
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 035
# ==========================================================

# ==========================================================
# TRADING PERFORMANCE ANALYZER
# ==========================================================

def analyze_trading_performance():

    if len(

        st.session_state.journal

    ) == 0:

        return {

            "total": 0,

            "wins": 0,

            "losses": 0,

            "winrate": 0,

            "profit": 0

        }

    total = len(

        st.session_state.journal

    )

    wins = 0

    losses = 0

    total_profit = 0

    for trade in st.session_state.journal:

        profit = trade["Profit"]

        total_profit += profit

        if profit > 0:

            wins += 1

        else:

            losses += 1

    winrate = (

        wins

        /

        total

    ) * 100

    return {

        "total": total,

        "wins": wins,

        "losses": losses,

        "winrate": winrate,

        "profit": total_profit

    }


# ==========================================================
# PERFORMANCE DISPLAY
# ==========================================================

if st.session_state.page == "Settings":

    st.divider()

    st.subheader(

        "📈 Trading Performance"

    )

    performance = analyze_trading_performance()

    col1, col2, col3, col4 = st.columns(

        4

    )

    with col1:

        st.metric(

            "Total Trades",

            performance["total"]

        )

    with col2:

        st.metric(

            "Wins",

            performance["wins"]

        )

    with col3:

        st.metric(

            "Win Rate",

            f'{performance["winrate"]:.2f}%'

        )

    with col4:

        st.metric(

            "Profit",

            round(

                performance["profit"],

                2

            )

        )


# ==========================================================
# RISK MANAGEMENT CALCULATOR
# ==========================================================

def calculate_risk_reward(

    entry,

    stop_loss,

    take_profit

):

    risk = abs(

        entry - stop_loss

    )

    reward = abs(

        take_profit - entry

    )

    if risk == 0:

        return 0

    return reward / risk


# ==========================================================
# RISK REWARD PAGE
# ==========================================================

if st.session_state.page == "Settings":

    st.divider()

    st.subheader(

        "⚖ Risk Reward Calculator"

    )

    entry_price = st.number_input(

        "Entry Price",

        value=0.0,

        key="rr_entry"

    )

    stop_price = st.number_input(

        "Stop Loss",

        value=0.0,

        key="rr_stop"

    )

    target_price = st.number_input(

        "Take Profit",

        value=0.0,

        key="rr_target"

    )

    rr = calculate_risk_reward(

        entry_price,

        stop_price,

        target_price

    )

    st.metric(

        "Risk Reward Ratio",

        f"1:{rr:.2f}"

    )


# ==========================================================
# KẾT THÚC ĐOẠN 035
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 036
# ==========================================================

# ==========================================================
# TRADING PLAN GENERATOR
# ==========================================================

def generate_trading_plan():

    signal, reasons = generate_gold_signal()

    trend = analyze_gold_trend()

    plan = {

        "Signal": signal,

        "Reasons": reasons,

        "Trend": "Unknown",

        "Strategy": "Wait"

    }

    if trend:

        plan["Trend"] = trend["trend"]

    if signal == "BUY":

        plan["Strategy"] = (

            "Look for Buy setup "

            "near support"

        )

    elif signal == "SELL":

        plan["Strategy"] = (

            "Look for Sell setup "

            "near resistance"

        )

    else:

        plan["Strategy"] = (

            "Wait for confirmation"

        )

    return plan


# ==========================================================
# TRADING PLAN PAGE
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "📋 Trading Plan"

    )

    plan = generate_trading_plan()

    st.write(

        "Signal:",

        plan["Signal"]

    )

    st.write(

        "Trend:",

        plan["Trend"]

    )

    st.write(

        "Strategy:",

        plan["Strategy"]

    )

    st.subheader(

        "Reasons"

    )

    for reason in plan["Reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# TRADE CHECKLIST
# ==========================================================

if "checklist" not in st.session_state:

    st.session_state.checklist = {

        "Trend Checked": False,

        "Risk Checked": False,

        "News Checked": False,

        "Entry Checked": False

    }


# ==========================================================
# CHECKLIST PAGE
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "✅ Trade Checklist"

    )

    for item in st.session_state.checklist:

        st.session_state.checklist[item] = st.checkbox(

            item,

            value=st.session_state.checklist[item]

        )


    completed = sum(

        st.session_state.checklist.values()

    )


    st.progress(

        completed / len(

            st.session_state.checklist

        )

    )


    st.write(

        f"Completed: {completed}/"

        f"{len(st.session_state.checklist)}"

    )


# ==========================================================
# MARKET TIMER
# ==========================================================

def get_market_timer():

    now = datetime.utcnow()

    return {

        "UTC": now.strftime(

            "%H:%M:%S"

        ),

        "Date": now.strftime(

            "%Y-%m-%d"

        )

    }


# ==========================================================
# TIMER DISPLAY
# ==========================================================

timer = get_market_timer()

st.sidebar.divider()

st.sidebar.subheader(

    "Market Time"

)

st.sidebar.write(

    timer["Date"]

)

st.sidebar.write(

    timer["UTC"]

)


# ==========================================================
# KẾT THÚC ĐOẠN 036
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 037
# ==========================================================

# ==========================================================
# DAILY REPORT GENERATOR
# ==========================================================

def generate_daily_report():

    sentiment, details = calculate_market_sentiment()

    risk = calculate_market_risk()

    fear_greed = calculate_fear_greed()

    report = {

        "Time":

            current_time(),

        "Market Sentiment":

            sentiment,

        "Fear Greed":

            fear_greed,

        "Risk Level":

            risk["level"],

        "Risk Score":

            risk["score"],

        "Details":

            details

    }

    return report


# ==========================================================
# REPORT PAGE
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "📄 Daily Market Report"

    )

    report = generate_daily_report()

    report_df = pd.DataFrame(

        {

            "Item":

            report.keys(),

            "Value":

            report.values()

        }

    )

    st.dataframe(

        report_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# EXPORT REPORT
# ==========================================================

def export_report():

    report = generate_daily_report()

    return json.dumps(

        report,

        indent=4,

        ensure_ascii=False

    )


# ==========================================================
# DOWNLOAD REPORT
# ==========================================================

if st.session_state.page == "Dashboard":

    st.download_button(

        "⬇ Download Report",

        export_report(),

        file_name="WEOS_Report.json",

        mime="application/json"

    )


# ==========================================================
# DATA CACHE MANAGEMENT
# ==========================================================

def clear_cache():

    st.cache_data.clear()

    log(

        "INFO",

        "Cache cleared"

    )


# ==========================================================
# CACHE CONTROL
# ==========================================================

if st.session_state.page == "Settings":

    st.divider()

    st.subheader(

        "System Maintenance"

    )

    if st.button(

        "Clear Data Cache"

    ):

        clear_cache()

        st.success(

            "Cache cleared successfully"

        )


# ==========================================================
# APPLICATION UPTIME
# ==========================================================

def calculate_uptime():

    uptime = datetime.now() - st.session_state.startup_time

    return str(

        uptime

    )


st.sidebar.divider()

st.sidebar.write(

    "⏱ Uptime:",

    calculate_uptime()

)


# ==========================================================
# KẾT THÚC ĐOẠN 037
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 038
# ==========================================================

# ==========================================================
# AI DECISION ENGINE
# ==========================================================

def ai_decision_engine():

    score = 50

    factors = []

    if gold_data:

        if gold_data["change"] > 0:

            score += 15

            factors.append(

                "Gold momentum positive"

            )

        else:

            score -= 15

            factors.append(

                "Gold momentum negative"

            )

    if dxy_data:

        if dxy_data["change"] < 0:

            score += 15

            factors.append(

                "USD weakness supports Gold"

            )

        else:

            score -= 15

            factors.append(

                "USD strength pressures Gold"

            )

    if sp500_data:

        if sp500_data["change"] > 0:

            score += 10

            factors.append(

                "Risk appetite positive"

            )

        else:

            score -= 10

            factors.append(

                "Risk sentiment weak"

            )

    score = max(

        0,

        min(

            score,

            100

        )

    )

    if score >= 75:

        decision = "BUY BIAS"

    elif score <= 25:

        decision = "SELL BIAS"

    else:

        decision = "WAIT"

    return {

        "score": score,

        "decision": decision,

        "factors": factors

    }


# ==========================================================
# AI DECISION PANEL
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🧠 AI Decision Engine"

    )

    decision = ai_decision_engine()

    st.progress(

        decision["score"]

        /

        100

    )

    st.metric(

        "AI Score",

        f'{decision["score"]}/100'

    )

    st.info(

        decision["decision"]

    )

    for factor in decision["factors"]:

        st.write(

            "•",

            factor

        )


# ==========================================================
# MARKET MONITOR
# ==========================================================

def market_monitor():

    monitor = []

    markets = {

        "Gold": gold_data,

        "DXY": dxy_data,

        "S&P500": sp500_data,

        "NASDAQ": nasdaq_data

    }

    for name, data in markets.items():

        if data:

            monitor.append(

                {

                    "Market": name,

                    "Price": data["price"],

                    "Change": data["change"]

                }

            )

    return pd.DataFrame(

        monitor

    )


# ==========================================================
# MONITOR DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.subheader(

        "📡 Market Monitor"

    )

    monitor_df = market_monitor()

    st.dataframe(

        monitor_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# KẾT THÚC ĐOẠN 038
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 039
# ==========================================================

# ==========================================================
# MARKET DATA STORAGE
# ==========================================================

if "market_history" not in st.session_state:

    st.session_state.market_history = []


def save_market_snapshot():

    snapshot = {

        "time": current_time(),

        "gold":

            gold_data["price"]

            if gold_data else None,

        "dxy":

            dxy_data["price"]

            if dxy_data else None,

        "sp500":

            sp500_data["price"]

            if sp500_data else None,

        "nasdaq":

            nasdaq_data["price"]

            if nasdaq_data else None

    }

    st.session_state.market_history.append(

        snapshot

    )

    if len(

        st.session_state.market_history

    ) > 500:

        st.session_state.market_history.pop(

            0

        )


save_market_snapshot()


# ==========================================================
# MARKET HISTORY PAGE
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "📈 Market History"

    )

    history_df = pd.DataFrame(

        st.session_state.market_history

    )

    if not history_df.empty:

        st.dataframe(

            history_df.tail(

                20

            ),

            use_container_width=True,

            hide_index=True

        )


# ==========================================================
# MARKET CHANGE TRACKER
# ==========================================================

def calculate_change_tracker():

    result = []

    markets = {

        "Gold": gold_data,

        "DXY": dxy_data,

        "S&P500": sp500_data,

        "NASDAQ": nasdaq_data

    }

    for name, data in markets.items():

        if data:

            result.append(

                {

                    "Market": name,

                    "Change %":

                    round(

                        data["change"],

                        2

                    )

                }

            )

    return pd.DataFrame(

        result

    )


# ==========================================================
# CHANGE TRACKER DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.subheader(

        "📊 Daily Change Tracker"

    )

    change_df = calculate_change_tracker()

    st.dataframe(

        change_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# KẾT THÚC ĐOẠN 039
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 040
# ==========================================================

# ==========================================================
# ECONOMIC IMPACT ENGINE
# ==========================================================

def calculate_economic_impact():

    impact_score = 50

    factors = []

    if dxy_data:

        if dxy_data["change"] > 0:

            impact_score -= 10

            factors.append(

                "USD strength may pressure Gold"

            )

        else:

            impact_score += 10

            factors.append(

                "USD weakness supports Gold"

            )

    if gold_data:

        if gold_data["change"] > 0:

            impact_score += 10

            factors.append(

                "Gold momentum positive"

            )

        else:

            impact_score -= 10

            factors.append(

                "Gold momentum negative"

            )

    if sp500_data:

        if sp500_data["change"] < 0:

            impact_score += 5

            factors.append(

                "Risk aversion increases"

            )

        else:

            factors.append(

                "Risk appetite stable"

            )

    impact_score = max(

        0,

        min(

            impact_score,

            100

        )

    )

    if impact_score >= 70:

        status = "Positive For Gold"

    elif impact_score <= 30:

        status = "Negative For Gold"

    else:

        status = "Neutral"


    return {

        "score": impact_score,

        "status": status,

        "factors": factors

    }


# ==========================================================
# ECONOMIC IMPACT DISPLAY
# ==========================================================

if st.session_state.page == "Macro":

    st.divider()

    st.subheader(

        "🌎 Economic Impact"

    )

    economic = calculate_economic_impact()

    st.progress(

        economic["score"]

        /

        100

    )

    st.metric(

        "Gold Impact Score",

        f'{economic["score"]}/100'

    )

    st.info(

        economic["status"]

    )

    for factor in economic["factors"]:

        st.write(

            "•",

            factor

        )


# ==========================================================
# MARKET TREND SUMMARY
# ==========================================================

def trend_summary():

    summary = []

    if gold_data:

        summary.append(

            {

                "Asset": "Gold",

                "Trend":

                "Up"

                if gold_data["change"] > 0

                else "Down"

            }

        )

    if dxy_data:

        summary.append(

            {

                "Asset": "DXY",

                "Trend":

                "Up"

                if dxy_data["change"] > 0

                else "Down"

            }

        )

    return pd.DataFrame(

        summary

    )


# ==========================================================
# TREND SUMMARY DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.subheader(

        "Trend Summary"

    )

    st.dataframe(

        trend_summary(),

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# KẾT THÚC ĐOẠN 040
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 041
# ==========================================================

# ==========================================================
# PRICE ALERT HISTORY
# ==========================================================

if "alert_history" not in st.session_state:

    st.session_state.alert_history = []


def save_alert_history(

    alert,

    price

):

    record = {

        "Time": current_time(),

        "Symbol": alert["symbol"],

        "Target": alert["target"],

        "Current": price,

        "Condition": alert["condition"]

    }

    st.session_state.alert_history.append(

        record

    )


# ==========================================================
# ALERT HISTORY CHECK
# ==========================================================

def process_alerts():

    triggered = check_alerts()

    for alert in triggered:

        market = {

            "Gold": gold_data,

            "DXY": dxy_data,

            "S&P500": sp500_data,

            "NASDAQ": nasdaq_data

        }

        data = market.get(

            alert["symbol"]

        )

        if data:

            save_alert_history(

                alert,

                data["price"]

            )


process_alerts()


# ==========================================================
# ALERT HISTORY DISPLAY
# ==========================================================

if st.session_state.page == "Settings":

    st.divider()

    st.subheader(

        "🔔 Alert History"

    )

    if len(

        st.session_state.alert_history

    ) == 0:

        st.info(

            "No triggered alerts"

        )

    else:

        alert_df = pd.DataFrame(

            st.session_state.alert_history

        )

        st.dataframe(

            alert_df,

            use_container_width=True,

            hide_index=True

        )


# ==========================================================
# FAVORITE SYSTEM
# ==========================================================

if "favorites" not in st.session_state:

    st.session_state.favorites = []


def add_favorite(

    symbol

):

    if symbol not in st.session_state.favorites:

        st.session_state.favorites.append(

            symbol

        )

        log(

            "INFO",

            f"Added favorite {symbol}"

        )


# ==========================================================
# FAVORITE PANEL
# ==========================================================

if st.session_state.page == "Watchlist":

    st.divider()

    st.subheader(

        "⭐ Favorites"

    )

    favorite_symbol = st.selectbox(

        "Choose Symbol",

        list(

            MARKET_SYMBOLS.keys()

        ),

        key="favorite_select"

    )

    if st.button(

        "Add Favorite"

    ):

        add_favorite(

            favorite_symbol

        )

        st.success(

            "Added"

        )


    if len(

        st.session_state.favorites

    ) > 0:

        st.write(

            st.session_state.favorites

        )


# ==========================================================
# KẾT THÚC ĐOẠN 041
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 042
# ==========================================================

# ==========================================================
# MARKET SCANNER ENGINE
# ==========================================================

def market_scanner():

    results = []

    markets = {

        "Gold": gold_data,

        "DXY": dxy_data,

        "S&P500": sp500_data,

        "NASDAQ": nasdaq_data

    }

    for name, data in markets.items():

        if data is None:

            continue

        change = data["change"]

        if change >= 1:

            signal = "Strong Buy"

        elif change > 0:

            signal = "Buy"

        elif change <= -1:

            signal = "Strong Sell"

        elif change < 0:

            signal = "Sell"

        else:

            signal = "Neutral"


        results.append(

            {

                "Market": name,

                "Price": round(

                    data["price"],

                    2

                ),

                "Change": round(

                    change,

                    2

                ),

                "Signal": signal

            }

        )

    return pd.DataFrame(

        results

    )


# ==========================================================
# SCANNER DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🔎 Market Scanner"

    )

    scanner_df = market_scanner()

    st.dataframe(

        scanner_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# TOP MOVERS
# ==========================================================

def find_top_movers():

    scanner = market_scanner()

    if scanner.empty:

        return None, None

    highest = scanner.sort_values(

        "Change",

        ascending=False

    ).iloc[0]

    lowest = scanner.sort_values(

        "Change",

        ascending=True

    ).iloc[0]

    return highest, lowest


# ==========================================================
# TOP MOVERS DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    top, bottom = find_top_movers()

    if top is not None:

        col1, col2 = st.columns(

            2

        )

        with col1:

            st.success(

                f"🚀 Strongest: {top['Market']} "

                f"{top['Change']}%"

            )

        with col2:

            st.error(

                f"📉 Weakest: {bottom['Market']} "

                f"{bottom['Change']}%"

            )


# ==========================================================
# MARKET RANKING
# ==========================================================

def market_ranking():

    scanner = market_scanner()

    if scanner.empty:

        return scanner

    ranking = scanner.sort_values(

        "Change",

        ascending=False

    )

    ranking.insert(

        0,

        "Rank",

        range(

            1,

            len(ranking)+1

        )

    )

    return ranking


# ==========================================================
# RANKING DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.subheader(

        "🏆 Market Ranking"

    )

    st.dataframe(

        market_ranking(),

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# KẾT THÚC ĐOẠN 042
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 043
# ==========================================================

# ==========================================================
# MARKET HEATMAP ENGINE
# ==========================================================

def create_market_heatmap():

    data = []

    markets = {

        "Gold": gold_data,

        "DXY": dxy_data,

        "S&P500": sp500_data,

        "NASDAQ": nasdaq_data,

        "EURUSD": eurusd_data,

        "GBPUSD": gbpusd_data,

        "USDJPY": usdjpy_data

    }

    for name, item in markets.items():

        if item is None:

            continue

        change = item["change"]

        if change > 0:

            status = "Positive"

        elif change < 0:

            status = "Negative"

        else:

            status = "Neutral"


        data.append(

            {

                "Asset": name,

                "Change %": round(

                    change,

                    2

                ),

                "Status": status

            }

        )

    return pd.DataFrame(

        data

    )


# ==========================================================
# HEATMAP DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🔥 Market Heatmap"

    )

    heatmap = create_market_heatmap()

    st.dataframe(

        heatmap,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# MARKET STRENGTH SCORE
# ==========================================================

def market_strength_score():

    results = []

    markets = {

        "Gold": gold_data,

        "DXY": dxy_data,

        "S&P500": sp500_data,

        "NASDAQ": nasdaq_data

    }

    for name, data in markets.items():

        if data is None:

            continue

        score = 50

        change = data["change"]

        score += change * 10

        score = max(

            0,

            min(

                score,

                100

            )

        )

        results.append(

            {

                "Market": name,

                "Strength": round(

                    score,

                    1

                )

            }

        )

    return pd.DataFrame(

        results

    )


# ==========================================================
# STRENGTH DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.subheader(

        "💪 Market Strength"

    )

    strength_df = market_strength_score()

    st.dataframe(

        strength_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# KẾT THÚC ĐOẠN 043
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 044
# ==========================================================

# ==========================================================
# MARKET TREND SCORE
# ==========================================================

def calculate_trend_score():

    markets = {

        "Gold": gold_data,

        "DXY": dxy_data,

        "S&P500": sp500_data,

        "NASDAQ": nasdaq_data

    }

    results = []

    for name, data in markets.items():

        if data is None:

            continue

        score = 50

        change = data["change"]

        if change > 0:

            score += abs(change) * 10

        else:

            score -= abs(change) * 10


        score = max(

            0,

            min(

                score,

                100

            )

        )

        if score >= 70:

            trend = "Strong"

        elif score >= 55:

            trend = "Positive"

        elif score <= 30:

            trend = "Weak"

        else:

            trend = "Neutral"


        results.append(

            {

                "Market": name,

                "Score": round(

                    score,

                    1

                ),

                "Trend": trend

            }

        )

    return pd.DataFrame(

        results

    )


# ==========================================================
# TREND SCORE DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "📈 Trend Score"

    )

    trend_score_df = calculate_trend_score()

    st.dataframe(

        trend_score_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# MARKET ALERT SUMMARY
# ==========================================================

def alert_summary():

    total = len(

        st.session_state.alerts

    )

    active = 0

    for alert in st.session_state.alerts:

        if alert["active"]:

            active += 1

    return {

        "Total": total,

        "Active": active

    }


# ==========================================================
# ALERT SIDEBAR
# ==========================================================

alert_data = alert_summary()

st.sidebar.subheader(

    "🔔 Alerts"

)

st.sidebar.metric(

    "Total",

    alert_data["Total"]

)

st.sidebar.metric(

    "Active",

    alert_data["Active"]

)


# ==========================================================
# KẾT THÚC ĐOẠN 044
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 045
# ==========================================================

# ==========================================================
# TRADING PSYCHOLOGY MODULE
# ==========================================================

if "psychology_notes" not in st.session_state:

    st.session_state.psychology_notes = []


def add_psychology_note(

    emotion,

    note

):

    record = {

        "Time": current_time(),

        "Emotion": emotion,

        "Note": note

    }

    st.session_state.psychology_notes.append(

        record

    )

    log(

        "INFO",

        "Added psychology note"

    )


# ==========================================================
# PSYCHOLOGY PAGE
# ==========================================================

if st.session_state.page == "Settings":

    st.divider()

    st.subheader(

        "🧠 Trading Psychology"

    )

    emotion = st.selectbox(

        "Current Emotion",

        [

            "Calm",

            "Confident",

            "Fear",

            "Greed",

            "Angry",

            "Stress"

        ]

    )

    psychology_note = st.text_area(

        "Trading Feeling"

    )

    if st.button(

        "Save Emotion"

    ):

        add_psychology_note(

            emotion,

            psychology_note

        )

        st.success(

            "Saved"

        )


# ==========================================================
# PSYCHOLOGY HISTORY
# ==========================================================

if st.session_state.page == "Settings":

    if len(

        st.session_state.psychology_notes

    ) > 0:

        st.subheader(

            "Emotion History"

        )

        psychology_df = pd.DataFrame(

            st.session_state.psychology_notes

        )

        st.dataframe(

            psychology_df,

            use_container_width=True,

            hide_index=True

        )


# ==========================================================
# TRADING RULE ENGINE
# ==========================================================

def trading_rules_check():

    rules = {

        "Risk Management": False,

        "Trend Confirmation": False,

        "News Check": False,

        "Emotion Control": False

    }

    if gold_data:

        rules["Trend Confirmation"] = True

    if len(

        st.session_state.news

    ) >= 0:

        rules["News Check"] = True

    if len(

        st.session_state.psychology_notes

    ) > 0:

        rules["Emotion Control"] = True

    return rules


# ==========================================================
# RULE DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "📌 Trading Rules"

    )

    rules = trading_rules_check()

    completed = 0

    for name, status in rules.items():

        if status:

            st.success(

                f"✔ {name}"

            )

            completed += 1

        else:

            st.warning(

                f"✖ {name}"

            )

    st.progress(

        completed /

        len(rules)

    )


# ==========================================================
# KẾT THÚC ĐOẠN 045
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 046
# ==========================================================

# ==========================================================
# RISK MANAGEMENT SYSTEM
# ==========================================================

if "risk_settings" not in st.session_state:

    st.session_state.risk_settings = {

        "capital": 100,

        "risk_percent": 2,

        "max_loss": 10

    }


def calculate_risk_amount():

    capital = st.session_state.risk_settings["capital"]

    risk_percent = st.session_state.risk_settings["risk_percent"]

    return (

        capital

        *

        risk_percent

        /

        100

    )


# ==========================================================
# RISK MANAGEMENT PAGE
# ==========================================================

if st.session_state.page == "Settings":

    st.divider()

    st.subheader(

        "🛡 Risk Management"

    )

    capital = st.number_input(

        "Account Capital",

        value=float(

            st.session_state.risk_settings["capital"]

        )

    )

    risk_percent = st.slider(

        "Risk Percentage",

        0.5,

        10.0,

        float(

            st.session_state.risk_settings["risk_percent"]

        )

    )


    st.session_state.risk_settings["capital"] = capital

    st.session_state.risk_settings["risk_percent"] = risk_percent


    max_loss = calculate_risk_amount()


    st.metric(

        "Maximum Loss",

        f"${max_loss:.2f}"

    )


# ==========================================================
# POSITION SIZE CALCULATOR
# ==========================================================

def calculate_position_size(

    risk_money,

    stop_loss_distance

):

    if stop_loss_distance <= 0:

        return 0

    position = (

        risk_money

        /

        stop_loss_distance

    )

    return round(

        position,

        2

    )


# ==========================================================
# POSITION SIZE PANEL
# ==========================================================

if st.session_state.page == "Settings":

    st.divider()

    st.subheader(

        "📐 Position Size"

    )

    stop_distance = st.number_input(

        "Stop Loss Distance",

        value=10.0

    )

    risk_money = calculate_risk_amount()

    position_size = calculate_position_size(

        risk_money,

        stop_distance

    )

    st.metric(

        "Suggested Size",

        position_size

    )


# ==========================================================
# DAILY LOSS LIMIT
# ==========================================================

if "daily_loss" not in st.session_state:

    st.session_state.daily_loss = 0


def check_daily_loss():

    limit = calculate_risk_amount()

    if st.session_state.daily_loss >= limit:

        return False

    return True


# ==========================================================
# LOSS STATUS
# ==========================================================

if st.session_state.page == "Dashboard":

    st.sidebar.subheader(

        "Daily Risk"

    )

    if check_daily_loss():

        st.sidebar.success(

            "Risk Available"

        )

    else:

        st.sidebar.error(

            "Risk Limit Reached"

        )


# ==========================================================
# KẾT THÚC ĐOẠN 046
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 047
# ==========================================================

# ==========================================================
# TRADE STATISTICS ENGINE
# ==========================================================

def calculate_trade_statistics():

    if len(

        st.session_state.journal

    ) == 0:

        return {

            "total": 0,

            "profit": 0,

            "average": 0,

            "best": 0,

            "worst": 0

        }

    profits = []

    for trade in st.session_state.journal:

        profits.append(

            trade["Profit"]

        )

    return {

        "total":

            len(profits),

        "profit":

            sum(profits),

        "average":

            sum(profits)

            /

            len(profits),

        "best":

            max(profits),

        "worst":

            min(profits)

    }


# ==========================================================
# STATISTICS DISPLAY
# ==========================================================

if st.session_state.page == "Settings":

    st.divider()

    st.subheader(

        "📊 Trade Statistics"

    )

    statistics = calculate_trade_statistics()

    col1, col2 = st.columns(

        2

    )

    with col1:

        st.metric(

            "Total Trades",

            statistics["total"]

        )

        st.metric(

            "Total Profit",

            round(

                statistics["profit"],

                2

            )

        )

    with col2:

        st.metric(

            "Best Trade",

            round(

                statistics["best"],

                2

            )

        )

        st.metric(

            "Worst Trade",

            round(

                statistics["worst"],

                2

            )

        )


# ==========================================================
# EQUITY TRACKING
# ==========================================================

if "equity_history" not in st.session_state:

    st.session_state.equity_history = []


def update_equity():

    stats = calculate_trade_statistics()

    equity = (

        st.session_state.risk_settings["capital"]

        +

        stats["profit"]

    )

    st.session_state.equity_history.append(

        {

            "Time": current_time(),

            "Equity": equity

        }

    )


update_equity()


# ==========================================================
# EQUITY CHART
# ==========================================================

if st.session_state.page == "Settings":

    st.divider()

    st.subheader(

        "💰 Equity Curve"

    )

    equity_df = pd.DataFrame(

        st.session_state.equity_history

    )

    if not equity_df.empty:

        st.line_chart(

            equity_df.set_index(

                "Time"

            )

        )


# ==========================================================
# DRAWDOWN CALCULATOR
# ==========================================================

def calculate_drawdown():

    if len(

        st.session_state.equity_history

    ) == 0:

        return 0

    values = [

        item["Equity"]

        for item in st.session_state.equity_history

    ]

    peak = max(values)

    current = values[-1]

    if peak == 0:

        return 0

    drawdown = (

        peak - current

    ) / peak * 100

    return drawdown


# ==========================================================
# DRAWDOWN DISPLAY
# ==========================================================

if st.session_state.page == "Settings":

    st.metric(

        "Drawdown",

        f"{calculate_drawdown():.2f}%"

    )


# ==========================================================
# KẾT THÚC ĐOẠN 047
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 048
# ==========================================================

# ==========================================================
# TRADE EXPORT SYSTEM
# ==========================================================

def export_trade_history():

    if len(

        st.session_state.journal

    ) == 0:

        return pd.DataFrame()

    return pd.DataFrame(

        st.session_state.journal

    )


# ==========================================================
# EXPORT JOURNAL
# ==========================================================

if st.session_state.page == "Settings":

    st.divider()

    st.subheader(

        "📤 Export Trading Journal"

    )

    export_df = export_trade_history()

    if export_df.empty:

        st.info(

            "No trading records."

        )

    else:

        csv_data = export_df.to_csv(

            index=False

        )

        st.download_button(

            "Download CSV",

            csv_data,

            file_name="WEOS_Trading_Journal.csv",

            mime="text/csv"

        )


# ==========================================================
# SYSTEM BACKUP
# ==========================================================

def create_backup():

    backup = {

        "watchlist":

            st.session_state.watchlist,

        "favorites":

            st.session_state.favorites,

        "alerts":

            st.session_state.alerts,

        "portfolio":

            st.session_state.portfolio,

        "journal":

            st.session_state.journal,

        "logs":

            st.session_state.logs,

        "created":

            current_time()

    }

    return json.dumps(

        backup,

        indent=4,

        ensure_ascii=False

    )


# ==========================================================
# BACKUP PANEL
# ==========================================================

if st.session_state.page == "Settings":

    st.divider()

    st.subheader(

        "💾 System Backup"

    )

    backup_file = create_backup()

    st.download_button(

        "Export WEOS Backup",

        backup_file,

        file_name="WEOS_Backup.json",

        mime="application/json"

    )


# ==========================================================
# RESTORE CHECK
# ==========================================================

def validate_backup(data):

    required = [

        "watchlist",

        "favorites",

        "alerts",

        "portfolio",

        "journal"

    ]

    for item in required:

        if item not in data:

            return False

    return True


# ==========================================================
# BACKUP VALIDATION
# ==========================================================

if st.session_state.page == "Settings":

    st.write(

        "Backup system ready."

    )


# ==========================================================
# PERFORMANCE SCORE
# ==========================================================

def calculate_performance_score():

    statistics = calculate_trade_statistics()

    score = 50

    if statistics["total"] > 0:

        if statistics["profit"] > 0:

            score += 25

        else:

            score -= 20

    drawdown = calculate_drawdown()

    if drawdown < 5:

        score += 10

    elif drawdown > 20:

        score -= 20

    return max(

        0,

        min(

            score,

            100

        )

    )


# ==========================================================
# PERFORMANCE SCORE DISPLAY
# ==========================================================

if st.session_state.page == "Settings":

    st.metric(

        "Performance Score",

        f"{calculate_performance_score()}/100"

    )


# ==========================================================
# KẾT THÚC ĐOẠN 048
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 049
# ==========================================================

# ==========================================================
# MARKET DATA QUALITY CHECK
# ==========================================================

def check_market_data_quality():

    results = []

    markets = {

        "Gold": gold_data,

        "DXY": dxy_data,

        "S&P500": sp500_data,

        "NASDAQ": nasdaq_data

    }

    for name, data in markets.items():

        if data is None:

            status = "Unavailable"

        else:

            if abs(

                data["change"]

            ) > 10:

                status = "Suspicious"

            else:

                status = "Healthy"

        results.append(

            {

                "Market": name,

                "Status": status

            }

        )

    return pd.DataFrame(

        results

    )


# ==========================================================
# DATA QUALITY DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🔍 Data Quality"

    )

    quality_df = check_market_data_quality()

    st.dataframe(

        quality_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# AUTO MARKET REFRESH
# ==========================================================

if "auto_refresh" not in st.session_state:

    st.session_state.auto_refresh = False


if st.session_state.page == "Settings":

    st.divider()

    st.subheader(

        "🔄 Auto Refresh"

    )

    st.session_state.auto_refresh = st.checkbox(

        "Enable Auto Refresh",

        value=st.session_state.auto_refresh

    )


# ==========================================================
# REFRESH CONTROL
# ==========================================================

def refresh_application():

    st.cache_data.clear()

    log(

        "INFO",

        "Manual refresh executed"

    )


if st.session_state.page == "Dashboard":

    if st.button(

        "Refresh Market Data"

    ):

        refresh_application()

        st.success(

            "Market data refreshed"

        )


# ==========================================================
# MARKET OPEN STATUS
# ==========================================================

def market_open_status():

    hour = datetime.utcnow().hour

    if 22 <= hour or hour < 0:

        return "Closed"

    elif 0 <= hour < 8:

        return "Asia"

    elif 8 <= hour < 16:

        return "London"

    else:

        return "New York"


# ==========================================================
# STATUS DISPLAY
# ==========================================================

st.sidebar.divider()

st.sidebar.subheader(

    "Market Status"

)

st.sidebar.info(

    market_open_status()

)


# ==========================================================
# SYSTEM MESSAGE CENTER
# ==========================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


def add_message(

    message

):

    st.session_state.messages.append(

        {

            "time": current_time(),

            "message": message

        }

    )


add_message(

    "WEOS monitoring active"

)


# ==========================================================
# MESSAGE DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.subheader(

        "📢 System Messages"

    )

    message_df = pd.DataFrame(

        st.session_state.messages[-10:]

    )

    st.dataframe(

        message_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# KẾT THÚC ĐOẠN 049
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 050
# ==========================================================

# ==========================================================
# MARKET WATCH ENGINE
# ==========================================================

def market_watch():

    watch_data = []

    symbols = {

        "Gold": gold_data,

        "DXY": dxy_data,

        "S&P500": sp500_data,

        "NASDAQ": nasdaq_data,

        "EURUSD": eurusd_data,

        "GBPUSD": gbpusd_data,

        "USDJPY": usdjpy_data

    }

    for name, data in symbols.items():

        if data is None:

            continue

        movement = data["change"]

        if movement > 1:

            state = "Strong Move"

        elif movement > 0:

            state = "Positive"

        elif movement < -1:

            state = "Strong Drop"

        elif movement < 0:

            state = "Negative"

        else:

            state = "Flat"


        watch_data.append(

            {

                "Asset": name,

                "Price": round(

                    data["price"],

                    4

                ),

                "Change": round(

                    movement,

                    2

                ),

                "State": state

            }

        )

    return pd.DataFrame(

        watch_data

    )


# ==========================================================
# MARKET WATCH DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "👀 Market Watch"

    )

    watch_df = market_watch()

    st.dataframe(

        watch_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# DAILY MARKET SCORE
# ==========================================================

def daily_market_score():

    score = 50

    if gold_data:

        score += (

            gold_data["change"]

            *

            5

        )

    if dxy_data:

        score -= (

            dxy_data["change"]

            *

            5

        )

    if sp500_data:

        score += (

            sp500_data["change"]

            *

            3

        )

    score = max(

        0,

        min(

            score,

            100

        )

    )

    return round(

        score,

        1

    )


# ==========================================================
# SCORE DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.subheader(

        "⭐ Daily Market Score"

    )

    market_score = daily_market_score()

    st.progress(

        market_score / 100

    )

    st.metric(

        "Score",

        f"{market_score}/100"

    )


# ==========================================================
# END OF CHUNK
# ==========================================================

# ==========================================================
# KẾT THÚC ĐOẠN 050
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 051
# ==========================================================

# ==========================================================
# MARKET SENTIMENT HISTORY
# ==========================================================

if "sentiment_history" not in st.session_state:

    st.session_state.sentiment_history = []


def save_sentiment_history():

    sentiment, details = calculate_market_sentiment()

    record = {

        "Time": current_time(),

        "Sentiment": sentiment,

        "Details": ", ".join(

            details

        )

    }

    st.session_state.sentiment_history.append(

        record

    )

    if len(

        st.session_state.sentiment_history

    ) > 200:

        st.session_state.sentiment_history.pop(

            0

        )


save_sentiment_history()


# ==========================================================
# SENTIMENT HISTORY DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🧠 Sentiment History"

    )

    sentiment_df = pd.DataFrame(

        st.session_state.sentiment_history

    )

    if not sentiment_df.empty:

        st.dataframe(

            sentiment_df.tail(

                20

            ),

            use_container_width=True,

            hide_index=True

        )


# ==========================================================
# GOLD MARKET PROFILE
# ==========================================================

def gold_market_profile():

    profile = {

        "Trend": "Unknown",

        "Momentum": "Unknown",

        "Risk": "Unknown"

    }

    trend = analyze_gold_trend()

    if trend:

        profile["Trend"] = trend["trend"]

    volatility = calculate_volatility()

    if volatility:

        if volatility["latest"] > volatility["average"]:

            profile["Risk"] = "High"

        else:

            profile["Risk"] = "Normal"


    rsi = calculate_rsi()

    if rsi:

        profile["Momentum"] = rsi["signal"]


    return profile


# ==========================================================
# GOLD PROFILE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🥇 Gold Market Profile"

    )

    profile = gold_market_profile()

    profile_df = pd.DataFrame(

        {

            "Metric":

            profile.keys(),

            "Value":

            profile.values()

        }

    )

    st.dataframe(

        profile_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# KẾT THÚC ĐOẠN 051
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 052
# ==========================================================

# ==========================================================
# MARKET COMPARISON ENGINE
# ==========================================================

def compare_markets():

    comparison = []

    markets = {

        "Gold": gold_data,

        "DXY": dxy_data,

        "S&P500": sp500_data,

        "NASDAQ": nasdaq_data

    }

    for name, data in markets.items():

        if data is None:

            continue

        strength = 50

        if data["change"] > 0:

            strength += data["change"] * 8

        else:

            strength -= abs(

                data["change"]

            ) * 8


        strength = max(

            0,

            min(

                strength,

                100

            )

        )

        comparison.append(

            {

                "Market": name,

                "Price": round(

                    data["price"],

                    2

                ),

                "Strength": round(

                    strength,

                    1

                )

            }

        )

    return pd.DataFrame(

        comparison

    )


# ==========================================================
# COMPARISON DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "⚖ Market Comparison"

    )

    comparison_df = compare_markets()

    st.dataframe(

        comparison_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# GOLD ENTRY ZONE ANALYZER
# ==========================================================

def calculate_entry_zone():

    sr = calculate_support_resistance()

    if sr is None:

        return None

    support = sr["support"]

    resistance = sr["resistance"]

    current = sr["price"]

    buy_zone = (

        support

        +

        (

            resistance

            -

            support

        )

        *

        0.35

    )

    sell_zone = (

        support

        +

        (

            resistance

            -

            support

        )

        *

        0.65

    )

    return {

        "Current":

            current,

        "Buy Zone":

            buy_zone,

        "Sell Zone":

            sell_zone

    }


# ==========================================================
# ENTRY ZONE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🎯 Entry Zone"

    )

    entry_zone = calculate_entry_zone()

    if entry_zone:

        entry_df = pd.DataFrame(

            {

                "Zone":

                entry_zone.keys(),

                "Price":

                entry_zone.values()

            }

        )

        st.dataframe(

            entry_df,

            use_container_width=True,

            hide_index=True

        )


# ==========================================================
# KẾT THÚC ĐOẠN 052
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 053
# ==========================================================

# ==========================================================
# MARKET MOMENTUM TRACKER
# ==========================================================

if "momentum_history" not in st.session_state:

    st.session_state.momentum_history = []


def calculate_market_momentum():

    momentum = []

    markets = {

        "Gold": gold_data,

        "DXY": dxy_data,

        "S&P500": sp500_data,

        "NASDAQ": nasdaq_data

    }

    for name, data in markets.items():

        if data is None:

            continue

        value = abs(

            data["change"]

        )

        if value >= 2:

            level = "Extreme"

        elif value >= 1:

            level = "Strong"

        elif value >= 0.5:

            level = "Medium"

        else:

            level = "Weak"


        momentum.append(

            {

                "Market": name,

                "Momentum": level,

                "Value": round(

                    value,

                    2

                )

            }

        )

    return pd.DataFrame(

        momentum

    )


# ==========================================================
# MOMENTUM DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🚀 Market Momentum"

    )

    momentum_df = calculate_market_momentum()

    st.dataframe(

        momentum_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# GOLD MARKET RATING
# ==========================================================

def gold_market_rating():

    rating = 50

    reasons = []

    if gold_data:

        if gold_data["change"] > 0:

            rating += 15

            reasons.append(

                "Gold price increasing"

            )

        else:

            rating -= 15

            reasons.append(

                "Gold price decreasing"

            )

    if dxy_data:

        if dxy_data["change"] < 0:

            rating += 20

            reasons.append(

                "Dollar weakness"

            )

        else:

            rating -= 20

            reasons.append(

                "Dollar strength"

            )

    if rating >= 80:

        status = "Excellent"

    elif rating >= 60:

        status = "Positive"

    elif rating >= 40:

        status = "Neutral"

    else:

        status = "Negative"


    return {

        "rating": rating,

        "status": status,

        "reasons": reasons

    }


# ==========================================================
# GOLD RATING DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "⭐ Gold Rating"

    )

    rating = gold_market_rating()

    st.progress(

        rating["rating"]

        /

        100

    )

    st.metric(

        "Rating",

        f'{rating["rating"]}/100'

    )

    st.info(

        rating["status"]

    )

    for reason in rating["reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# KẾT THÚC ĐOẠN 053
# ==========================================================
