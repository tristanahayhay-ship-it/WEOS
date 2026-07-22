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
# ==========================================================
# WEOS
# ĐOẠN 054
# ==========================================================

# ==========================================================
# MARKET REGIME DETECTOR
# ==========================================================

def detect_market_regime():

    trend_score = 0

    volatility_score = 0

    if gold_data:

        if gold_data["change"] > 0:

            trend_score += 1

        else:

            trend_score -= 1

        if abs(

            gold_data["change"]

        ) > 1:

            volatility_score += 1


    if dxy_data:

        if dxy_data["change"] > 0:

            trend_score -= 1

        else:

            trend_score += 1


        if abs(

            dxy_data["change"]

        ) > 0.5:

            volatility_score += 1


    if volatility_score >= 2:

        volatility = "High"

    else:

        volatility = "Normal"


    if trend_score >= 2:

        regime = "Bull Market"

    elif trend_score <= -2:

        regime = "Bear Market"

    else:

        regime = "Sideway Market"


    return {

        "regime": regime,

        "volatility": volatility,

        "trend_score": trend_score

    }


# ==========================================================
# REGIME DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🌐 Market Regime"

    )

    regime = detect_market_regime()

    col1, col2 = st.columns(

        2

    )

    with col1:

        st.metric(

            "Regime",

            regime["regime"]

        )

    with col2:

        st.metric(

            "Volatility",

            regime["volatility"]

        )


# ==========================================================
# GOLD TRADE CONFIDENCE
# ==========================================================

def gold_trade_confidence():

    confidence = 50

    reasons = []


    if gold_data:

        if gold_data["change"] > 0:

            confidence += 15

            reasons.append(

                "Gold momentum positive"

            )

        else:

            confidence -= 15

            reasons.append(

                "Gold momentum negative"

            )


    if dxy_data:

        if dxy_data["change"] < 0:

            confidence += 20

            reasons.append(

                "USD supports Gold"

            )

        else:

            confidence -= 20

            reasons.append(

                "USD pressures Gold"

            )


    confidence = max(

        0,

        min(

            confidence,

            100

        )

    )


    return {

        "confidence": confidence,

        "reasons": reasons

    }


# ==========================================================
# CONFIDENCE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🎯 Trade Confidence"

    )

    confidence = gold_trade_confidence()

    st.progress(

        confidence["confidence"]

        /

        100

    )

    st.metric(

        "Confidence",

        f'{confidence["confidence"]}%'

    )

    for reason in confidence["reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# KẾT THÚC ĐOẠN 054
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 055
# ==========================================================

# ==========================================================
# MARKET NEWS SENTIMENT ENGINE
# ==========================================================

def analyze_news_sentiment():

    positive_words = [

        "rise",

        "gain",

        "growth",

        "bullish",

        "strong",

        "higher",

        "support"

    ]

    negative_words = [

        "fall",

        "drop",

        "weak",

        "bearish",

        "lower",

        "risk",

        "pressure"

    ]

    positive = 0

    negative = 0

    total = 0


    for article in st.session_state.news:

        text = str(

            article

        ).lower()

        total += 1

        for word in positive_words:

            if word in text:

                positive += 1

        for word in negative_words:

            if word in text:

                negative += 1


    if positive > negative:

        sentiment = "Positive"

    elif negative > positive:

        sentiment = "Negative"

    else:

        sentiment = "Neutral"


    return {

        "positive": positive,

        "negative": negative,

        "total": total,

        "sentiment": sentiment

    }


# ==========================================================
# NEWS SENTIMENT DISPLAY
# ==========================================================

if st.session_state.page == "News":

    st.divider()

    st.subheader(

        "📰 News Sentiment"

    )

    news_sentiment = analyze_news_sentiment()

    col1, col2, col3 = st.columns(

        3

    )

    with col1:

        st.metric(

            "Positive",

            news_sentiment["positive"]

        )

    with col2:

        st.metric(

            "Negative",

            news_sentiment["negative"]

        )

    with col3:

        st.metric(

            "Total",

            news_sentiment["total"]

        )


    st.info(

        news_sentiment["sentiment"]

    )


# ==========================================================
# ECONOMIC IMPACT RATING
# ==========================================================

def economic_rating():

    score = 50

    reasons = []


    if gold_data:

        if gold_data["change"] > 0:

            score += 10

            reasons.append(

                "Gold strength"

            )

        else:

            score -= 10

            reasons.append(

                "Gold weakness"

            )


    if dxy_data:

        if dxy_data["change"] < 0:

            score += 20

            reasons.append(

                "USD weakness"

            )

        else:

            score -= 20

            reasons.append(

                "USD strength"

            )


    score = max(

        0,

        min(

            score,

            100

        )

    )


    return {

        "score": score,

        "reasons": reasons

    }


# ==========================================================
# ECONOMIC RATING DISPLAY
# ==========================================================

if st.session_state.page == "Macro":

    st.divider()

    st.subheader(

        "📊 Economic Rating"

    )

    economic = economic_rating()

    st.progress(

        economic["score"]

        /

        100

    )

    st.metric(

        "Macro Score",

        f'{economic["score"]}/100'

    )

    for reason in economic["reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# KẾT THÚC ĐOẠN 055
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 056
# ==========================================================

# ==========================================================
# MARKET ALERT PRIORITY ENGINE
# ==========================================================

def calculate_alert_priority():

    priority = []

    markets = {

        "Gold": gold_data,

        "DXY": dxy_data,

        "S&P500": sp500_data,

        "NASDAQ": nasdaq_data

    }

    for name, data in markets.items():

        if data is None:

            continue

        change = abs(

            data["change"]

        )

        if change >= 3:

            level = "Critical"

        elif change >= 1.5:

            level = "High"

        elif change >= 0.5:

            level = "Medium"

        else:

            level = "Low"


        priority.append(

            {

                "Market": name,

                "Movement": round(

                    data["change"],

                    2

                ),

                "Priority": level

            }

        )


    return pd.DataFrame(

        priority

    )


# ==========================================================
# ALERT PRIORITY DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🚨 Alert Priority"

    )

    priority_df = calculate_alert_priority()

    st.dataframe(

        priority_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# GOLD ENTRY QUALITY SCORE
# ==========================================================

def calculate_entry_quality():

    score = 50

    reasons = []


    trend = analyze_gold_trend()

    rsi = calculate_rsi()

    macd = calculate_macd()


    if trend:

        if "Uptrend" in trend["trend"]:

            score += 15

            reasons.append(

                "Trend supports buyers"

            )

        elif "Downtrend" in trend["trend"]:

            score -= 15

            reasons.append(

                "Trend supports sellers"

            )


    if rsi:

        if rsi["signal"] == "Oversold":

            score += 10

            reasons.append(

                "RSI oversold"

            )

        elif rsi["signal"] == "Overbought":

            score -= 10

            reasons.append(

                "RSI overbought"

            )


    if macd:

        if macd["histogram"] > 0:

            score += 10

            reasons.append(

                "MACD positive"

            )

        else:

            score -= 10

            reasons.append(

                "MACD negative"

            )


    score = max(

        0,

        min(

            score,

            100

        )

    )


    return {

        "score": score,

        "reasons": reasons

    }


# ==========================================================
# ENTRY QUALITY DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🎯 Entry Quality"

    )


    quality = calculate_entry_quality()


    st.progress(

        quality["score"]

        /

        100

    )


    st.metric(

        "Quality Score",

        f'{quality["score"]}/100'

    )


    for reason in quality["reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# KẾT THÚC ĐOẠN 056
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 057
# ==========================================================

# ==========================================================
# GOLD MARKET STRUCTURE ANALYZER
# ==========================================================

def analyze_market_structure():

    history = load_price_history(

        MARKET_SYMBOLS["Gold"],

        period="3mo"

    )

    if history.empty:

        return None


    recent_high = float(

        history["High"].tail(

            20

        ).max()

    )


    recent_low = float(

        history["Low"].tail(

            20

        ).min()

    )


    current_price = float(

        history["Close"].iloc[-1]

    )


    if current_price > recent_high * 0.98:

        structure = "Near Resistance"

    elif current_price < recent_low * 1.02:

        structure = "Near Support"

    else:

        structure = "Middle Range"


    return {

        "high": recent_high,

        "low": recent_low,

        "price": current_price,

        "structure": structure

    }


# ==========================================================
# STRUCTURE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🏗 Market Structure"

    )


    structure = analyze_market_structure()


    if structure:

        structure_df = pd.DataFrame(

            {

                "Level":

                [

                    "Resistance",

                    "Current",

                    "Support"

                ],

                "Price":

                [

                    structure["high"],

                    structure["price"],

                    structure["low"]

                ]

            }

        )


        st.dataframe(

            structure_df,

            use_container_width=True,

            hide_index=True

        )


        st.info(

            structure["structure"]

        )


# ==========================================================
# SMART ENTRY ASSISTANT
# ==========================================================

def smart_entry_assistant():

    result = {

        "Action": "WAIT",

        "Reason": []

    }


    confidence = calculate_entry_quality()


    if confidence["score"] >= 75:

        result["Action"] = "HIGH QUALITY SETUP"

    elif confidence["score"] >= 60:

        result["Action"] = "POSSIBLE SETUP"

    else:

        result["Action"] = "NO TRADE"


    result["Reason"] = confidence["reasons"]


    return result


# ==========================================================
# SMART ENTRY DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🤖 Smart Entry Assistant"

    )


    assistant = smart_entry_assistant()


    st.metric(

        "Recommendation",

        assistant["Action"]

    )


    for item in assistant["Reason"]:

        st.write(

            "•",

            item

        )


# ==========================================================
# KẾT THÚC ĐOẠN 057
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 058
# ==========================================================

# ==========================================================
# MARKET PHASE DETECTOR
# ==========================================================

def detect_market_phase():

    phase_score = 0

    factors = []


    trend = analyze_gold_trend()

    volatility = calculate_volatility()

    momentum = calculate_market_momentum()


    if trend:

        if "Uptrend" in trend["trend"]:

            phase_score += 1

            factors.append(

                "Price trend is positive"

            )

        elif "Downtrend" in trend["trend"]:

            phase_score -= 1

            factors.append(

                "Price trend is negative"

            )


    if volatility:

        if volatility["latest"] > volatility["average"]:

            factors.append(

                "High volatility environment"

            )

        else:

            factors.append(

                "Normal volatility environment"

            )


    if momentum is not None:

        if not momentum.empty:

            gold_row = momentum[

                momentum["Market"]

                ==

                "Gold"

            ]

            if not gold_row.empty:

                value = float(

                    gold_row["Value"].iloc[0]

                )

                if value > 1:

                    phase_score += 1

                    factors.append(

                        "Strong momentum"

                    )


    if phase_score >= 2:

        phase = "Expansion"

    elif phase_score <= -1:

        phase = "Contraction"

    else:

        phase = "Accumulation"


    return {

        "phase": phase,

        "score": phase_score,

        "factors": factors

    }


# ==========================================================
# MARKET PHASE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🌊 Market Phase"

    )


    phase = detect_market_phase()


    st.metric(

        "Current Phase",

        phase["phase"]

    )


    for factor in phase["factors"]:

        st.write(

            "•",

            factor

        )


# ==========================================================
# SUPPORT ZONE QUALITY
# ==========================================================

def support_zone_quality():

    sr = calculate_support_resistance()

    if sr is None:

        return None


    distance = abs(

        sr["price"]

        -

        sr["support"]

    )


    if distance < 20:

        quality = "Strong Support Zone"

    elif distance < 50:

        quality = "Medium Support Zone"

    else:

        quality = "Weak Support Zone"


    return {

        "distance": distance,

        "quality": quality

    }


# ==========================================================
# SUPPORT DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🟢 Support Analysis"

    )


    support = support_zone_quality()


    if support:

        st.metric(

            "Distance To Support",

            format_price(

                support["distance"]

            )

        )


        st.info(

            support["quality"]

        )


# ==========================================================
# KẾT THÚC ĐOẠN 058
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 059
# ==========================================================

# ==========================================================
# RESISTANCE ZONE QUALITY
# ==========================================================

def resistance_zone_quality():

    sr = calculate_support_resistance()

    if sr is None:

        return None


    distance = abs(

        sr["resistance"]

        -

        sr["price"]

    )


    if distance < 20:

        quality = "Strong Resistance Zone"

    elif distance < 50:

        quality = "Medium Resistance Zone"

    else:

        quality = "Weak Resistance Zone"


    return {

        "distance": distance,

        "quality": quality

    }


# ==========================================================
# RESISTANCE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🔴 Resistance Analysis"

    )


    resistance = resistance_zone_quality()


    if resistance:

        st.metric(

            "Distance To Resistance",

            format_price(

                resistance["distance"]

            )

        )


        st.info(

            resistance["quality"]

        )


# ==========================================================
# GOLD POSITION BIAS
# ==========================================================

def calculate_position_bias():

    buy_score = 0

    sell_score = 0

    reasons = []


    if gold_data:

        if gold_data["change"] > 0:

            buy_score += 1

            reasons.append(

                "Gold daily movement positive"

            )

        else:

            sell_score += 1

            reasons.append(

                "Gold daily movement negative"

            )


    if dxy_data:

        if dxy_data["change"] < 0:

            buy_score += 1

            reasons.append(

                "Dollar weakness"

            )

        else:

            sell_score += 1

            reasons.append(

                "Dollar strength"

            )


    if buy_score > sell_score:

        bias = "BUY BIAS"

    elif sell_score > buy_score:

        bias = "SELL BIAS"

    else:

        bias = "NEUTRAL"


    return {

        "buy": buy_score,

        "sell": sell_score,

        "bias": bias,

        "reasons": reasons

    }


# ==========================================================
# POSITION BIAS DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "⚖ Position Bias"

    )


    bias = calculate_position_bias()


    st.metric(

        "Current Bias",

        bias["bias"]

    )


    col1, col2 = st.columns(

        2

    )


    with col1:

        st.metric(

            "Buy Score",

            bias["buy"]

        )


    with col2:

        st.metric(

            "Sell Score",

            bias["sell"]

        )


    for reason in bias["reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# KẾT THÚC ĐOẠN 059
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 060
# ==========================================================

# ==========================================================
# TRADE DECISION MATRIX
# ==========================================================

def trade_decision_matrix():

    factors = {

        "Trend":

        0,

        "Momentum":

        0,

        "USD":

        0,

        "Volatility":

        0

    }


    trend = analyze_gold_trend()

    if trend:

        if "Uptrend" in trend["trend"]:

            factors["Trend"] = 1

        elif "Downtrend" in trend["trend"]:

            factors["Trend"] = -1


    momentum = calculate_market_momentum()

    if momentum is not None:

        if not momentum.empty:

            gold = momentum[

                momentum["Market"]

                ==

                "Gold"

            ]

            if not gold.empty:

                value = float(

                    gold["Value"].iloc[0]

                )

                if value > 1:

                    factors["Momentum"] = 1

                elif value < 0.5:

                    factors["Momentum"] = -1


    if dxy_data:

        if dxy_data["change"] < 0:

            factors["USD"] = 1

        else:

            factors["USD"] = -1


    volatility = calculate_volatility()

    if volatility:

        if volatility["latest"] < volatility["average"]:

            factors["Volatility"] = 1

        else:

            factors["Volatility"] = -1


    total = sum(

        factors.values()

    )


    if total >= 3:

        decision = "STRONG BUY"

    elif total >= 1:

        decision = "BUY"

    elif total <= -3:

        decision = "STRONG SELL"

    elif total <= -1:

        decision = "SELL"

    else:

        decision = "WAIT"


    return {

        "decision": decision,

        "score": total,

        "factors": factors

    }


# ==========================================================
# DECISION MATRIX DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🧩 Trade Decision Matrix"

    )


    matrix = trade_decision_matrix()


    st.metric(

        "Final Decision",

        matrix["decision"]

    )


    st.metric(

        "Score",

        matrix["score"]

    )


    matrix_df = pd.DataFrame(

        {

            "Factor":

            matrix["factors"].keys(),

            "Value":

            matrix["factors"].values()

        }

    )


    st.dataframe(

        matrix_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# TRADE WARNING SYSTEM
# ==========================================================

def trade_warning():

    warnings = []


    if calculate_drawdown() > 10:

        warnings.append(

            "High drawdown detected"

        )


    if not check_daily_loss():

        warnings.append(

            "Daily loss limit reached"

        )


    if len(

        st.session_state.psychology_notes

    ) > 0:

        last = st.session_state.psychology_notes[-1]

        if last["Emotion"] in [

            "Fear",

            "Greed",

            "Angry",

            "Stress"

        ]:

            warnings.append(

                "Emotional trading risk"

            )


    return warnings


# ==========================================================
# WARNING DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    warnings = trade_warning()


    if len(warnings) > 0:

        st.divider()

        st.subheader(

            "⚠ Trading Warnings"

        )


        for warning in warnings:

            st.warning(

                warning

            )


# ==========================================================
# KẾT THÚC ĐOẠN 060
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 061
# ==========================================================

# ==========================================================
# MARKET OPENING ANALYZER
# ==========================================================

def analyze_market_opening():

    utc_hour = datetime.utcnow().hour

    if 0 <= utc_hour < 8:

        session = "Asian Session"

        liquidity = "Medium"

    elif 8 <= utc_hour < 16:

        session = "London Session"

        liquidity = "High"

    elif 16 <= utc_hour < 22:

        session = "New York Session"

        liquidity = "Very High"

    else:

        session = "Market Transition"

        liquidity = "Low"


    return {

        "session": session,

        "liquidity": liquidity

    }


# ==========================================================
# OPENING DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🌅 Market Opening"

    )


    opening = analyze_market_opening()


    col1, col2 = st.columns(

        2

    )


    with col1:

        st.metric(

            "Session",

            opening["session"]

        )


    with col2:

        st.metric(

            "Liquidity",

            opening["liquidity"]

        )


