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
