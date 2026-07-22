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