# ==========================================================
# GOLD VOLATILITY WARNING
# ==========================================================

def gold_volatility_warning():

    warnings = []

    volatility = calculate_volatility()


    if volatility:

        current = volatility["latest"]

        average = volatility["average"]


        if current > average * 2:

            warnings.append(

                "Gold volatility extremely high"

            )

        elif current > average:

            warnings.append(

                "Gold volatility above average"

            )


    return warnings


# ==========================================================
# VOLATILITY WARNING DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    volatility_warning = gold_volatility_warning()


    if len(

        volatility_warning

    ) > 0:

        st.divider()

        st.subheader(

            "⚡ Volatility Alert"

        )


        for warning in volatility_warning:

            st.warning(

                warning

            )


# ==========================================================
# MARKET CONFIRMATION ENGINE
# ==========================================================

def market_confirmation():

    confirmations = []

    confirmations_count = 0


    trend = analyze_gold_trend()

    if trend:

        if "Uptrend" in trend["trend"]:

            confirmations.append(

                "Trend confirms BUY"

            )

            confirmations_count += 1


        elif "Downtrend" in trend["trend"]:

            confirmations.append(

                "Trend confirms SELL"

            )

            confirmations_count += 1


    rsi = calculate_rsi()

    if rsi:

        if rsi["signal"] != "Neutral":

            confirmations.append(

                f'RSI {rsi["signal"]}'

            )

            confirmations_count += 1


    macd = calculate_macd()

    if macd:

        if macd["histogram"] > 0:

            confirmations.append(

                "MACD bullish"

            )

            confirmations_count += 1

        else:

            confirmations.append(

                "MACD bearish"

            )

            confirmations_count += 1


    return {

        "count": confirmations_count,

        "details": confirmations

    }


# ==========================================================
# CONFIRMATION DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "✅ Market Confirmation"

    )


    confirmation = market_confirmation()


    st.metric(

        "Confirmations",

        confirmation["count"]

    )


    for item in confirmation["details"]:

        st.write(

            "•",

            item

        )


# ==========================================================
# KẾT THÚC ĐOẠN 061
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 062
# ==========================================================

# ==========================================================
# MARKET SCENARIO GENERATOR
# ==========================================================

def generate_market_scenario():

    scenario = {

        "Scenario": "Neutral",

        "Probability": 50,

        "Action": "Wait"

    }


    decision = trade_decision_matrix()


    if decision["decision"] in [

        "STRONG BUY",

        "BUY"

    ]:

        scenario["Scenario"] = (

            "Bullish Gold Scenario"

        )

        scenario["Probability"] = 70

        scenario["Action"] = (

            "Look for Buy opportunities"

        )


    elif decision["decision"] in [

        "STRONG SELL",

        "SELL"

    ]:

        scenario["Scenario"] = (

            "Bearish Gold Scenario"

        )

        scenario["Probability"] = 70

        scenario["Action"] = (

            "Look for Sell opportunities"

        )


    return scenario


# ==========================================================
# SCENARIO DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🔮 Market Scenario"

    )


    scenario = generate_market_scenario()


    col1, col2 = st.columns(

        2

    )


    with col1:

        st.metric(

            "Scenario",

            scenario["Scenario"]

        )


    with col2:

        st.metric(

            "Probability",

            f'{scenario["Probability"]}%'

        )


    st.info(

        scenario["Action"]

    )


# ==========================================================
# PRICE DISTANCE CALCULATOR
# ==========================================================

def calculate_price_distance():

    sr = calculate_support_resistance()


    if sr is None:

        return None


    current = sr["price"]

    support = sr["support"]

    resistance = sr["resistance"]


    return {

        "Support Distance":

            current - support,

        "Resistance Distance":

            resistance - current

    }


# ==========================================================
# DISTANCE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "📏 Price Distance"

    )


    distance = calculate_price_distance()


    if distance:

        distance_df = pd.DataFrame(

            {

                "Level":

                [

                    "Support",

                    "Resistance"

                ],

                "Distance":

                [

                    distance["Support Distance"],

                    distance["Resistance Distance"]

                ]

            }

        )


        st.dataframe(

            distance_df,

            use_container_width=True,

            hide_index=True

        )


# ==========================================================
# MARKET BALANCE INDEX
# ==========================================================

def calculate_market_balance():

    balance = 50


    if gold_data:

        if gold_data["change"] > 0:

            balance += 10

        else:

            balance -= 10


    if dxy_data:

        if dxy_data["change"] < 0:

            balance += 15

        else:

            balance -= 15


    balance = max(

        0,

        min(

            balance,

            100

        )

    )


    return balance


# ==========================================================
# BALANCE DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "⚖ Market Balance"

    )


    balance = calculate_market_balance()


    st.progress(

        balance / 100

    )


    st.metric(

        "Balance Index",

        f"{balance}/100"

    )


# ==========================================================
# KẾT THÚC ĐOẠN 062
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 063
# ==========================================================

# ==========================================================
# MARKET OPPORTUNITY SCANNER
# ==========================================================

def scan_market_opportunity():

    opportunities = []

    decision = trade_decision_matrix()

    confidence = gold_trade_confidence()

    entry_quality = calculate_entry_quality()


    if confidence["confidence"] >= 70:

        opportunities.append(

            {

                "Type": "Confidence",

                "Status": "High",

                "Value":

                confidence["confidence"]

            }

        )


    if entry_quality["score"] >= 70:

        opportunities.append(

            {

                "Type": "Entry Quality",

                "Status": "Good",

                "Value":

                entry_quality["score"]

            }

        )


    opportunities.append(

        {

            "Type": "Decision",

            "Status":

            decision["decision"],

            "Value":

            decision["score"]

        }

    )


    return pd.DataFrame(

        opportunities

    )


# ==========================================================
# OPPORTUNITY DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🎯 Opportunity Scanner"

    )


    opportunity_df = scan_market_opportunity()


    st.dataframe(

        opportunity_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# TRADE EXECUTION CHECK
# ==========================================================

def trade_execution_check():

    checklist = {

        "Signal":

        False,

        "Risk":

        False,

        "Emotion":

        False,

        "Confirmation":

        False

    }


    decision = trade_decision_matrix()


    if decision["decision"] != "WAIT":

        checklist["Signal"] = True


    if check_daily_loss():

        checklist["Risk"] = True


    if len(

        st.session_state.psychology_notes

    ) == 0:

        checklist["Emotion"] = True


    confirmation = market_confirmation()


    if confirmation["count"] >= 2:

        checklist["Confirmation"] = True


    return checklist


# ==========================================================
# EXECUTION DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "⚔ Trade Execution Check"

    )


    execution = trade_execution_check()


    completed = 0


    for name, status in execution.items():

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

        len(execution)

    )


# ==========================================================
# MARKET CONDITION MEMORY
# ==========================================================

if "condition_history" not in st.session_state:

    st.session_state.condition_history = []


def save_condition():

    condition = {

        "Time":

        current_time(),

        "Condition":

        market_condition()

    }


    st.session_state.condition_history.append(

        condition

    )


save_condition()


# ==========================================================
# CONDITION HISTORY DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.subheader(

        "🗂 Condition History"

    )


    condition_df = pd.DataFrame(

        st.session_state.condition_history[-20:]

    )


    st.dataframe(

        condition_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# KẾT THÚC ĐOẠN 063
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 064
# ==========================================================

# ==========================================================
# MARKET MEMORY ENGINE
# ==========================================================

if "market_memory" not in st.session_state:

    st.session_state.market_memory = []


def save_market_memory():

    memory = {

        "Time":

        current_time(),

        "Gold":

        gold_data["change"]

        if gold_data else None,

        "DXY":

        dxy_data["change"]

        if dxy_data else None,

        "Condition":

        market_condition()

    }


    st.session_state.market_memory.append(

        memory

    )


    if len(

        st.session_state.market_memory

    ) > 300:

        st.session_state.market_memory.pop(

            0

        )


save_market_memory()


# ==========================================================
# MEMORY DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🧠 Market Memory"

    )


    memory_df = pd.DataFrame(

        st.session_state.market_memory[-20:]

    )


    st.dataframe(

        memory_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# GOLD MOMENTUM SCORE
# ==========================================================

def calculate_gold_momentum_score():

    score = 50

    factors = []


    if gold_data:

        change = gold_data["change"]

        if change > 0:

            score += 15

            factors.append(

                "Price momentum positive"

            )

        else:

            score -= 15

            factors.append(

                "Price momentum negative"

            )


    rsi = calculate_rsi()


    if rsi:

        if rsi["rsi"] < 30:

            score += 10

            factors.append(

                "RSI oversold"

            )

        elif rsi["rsi"] > 70:

            score -= 10

            factors.append(

                "RSI overbought"

            )


    score = max(

        0,

        min(

            score,

            100

        )

    )


    return {

        "score": score,

        "factors": factors

    }


# ==========================================================
# MOMENTUM DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🚀 Gold Momentum Score"

    )


    momentum_score = calculate_gold_momentum_score()


    st.progress(

        momentum_score["score"]

        /

        100

    )


    st.metric(

        "Momentum",

        f'{momentum_score["score"]}/100'

    )


    for factor in momentum_score["factors"]:

        st.write(

            "•",

            factor

        )


# ==========================================================
# MARKET DIRECTION ENGINE
# ==========================================================

def market_direction():

    score = 0


    if gold_data:

        score += 1 if gold_data["change"] > 0 else -1


    if dxy_data:

        score += 1 if dxy_data["change"] < 0 else -1


    if sp500_data:

        score += 1 if sp500_data["change"] > 0 else -1


    if score >= 2:

        return "UP"

    elif score <= -2:

        return "DOWN"

    else:

        return "SIDEWAY"


# ==========================================================
# DIRECTION DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🧭 Market Direction"

    )


    st.metric(

        "Direction",

        market_direction()

    )


# ==========================================================
# KẾT THÚC ĐOẠN 064
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 065
# ==========================================================

# ==========================================================
# MARKET DECISION HISTORY
# ==========================================================

if "decision_history" not in st.session_state:

    st.session_state.decision_history = []


def save_decision_history():

    decision = trade_decision_matrix()

    record = {

        "Time":

        current_time(),

        "Decision":

        decision["decision"],

        "Score":

        decision["score"]

    }

    st.session_state.decision_history.append(

        record

    )


    if len(

        st.session_state.decision_history

    ) > 200:

        st.session_state.decision_history.pop(

            0

        )


save_decision_history()


# ==========================================================
# DECISION HISTORY DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "📚 Decision History"

    )


    decision_df = pd.DataFrame(

        st.session_state.decision_history[-20:]

    )


    st.dataframe(

        decision_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# GOLD TREND REVERSAL DETECTOR
# ==========================================================

def detect_trend_reversal():

    history = load_price_history(

        MARKET_SYMBOLS["Gold"],

        period="3mo"

    )


    if history.empty:

        return None


    close = history["Close"]


    short_ma = close.rolling(

        10

    ).mean()


    long_ma = close.rolling(

        30

    ).mean()


    current_short = float(

        short_ma.iloc[-1]

    )


    current_long = float(

        long_ma.iloc[-1]

    )


    previous_short = float(

        short_ma.iloc[-2]

    )


    previous_long = float(

        long_ma.iloc[-2]

    )


    if (

        previous_short < previous_long

        and

        current_short > current_long

    ):

        signal = "Bullish Reversal"


    elif (

        previous_short > previous_long

        and

        current_short < current_long

    ):

        signal = "Bearish Reversal"


    else:

        signal = "No Reversal"


    return {

        "signal":

        signal,

        "short_ma":

        current_short,

        "long_ma":

        current_long

    }


# ==========================================================
# REVERSAL DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🔄 Trend Reversal Detector"

    )


    reversal = detect_trend_reversal()


    if reversal:

        st.metric(

            "Signal",

            reversal["signal"]

        )


        col1, col2 = st.columns(

            2

        )


        with col1:

            st.metric(

                "MA10",

                format_price(

                    reversal["short_ma"]

                )

            )


        with col2:

            st.metric(

                "MA30",

                format_price(

                    reversal["long_ma"]

                )

            )


# ==========================================================
# GOLD PRICE ACTION ANALYZER
# ==========================================================

def analyze_price_action():

    history = load_price_history(

        MARKET_SYMBOLS["Gold"],

        period="1mo"

    )


    if history.empty:

        return None


    last = history.iloc[-1]


    body = abs(

        last["Close"]

        -

        last["Open"]

    )


    candle_range = (

        last["High"]

        -

        last["Low"]

    )


    if candle_range == 0:

        return "Neutral"


    ratio = body / candle_range


    if ratio > 0.7:

        return "Strong Momentum Candle"

    elif ratio < 0.3:

        return "Indecision Candle"

    else:

        return "Normal Candle"


# ==========================================================
# PRICE ACTION DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🕯 Price Action"

    )


    action = analyze_price_action()


    if action:

        st.info(

            action

        )


# ==========================================================
# KẾT THÚC ĐOẠN 065
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 066
# ==========================================================

# ==========================================================
# CANDLE PATTERN DETECTOR
# ==========================================================

def detect_candle_pattern():

    history = load_price_history(

        MARKET_SYMBOLS["Gold"],

        period="3mo"

    )


    if history.empty:

        return None


    last = history.iloc[-1]

    previous = history.iloc[-2]


    current_body = abs(

        last["Close"]

        -

        last["Open"]

    )


    previous_body = abs(

        previous["Close"]

        -

        previous["Open"]

    )


    if (

        last["Close"] > last["Open"]

        and

        previous["Close"] < previous["Open"]

        and

        current_body > previous_body

    ):

        pattern = "Bullish Engulfing"


    elif (

        last["Close"] < last["Open"]

        and

        previous["Close"] > previous["Open"]

        and

        current_body > previous_body

    ):

        pattern = "Bearish Engulfing"


    elif current_body < (

        last["High"]

        -

        last["Low"]

    ) * 0.2:

        pattern = "Doji"


    else:

        pattern = "Normal"


    return pattern


# ==========================================================
# CANDLE PATTERN DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🕯 Candle Pattern"

    )


    candle_pattern = detect_candle_pattern()


    if candle_pattern:

        st.metric(

            "Pattern",

            candle_pattern

        )


# ==========================================================
# GOLD BUY SELL PRESSURE
# ==========================================================

def calculate_buy_sell_pressure():

    history = load_price_history(

        MARKET_SYMBOLS["Gold"],

        period="1mo"

    )


    if history.empty:

        return None


    buyers = 0

    sellers = 0


    for _, candle in history.iterrows():

        if candle["Close"] > candle["Open"]:

            buyers += 1

        elif candle["Close"] < candle["Open"]:

            sellers += 1


    total = buyers + sellers


    if total == 0:

        return None


    buy_percent = (

        buyers

        /

        total

    ) * 100


    sell_percent = (

        sellers

        /

        total

    ) * 100


    return {

        "buy":

        buy_percent,

        "sell":

        sell_percent

    }


# ==========================================================
# PRESSURE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "⚔ Buy / Sell Pressure"

    )


    pressure = calculate_buy_sell_pressure()


    if pressure:

        col1, col2 = st.columns(

            2

        )


        with col1:

            st.metric(

                "Buy Pressure",

                f'{pressure["buy"]:.2f}%'

            )


        with col2:

            st.metric(

                "Sell Pressure",

                f'{pressure["sell"]:.2f}%'

            )


# ==========================================================
# LIQUIDITY ANALYZER
# ==========================================================

def analyze_liquidity():

    history = load_price_history(

        MARKET_SYMBOLS["Gold"],

        period="3mo"

    )


    if history.empty:

        return None


    volume = history["Volume"]


    average = float(

        volume.mean()

    )


    latest = float(

        volume.iloc[-1]

    )


    ratio = latest / average


    if ratio >= 1.5:

        status = "High Liquidity"

    elif ratio >= 1:

        status = "Normal Liquidity"

    else:

        status = "Low Liquidity"


    return {

        "ratio":

        ratio,

        "status":

        status

    }


# ==========================================================
# LIQUIDITY DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "💧 Liquidity Analysis"

    )


    liquidity = analyze_liquidity()


    if liquidity:

        st.metric(

            "Liquidity",

            liquidity["status"]

        )


# ==========================================================
# KẾT THÚC ĐOẠN 066
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 067
# ==========================================================

# ==========================================================
# GOLD MARKET PRESSURE INDEX
# ==========================================================

