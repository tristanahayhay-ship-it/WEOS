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
