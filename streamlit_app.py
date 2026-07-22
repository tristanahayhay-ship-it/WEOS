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