def calculate_market_pressure_index():

    score = 50

    factors = []


    pressure = calculate_buy_sell_pressure()


    if pressure:

        if pressure["buy"] > pressure["sell"]:

            score += 15

            factors.append(

                "Buying pressure stronger"

            )

        else:

            score -= 15

            factors.append(

                "Selling pressure stronger"

            )


    candle = detect_candle_pattern()


    if candle:

        if candle == "Bullish Engulfing":

            score += 10

            factors.append(

                "Bullish candle pattern"

            )

        elif candle == "Bearish Engulfing":

            score -= 10

            factors.append(

                "Bearish candle pattern"

            )


    score = max(

        0,

        min(

            score,

            100

        )

    )


    return {

        "score":

        score,

        "factors":

        factors

    }


# ==========================================================
# PRESSURE INDEX DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🔥 Market Pressure Index"

    )


    pressure_index = calculate_market_pressure_index()


    st.progress(

        pressure_index["score"]

        /

        100

    )


    st.metric(

        "Pressure Score",

        f'{pressure_index["score"]}/100'

    )


    for factor in pressure_index["factors"]:

        st.write(

            "•",

            factor

        )


# ==========================================================
# GOLD TREND ALIGNMENT
# ==========================================================

def calculate_trend_alignment():

    alignment = 0

    details = []


    ema = calculate_ema_signal()


    macd = calculate_macd()


    rsi = calculate_rsi()


    if ema:

        if "Bullish" in ema["signal"]:

            alignment += 1

            details.append(

                "EMA bullish alignment"

            )

        elif "Bearish" in ema["signal"]:

            alignment -= 1

            details.append(

                "EMA bearish alignment"

            )


    if macd:

        if macd["histogram"] > 0:

            alignment += 1

            details.append(

                "MACD positive"

            )

        else:

            alignment -= 1

            details.append(

                "MACD negative"

            )


    if rsi:

        if 40 < rsi["rsi"] < 70:

            alignment += 1

            details.append(

                "RSI healthy zone"

            )


    if alignment >= 2:

        result = "Aligned Bullish"

    elif alignment <= -2:

        result = "Aligned Bearish"

    else:

        result = "Mixed"


    return {

        "result":

        result,

        "score":

        alignment,

        "details":

        details

    }


# ==========================================================
# ALIGNMENT DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🔗 Trend Alignment"

    )


    alignment = calculate_trend_alignment()


    st.metric(

        "Alignment",

        alignment["result"]

    )


    for detail in alignment["details"]:

        st.write(

            "•",

            detail

        )


# ==========================================================
# KẾT THÚC ĐOẠN 067
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 068
# ==========================================================

# ==========================================================
# GOLD MARKET SCORECARD
# ==========================================================

def create_gold_scorecard():

    score = 0

    maximum = 10

    items = []


    trend = analyze_gold_trend()

    if trend:

        if "Uptrend" in trend["trend"]:

            score += 1

            items.append(

                {

                    "Factor":

                    "Trend",

                    "Status":

                    "Bullish"

                }

            )

        elif "Downtrend" in trend["trend"]:

            score -= 1

            items.append(

                {

                    "Factor":

                    "Trend",

                    "Status":

                    "Bearish"

                }

            )


    momentum = calculate_gold_momentum_score()


    if momentum:

        if momentum["score"] >= 60:

            score += 1

            items.append(

                {

                    "Factor":

                    "Momentum",

                    "Status":

                    "Positive"

                }

            )

        else:

            score -= 1

            items.append(

                {

                    "Factor":

                    "Momentum",

                    "Status":

                    "Weak"

                }

            )


    pressure = calculate_market_pressure_index()


    if pressure:

        if pressure["score"] >= 60:

            score += 1

            items.append(

                {

                    "Factor":

                    "Pressure",

                    "Status":

                    "Buying"

                }

            )

        else:

            score -= 1

            items.append(

                {

                    "Factor":

                    "Pressure",

                    "Status":

                    "Selling"

                }

            )


    confidence = gold_trade_confidence()


    if confidence["confidence"] >= 70:

        score += 1

        items.append(

            {

                "Factor":

                "Confidence",

                "Status":

                "High"

            }

        )


    final_score = int(

        (

            (

                score + maximum

            )

            /

            (

                maximum * 2

            )

        )

        *

        100

    )


    return {

        "score":

        final_score,

        "items":

        items

    }


# ==========================================================
# SCORECARD DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🏆 Gold Scorecard"

    )


    scorecard = create_gold_scorecard()


    st.progress(

        scorecard["score"]

        /

        100

    )


    st.metric(

        "Gold Score",

        f'{scorecard["score"]}/100'

    )


    score_df = pd.DataFrame(

        scorecard["items"]

    )


    if not score_df.empty:

        st.dataframe(

            score_df,

            use_container_width=True,

            hide_index=True

        )


# ==========================================================
# MARKET RISK ALERT LEVEL
# ==========================================================

def market_risk_alert_level():

    risk = calculate_market_risk()


    score = risk["score"]


    if score >= 80:

        level = "DANGER"

    elif score >= 60:

        level = "WARNING"

    else:

        level = "SAFE"


    return {

        "level":

        level,

        "score":

        score

    }


# ==========================================================
# RISK ALERT DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🚨 Risk Alert"

    )


    risk_alert = market_risk_alert_level()


    st.metric(

        "Risk Level",

        risk_alert["level"]

    )


    st.progress(

        risk_alert["score"]

        /

        100

    )


# ==========================================================
# KẾT THÚC ĐOẠN 068
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 069
# ==========================================================

# ==========================================================
# MARKET REGIME HISTORY
# ==========================================================

if "regime_history" not in st.session_state:

    st.session_state.regime_history = []


def save_regime_history():

    regime = detect_market_regime()

    record = {

        "Time":

        current_time(),

        "Regime":

        regime["regime"],

        "Volatility":

        regime["volatility"]

    }

    st.session_state.regime_history.append(

        record

    )


    if len(

        st.session_state.regime_history

    ) > 200:

        st.session_state.regime_history.pop(

            0

        )


save_regime_history()


# ==========================================================
# REGIME HISTORY DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🌐 Regime History"

    )


    regime_df = pd.DataFrame(

        st.session_state.regime_history[-20:]

    )


    st.dataframe(

        regime_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# GOLD TRADE SETUP GENERATOR
# ==========================================================

def generate_gold_setup():

    setup = {

        "Direction":

        "WAIT",

        "Entry":

        None,

        "Stop Loss":

        None,

        "Take Profit":

        None

    }


    sr = calculate_support_resistance()


    decision = trade_decision_matrix()


    if sr is None:

        return setup


    if "BUY" in decision["decision"]:

        setup["Direction"] = "BUY"

        setup["Entry"] = sr["support"]

        setup["Stop Loss"] = (

            sr["support"]

            -

            20

        )

        setup["Take Profit"] = (

            sr["resistance"]

        )


    elif "SELL" in decision["decision"]:

        setup["Direction"] = "SELL"

        setup["Entry"] = sr["resistance"]

        setup["Stop Loss"] = (

            sr["resistance"]

            +

            20

        )

        setup["Take Profit"] = (

            sr["support"]

        )


    return setup


# ==========================================================
# SETUP DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "📌 Gold Setup Generator"

    )


    setup = generate_gold_setup()


    setup_df = pd.DataFrame(

        {

            "Parameter":

            setup.keys(),

            "Value":

            setup.values()

        }

    )


    st.dataframe(

        setup_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# MARKET ALERT MESSAGE
# ==========================================================

def generate_market_message():

    direction = market_direction()

    risk = market_risk_alert_level()


    if risk["level"] == "DANGER":

        return (

            "High risk market condition. "

            "Avoid aggressive positions."

        )


    if direction == "UP":

        return (

            "Market momentum favors buyers."

        )


    if direction == "DOWN":

        return (

            "Market momentum favors sellers."

        )


    return (

        "Market is waiting for confirmation."

    )


# ==========================================================
# MESSAGE DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "💬 WEOS Message"

    )


    st.info(

        generate_market_message()

    )


# ==========================================================
# KẾT THÚC ĐOẠN 069
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 070
# ==========================================================

# ==========================================================
# MARKET ACTION PLAN
# ==========================================================

def generate_action_plan():

    plan = []

    direction = market_direction()

    risk = market_risk_alert_level()

    confidence = gold_trade_confidence()


    if risk["level"] == "DANGER":

        plan.append(

            "Reduce position size"

        )

        plan.append(

            "Wait for market stability"

        )


    if direction == "UP":

        plan.append(

            "Monitor buying opportunities"

        )


    elif direction == "DOWN":

        plan.append(

            "Monitor selling opportunities"

        )


    else:

        plan.append(

            "Wait for confirmation"

        )


    if confidence["confidence"] >= 70:

        plan.append(

            "Setup quality is acceptable"

        )


    return plan


# ==========================================================
# ACTION PLAN DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "📝 Action Plan"

    )


    action_plan = generate_action_plan()


    for action in action_plan:

        st.write(

            "•",

            action

        )


# ==========================================================
# GOLD ENTRY CONFIRMATION SCORE
# ==========================================================

def calculate_confirmation_score():

    score = 0

    maximum = 5

    confirmations = []


    trend = analyze_gold_trend()

    if trend:

        if (

            "Uptrend"

            in

            trend["trend"]

        ):

            score += 1

            confirmations.append(

                "Trend bullish"

            )


    macd = calculate_macd()

    if macd:

        if macd["histogram"] > 0:

            score += 1

            confirmations.append(

                "MACD positive"

            )


    rsi = calculate_rsi()

    if rsi:

        if 30 < rsi["rsi"] < 70:

            score += 1

            confirmations.append(

                "RSI normal zone"

            )


    pressure = calculate_market_pressure_index()

    if pressure:

        if pressure["score"] > 50:

            score += 1

            confirmations.append(

                "Buying pressure"

            )


    volatility = calculate_volatility()

    if volatility:

        if volatility["latest"] <= volatility["average"]:

            score += 1

            confirmations.append(

                "Stable volatility"

            )


    percentage = int(

        (

            score

            /

            maximum

        )

        *

        100

    )


    return {

        "score":

        percentage,

        "confirmations":

        confirmations

    }


# ==========================================================
# CONFIRMATION SCORE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "✅ Entry Confirmation Score"

    )


    confirmation_score = calculate_confirmation_score()


    st.progress(

        confirmation_score["score"]

        /

        100

    )


    st.metric(

        "Confirmation",

        f'{confirmation_score["score"]}%'

    )


    for item in confirmation_score["confirmations"]:

        st.write(

            "•",

            item

        )


# ==========================================================
# KẾT THÚC ĐOẠN 070
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 071
# ==========================================================

# ==========================================================
# MARKET DECISION EXPLANATION
# ==========================================================

def explain_market_decision():

    decision = trade_decision_matrix()

    explanation = []


    if decision["score"] > 0:

        explanation.append(

            "Positive market factors detected."

        )

    elif decision["score"] < 0:

        explanation.append(

            "Negative market factors detected."

        )

    else:

        explanation.append(

            "Market signals are balanced."

        )


    for name, value in decision["factors"].items():

        if value > 0:

            explanation.append(

                f"{name}: Supports buyers"

            )

        elif value < 0:

            explanation.append(

                f"{name}: Supports sellers"

            )

        else:

            explanation.append(

                f"{name}: Neutral"

            )


    return explanation


# ==========================================================
# DECISION EXPLANATION DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "💡 Decision Explanation"

    )


    explanations = explain_market_decision()


    for item in explanations:

        st.write(

            "•",

            item

        )


# ==========================================================
# MARKET RISK REWARD MODEL
# ==========================================================

def calculate_dynamic_risk_reward():

    setup = generate_gold_setup()


    if (

        setup["Entry"] is None

        or

        setup["Stop Loss"] is None

        or

        setup["Take Profit"] is None

    ):

        return None


    risk = abs(

        setup["Entry"]

        -

        setup["Stop Loss"]

    )


    reward = abs(

        setup["Take Profit"]

        -

        setup["Entry"]

    )


    if risk == 0:

        ratio = 0

    else:

        ratio = reward / risk


    return {

        "risk":

        risk,

        "reward":

        reward,

        "ratio":

        ratio

    }


# ==========================================================
# DYNAMIC RR DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "⚖ Dynamic Risk Reward"

    )


    dynamic_rr = calculate_dynamic_risk_reward()


    if dynamic_rr:

        col1, col2, col3 = st.columns(

            3

        )


        with col1:

            st.metric(

                "Risk",

                format_price(

                    dynamic_rr["risk"]

                )

            )


        with col2:

            st.metric(

                "Reward",

                format_price(

                    dynamic_rr["reward"]

                )

            )


        with col3:

            st.metric(

                "Ratio",

                f'1:{dynamic_rr["ratio"]:.2f}'

            )


# ==========================================================
# MARKET CONFIDENCE HISTORY
# ==========================================================

if "confidence_history" not in st.session_state:

    st.session_state.confidence_history = []


def save_confidence_history():

    confidence = gold_trade_confidence()


    st.session_state.confidence_history.append(

        {

            "Time":

            current_time(),

            "Confidence":

            confidence["confidence"]

        }

    )


    if len(

        st.session_state.confidence_history

    ) > 100:

        st.session_state.confidence_history.pop(

            0

        )


save_confidence_history()


# ==========================================================
# CONFIDENCE HISTORY DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "📈 Confidence History"

    )


    confidence_df = pd.DataFrame(

        st.session_state.confidence_history[-20:]

    )


    st.dataframe(

        confidence_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# KẾT THÚC ĐOẠN 071
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 072
# ==========================================================

# ==========================================================
# MARKET SIGNAL HISTORY
# ==========================================================

if "signal_history" not in st.session_state:

    st.session_state.signal_history = []


def save_signal_history():

    signal, reasons = generate_gold_signal()

    record = {

        "Time":

        current_time(),

        "Signal":

        signal,

        "Reasons":

        ", ".join(

            reasons

        )

    }


    st.session_state.signal_history.append(

        record

    )


    if len(

        st.session_state.signal_history

    ) > 200:

        st.session_state.signal_history.pop(

            0

        )


save_signal_history()


# ==========================================================
# SIGNAL HISTORY DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "📡 Signal History"

    )


    signal_df = pd.DataFrame(

        st.session_state.signal_history[-20:]

    )


    st.dataframe(

        signal_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# GOLD MARKET PHASE SCORE
# ==========================================================

def calculate_gold_phase_score():

    score = 50

    factors = []


    phase = detect_market_phase()


    if phase:

        if phase["phase"] == "Expansion":

            score += 20

            factors.append(

                "Market expansion phase"

            )


        elif phase["phase"] == "Contraction":

            score -= 20

            factors.append(

                "Market contraction phase"

            )


        else:

            factors.append(

                "Accumulation phase"

            )


    structure = analyze_market_structure()


    if structure:

        if structure["structure"] == "Near Support":

            score += 10

            factors.append(

                "Price near support"

            )


        elif structure["structure"] == "Near Resistance":

            score -= 10

            factors.append(

                "Price near resistance"

            )


    score = max(

        0,

        min(

            score,

            100

        )

    )


    return {

        "score":

        score,

        "factors":

        factors

    }


# ==========================================================
# PHASE SCORE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🌊 Gold Phase Score"

    )


    phase_score = calculate_gold_phase_score()


    st.progress(

        phase_score["score"]

        /

        100

    )


    st.metric(

        "Phase Score",

        f'{phase_score["score"]}/100'

    )


    for factor in phase_score["factors"]:

        st.write(

            "•",

            factor

        )


# ==========================================================
# MARKET STABILITY INDEX
# ==========================================================

def calculate_market_stability():

    stability = 100


    volatility = calculate_volatility()


    if volatility:

        if volatility["latest"] > volatility["average"]:

            stability -= 25


    risk = calculate_market_risk()


    stability -= risk["score"] * 0.3


    stability = max(

        0,

        min(

            stability,

            100

        )

    )


    return round(

        stability,

        1

    )


# ==========================================================
# STABILITY DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🛡 Market Stability"

    )


    stability = calculate_market_stability()


    st.progress(

        stability / 100

    )


    st.metric(

        "Stability",

        f"{stability}/100"

    )


# ==========================================================
# KẾT THÚC ĐOẠN 072
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 073
# ==========================================================

# ==========================================================
# MARKET VOLATILITY HISTORY
# ==========================================================

if "volatility_history" not in st.session_state:

    st.session_state.volatility_history = []


def save_volatility_history():

    volatility = calculate_volatility()

    if volatility:

        record = {

            "Time":

            current_time(),

            "Current Range":

            volatility["latest"],

            "Average Range":

            volatility["average"]

        }

        st.session_state.volatility_history.append(

            record

        )


    if len(

        st.session_state.volatility_history

    ) > 200:

        st.session_state.volatility_history.pop(

            0

        )


save_volatility_history()


# ==========================================================
# VOLATILITY HISTORY DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "📊 Volatility History"

    )


    volatility_df = pd.DataFrame(

        st.session_state.volatility_history[-20:]

    )


    st.dataframe(

        volatility_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# GOLD MARKET OPPORTUNITY LEVEL
# ==========================================================

def calculate_opportunity_level():

    score = 0

    reasons = []


    confidence = gold_trade_confidence()


    if confidence["confidence"] >= 70:

        score += 2

        reasons.append(

            "High confidence"

        )


    confirmation = calculate_confirmation_score()


    if confirmation["score"] >= 60:

        score += 2

        reasons.append(

            "Strong confirmation"

        )


    risk = market_risk_alert_level()


    if risk["level"] == "SAFE":

        score += 1

        reasons.append(

            "Risk acceptable"

        )


    if score >= 4:

        level = "High Opportunity"

    elif score >= 2:

        level = "Medium Opportunity"

    else:

        level = "Low Opportunity"


    return {

        "level":

        level,

        "score":

        score,

        "reasons":

        reasons

    }


# ==========================================================
# OPPORTUNITY LEVEL DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "💎 Opportunity Level"

    )


    opportunity = calculate_opportunity_level()


    st.metric(

        "Level",

        opportunity["level"]

    )


    for reason in opportunity["reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# GOLD MARKET SUMMARY CARD
# ==========================================================

def create_gold_summary():

    summary = {

        "Price":

        gold_data["price"]

        if gold_data else None,

        "Change":

        gold_data["change"]

        if gold_data else None,

        "Trend":

        analyze_gold_trend()["trend"]

        if analyze_gold_trend()

        else "Unknown",

        "Signal":

        generate_gold_signal()[0]

    }


    return summary


# ==========================================================
# SUMMARY DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🥇 Gold Summary"

    )


    summary = create_gold_summary()


    summary_df = pd.DataFrame(

        {

            "Metric":

            summary.keys(),

            "Value":

            summary.values()

        }

    )


    st.dataframe(

        summary_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# KẾT THÚC ĐOẠN 073
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 074
# ==========================================================

# ==========================================================
# MARKET SIGNAL STRENGTH ENGINE
# ==========================================================

def calculate_signal_strength():

    strength = 50

    factors = []


    signal, reasons = generate_gold_signal()


    if signal == "BUY":

        strength += 20

        factors.append(

            "BUY signal detected"

        )


    elif signal == "SELL":

        strength -= 20

        factors.append(

            "SELL signal detected"

        )


    else:

        factors.append(

            "No clear signal"

        )


    confirmation = calculate_confirmation_score()


    if confirmation["score"] >= 70:

        strength += 15

        factors.append(

            "Strong confirmation"

        )


    elif confirmation["score"] < 40:

        strength -= 15

        factors.append(

            "Weak confirmation"

        )


    strength = max(

        0,

        min(

            strength,

            100

        )

    )


    return {

        "strength":

        strength,

        "factors":

        factors

    }


# ==========================================================
# SIGNAL STRENGTH DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "📡 Signal Strength"

    )


    signal_strength = calculate_signal_strength()


    st.progress(

        signal_strength["strength"]

        /

        100

    )


    st.metric(

        "Strength",

        f'{signal_strength["strength"]}/100'

    )


    for factor in signal_strength["factors"]:

        st.write(

            "•",

            factor

        )


# ==========================================================
# MARKET REVERSAL RISK
# ==========================================================

def calculate_reversal_risk():

    risk = 0

    reasons = []


    reversal = detect_trend_reversal()


    if reversal:

        if reversal["signal"] != "No Reversal":

            risk += 40

            reasons.append(

                reversal["signal"]

            )


    candle = detect_candle_pattern()


    if candle:

        if candle in [

            "Bearish Engulfing",

            "Doji"

        ]:

            risk += 20

            reasons.append(

                "Warning candle pattern"

            )


    rsi = calculate_rsi()


    if rsi:

        if rsi["rsi"] > 70:

            risk += 20

            reasons.append(

                "RSI overbought"

            )


        elif rsi["rsi"] < 30:

            risk += 20

            reasons.append(

                "RSI oversold"

            )


    risk = max(

        0,

        min(

            risk,

            100

        )

    )


    if risk >= 70:

        level = "High"

    elif risk >= 40:

        level = "Medium"

    else:

        level = "Low"


    return {

        "risk":

        risk,

        "level":

        level,

        "reasons":

        reasons

    }


# ==========================================================
# REVERSAL RISK DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🔄 Reversal Risk"

    )


    reversal_risk = calculate_reversal_risk()


    st.metric(

        "Risk Level",

        reversal_risk["level"]

    )


    st.progress(

        reversal_risk["risk"]

        /

        100

    )


    for reason in reversal_risk["reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# MARKET DECISION SUMMARY
# ==========================================================

def create_decision_summary():

    decision = trade_decision_matrix()

    confidence = gold_trade_confidence()

    risk = market_risk_alert_level()


    return {

        "Decision":

        decision["decision"],

        "Score":

        decision["score"],

        "Confidence":

        confidence["confidence"],

        "Risk":

        risk["level"]

    }


# ==========================================================
# DECISION SUMMARY DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "📋 Decision Summary"

    )


    decision_summary = create_decision_summary()


    decision_df = pd.DataFrame(

        {

            "Metric":

            decision_summary.keys(),

            "Value":

            decision_summary.values()

        }

    )


    st.dataframe(

        decision_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# KẾT THÚC ĐOẠN 074
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 075
# ==========================================================

# ==========================================================
# MULTI TIMEFRAME ANALYZER
# ==========================================================

def analyze_multi_timeframe():

    timeframes = [

        "M5",

        "M15",

        "H1",

        "H4",

        "D1"

    ]


    results = []


    for tf in timeframes:

        history = load_price_history(

            MARKET_SYMBOLS["Gold"],

            period=tf

        )


        if history.empty:

            continue


        close = history["Close"]


        fast_ma = close.rolling(

            10

        ).mean()


        slow_ma = close.rolling(

            30

        ).mean()


        if fast_ma.iloc[-1] > slow_ma.iloc[-1]:

            trend = "Bullish"

        elif fast_ma.iloc[-1] < slow_ma.iloc[-1]:

            trend = "Bearish"

        else:

            trend = "Neutral"


        results.append(

            {

                "Timeframe":

                tf,

                "Trend":

                trend,

                "Price":

                round(

                    close.iloc[-1],

                    2

                )

            }

        )


    return pd.DataFrame(

        results

    )


# ==========================================================
# MULTI TIMEFRAME DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🕒 Multi Timeframe Analysis"

    )


    timeframe_df = analyze_multi_timeframe()


    st.dataframe(

        timeframe_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# TIMEFRAME AGREEMENT SCORE
# ==========================================================

def calculate_timeframe_agreement():

    dataframe = analyze_multi_timeframe()


    if dataframe.empty:

        return {

            "score": 0,

            "direction": "Unknown"

        }


    bullish = len(

        dataframe[

            dataframe["Trend"]

            ==

            "Bullish"

        ]

    )


    bearish = len(

        dataframe[

            dataframe["Trend"]

            ==

            "Bearish"

        ]

    )


    total = len(

        dataframe

    )


    if bullish > bearish:

        direction = "Bullish"

    elif bearish > bullish:

        direction = "Bearish"

    else:

        direction = "Mixed"


    score = int(

        max(

            bullish,

            bearish

        )

        /

        total

        *

        100

    )


    return {

        "score":

        score,

        "direction":

        direction

    }


# ==========================================================
# AGREEMENT DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "📊 Timeframe Agreement"

    )


    agreement = calculate_timeframe_agreement()


    st.metric(

        "Direction",

        agreement["direction"]

    )


    st.metric(

        "Agreement",

        f'{agreement["score"]}%'

    )


# ==========================================================
# MARKET ENTRY TIMING
# ==========================================================

def calculate_entry_timing():

    timing = "WAIT"

    reasons = []


    agreement = calculate_timeframe_agreement()

    confirmation = calculate_confirmation_score()

    volatility = calculate_volatility()


    if agreement["score"] >= 70:

        reasons.append(

            "Multiple timeframes agree"

        )


    if confirmation["score"] >= 70:

        reasons.append(

            "Entry confirmation strong"

        )


    if volatility:

        if volatility["latest"] < volatility["average"]:

            reasons.append(

                "Volatility acceptable"

            )


    if len(reasons) >= 3:

        timing = "GOOD ENTRY WINDOW"

    elif len(reasons) >= 1:

        timing = "PREPARE"

    else:

        timing = "WAIT"


    return {

        "timing":

        timing,

        "reasons":

        reasons

    }


# ==========================================================
# ENTRY TIMING DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "⏱ Entry Timing"

    )


    timing = calculate_entry_timing()


    st.metric(

        "Timing",

        timing["timing"]

    )


    for reason in timing["reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# KẾT THÚC ĐOẠN 075
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 076
# ==========================================================

# ==========================================================
# SMART MONEY FLOW ANALYZER
# ==========================================================

def analyze_smart_money_flow():

    flow_score = 50

    signals = []


    volume_data = analyze_liquidity()


    if volume_data:

        if volume_data["ratio"] > 1.2:

            flow_score += 15

            signals.append(

                "High volume activity"

            )

        else:

            signals.append(

                "Normal volume activity"

            )


    pressure = calculate_buy_sell_pressure()


    if pressure:

        if pressure["buy"] > pressure["sell"]:

            flow_score += 15

            signals.append(

                "Buyers dominate"

            )

        else:

            flow_score -= 15

            signals.append(

                "Sellers dominate"

            )


    flow_score = max(

        0,

        min(

            flow_score,

            100

        )

    )


    if flow_score >= 70:

        status = "Smart Money Buying"

    elif flow_score <= 30:

        status = "Smart Money Selling"

    else:

        status = "Balanced Flow"


    return {

        "score":

        flow_score,

        "status":

        status,

        "signals":

        signals

    }


# ==========================================================
# SMART MONEY DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "💰 Smart Money Flow"

    )


    smart_money = analyze_smart_money_flow()


    st.progress(

        smart_money["score"]

        /

        100

    )


    st.metric(

        "Flow Status",

        smart_money["status"]

    )


    for signal in smart_money["signals"]:

        st.write(

            "•",

            signal

        )


# ==========================================================
# GOLD LIQUIDITY ZONE DETECTOR
# ==========================================================

def detect_liquidity_zone():

    history = load_price_history(

        MARKET_SYMBOLS["Gold"],

        period="3mo"

    )


    if history.empty:

        return None


    high_volume = history[

        history["Volume"]

        >

        history["Volume"].mean()

    ]


    if high_volume.empty:

        return None


    high_zone = high_volume["High"].max()

    low_zone = high_volume["Low"].min()


    return {

        "high":

        high_zone,

        "low":

        low_zone

    }


# ==========================================================
# LIQUIDITY ZONE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "💧 Liquidity Zone"

    )


    liquidity_zone = detect_liquidity_zone()


    if liquidity_zone:

        liquidity_df = pd.DataFrame(

            {

                "Level":

                [

                    "High Liquidity",

                    "Low Liquidity"

                ],

                "Price":

                [

                    liquidity_zone["high"],

                    liquidity_zone["low"]

                ]

            }

        )


        st.dataframe(

            liquidity_df,

            use_container_width=True,

            hide_index=True

        )


# ==========================================================
# MARKET IMBALANCE DETECTOR
# ==========================================================

def detect_market_imbalance():

    pressure = calculate_buy_sell_pressure()


    if pressure is None:

        return "Unknown"


    difference = (

        pressure["buy"]

        -

        pressure["sell"]

    )


    if difference > 20:

        return "Buyer Imbalance"


    elif difference < -20:

        return "Seller Imbalance"


    return "Balanced"


# ==========================================================
# IMBALANCE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "⚖ Market Imbalance"

    )


    st.info(

        detect_market_imbalance()

    )


# ==========================================================
# KẾT THÚC ĐOẠN 076
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 077
# ==========================================================

# ==========================================================
# SMART MONEY REVERSAL DETECTOR
# ==========================================================

def detect_smart_money_reversal():

    risk = 0

    signals = []


    imbalance = detect_market_imbalance()


    if imbalance == "Seller Imbalance":

        risk += 20

        signals.append(

            "Selling imbalance detected"

        )


    elif imbalance == "Buyer Imbalance":

        risk += 10

        signals.append(

            "Buying imbalance detected"

        )


    candle = detect_candle_pattern()


    if candle == "Bearish Engulfing":

        risk += 25

        signals.append(

            "Bearish reversal candle"

        )


    elif candle == "Bullish Engulfing":

        signals.append(

            "Bullish reversal candle"

        )


    reversal = detect_trend_reversal()


    if reversal:

        if reversal["signal"] != "No Reversal":

            risk += 20

            signals.append(

                reversal["signal"]

            )


    risk = max(

        0,

        min(

            risk,

            100

        )

    )


    if risk >= 60:

        status = "Potential Reversal"

    elif risk >= 30:

        status = "Watch Carefully"

    else:

        status = "Trend Stable"


    return {

        "risk":

        risk,

        "status":

        status,

        "signals":

        signals

    }


# ==========================================================
# SMART MONEY REVERSAL DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🔄 Smart Money Reversal"

    )


    reversal = detect_smart_money_reversal()


    st.metric(

        "Status",

        reversal["status"]

    )


    st.progress(

        reversal["risk"]

        /

        100

    )


    for signal in reversal["signals"]:

        st.write(

            "•",

            signal

        )


# ==========================================================
# GOLD PRICE RANGE ANALYZER
# ==========================================================

def calculate_price_range():

    history = load_price_history(

        MARKET_SYMBOLS["Gold"],

        period="1mo"

    )


    if history.empty:

        return None


    highest = float(

        history["High"].max()

    )


    lowest = float(

        history["Low"].min()

    )


    current = float(

        history["Close"].iloc[-1]

    )


    range_size = (

        highest

        -

        lowest

    )


    position = (

        (

            current

            -

            lowest

        )

        /

        range_size

        *

        100

    ) if range_size else 0


    return {

        "high":

        highest,

        "low":

        lowest,

        "current":

        current,

        "position":

        position

    }


# ==========================================================
# PRICE RANGE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "📏 Price Range Position"

    )


    price_range = calculate_price_range()


    if price_range:

        st.progress(

            price_range["position"]

            /

            100

        )


        st.metric(

            "Range Position",

            f'{price_range["position"]:.1f}%'

        )


# ==========================================================
# MARKET EFFICIENCY SCORE
# ==========================================================

def calculate_market_efficiency():

    score = 50


    volatility = calculate_volatility()


    if volatility:

        if volatility["latest"] < volatility["average"]:

            score += 15

        else:

            score -= 15


    liquidity = analyze_liquidity()


    if liquidity:

        if liquidity["ratio"] > 1:

            score += 10


    score = max(

        0,

        min(

            score,

            100

        )

    )


    return score


# ==========================================================
# EFFICIENCY DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "⚙ Market Efficiency"

    )


    efficiency = calculate_market_efficiency()


    st.progress(

        efficiency /

        100

    )


    st.metric(

        "Efficiency",

        f"{efficiency}/100"

    )


# ==========================================================
# KẾT THÚC ĐOẠN 077
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 078
# ==========================================================

# ==========================================================
# GOLD MARKET CONDITION SCORE
# ==========================================================

def calculate_gold_condition_score():

    score = 50

    factors = []


    trend = analyze_gold_trend()


    if trend:

        if "Uptrend" in trend["trend"]:

            score += 15

            factors.append(

                "Bullish trend"

            )


        elif "Downtrend" in trend["trend"]:

            score -= 15

            factors.append(

                "Bearish trend"

            )


    momentum = calculate_gold_momentum_score()


    if momentum:

        if momentum["score"] >= 60:

            score += 15

            factors.append(

                "Strong momentum"

            )

        else:

            score -= 10

            factors.append(

                "Weak momentum"

            )


    smart_money = analyze_smart_money_flow()


    if smart_money:

        if smart_money["score"] >= 60:

            score += 10

            factors.append(

                "Positive money flow"

            )

        else:

            score -= 10

            factors.append(

                "Negative money flow"

            )


    score = max(

        0,

        min(

            score,

            100

        )

    )


    if score >= 75:

        condition = "Strong Bullish"

    elif score >= 60:

        condition = "Bullish"

    elif score <= 25:

        condition = "Strong Bearish"

    elif score <= 40:

        condition = "Bearish"

    else:

        condition = "Neutral"


    return {

        "score":

        score,

        "condition":

        condition,

        "factors":

        factors

    }


# ==========================================================
# CONDITION SCORE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🥇 Gold Condition Score"

    )


    condition = calculate_gold_condition_score()


    st.progress(

        condition["score"]

        /

        100

    )


    st.metric(

        "Condition",

        condition["condition"]

    )


    st.metric(

        "Score",

        f'{condition["score"]}/100'

    )


    for factor in condition["factors"]:

        st.write(

            "•",

            factor

        )


# ==========================================================
# TRADE QUALITY RATING
# ==========================================================

def calculate_trade_quality():

    score = 0

    factors = []


    confidence = gold_trade_confidence()


    if confidence["confidence"] >= 70:

        score += 25

        factors.append(

            "High confidence"

        )


    confirmation = calculate_confirmation_score()


    if confirmation["score"] >= 60:

        score += 25

        factors.append(

            "Market confirmation"

        )


    rr = calculate_dynamic_risk_reward()


    if rr:

        if rr["ratio"] >= 2:

            score += 25

            factors.append(

                "Good risk reward"

            )


    risk = market_risk_alert_level()


    if risk["level"] == "SAFE":

        score += 25

        factors.append(

            "Risk acceptable"

        )


    return {

        "score":

        score,

        "factors":

        factors

    }


# ==========================================================
# TRADE QUALITY DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "⭐ Trade Quality Rating"

    )


    quality = calculate_trade_quality()


    st.progress(

        quality["score"]

        /

        100

    )


    st.metric(

        "Quality",

        f'{quality["score"]}/100'

    )


    for factor in quality["factors"]:

        st.write(

            "•",

            factor

        )


# ==========================================================
# KẾT THÚC ĐOẠN 078
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 079
# ==========================================================

# ==========================================================
# TRADE ENTRY DECISION ENGINE
# ==========================================================

def trade_entry_decision():

    decision = {

        "Action":

        "WAIT",

        "Confidence":

        0,

        "Reasons":

        []

    }


    quality = calculate_trade_quality()

    matrix = trade_decision_matrix()

    timing = calculate_entry_timing()


    confidence = 0


    if quality["score"] >= 75:

        confidence += 30

        decision["Reasons"].append(

            "High trade quality"

        )


    if matrix["decision"] in [

        "STRONG BUY",

        "STRONG SELL"

    ]:

        confidence += 30

        decision["Reasons"].append(

            "Strong market signal"

        )


    elif matrix["decision"] != "WAIT":

        confidence += 15

        decision["Reasons"].append(

            "Trade direction available"

        )


    if timing["timing"] == "GOOD ENTRY WINDOW":

        confidence += 40

        decision["Reasons"].append(

            "Good timing"

        )


    decision["Confidence"] = min(

        confidence,

        100

    )


    if confidence >= 80:

        decision["Action"] = "EXECUTE SETUP"

    elif confidence >= 50:

        decision["Action"] = "PREPARE TRADE"

    else:

        decision["Action"] = "WAIT"


    return decision


# ==========================================================
# ENTRY DECISION DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🎯 Entry Decision"

    )


    entry_decision = trade_entry_decision()


    st.metric(

        "Action",

        entry_decision["Action"]

    )


    st.progress(

        entry_decision["Confidence"]

        /

        100

    )


    st.metric(

        "Confidence",

        f'{entry_decision["Confidence"]}%'

    )


    for reason in entry_decision["Reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# MARKET NOISE FILTER
# ==========================================================

def market_noise_filter():

    noise = 0

    reasons = []


    volatility = calculate_volatility()


    if volatility:

        if volatility["latest"] > (

            volatility["average"]

            *

            2

        ):

            noise += 40

            reasons.append(

                "Extreme volatility"

            )


    liquidity = analyze_liquidity()


    if liquidity:

        if liquidity["ratio"] < 0.7:

            noise += 30

            reasons.append(

                "Low liquidity"

            )


    candle = detect_candle_pattern()


    if candle == "Doji":

        noise += 20

        reasons.append(

            "Indecision candle"

        )


    noise = max(

        0,

        min(

            noise,

            100

        )

    )


    if noise >= 70:

        status = "High Noise"

    elif noise >= 40:

        status = "Medium Noise"

    else:

        status = "Clean Market"


    return {

        "noise":

        noise,

        "status":

        status,

        "reasons":

        reasons

    }


# ==========================================================
# NOISE FILTER DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🔇 Market Noise Filter"

    )


    noise = market_noise_filter()


    st.metric(

        "Market State",

        noise["status"]

    )


    st.progress(

        noise["noise"]

        /

        100

    )


    for reason in noise["reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# KẾT THÚC ĐOẠN 079
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 080
# ==========================================================

# ==========================================================
# MARKET TREND CONSISTENCY ENGINE
# ==========================================================

def calculate_trend_consistency():

    consistency = 0

    details = []


    multi_tf = analyze_multi_timeframe()


    if not multi_tf.empty:

        bullish = len(

            multi_tf[

                multi_tf["Trend"]

                ==

                "Bullish"

            ]

        )


        bearish = len(

            multi_tf[

                multi_tf["Trend"]

                ==

                "Bearish"

            ]

        )


        if bullish > bearish:

            consistency = (

                bullish

                /

                len(multi_tf)

            ) * 100


            details.append(

                "Multiple timeframes bullish"

            )


        elif bearish > bullish:

            consistency = (

                bearish

                /

                len(multi_tf)

            ) * 100


            details.append(

                "Multiple timeframes bearish"

            )


        else:

            details.append(

                "Timeframes disagree"

            )


    return {

        "score":

        round(

            consistency,

            1

        ),

        "details":

        details

    }


# ==========================================================
# TREND CONSISTENCY DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "📐 Trend Consistency"

    )


    consistency = calculate_trend_consistency()


    st.progress(

        consistency["score"]

        /

        100

    )


    st.metric(

        "Consistency",

        f'{consistency["score"]}%'

    )


    for detail in consistency["details"]:

        st.write(

            "•",

            detail

        )


# ==========================================================
# GOLD MARKET FINAL SCORE
# ==========================================================

def calculate_final_gold_score():

    scores = []


    condition = calculate_gold_condition_score()

    quality = calculate_trade_quality()

    confidence = gold_trade_confidence()

    signal = calculate_signal_strength()


    scores.append(

        condition["score"]

    )

    scores.append(

        quality["score"]

    )

    scores.append(

        confidence["confidence"]

    )

    scores.append(

        signal["strength"]

    )


    final_score = sum(

        scores

    ) / len(scores)


    if final_score >= 80:

        status = "Excellent Setup"

    elif final_score >= 60:

        status = "Good Setup"

    elif final_score >= 40:

        status = "Neutral Setup"

    else:

        status = "Avoid"


    return {

        "score":

        round(

            final_score,

            1

        ),

        "status":

        status

    }


# ==========================================================
# FINAL SCORE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🏆 Final Gold Score"

    )


    final_score = calculate_final_gold_score()


    st.progress(

        final_score["score"]

        /

        100

    )


    st.metric(

        "Final Score",

        f'{final_score["score"]}/100'

    )


    st.info(

        final_score["status"]

    )


# ==========================================================
# MARKET DECISION LOG
# ==========================================================

if "decision_log" not in st.session_state:

    st.session_state.decision_log = []


def save_decision_log():

    final = calculate_final_gold_score()


    st.session_state.decision_log.append(

        {

            "Time":

            current_time(),

            "Score":

            final["score"],

            "Status":

            final["status"]

        }

    )


    if len(

        st.session_state.decision_log

    ) > 100:

        st.session_state.decision_log.pop(

            0

        )


save_decision_log()


# ==========================================================
# DECISION LOG DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "📘 Decision Log"

    )


    log_df = pd.DataFrame(

        st.session_state.decision_log[-20:]

    )


    st.dataframe(

        log_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# KẾT THÚC ĐOẠN 080
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 081
# ==========================================================

# ==========================================================
# MARKET LEARNING ENGINE
# ==========================================================

if "learning_data" not in st.session_state:

    st.session_state.learning_data = []


def save_learning_data():

    final_score = calculate_final_gold_score()

    decision = trade_decision_matrix()

    record = {

        "Time":

        current_time(),

        "Market":

        "Gold",

        "Score":

        final_score["score"],

        "Decision":

        decision["decision"],

        "Condition":

        final_score["status"]

    }


    st.session_state.learning_data.append(

        record

    )


    if len(

        st.session_state.learning_data

    ) > 500:

        st.session_state.learning_data.pop(

            0

        )


save_learning_data()


# ==========================================================
# LEARNING DATA DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🧠 Learning Memory"

    )


    learning_df = pd.DataFrame(

        st.session_state.learning_data[-20:]

    )


    st.dataframe(

        learning_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# MARKET PATTERN RECOGNITION
# ==========================================================

def recognize_market_pattern():

    patterns = []


    candle = detect_candle_pattern()


    if candle:

        patterns.append(

            candle

        )


    structure = analyze_market_structure()


    if structure:

        patterns.append(

            structure["structure"]

        )


    phase = detect_market_phase()


    if phase:

        patterns.append(

            phase["phase"]

        )


    if len(patterns) == 0:

        result = "No Pattern"

    else:

        result = ", ".join(

            patterns

        )


    return result


# ==========================================================
# PATTERN DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🔎 Pattern Recognition"

    )


    pattern = recognize_market_pattern()


    st.info(

        pattern

    )


# ==========================================================
# MARKET OPPORTUNITY SCORE 2.0
# ==========================================================

def calculate_opportunity_score_v2():

    score = 0

    factors = []


    final = calculate_final_gold_score()


    if final["score"] >= 70:

        score += 30

        factors.append(

            "High final score"

        )


    consistency = calculate_trend_consistency()


    if consistency["score"] >= 70:

        score += 20

        factors.append(

            "Trend agreement"

        )


    smart_money = analyze_smart_money_flow()


    if smart_money["score"] >= 60:

        score += 20

        factors.append(

            "Smart money support"

        )


    timing = calculate_entry_timing()


    if timing["timing"] == "GOOD ENTRY WINDOW":

        score += 30

        factors.append(

            "Good timing"

        )


    return {

        "score":

        min(

            score,

            100

        ),

        "factors":

        factors

    }


# ==========================================================
# OPPORTUNITY SCORE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "💎 Opportunity Score 2.0"

    )


    opportunity = calculate_opportunity_score_v2()


    st.progress(

        opportunity["score"]

        /

        100

    )


    st.metric(

        "Opportunity",

        f'{opportunity["score"]}/100'

    )


    for factor in opportunity["factors"]:

        st.write(

            "•",

            factor

        )


# ==========================================================
# KẾT THÚC ĐOẠN 081
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 082
# ==========================================================

# ==========================================================
# MARKET INTELLIGENCE ENGINE
# ==========================================================

def generate_market_intelligence():

    intelligence = {

        "Trend":

        "Unknown",

        "Momentum":

        "Unknown",

        "Risk":

        "Unknown",

        "Opportunity":

        "Unknown"

    }


    trend = calculate_trend_consistency()

    if trend["score"] >= 70:

        intelligence["Trend"] = "Strong"

    elif trend["score"] >= 40:

        intelligence["Trend"] = "Mixed"

    else:

        intelligence["Trend"] = "Weak"


    momentum = calculate_gold_momentum_score()


    if momentum["score"] >= 70:

        intelligence["Momentum"] = "Strong"

    elif momentum["score"] >= 40:

        intelligence["Momentum"] = "Normal"

    else:

        intelligence["Momentum"] = "Weak"


    risk = market_risk_alert_level()


    intelligence["Risk"] = risk["level"]


    opportunity = calculate_opportunity_score_v2()


    if opportunity["score"] >= 70:

        intelligence["Opportunity"] = "High"

    elif opportunity["score"] >= 40:

        intelligence["Opportunity"] = "Medium"

    else:

        intelligence["Opportunity"] = "Low"


    return intelligence


# ==========================================================
# INTELLIGENCE DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🤖 Market Intelligence"

    )


    intelligence = generate_market_intelligence()


    intelligence_df = pd.DataFrame(

        {

            "Category":

            intelligence.keys(),

            "Status":

            intelligence.values()

        }

    )


    st.dataframe(

        intelligence_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# GOLD MARKET COMMAND CENTER
# ==========================================================

def gold_command_center():

    decision = trade_entry_decision()

    final_score = calculate_final_gold_score()

    setup = generate_gold_setup()


    return {

        "Action":

        decision["Action"],

        "Confidence":

        decision["Confidence"],

        "Market Score":

        final_score["score"],

        "Setup":

        setup["Direction"]

    }


# ==========================================================
# COMMAND CENTER DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🎮 Gold Command Center"

    )


    command = gold_command_center()


    command_df = pd.DataFrame(

        {

            "Metric":

            command.keys(),

            "Value":

            command.values()

        }

    )


    st.dataframe(

        command_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# MARKET ALERT INTELLIGENCE
# ==========================================================

def generate_alert_intelligence():

    alerts = []


    risk = market_risk_alert_level()


    if risk["level"] == "DANGER":

        alerts.append(

            "Market risk extremely high"

        )


    reversal = detect_smart_money_reversal()


    if reversal["risk"] >= 60:

        alerts.append(

            "Possible reversal detected"

        )


    noise = market_noise_filter()


    if noise["noise"] >= 70:

        alerts.append(

            "Market noise too high"

        )


    if len(alerts) == 0:

        alerts.append(

            "No critical alerts"

        )


    return alerts


# ==========================================================
# ALERT INTELLIGENCE DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🚨 Intelligence Alerts"

    )


    intelligence_alerts = generate_alert_intelligence()


    for alert in intelligence_alerts:

        st.warning(

            alert

        )


# ==========================================================
# KẾT THÚC ĐOẠN 082
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 083
# ==========================================================

# ==========================================================
# MARKET DECISION AI SUMMARY
# ==========================================================

def generate_ai_trade_summary():

    decision = trade_entry_decision()

    confidence = gold_trade_confidence()

    risk = market_risk_alert_level()

    summary = []


    if decision["Action"] == "EXECUTE SETUP":

        summary.append(

            "Market conditions support execution."

        )

    elif decision["Action"] == "PREPARE TRADE":

        summary.append(

            "Prepare setup and wait confirmation."

        )

    else:

        summary.append(

            "No high quality opportunity."

        )


    if confidence["confidence"] >= 70:

        summary.append(

            "Confidence level is strong."

        )

    else:

        summary.append(

            "Confidence needs improvement."

        )


    if risk["level"] == "DANGER":

        summary.append(

            "Reduce risk exposure."

        )


    return summary


# ==========================================================
# AI SUMMARY DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🤖 AI Trade Summary"

    )


    ai_summary = generate_ai_trade_summary()


    for item in ai_summary:

        st.write(

            "•",

            item

        )


# ==========================================================
# MARKET BEHAVIOR ANALYZER
# ==========================================================

def analyze_market_behavior():

    behavior = {

        "Behavior":

        "Unknown",

        "Reason":

        []

    }


    phase = detect_market_phase()

    volatility = calculate_volatility()

    liquidity = analyze_liquidity()


    if phase:

        behavior["Reason"].append(

            phase["phase"]

        )


    if volatility:

        if volatility["latest"] > volatility["average"]:

            behavior["Reason"].append(

                "High volatility"

            )

        else:

            behavior["Reason"].append(

                "Stable volatility"

            )


    if liquidity:

        behavior["Reason"].append(

            liquidity["status"]

        )


    if (

        "Expansion"

        in

        behavior["Reason"]

    ):

        behavior["Behavior"] = "Trending Market"


    elif (

        "Accumulation"

        in

        behavior["Reason"]

    ):

        behavior["Behavior"] = "Accumulation Market"


    else:

        behavior["Behavior"] = "Unclear Market"


    return behavior


# ==========================================================
# BEHAVIOR DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🌊 Market Behavior"

    )


    behavior = analyze_market_behavior()


    st.metric(

        "Behavior",

        behavior["Behavior"]

    )


    for reason in behavior["Reason"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# GOLD MARKET ACTION MATRIX
# ==========================================================

def gold_action_matrix():

    actions = []


    score = calculate_final_gold_score()

    risk = market_risk_alert_level()

    opportunity = calculate_opportunity_score_v2()


    if score["score"] >= 70:

        actions.append(

            "Look for valid entry"

        )

    else:

        actions.append(

            "Wait for better setup"

        )


    if opportunity["score"] >= 70:

        actions.append(

            "Opportunity is attractive"

        )


    if risk["level"] != "SAFE":

        actions.append(

            "Reduce position size"

        )


    return actions


# ==========================================================
# ACTION MATRIX DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "⚔ Gold Action Matrix"

    )


    actions = gold_action_matrix()


    for action in actions:

        st.write(

            "•",

            action

        )


# ==========================================================
# KẾT THÚC ĐOẠN 083
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 084
# ==========================================================

# ==========================================================
# MARKET STRATEGY GENERATOR
# ==========================================================

def generate_market_strategy():

    strategy = {

        "Mode":

        "WAIT",

        "Entry":

        "None",

        "Risk":

        "Normal",

        "Management":

        []

    }


    decision = trade_entry_decision()

    setup = generate_gold_setup()

    risk = market_risk_alert_level()


    if decision["Action"] == "EXECUTE SETUP":

        strategy["Mode"] = "ACTIVE TRADE"


    elif decision["Action"] == "PREPARE TRADE":

        strategy["Mode"] = "PREPARE"


    else:

        strategy["Mode"] = "WAIT"


    strategy["Entry"] = setup["Direction"]


    strategy["Risk"] = risk["level"]


    if risk["level"] == "DANGER":

        strategy["Management"].append(

            "Lower position size"

        )


    else:

        strategy["Management"].append(

            "Maintain normal risk"

        )


    return strategy


# ==========================================================
# STRATEGY DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "📋 Market Strategy"

    )


    strategy = generate_market_strategy()


    strategy_df = pd.DataFrame(

        {

            "Item":

            strategy.keys(),

            "Value":

            strategy.values()

        }

    )


    st.dataframe(

        strategy_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# SMART RISK CONTROLLER
# ==========================================================

def smart_risk_controller():

    risk_score = 100

    warnings = []


    drawdown = calculate_drawdown()


    if drawdown > 10:

        risk_score -= 30

        warnings.append(

            "Account drawdown high"

        )


    daily_status = check_daily_loss()


    if not daily_status:

        risk_score -= 40

        warnings.append(

            "Daily loss limit reached"

        )


    psychology = trade_warning()


    if len(psychology) > 0:

        risk_score -= 20

        warnings.append(

            "Trading psychology warning"

        )


    risk_score = max(

        0,

        risk_score

    )


    if risk_score >= 70:

        status = "Safe Trading"

    elif risk_score >= 40:

        status = "Caution"

    else:

        status = "Stop Trading"


    return {

        "score":

        risk_score,

        "status":

        status,

        "warnings":

        warnings

    }


# ==========================================================
# RISK CONTROLLER DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🛡 Smart Risk Controller"

    )


    controller = smart_risk_controller()


    st.progress(

        controller["score"]

        /

        100

    )


    st.metric(

        "Risk Status",

        controller["status"]

    )


    for warning in controller["warnings"]:

        st.warning(

            warning

        )


# ==========================================================
# MARKET OPERATION MODE
# ==========================================================

def determine_operation_mode():

    risk = smart_risk_controller()

    opportunity = calculate_opportunity_score_v2()


    if risk["score"] < 40:

        return "DEFENSIVE MODE"


    if opportunity["score"] >= 70:

        return "OPPORTUNITY MODE"


    return "NORMAL MODE"


# ==========================================================
# MODE DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "⚙ Operation Mode"

    )


    st.info(

        determine_operation_mode()

    )


# ==========================================================
# KẾT THÚC ĐOẠN 084
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 085
# ==========================================================

# ==========================================================
# MARKET INTELLIGENCE REPORT GENERATOR
# ==========================================================

def generate_intelligence_report():

    intelligence = generate_market_intelligence()

    strategy = generate_market_strategy()

    controller = smart_risk_controller()


    report = {

        "Time":

        current_time(),

        "Trend":

        intelligence["Trend"],

        "Momentum":

        intelligence["Momentum"],

        "Risk":

        intelligence["Risk"],

        "Opportunity":

        intelligence["Opportunity"],

        "Strategy":

        strategy["Mode"],

        "Risk Control":

        controller["status"]

    }


    return report


# ==========================================================
# REPORT DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "📑 Intelligence Report"

    )


    intelligence_report = generate_intelligence_report()


    report_df = pd.DataFrame(

        {

            "Category":

            intelligence_report.keys(),

            "Result":

            intelligence_report.values()

        }

    )


    st.dataframe(

        report_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# MARKET SCORING HISTORY
# ==========================================================

if "score_history" not in st.session_state:

    st.session_state.score_history = []


def save_score_history():

    final_score = calculate_final_gold_score()


    st.session_state.score_history.append(

        {

            "Time":

            current_time(),

            "Score":

            final_score["score"],

            "Status":

            final_score["status"]

        }

    )


    if len(

        st.session_state.score_history

    ) > 200:

        st.session_state.score_history.pop(

            0

        )


save_score_history()


# ==========================================================
# SCORE HISTORY DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "📈 Score History"

    )


    score_df = pd.DataFrame(

        st.session_state.score_history[-20:]

    )


    st.dataframe(

        score_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# MARKET DECISION ENGINE V2
# ==========================================================

def market_decision_engine_v2():

    score = 0

    reasons = []


    final = calculate_final_gold_score()


    if final["score"] >= 70:

        score += 2

        reasons.append(

            "High quality market"

        )


    elif final["score"] < 40:

        score -= 2

        reasons.append(

            "Poor market quality"

        )


    operation = determine_operation_mode()


    if operation == "OPPORTUNITY MODE":

        score += 2

        reasons.append(

            "Opportunity mode active"

        )


    elif operation == "DEFENSIVE MODE":

        score -= 2

        reasons.append(

            "Defensive mode active"

        )


    if score >= 3:

        decision = "TRADE"

    elif score <= -2:

        decision = "AVOID"

    else:

        decision = "WAIT"


    return {

        "decision":

        decision,

        "score":

        score,

        "reasons":

        reasons

    }


# ==========================================================
# DECISION ENGINE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🧠 Decision Engine V2"

    )


    engine = market_decision_engine_v2()


    st.metric(

        "Decision",

        engine["decision"]

    )


    for reason in engine["reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# KẾT THÚC ĐOẠN 085
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 086
# ==========================================================

# ==========================================================
# MARKET AI ADVISOR
# ==========================================================

def generate_market_advisor():

    advice = []

    engine = market_decision_engine_v2()

    risk = smart_risk_controller()

    strategy = generate_market_strategy()


    if engine["decision"] == "TRADE":

        advice.append(

            "Market setup is acceptable."

        )

    elif engine["decision"] == "AVOID":

        advice.append(

            "Avoid low quality conditions."

        )

    else:

        advice.append(

            "Wait for stronger confirmation."

        )


    if risk["status"] == "Stop Trading":

        advice.append(

            "Trading should be paused."

        )


    if strategy["Mode"] == "ACTIVE TRADE":

        advice.append(

            "Follow planned execution."

        )


    return advice


# ==========================================================
# ADVISOR DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🤖 Market AI Advisor"

    )


    advisor = generate_market_advisor()


    for item in advisor:

        st.write(

            "•",

            item

        )


# ==========================================================
# GOLD TRADE PLAN MEMORY
# ==========================================================

if "trade_plan_history" not in st.session_state:

    st.session_state.trade_plan_history = []


def save_trade_plan():

    setup = generate_gold_setup()

    decision = trade_entry_decision()


    st.session_state.trade_plan_history.append(

        {

            "Time":

            current_time(),

            "Direction":

            setup["Direction"],

            "Action":

            decision["Action"],

            "Confidence":

            decision["Confidence"]

        }

    )


    if len(

        st.session_state.trade_plan_history

    ) > 200:

        st.session_state.trade_plan_history.pop(

            0

        )


save_trade_plan()


# ==========================================================
# TRADE PLAN HISTORY DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "📒 Trade Plan History"

    )


    plan_history_df = pd.DataFrame(

        st.session_state.trade_plan_history[-20:]

    )


    st.dataframe(

        plan_history_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# MARKET PRESSURE BALANCE
# ==========================================================

def calculate_pressure_balance():

    pressure = calculate_buy_sell_pressure()


    if pressure is None:

        return None


    balance = (

        pressure["buy"]

        -

        pressure["sell"]

    )


    if balance > 25:

        status = "Buyer Control"

    elif balance < -25:

        status = "Seller Control"

    else:

        status = "Balanced"


    return {

        "balance":

        round(

            balance,

            2

        ),

        "status":

        status

    }


# ==========================================================
# PRESSURE BALANCE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "⚖ Pressure Balance"

    )


    pressure_balance = calculate_pressure_balance()


    if pressure_balance:

        st.metric(

            "Market Control",

            pressure_balance["status"]

        )


        st.metric(

            "Balance",

            pressure_balance["balance"]

        )


# ==========================================================
# KẾT THÚC ĐOẠN 086
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 087
# ==========================================================

# ==========================================================
# MARKET CONTROL ANALYZER
# ==========================================================

def analyze_market_control():

    control = {

        "Controller":

        "Unknown",

        "Strength":

        50,

        "Reasons":

        []

    }


    pressure = calculate_pressure_balance()

    smart_money = analyze_smart_money_flow()

    imbalance = detect_market_imbalance()


    score = 50


    if pressure:

        if pressure["status"] == "Buyer Control":

            score += 20

            control["Reasons"].append(

                "Buyers controlling market"

            )


        elif pressure["status"] == "Seller Control":

            score -= 20

            control["Reasons"].append(

                "Sellers controlling market"

            )


    if smart_money:

        if smart_money["score"] > 60:

            score += 15

            control["Reasons"].append(

                "Smart money inflow"

            )

        else:

            score -= 15

            control["Reasons"].append(

                "Smart money weakness"

            )


    if imbalance == "Buyer Imbalance":

        score += 10


    elif imbalance == "Seller Imbalance":

        score -= 10


    score = max(

        0,

        min(

            score,

            100

        )

    )


    if score >= 70:

        controller = "Buyers"

    elif score <= 30:

        controller = "Sellers"

    else:

        controller = "Balanced"


    control["Controller"] = controller

    control["Strength"] = score


    return control


# ==========================================================
# CONTROL DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🎮 Market Control"

    )


    control = analyze_market_control()


    st.metric(

        "Controller",

        control["Controller"]

    )


    st.progress(

        control["Strength"]

        /

        100

    )


    st.metric(

        "Strength",

        f'{control["Strength"]}/100'

    )


    for reason in control["Reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# GOLD ENTRY MAP
# ==========================================================

def create_gold_entry_map():

    sr = calculate_support_resistance()


    if sr is None:

        return None


    current = sr["price"]

    support = sr["support"]

    resistance = sr["resistance"]


    return {

        "Current Price":

        current,

        "Buy Area":

        support,

        "Middle Area":

        (

            support

            +

            resistance

        )

        /

        2,

        "Sell Area":

        resistance

    }


# ==========================================================
# ENTRY MAP DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🗺 Entry Map"

    )


    entry_map = create_gold_entry_map()


    if entry_map:

        entry_map_df = pd.DataFrame(

            {

                "Zone":

                entry_map.keys(),

                "Price":

                entry_map.values()

            }

        )


        st.dataframe(

            entry_map_df,

            use_container_width=True,

            hide_index=True

        )


# ==========================================================
# MARKET OPPORTUNITY ALERT
# ==========================================================

def opportunity_alert():

    opportunity = calculate_opportunity_score_v2()


    if opportunity["score"] >= 80:

        return "🔥 Premium Opportunity"


    elif opportunity["score"] >= 60:

        return "🟡 Good Opportunity"


    else:

        return "⚪ Wait"


# ==========================================================
# OPPORTUNITY ALERT DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "💎 Opportunity Alert"

    )


    st.info(

        opportunity_alert()

    )


# ==========================================================
# KẾT THÚC ĐOẠN 087
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 088
# ==========================================================

# ==========================================================
# MARKET ENTRY FILTER ENGINE
# ==========================================================

def market_entry_filter():

    filters = {

        "Trend":

        False,

        "Momentum":

        False,

        "Risk":

        False,

        "Timing":

        False

    }


    trend = calculate_trend_consistency()

    momentum = calculate_gold_momentum_score()

    risk = smart_risk_controller()

    timing = calculate_entry_timing()


    if trend["score"] >= 60:

        filters["Trend"] = True


    if momentum["score"] >= 60:

        filters["Momentum"] = True


    if risk["score"] >= 60:

        filters["Risk"] = True


    if timing["timing"] != "WAIT":

        filters["Timing"] = True


    return filters


# ==========================================================
# ENTRY FILTER DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🔍 Entry Filter"

    )


    entry_filters = market_entry_filter()


    completed = 0


    for name, status in entry_filters.items():

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

        len(entry_filters)

    )


# ==========================================================
# GOLD MARKET PHASE MEMORY
# ==========================================================

if "gold_phase_history" not in st.session_state:

    st.session_state.gold_phase_history = []


def save_gold_phase():

    phase = detect_market_phase()


    st.session_state.gold_phase_history.append(

        {

            "Time":

            current_time(),

            "Phase":

            phase["phase"],

            "Score":

            phase["score"]

        }

    )


    if len(

        st.session_state.gold_phase_history

    ) > 200:

        st.session_state.gold_phase_history.pop(

            0

        )


save_gold_phase()


# ==========================================================
# PHASE HISTORY DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🌊 Gold Phase History"

    )


    phase_history_df = pd.DataFrame(

        st.session_state.gold_phase_history[-20:]

    )


    st.dataframe(

        phase_history_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# MARKET CONFIDENCE ENGINE V2
# ==========================================================

def calculate_confidence_v2():

    score = 0

    reasons = []


    final_score = calculate_final_gold_score()

    consistency = calculate_trend_consistency()

    entry = market_entry_filter()


    if final_score["score"] >= 70:

        score += 40

        reasons.append(

            "High market score"

        )


    if consistency["score"] >= 70:

        score += 30

        reasons.append(

            "Trend agreement"

        )


    passed = sum(

        entry.values()

    )


    if passed >= 3:

        score += 30

        reasons.append(

            "Entry filters passed"

        )


    return {

        "score":

        min(

            score,

            100

        ),

        "reasons":

        reasons

    }


# ==========================================================
# CONFIDENCE V2 DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🎯 Confidence Engine V2"

    )


    confidence_v2 = calculate_confidence_v2()


    st.progress(

        confidence_v2["score"]

        /

        100

    )


    st.metric(

        "Confidence",

        f'{confidence_v2["score"]}/100'

    )


    for reason in confidence_v2["reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# KẾT THÚC ĐOẠN 088
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 089
# ==========================================================

# ==========================================================
# MARKET EXECUTION READINESS
# ==========================================================

def calculate_execution_readiness():

    score = 0

    reasons = []


    confidence = calculate_confidence_v2()

    risk = smart_risk_controller()

    noise = market_noise_filter()

    entry = market_entry_filter()


    if confidence["score"] >= 70:

        score += 30

        reasons.append(

            "Confidence level acceptable"

        )


    if risk["score"] >= 70:

        score += 25

        reasons.append(

            "Risk condition healthy"

        )


    if noise["noise"] < 40:

        score += 20

        reasons.append(

            "Market noise low"

        )


    passed = sum(

        entry.values()

    )


    if passed >= 3:

        score += 25

        reasons.append(

            "Entry conditions satisfied"

        )


    score = min(

        score,

        100

    )


    if score >= 80:

        status = "READY"

    elif score >= 50:

        status = "PREPARE"

    else:

        status = "NOT READY"


    return {

        "score":

        score,

        "status":

        status,

        "reasons":

        reasons

    }


# ==========================================================
# EXECUTION READINESS DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "⚔ Execution Readiness"

    )


    readiness = calculate_execution_readiness()


    st.progress(

        readiness["score"]

        /

        100

    )


    st.metric(

        "Status",

        readiness["status"]

    )


    st.metric(

        "Readiness",

        f'{readiness["score"]}%'

    )


    for reason in readiness["reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# TRADE MANAGEMENT ASSISTANT
# ==========================================================

def trade_management_assistant():

    management = []


    setup = generate_gold_setup()

    risk = market_risk_alert_level()


    if setup["Direction"] == "BUY":

        management.append(

            "Protect position below support"

        )


    elif setup["Direction"] == "SELL":

        management.append(

            "Protect position above resistance"

        )


    else:

        management.append(

            "No active position"

        )


    if risk["level"] != "SAFE":

        management.append(

            "Use smaller position size"

        )


    management.append(

        "Follow predefined stop loss"

    )


    return management


# ==========================================================
# MANAGEMENT DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🛠 Trade Management"

    )


    management = trade_management_assistant()


    for item in management:

        st.write(

            "•",

            item

        )


# ==========================================================
# MARKET DECISION CONFIRMATION
# ==========================================================

def final_trade_confirmation():

    readiness = calculate_execution_readiness()

    decision = market_decision_engine_v2()


    if (

        readiness["status"]

        ==

        "READY"

        and

        decision["decision"]

        ==

        "TRADE"

    ):

        return "CONFIRMED SETUP"


    elif readiness["status"] == "PREPARE":

        return "WAIT CONFIRMATION"


    return "NO TRADE"


# ==========================================================
# CONFIRMATION DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🔐 Final Confirmation"

    )


    st.info(

        final_trade_confirmation()

    )


# ==========================================================
# KẾT THÚC ĐOẠN 089
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 090
# ==========================================================

# ==========================================================
# TRADE PERFORMANCE TRACKER
# ==========================================================

if "trade_performance" not in st.session_state:

    st.session_state.trade_performance = []


def save_trade_performance():

    readiness = calculate_execution_readiness()

    confirmation = final_trade_confirmation()


    record = {

        "Time":

        current_time(),

        "Readiness":

        readiness["score"],

        "Confirmation":

        confirmation

    }


    st.session_state.trade_performance.append(

        record

    )


    if len(

        st.session_state.trade_performance

    ) > 300:

        st.session_state.trade_performance.pop(

            0

        )


save_trade_performance()


# ==========================================================
# PERFORMANCE DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "📊 Trade Performance Tracker"

    )


    performance_df = pd.DataFrame(

        st.session_state.trade_performance[-20:]

    )


    st.dataframe(

        performance_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# MARKET OPPORTUNITY RADAR
# ==========================================================

def opportunity_radar():

    radar = {

        "Signal":

        "NONE",

        "Strength":

        0,

        "Reason":

        []

    }


    opportunity = calculate_opportunity_score_v2()

    confidence = calculate_confidence_v2()

    readiness = calculate_execution_readiness()


    strength = (

        opportunity["score"]

        +

        confidence["score"]

        +

        readiness["score"]

    ) / 3


    radar["Strength"] = round(

        strength,

        1

    )


    if strength >= 80:

        radar["Signal"] = "HIGH QUALITY"

    elif strength >= 60:

        radar["Signal"] = "POSSIBLE"

    else:

        radar["Signal"] = "WAIT"


    radar["Reason"] = (

        opportunity["factors"]

        +

        confidence["reasons"]

        +

        readiness["reasons"]

    )


    return radar


# ==========================================================
# RADAR DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "📡 Opportunity Radar"

    )


    radar = opportunity_radar()


    st.metric(

        "Signal",

        radar["Signal"]

    )


    st.progress(

        radar["Strength"]

        /

        100

    )


    st.metric(

        "Strength",

        f'{radar["Strength"]}%'

    )


    for reason in radar["Reason"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# GOLD MARKET CONTROL PANEL
# ==========================================================

def gold_control_panel():

    return {

        "Trend":

        analyze_gold_trend()["trend"]

        if analyze_gold_trend()

        else "Unknown",


        "Signal":

        generate_gold_signal()[0],


        "Risk":

        market_risk_alert_level()["level"],


        "Mode":

        determine_operation_mode(),


        "Final":

        final_trade_confirmation()

    }


# ==========================================================
# CONTROL PANEL DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🎛 Gold Control Panel"

    )


    panel = gold_control_panel()


    panel_df = pd.DataFrame(

        {

            "Metric":

            panel.keys(),

            "Value":

            panel.values()

        }

    )


    st.dataframe(

        panel_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# KẾT THÚC ĐOẠN 090
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 091
# ==========================================================

# ==========================================================
# MARKET SESSION PERFORMANCE ANALYZER
# ==========================================================

if "session_history" not in st.session_state:

    st.session_state.session_history = []


def analyze_trading_session():

    hour = datetime.utcnow().hour


    if 0 <= hour < 8:

        session = "Asian"

    elif 8 <= hour < 16:

        session = "London"

    elif 16 <= hour < 22:

        session = "New York"

    else:

        session = "Transition"


    volatility = calculate_volatility()


    if volatility:

        if volatility["latest"] > volatility["average"]:

            activity = "High"

        else:

            activity = "Normal"

    else:

        activity = "Unknown"


    return {

        "session":

        session,

        "activity":

        activity

    }


# ==========================================================
# SESSION DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🌍 Trading Session"

    )


    session = analyze_trading_session()


    session_df = pd.DataFrame(

        {

            "Metric":

            session.keys(),

            "Value":

            session.values()

        }

    )


    st.dataframe(

        session_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# GOLD MOMENTUM DIRECTION ENGINE
# ==========================================================

def momentum_direction_engine():

    bullish = 0

    bearish = 0

    reasons = []


    momentum = calculate_gold_momentum_score()


    if momentum["score"] >= 60:

        bullish += 1

        reasons.append(

            "Momentum supports buyers"

        )

    else:

        bearish += 1

        reasons.append(

            "Momentum weak"

        )


    pressure = calculate_market_pressure_index()


    if pressure["score"] >= 60:

        bullish += 1

        reasons.append(

            "Buying pressure"

        )

    else:

        bearish += 1

        reasons.append(

            "Selling pressure"

        )


    if bullish > bearish:

        direction = "UP"

    elif bearish > bullish:

        direction = "DOWN"

    else:

        direction = "SIDEWAY"


    return {

        "direction":

        direction,

        "bullish":

        bullish,

        "bearish":

        bearish,

        "reasons":

        reasons

    }


# ==========================================================
# MOMENTUM DIRECTION DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🧭 Momentum Direction"

    )


    momentum_direction = momentum_direction_engine()


    st.metric(

        "Direction",

        momentum_direction["direction"]

    )


    col1, col2 = st.columns(

        2

    )


    with col1:

        st.metric(

            "Bullish",

            momentum_direction["bullish"]

        )


    with col2:

        st.metric(

            "Bearish",

            momentum_direction["bearish"]

        )


    for reason in momentum_direction["reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# MARKET ENTRY ZONE QUALITY
# ==========================================================

def entry_zone_quality():

    score = 50

    reasons = []


    zone = calculate_entry_zone()


    if zone:

        current = zone["Current"]

        buy_zone = zone["Buy Zone"]

        sell_zone = zone["Sell Zone"]


        if current <= buy_zone:

            score += 20

            reasons.append(

                "Near buy zone"

            )


        elif current >= sell_zone:

            score += 20

            reasons.append(

                "Near sell zone"

            )


        else:

            reasons.append(

                "Middle zone"

            )


    score = max(

        0,

        min(

            score,

            100

        )

    )


    return {

        "score":

        score,

        "reasons":

        reasons

    }


# ==========================================================
# ENTRY ZONE QUALITY DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🎯 Entry Zone Quality"

    )


    zone_quality = entry_zone_quality()


    st.progress(

        zone_quality["score"]

        /

        100

    )


    st.metric(

        "Quality",

        f'{zone_quality["score"]}/100'

    )


    for reason in zone_quality["reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# KẾT THÚC ĐOẠN 091
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 092
# ==========================================================

# ==========================================================
# MARKET SENTIMENT FUSION ENGINE
# ==========================================================

def sentiment_fusion_engine():

    score = 50

    factors = []


    news = analyze_news_sentiment()


    if news["sentiment"] == "Positive":

        score += 15

        factors.append(

            "Positive news sentiment"

        )


    elif news["sentiment"] == "Negative":

        score -= 15

        factors.append(

            "Negative news sentiment"

        )


    sentiment = calculate_market_sentiment()


    if sentiment:

        score += sentiment[0] - 50

        factors.append(

            "Technical sentiment included"

        )


    score = max(

        0,

        min(

            score,

            100

        )

    )


    if score >= 70:

        status = "Bullish Sentiment"

    elif score <= 30:

        status = "Bearish Sentiment"

    else:

        status = "Neutral Sentiment"


    return {

        "score":

        score,

        "status":

        status,

        "factors":

        factors

    }


# ==========================================================
# SENTIMENT FUSION DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🧠 Sentiment Fusion"

    )


    sentiment = sentiment_fusion_engine()


    st.progress(

        sentiment["score"]

        /

        100

    )


    st.metric(

        "Sentiment",

        sentiment["status"]

    )


    for factor in sentiment["factors"]:

        st.write(

            "•",

            factor

        )


# ==========================================================
# GOLD MARKET MASTER SIGNAL
# ==========================================================

def generate_master_signal():

    buy_points = 0

    sell_points = 0

    reasons = []


    decision = trade_decision_matrix()

    confidence = calculate_confidence_v2()

    control = analyze_market_control()


    if "BUY" in decision["decision"]:

        buy_points += 2

        reasons.append(

            "Decision supports BUY"

        )


    elif "SELL" in decision["decision"]:

        sell_points += 2

        reasons.append(

            "Decision supports SELL"

        )


    if confidence["score"] >= 70:

        buy_points += 1

        reasons.append(

            "High confidence"

        )


    if control["Controller"] == "Buyers":

        buy_points += 1

        reasons.append(

            "Buyers control market"

        )


    elif control["Controller"] == "Sellers":

        sell_points += 1

        reasons.append(

            "Sellers control market"

        )


    if buy_points > sell_points:

        signal = "BUY"

    elif sell_points > buy_points:

        signal = "SELL"

    else:

        signal = "WAIT"


    strength = abs(

        buy_points

        -

        sell_points

    )


    return {

        "signal":

        signal,

        "strength":

        strength,

        "reasons":

        reasons

    }


# ==========================================================
# MASTER SIGNAL DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🚀 Master Signal"

    )


    master = generate_master_signal()


    st.metric(

        "Signal",

        master["signal"]

    )


    st.metric(

        "Strength",

        master["strength"]

    )


    for reason in master["reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# GOLD MARKET COMMAND MEMORY
# ==========================================================

if "command_history" not in st.session_state:

    st.session_state.command_history = []


def save_command_history():

    command = gold_command_center()


    st.session_state.command_history.append(

        {

            "Time":

            current_time(),

            "Action":

            command["Action"],

            "Confidence":

            command["Confidence"],

            "Setup":

            command["Setup"]

        }

    )


    if len(

        st.session_state.command_history

    ) > 200:

        st.session_state.command_history.pop(

            0

        )


save_command_history()


# ==========================================================
# COMMAND HISTORY DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "📘 Command History"

    )


    command_df = pd.DataFrame(

        st.session_state.command_history[-20:]

    )


    st.dataframe(

        command_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# KẾT THÚC ĐOẠN 092
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 093
# ==========================================================

# ==========================================================
# MARKET MASTER DECISION ENGINE
# ==========================================================

def market_master_decision():

    result = {

        "Decision":

        "WAIT",

        "Confidence":

        0,

        "Reasons":

        []

    }


    master_signal = generate_master_signal()

    readiness = calculate_execution_readiness()

    opportunity = opportunity_radar()


    confidence = 0


    if master_signal["signal"] == "BUY":

        result["Reasons"].append(

            "Master system detects BUY"

        )

        confidence += 30


    elif master_signal["signal"] == "SELL":

        result["Reasons"].append(

            "Master system detects SELL"

        )

        confidence += 30


    else:

        result["Reasons"].append(

            "No dominant direction"

        )


    if readiness["status"] == "READY":

        confidence += 40

        result["Reasons"].append(

            "Execution conditions ready"

        )


    if opportunity["Strength"] >= 70:

        confidence += 30

        result["Reasons"].append(

            "High opportunity score"

        )


    result["Confidence"] = min(

        confidence,

        100

    )


    if (

        result["Confidence"] >= 80

        and

        master_signal["signal"] != "WAIT"

    ):

        result["Decision"] = (

            master_signal["signal"]

        )


    elif result["Confidence"] >= 50:

        result["Decision"] = "PREPARE"


    return result


# ==========================================================
# MASTER DECISION DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "👑 Master Decision"

    )


    master_decision = market_master_decision()


    st.metric(

        "Decision",

        master_decision["Decision"]

    )


    st.progress(

        master_decision["Confidence"]

        /

        100

    )


    st.metric(

        "Confidence",

        f'{master_decision["Confidence"]}%'

    )


    for reason in master_decision["Reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# MARKET AUTO REPORT STORAGE
# ==========================================================

if "auto_reports" not in st.session_state:

    st.session_state.auto_reports = []


def save_auto_report():

    report = generate_intelligence_report()

    st.session_state.auto_reports.append(

        report

    )


    if len(

        st.session_state.auto_reports

    ) > 100:

        st.session_state.auto_reports.pop(

            0

        )


save_auto_report()


# ==========================================================
# AUTO REPORT DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "📂 Auto Reports"

    )


    auto_report_df = pd.DataFrame(

        st.session_state.auto_reports[-10:]

    )


    st.dataframe(

        auto_report_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# GOLD MARKET FINAL COMMAND
# ==========================================================

def final_gold_command():

    decision = market_master_decision()

    setup = generate_gold_setup()

    risk = smart_risk_controller()


    command = {

        "Action":

        decision["Decision"],

        "Confidence":

        decision["Confidence"],

        "Entry":

        setup["Entry"],

        "Stop Loss":

        setup["Stop Loss"],

        "Take Profit":

        setup["Take Profit"],

        "Risk":

        risk["status"]

    }


    return command


# ==========================================================
# FINAL COMMAND DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🎯 Final Gold Command"

    )


    final_command = final_gold_command()


    command_final_df = pd.DataFrame(

        {

            "Parameter":

            final_command.keys(),

            "Value":

            final_command.values()

        }

    )


    st.dataframe(

        command_final_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# KẾT THÚC ĐOẠN 093
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 094
# ==========================================================

# ==========================================================
# TRADE JOURNAL SYSTEM
# ==========================================================

if "trade_journal" not in st.session_state:

    st.session_state.trade_journal = []


def add_trade_journal():

    command = final_gold_command()

    journal = {

        "Time":

        current_time(),

        "Action":

        command["Action"],

        "Confidence":

        command["Confidence"],

        "Entry":

        command["Entry"],

        "Stop Loss":

        command["Stop Loss"],

        "Take Profit":

        command["Take Profit"],

        "Risk":

        command["Risk"]

    }


    st.session_state.trade_journal.append(

        journal

    )


    if len(

        st.session_state.trade_journal

    ) > 300:

        st.session_state.trade_journal.pop(

            0

        )


add_trade_journal()


# ==========================================================
# TRADE JOURNAL DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "📔 Trade Journal"

    )


    journal_df = pd.DataFrame(

        st.session_state.trade_journal[-20:]

    )


    st.dataframe(

        journal_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# MARKET DECISION CONFIRMATION V2
# ==========================================================

def market_confirmation_v2():

    confirmations = 0

    reasons = []


    master = market_master_decision()

    control = analyze_market_control()

    sentiment = sentiment_fusion_engine()


    if master["Confidence"] >= 70:

        confirmations += 1

        reasons.append(

            "Master confidence confirmed"

        )


    if control["Strength"] >= 60:

        confirmations += 1

        reasons.append(

            "Market control confirmed"

        )


    if sentiment["score"] >= 60:

        confirmations += 1

        reasons.append(

            "Sentiment supports direction"

        )


    if confirmations >= 3:

        status = "FULL CONFIRMATION"

    elif confirmations >= 2:

        status = "PARTIAL CONFIRMATION"

    else:

        status = "NO CONFIRMATION"


    return {

        "status":

        status,

        "count":

        confirmations,

        "reasons":

        reasons

    }


# ==========================================================
# CONFIRMATION V2 DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🔐 Confirmation Engine V2"

    )


    confirmation_v2 = market_confirmation_v2()


    st.metric(

        "Status",

        confirmation_v2["status"]

    )


    st.metric(

        "Confirmations",

        confirmation_v2["count"]

    )


    for reason in confirmation_v2["reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# GOLD TRADE EXECUTION SCORE
# ==========================================================

def calculate_execution_score():

    score = 0

    reasons = []


    readiness = calculate_execution_readiness()

    confirmation = market_confirmation_v2()

    quality = calculate_trade_quality()


    if readiness["score"] >= 70:

        score += 40

        reasons.append(

            "Execution readiness good"

        )


    if confirmation["count"] >= 2:

        score += 30

        reasons.append(

            "Multiple confirmations"

        )


    if quality["score"] >= 70:

        score += 30

        reasons.append(

            "Trade quality acceptable"

        )


    return {

        "score":

        min(

            score,

            100

        ),

        "reasons":

        reasons

    }


# ==========================================================
# EXECUTION SCORE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "⚡ Execution Score"

    )


    execution_score = calculate_execution_score()


    st.progress(

        execution_score["score"]

        /

        100

    )


    st.metric(

        "Execution",

        f'{execution_score["score"]}/100'

    )


    for reason in execution_score["reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# KẾT THÚC ĐOẠN 094
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 095
# ==========================================================

# ==========================================================
# AI TRADE RATING SYSTEM
# ==========================================================

def calculate_ai_trade_rating():

    rating = 0

    reasons = []


    execution = calculate_execution_score()

    confirmation = market_confirmation_v2()

    final_score = calculate_final_gold_score()

    risk = smart_risk_controller()


    if execution["score"] >= 70:

        rating += 30

        reasons.append(

            "Execution score strong"

        )


    if confirmation["count"] >= 2:

        rating += 25

        reasons.append(

            "Confirmation available"

        )


    if final_score["score"] >= 70:

        rating += 25

        reasons.append(

            "Market quality high"

        )


    if risk["score"] >= 70:

        rating += 20

        reasons.append(

            "Risk condition acceptable"

        )


    rating = min(

        rating,

        100

    )


    if rating >= 80:

        grade = "A"

    elif rating >= 60:

        grade = "B"

    elif rating >= 40:

        grade = "C"

    else:

        grade = "D"


    return {

        "rating":

        rating,

        "grade":

        grade,

        "reasons":

        reasons

    }


# ==========================================================
# AI RATING DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🏅 AI Trade Rating"

    )


    ai_rating = calculate_ai_trade_rating()


    st.progress(

        ai_rating["rating"]

        /

        100

    )


    st.metric(

        "Grade",

        ai_rating["grade"]

    )


    st.metric(

        "Rating",

        f'{ai_rating["rating"]}/100'

    )


    for reason in ai_rating["reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# MARKET ALERT MEMORY
# ==========================================================

if "alert_memory" not in st.session_state:

    st.session_state.alert_memory = []


def save_alert_memory():

    alerts = generate_alert_intelligence()


    st.session_state.alert_memory.append(

        {

            "Time":

            current_time(),

            "Alerts":

            ", ".join(

                alerts

            )

        }

    )


    if len(

        st.session_state.alert_memory

    ) > 200:

        st.session_state.alert_memory.pop(

            0

        )


save_alert_memory()


# ==========================================================
# ALERT MEMORY DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🚨 Alert Memory"

    )


    alert_df = pd.DataFrame(

        st.session_state.alert_memory[-20:]

    )


    st.dataframe(

        alert_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# GOLD MARKET AI DECISION TREE
# ==========================================================

def gold_ai_decision_tree():

    rating = calculate_ai_trade_rating()

    command = final_gold_command()

    confirmation = market_confirmation_v2()


    if (

        rating["rating"] >= 80

        and

        confirmation["count"] >= 2

    ):

        decision = command["Action"]

    elif rating["rating"] >= 50:

        decision = "WAIT CONFIRMATION"

    else:

        decision = "NO TRADE"


    return {

        "decision":

        decision,

        "rating":

        rating["rating"]

    }


# ==========================================================
# DECISION TREE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🌳 AI Decision Tree"

    )


    tree = gold_ai_decision_tree()


    st.metric(

        "AI Decision",

        tree["decision"]

    )


    st.metric(

        "AI Score",

        f'{tree["rating"]}/100'

    )


# ==========================================================
# KẾT THÚC ĐOẠN 095
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 096
# ==========================================================

# ==========================================================
# AI MARKET EXPLANATION ENGINE
# ==========================================================

def generate_market_explanation():

    explanation = []

    decision = gold_ai_decision_tree()

    rating = calculate_ai_trade_rating()

    control = analyze_market_control()


    explanation.append(

        f"AI Decision: {decision['decision']}"

    )


    explanation.append(

        f"Market Rating: {rating['rating']}/100"

    )


    explanation.append(

        f"Market Controller: {control['Controller']}"

    )


    for reason in rating["reasons"]:

        explanation.append(

            reason

        )


    return explanation


# ==========================================================
# EXPLANATION DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🧠 AI Market Explanation"

    )


    explanation = generate_market_explanation()


    for item in explanation:

        st.write(

            "•",

            item

        )


# ==========================================================
# MARKET SCENARIO SIMULATOR
# ==========================================================

def simulate_market_scenario():

    scenarios = []


    current = gold_data


    if current:

        price_change = current["change"]


        if price_change > 0:

            scenarios.append(

                {

                    "Scenario":

                    "Continuation Up",

                    "Probability":

                    60

                }

            )


        else:

            scenarios.append(

                {

                    "Scenario":

                    "Continuation Down",

                    "Probability":

                    60

                }

            )


    scenarios.append(

        {

            "Scenario":

            "Reversal",

            "Probability":

            25

        }

    )


    scenarios.append(

        {

            "Scenario":

            "Sideway",

            "Probability":

            15

        }

    )


    return pd.DataFrame(

        scenarios

    )


# ==========================================================
# SCENARIO SIMULATION DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🔮 Scenario Simulator"

    )


    scenario_df = simulate_market_scenario()


    st.dataframe(

        scenario_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# GOLD RISK MANAGEMENT ENGINE
# ==========================================================

def gold_risk_management():

    setup = generate_gold_setup()

    management = {

        "Position":

        "Normal",

        "Stop":

        setup["Stop Loss"],

        "Target":

        setup["Take Profit"]

    }


    risk = smart_risk_controller()


    if risk["score"] < 50:

        management["Position"] = (

            "Reduce Size"

        )


    elif risk["score"] < 30:

        management["Position"] = (

            "Stop Trading"

        )


    return management


# ==========================================================
# RISK MANAGEMENT DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🛡 Gold Risk Management"

    )


    risk_management = gold_risk_management()


    risk_df = pd.DataFrame(

        {

            "Parameter":

            risk_management.keys(),

            "Value":

            risk_management.values()

        }

    )


    st.dataframe(

        risk_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# MARKET FINAL CHECKLIST
# ==========================================================

def final_market_checklist():

    checklist = {

        "Signal":

        False,

        "Risk":

        False,

        "Timing":

        False,

        "Confirmation":

        False,

        "Quality":

        False

    }


    if generate_master_signal()["signal"] != "WAIT":

        checklist["Signal"] = True


    if smart_risk_controller()["score"] >= 50:

        checklist["Risk"] = True


    if calculate_entry_timing()["timing"] != "WAIT":

        checklist["Timing"] = True


    if market_confirmation_v2()["count"] >= 2:

        checklist["Confirmation"] = True


    if calculate_trade_quality()["score"] >= 50:

        checklist["Quality"] = True


    return checklist


# ==========================================================
# CHECKLIST DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "✅ Final Market Checklist"

    )


    checklist = final_market_checklist()


    completed = 0


    for item, status in checklist.items():

        if status:

            st.success(

                f"✔ {item}"

            )

            completed += 1

        else:

            st.warning(

                f"✖ {item}"

            )


    st.progress(

        completed /

        len(checklist)

    )


# ==========================================================
# KẾT THÚC ĐOẠN 096
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 097
# ==========================================================

# ==========================================================
# MARKET HEALTH MONITOR
# ==========================================================

def calculate_market_health():

    health = 100

    warnings = []


    volatility = calculate_volatility()

    if volatility:

        if volatility["latest"] > (

            volatility["average"]

            *

            2

        ):

            health -= 25

            warnings.append(

                "Extreme volatility"

            )


    liquidity = analyze_liquidity()


    if liquidity:

        if liquidity["ratio"] < 0.7:

            health -= 20

            warnings.append(

                "Low liquidity"

            )


    noise = market_noise_filter()


    if noise["noise"] > 60:

        health -= 20

        warnings.append(

            "High market noise"

        )


    health = max(

        0,

        health

    )


    if health >= 80:

        status = "Healthy Market"

    elif health >= 50:

        status = "Caution Market"

    else:

        status = "Unstable Market"


    return {

        "health":

        health,

        "status":

        status,

        "warnings":

        warnings

    }


# ==========================================================
# MARKET HEALTH DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "❤️ Market Health"

    )


    health = calculate_market_health()


    st.progress(

        health["health"]

        /

        100

    )


    st.metric(

        "Health",

        f'{health["health"]}/100'

    )


    st.info(

        health["status"]

    )


    for warning in health["warnings"]:

        st.warning(

            warning

        )


# ==========================================================
# GOLD MARKET DOMINANCE INDEX
# ==========================================================

def calculate_gold_dominance():

    score = 50

    reasons = []


    gold = gold_data

    dxy = dxy_data


    if gold:

        if gold["change"] > 0:

            score += 20

            reasons.append(

                "Gold strength"

            )

        else:

            score -= 20

            reasons.append(

                "Gold weakness"

            )


    if dxy:

        if dxy["change"] < 0:

            score += 20

            reasons.append(

                "USD weakness supports gold"

            )

        else:

            score -= 20

            reasons.append(

                "USD strength pressures gold"

            )


    score = max(

        0,

        min(

            score,

            100

        )

    )


    if score >= 70:

        status = "Gold Dominant"

    elif score <= 30:

        status = "USD Dominant"

    else:

        status = "Balanced"


    return {

        "score":

        score,

        "status":

        status,

        "reasons":

        reasons

    }


# ==========================================================
# GOLD DOMINANCE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🥇 Gold Dominance Index"

    )


    dominance = calculate_gold_dominance()


    st.progress(

        dominance["score"]

        /

        100

    )


    st.metric(

        "Status",

        dominance["status"]

    )


    for reason in dominance["reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# MARKET OPERATOR MODE
# ==========================================================

def market_operator_mode():

    health = calculate_market_health()

    opportunity = calculate_opportunity_score_v2()

    risk = smart_risk_controller()


    if health["health"] < 40:

        return "PROTECT CAPITAL"


    if opportunity["score"] >= 70:

        return "HUNT OPPORTUNITY"


    if risk["score"] < 50:

        return "REDUCE ACTIVITY"


    return "NORMAL OPERATION"


# ==========================================================
# OPERATOR MODE DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🎛 Operator Mode"

    )


    st.info(

        market_operator_mode()

    )


# ==========================================================
# KẾT THÚC ĐOẠN 097
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 098
# ==========================================================

# ==========================================================
# MARKET INTELLIGENCE DASHBOARD ENGINE
# ==========================================================

def generate_dashboard_summary():

    health = calculate_market_health()

    dominance = calculate_gold_dominance()

    operator = market_operator_mode()

    intelligence = generate_market_intelligence()


    summary = {

        "Market Health":

        health["status"],

        "Gold Dominance":

        dominance["status"],

        "Operation":

        operator,

        "Trend":

        intelligence["Trend"],

        "Momentum":

        intelligence["Momentum"],

        "Opportunity":

        intelligence["Opportunity"]

    }


    return summary


# ==========================================================
# DASHBOARD SUMMARY DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🌐 WEOS Intelligence Dashboard"

    )


    dashboard_summary = generate_dashboard_summary()


    dashboard_df = pd.DataFrame(

        {

            "System":

            dashboard_summary.keys(),

            "Status":

            dashboard_summary.values()

        }

    )


    st.dataframe(

        dashboard_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# GOLD MARKET AI SCORE FUSION
# ==========================================================

def calculate_ai_fusion_score():

    scores = []

    reasons = []


    final_score = calculate_final_gold_score()

    confidence = calculate_confidence_v2()

    ai_rating = calculate_ai_trade_rating()

    execution = calculate_execution_score()


    scores.append(

        final_score["score"]

    )


    scores.append(

        confidence["score"]

    )


    scores.append(

        ai_rating["rating"]

    )


    scores.append(

        execution["score"]

    )


    average = sum(scores) / len(scores)


    if average >= 80:

        status = "Elite Setup"

    elif average >= 60:

        status = "Strong Setup"

    elif average >= 40:

        status = "Normal Setup"

    else:

        status = "Weak Setup"


    if final_score["score"] >= 70:

        reasons.append(

            "Final score strong"

        )


    if execution["score"] >= 70:

        reasons.append(

            "Execution condition good"

        )


    return {

        "score":

        round(

            average,

            1

        ),

        "status":

        status,

        "reasons":

        reasons

    }


# ==========================================================
# AI FUSION DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🧬 AI Fusion Score"

    )


    fusion = calculate_ai_fusion_score()


    st.progress(

        fusion["score"]

        /

        100

    )


    st.metric(

        "Fusion",

        f'{fusion["score"]}/100'

    )


    st.info(

        fusion["status"]

    )


    for reason in fusion["reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# MARKET SIGNAL CONSENSUS ENGINE
# ==========================================================

def calculate_signal_consensus():

    signals = []


    master = generate_master_signal()

    decision = trade_decision_matrix()

    ai_tree = gold_ai_decision_tree()


    signals.append(

        master["signal"]

    )


    signals.append(

        decision["decision"]

    )


    signals.append(

        ai_tree["decision"]

    )


    buy = 0

    sell = 0


    for signal in signals:

        if "BUY" in signal:

            buy += 1

        elif "SELL" in signal:

            sell += 1


    if buy > sell:

        result = "BUY CONSENSUS"

    elif sell > buy:

        result = "SELL CONSENSUS"

    else:

        result = "NO CONSENSUS"


    return {

        "result":

        result,

        "buy":

        buy,

        "sell":

        sell

    }


# ==========================================================
# CONSENSUS DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🤝 Signal Consensus"

    )


    consensus = calculate_signal_consensus()


    st.metric(

        "Consensus",

        consensus["result"]

    )


    col1, col2 = st.columns(

        2

    )


    with col1:

        st.metric(

            "BUY",

            consensus["buy"]

        )


    with col2:

        st.metric(

            "SELL",

            consensus["sell"]

        )


# ==========================================================
# KẾT THÚC ĐOẠN 098
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 099
# ==========================================================

# ==========================================================
# MARKET FINAL AUTHORITY ENGINE
# ==========================================================

def final_authority_engine():

    authority = {

        "Decision":

        "WAIT",

        "Score":

        0,

        "Reasons":

        []

    }


    fusion = calculate_ai_fusion_score()

    consensus = calculate_signal_consensus()

    health = calculate_market_health()


    score = 0


    if fusion["score"] >= 70:

        score += 40

        authority["Reasons"].append(

            "AI fusion supports setup"

        )


    if consensus["result"] != "NO CONSENSUS":

        score += 30

        authority["Reasons"].append(

            "Signal consensus detected"

        )


    if health["health"] >= 70:

        score += 30

        authority["Reasons"].append(

            "Market health acceptable"

        )


    authority["Score"] = min(

        score,

        100

    )


    if (

        authority["Score"] >= 80

        and

        consensus["result"]

        ==

        "BUY CONSENSUS"

    ):

        authority["Decision"] = "BUY"


    elif (

        authority["Score"] >= 80

        and

        consensus["result"]

        ==

        "SELL CONSENSUS"

    ):

        authority["Decision"] = "SELL"


    elif authority["Score"] >= 50:

        authority["Decision"] = "PREPARE"


    return authority


# ==========================================================
# AUTHORITY DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "👑 Final Authority Engine"

    )


    authority = final_authority_engine()


    st.metric(

        "Decision",

        authority["Decision"]

    )


    st.progress(

        authority["Score"]

        /

        100

    )


    st.metric(

        "Authority Score",

        f'{authority["Score"]}/100'

    )


    for reason in authority["Reasons"]:

        st.write(

            "•",

            reason

        )


# ==========================================================
# WEOS AUTO COMMENTARY ENGINE
# ==========================================================

def generate_weos_commentary():

    authority = final_authority_engine()

    commentary = []


    if authority["Decision"] == "BUY":

        commentary.append(

            "WEOS detects a potential bullish opportunity."

        )


    elif authority["Decision"] == "SELL":

        commentary.append(

            "WEOS detects a potential bearish opportunity."

        )


    elif authority["Decision"] == "PREPARE":

        commentary.append(

            "Market is preparing but needs confirmation."

        )


    else:

        commentary.append(

            "Market conditions are not suitable."

        )


    commentary.append(

        f"Confidence score: {authority['Score']}%"

    )


    return commentary


# ==========================================================
# COMMENTARY DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "💬 WEOS Commentary"

    )


    commentary = generate_weos_commentary()


    for line in commentary:

        st.info(

            line

        )


# ==========================================================
# MARKET SNAPSHOT DATABASE
# ==========================================================

if "market_snapshot" not in st.session_state:

    st.session_state.market_snapshot = []


def save_market_snapshot():

    authority = final_authority_engine()

    snapshot = {

        "Time":

        current_time(),

        "Decision":

        authority["Decision"],

        "Score":

        authority["Score"],

        "Gold":

        gold_data["price"]

        if gold_data else None

    }


    st.session_state.market_snapshot.append(

        snapshot

    )


    if len(

        st.session_state.market_snapshot

    ) > 500:

        st.session_state.market_snapshot.pop(

            0

        )


save_market_snapshot()


# ==========================================================
# SNAPSHOT DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "📸 Market Snapshot"

    )


    snapshot_df = pd.DataFrame(

        st.session_state.market_snapshot[-20:]

    )


    st.dataframe(

        snapshot_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# KẾT THÚC ĐOẠN 099
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 100
# ==========================================================

# ==========================================================
# MARKET EVOLUTION TRACKER
# ==========================================================

if "market_evolution" not in st.session_state:

    st.session_state.market_evolution = []


def save_market_evolution():

    authority = final_authority_engine()

    fusion = calculate_ai_fusion_score()

    record = {

        "Time":

        current_time(),

        "Decision":

        authority["Decision"],

        "Authority":

        authority["Score"],

        "Fusion":

        fusion["score"],

        "Status":

        fusion["status"]

    }


    st.session_state.market_evolution.append(

        record

    )


    if len(

        st.session_state.market_evolution

    ) > 300:

        st.session_state.market_evolution.pop(

            0

        )


save_market_evolution()


# ==========================================================
# EVOLUTION DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "📈 Market Evolution"

    )


    evolution_df = pd.DataFrame(

        st.session_state.market_evolution[-20:]

    )


    st.dataframe(

        evolution_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# WEOS AUTONOMOUS DECISION CORE
# ==========================================================

def autonomous_decision_core():

    authority = final_authority_engine()

    risk = smart_risk_controller()

    execution = calculate_execution_score()


    core = {

        "Decision":

        "WAIT",

        "Confidence":

        0,

        "Risk":

        risk["status"],

        "Execution":

        execution["score"]

    }


    confidence = (

        authority["Score"]

        +

        execution["score"]

    ) / 2


    core["Confidence"] = round(

        confidence,

        1

    )


    if (

        authority["Decision"]

        in

        [

            "BUY",

            "SELL"

        ]

        and

        confidence >= 80

    ):

        core["Decision"] = authority["Decision"]


    elif confidence >= 50:

        core["Decision"] = "PREPARE"


    return core


# ==========================================================
# AUTONOMOUS CORE DISPLAY
# ==========================================================

if st.session_state.page == "Gold":

    st.divider()

    st.subheader(

        "🧠 Autonomous Decision Core"

    )


    core = autonomous_decision_core()


    core_df = pd.DataFrame(

        {

            "System":

            core.keys(),

            "Value":

            core.values()

        }

    )


    st.dataframe(

        core_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# WEOS FINAL STATUS ENGINE
# ==========================================================

def weos_final_status():

    core = autonomous_decision_core()

    health = calculate_market_health()


    if (

        core["Decision"]

        ==

        "WAIT"

    ):

        status = "Monitoring Market"


    elif (

        core["Risk"]

        ==

        "Stop Trading"

    ):

        status = "Risk Protection Mode"


    elif (

        core["Confidence"]

        >=

        80

    ):

        status = "High Probability Setup"


    else:

        status = "Active Analysis"


    return {

        "Status":

        status,

        "Decision":

        core["Decision"],

        "Confidence":

        core["Confidence"],

        "Health":

        health["health"]

    }


# ==========================================================
# FINAL STATUS DISPLAY
# ==========================================================

if st.session_state.page == "Dashboard":

    st.divider()

    st.subheader(

        "🚦 WEOS Final Status"

    )


    status = weos_final_status()


    status_df = pd.DataFrame(

        {

            "Metric":

            status.keys(),

            "Value":

            status.values()

        }

    )


    st.dataframe(

        status_df,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# KẾT THÚC ĐOẠN 100
# ==========================================================
