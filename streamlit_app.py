# ==========================================================
# WEOS
# ĐOẠN 001
# ==========================================================

import asyncio
import json
import math
import os
import random
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import aiohttp
import httpx
import networkx as nx
import numpy as np
import orjson
import pandas as pd
import plotly.graph_objects as go
import pydeck as pdk
import requests
import streamlit as st
import websockets
from bs4 import BeautifulSoup
from cachetools import TTLCache
from dateutil import parser as date_parser
from geopy.distance import geodesic
from pydantic import BaseModel, Field
from shapely.geometry import LineString, Point

APP_NAME = "WEOS"
APP_FULL_NAME = "World Economic Observation System"
APP_VERSION = "1.0.0"
APP_AUTHOR = "OpenAI + Duy Trịnh"
APP_LANGUAGE = "vi"
APP_TIMEZONE = timezone.utc
APP_THEME = "dark"
FRAME_INTERVAL = 1
DEFAULT_ZOOM = 1
MIN_ZOOM = 0
MAX_ZOOM = 20
DEFAULT_CENTER = (20.0, 0.0)
EARTH_RADIUS_KM = 6371.0
REAL_DATA_ONLY = True
AUTO_DISCOVERY = True
AUTO_NODE_CREATION = True
ENABLE_TIMELINE = True
ENABLE_PULSE = True
ENABLE_FLOW = True
ENABLE_INDICATORS = True
ENABLE_NEWS = True
ENABLE_MARKETS = True
ENABLE_MACRO = True
ENABLE_INFRASTRUCTURE = True
ENABLE_LOGISTICS = True
ENABLE_PORTS = True
ENABLE_AIRPORTS = True
ENABLE_FACTORIES = True
ENABLE_POWER_PLANTS = True
ENABLE_DATA_CENTERS = True
ENABLE_ETF = True
ENABLE_COMPANIES = True
ENABLE_BANKS = True
ENABLE_MINES = True
ENABLE_HISTORY = True
ENABLE_SEARCH = True
ENABLE_GLOBE = True
ENABLE_MAP = True
ENABLE_BACKGROUND_SYNC = True
CACHE = TTLCache(maxsize=10000, ttl=60)

if "weos_initialized" not in st.session_state:
    st.session_state.weos_initialized = False
    st.session_state.nodes = {}
    st.session_state.edges = {}
    st.session_state.flows = {}
    st.session_state.timeline = {}
    st.session_state.market = {}
    st.session_state.news = {}
    st.session_state.indicators = {}
    st.session_state.viewport = DEFAULT_CENTER
    st.session_state.zoom = DEFAULT_ZOOM
    st.session_state.selected_node = None
    st.session_state.last_refresh = None
    st.session_state.running = True

# ==========================================================
# KẾT THÚC ĐOẠN 001
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 002
# ==========================================================

class NodeType(str, Enum):
    WORLD = "world"
    CONTINENT = "continent"
    COUNTRY = "country"
    PROVINCE = "province"
    CITY = "city"
    DISTRICT = "district"
    CAPITAL = "capital"
    COMPANY = "company"
    FACTORY = "factory"
    HEADQUARTERS = "headquarters"
    PORT = "port"
    AIRPORT = "airport"
    WAREHOUSE = "warehouse"
    LOGISTICS = "logistics"
    POWER_PLANT = "power_plant"
    DATA_CENTER = "data_center"
    MINE = "mine"
    OIL_FIELD = "oil_field"
    GAS_FIELD = "gas_field"
    EXCHANGE = "exchange"
    ETF = "etf"
    BANK = "bank"
    CENTRAL_BANK = "central_bank"


class FlowType(str, Enum):
    CAPITAL = "capital"
    GOODS = "goods"
    ENERGY = "energy"
    FOREX = "forex"
    SUPPLY_CHAIN = "supply_chain"
    LOGISTICS = "logistics"
    CREDIT = "credit"
    INVESTMENT = "investment"


@dataclass(slots=True)
class EconomicNode:
    id: str
    name: str
    node_type: NodeType
    latitude: float
    longitude: float
    country: str = ""
    region: str = ""
    parent_id: str = ""
    founded: str = ""
    status: str = "active"
    pulse: float = 0.0
    inflow_usd: float = 0.0
    outflow_usd: float = 0.0
    netflow_usd: float = 0.0
    color: str = "#00FF99"
    visible: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class EconomicFlow:
    id: str
    source: str
    target: str
    flow_type: FlowType
    amount_usd: float = 0.0
    color: str = "#00FF99"
    width: float = 1.0
    animated: bool = True
    updated_at: Optional[datetime] = None


class GlobalGraph:
    def __init__(self) -> None:
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, EconomicNode] = {}
        self.flows: Dict[str, EconomicFlow] = {}

# ==========================================================
# KẾT THÚC ĐOẠN 002
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 003
# ==========================================================

GLOBAL_GRAPH = GlobalGraph()


class DataStatus(str, Enum):
    LIVE = "live"
    DELAYED = "delayed"
    SCHEDULED = "scheduled"
    HISTORICAL = "historical"
    WAITING = "waiting"
    OFFLINE = "offline"


class DataSource(BaseModel):
    id: str
    name: str
    url: str
    enabled: bool = True
    priority: int = 0
    realtime: bool = False
    refresh_seconds: int = 60
    timeout: int = 30
    status: DataStatus = DataStatus.WAITING
    last_update: Optional[datetime] = None


DATA_SOURCES: Dict[str, DataSource] = {}
BACKGROUND_TASKS: Dict[str, asyncio.Task] = {}
HTTP_SESSION: Optional[aiohttp.ClientSession] = None
ASYNC_CLIENT: Optional[httpx.AsyncClient] = None
SYNC_LOCK = threading.Lock()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def unix_time() -> int:
    return int(time.time())


def generate_id(prefix: str) -> str:
    return f"{prefix}_{unix_time()}_{random.randint(100000,999999)}"


def register_node(node: EconomicNode) -> None:
    GLOBAL_GRAPH.nodes[node.id] = node
    GLOBAL_GRAPH.graph.add_node(node.id)


def register_flow(flow: EconomicFlow) -> None:
    GLOBAL_GRAPH.flows[flow.id] = flow
    GLOBAL_GRAPH.graph.add_edge(
        flow.source,
        flow.target,
        id=flow.id,
        flow_type=flow.flow_type.value,
        amount_usd=flow.amount_usd,
    )


def node_exists(node_id: str) -> bool:
    return node_id in GLOBAL_GRAPH.nodes


def flow_exists(flow_id: str) -> bool:
    return flow_id in GLOBAL_GRAPH.flows


def get_node(node_id: str) -> Optional[EconomicNode]:
    return GLOBAL_GRAPH.nodes.get(node_id)


def get_flow(flow_id: str) -> Optional[EconomicFlow]:
    return GLOBAL_GRAPH.flows.get(flow_id)


# ==========================================================
# KẾT THÚC ĐOẠN 003
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 004
# ==========================================================

class DataEngine:

    def __init__(self) -> None:
        self.sources: Dict[str, DataSource] = {}

    def add_source(self, source: DataSource) -> None:
        self.sources[source.id] = source
        DATA_SOURCES[source.id] = source

    def remove_source(self, source_id: str) -> None:
        self.sources.pop(source_id, None)
        DATA_SOURCES.pop(source_id, None)

    def get_source(self, source_id: str) -> Optional[DataSource]:
        return self.sources.get(source_id)

    def all_sources(self) -> List[DataSource]:
        return list(self.sources.values())

    def mark_live(self, source_id: str) -> None:
        source = self.get_source(source_id)
        if source:
            source.status = DataStatus.LIVE
            source.last_update = utc_now()

    def mark_waiting(self, source_id: str) -> None:
        source = self.get_source(source_id)
        if source:
            source.status = DataStatus.WAITING

    def mark_offline(self, source_id: str) -> None:
        source = self.get_source(source_id)
        if source:
            source.status = DataStatus.OFFLINE

    async def initialize_http(self) -> None:
        global HTTP_SESSION
        global ASYNC_CLIENT
        if HTTP_SESSION is None:
            HTTP_SESSION = aiohttp.ClientSession()
        if ASYNC_CLIENT is None:
            ASYNC_CLIENT = httpx.AsyncClient(timeout=30)

    async def shutdown_http(self) -> None:
        global HTTP_SESSION
        global ASYNC_CLIENT
        if HTTP_SESSION is not None:
            await HTTP_SESSION.close()
            HTTP_SESSION = None
        if ASYNC_CLIENT is not None:
            await ASYNC_CLIENT.aclose()
            ASYNC_CLIENT = None


DATA_ENGINE = DataEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 004
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 005
# ==========================================================

DATA_ENGINE.add_source(
    DataSource(
        id="gold_price",
        name="Gold Price",
        url="",
        realtime=True,
        refresh_seconds=1,
        priority=100,
    )
)

DATA_ENGINE.add_source(
    DataSource(
        id="forex",
        name="Forex Market",
        url="",
        realtime=True,
        refresh_seconds=1,
        priority=95,
    )
)

DATA_ENGINE.add_source(
    DataSource(
        id="dxy",
        name="US Dollar Index",
        url="",
        realtime=True,
        refresh_seconds=1,
        priority=90,
    )
)

DATA_ENGINE.add_source(
    DataSource(
        id="stocks",
        name="Global Stocks",
        url="",
        realtime=True,
        refresh_seconds=1,
        priority=85,
    )
)

DATA_ENGINE.add_source(
    DataSource(
        id="crypto",
        name="Cryptocurrency",
        url="",
        realtime=True,
        refresh_seconds=1,
        priority=80,
    )
)

DATA_ENGINE.add_source(
    DataSource(
        id="macro_calendar",
        name="Economic Calendar",
        url="",
        realtime=False,
        refresh_seconds=60,
        priority=75,
    )
)

DATA_ENGINE.add_source(
    DataSource(
        id="world_news",
        name="World Economic News",
        url="",
        realtime=False,
        refresh_seconds=30,
        priority=70,
    )
)

DATA_ENGINE.add_source(
    DataSource(
        id="infrastructure",
        name="Infrastructure Discovery",
        url="",
        realtime=False,
        refresh_seconds=3600,
        priority=60,
    )
)

# ==========================================================
# KẾT THÚC ĐOẠN 005
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 006
# ==========================================================

class MarketState(BaseModel):
    symbol: str
    price: float = 0.0
    change: float = 0.0
    change_percent: float = 0.0
    volume: float = 0.0
    timestamp: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING


MARKETS: Dict[str, MarketState] = {}


def register_market(symbol: str) -> None:
    if symbol not in MARKETS:
        MARKETS[symbol] = MarketState(symbol=symbol)


register_market("XAUUSD")
register_market("DXY")
register_market("EURUSD")
register_market("GBPUSD")
register_market("USDJPY")
register_market("USDCNY")
register_market("BTCUSD")
register_market("ETHUSD")
register_market("SPX")
register_market("NDX")
register_market("DJI")
register_market("VIX")
register_market("US10Y")


def update_market(
    symbol: str,
    price: float,
    change: float,
    change_percent: float,
    volume: float,
    source: str,
) -> None:
    if symbol not in MARKETS:
        register_market(symbol)
    market = MARKETS[symbol]
    market.price = price
    market.change = change
    market.change_percent = change_percent
    market.volume = volume
    market.source = source
    market.timestamp = utc_now()
    market.status = DataStatus.LIVE


def get_market(symbol: str) -> Optional[MarketState]:
    return MARKETS.get(symbol)


# ==========================================================
# KẾT THÚC ĐOẠN 006
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 007
# ==========================================================

class WorldClock:

    def __init__(self) -> None:
        self.started_at = utc_now()
        self.last_frame = utc_now()
        self.frame = 0

    def tick(self) -> None:
        self.frame += 1
        self.last_frame = utc_now()

    @property
    def uptime(self) -> float:
        return (utc_now() - self.started_at).total_seconds()


WORLD_CLOCK = WorldClock()


class PulseEngine:

    def __init__(self) -> None:
        self.period = 3.0

    def calculate(self, node: EconomicNode) -> float:
        total = abs(node.inflow_usd) + abs(node.outflow_usd)
        if total <= 0:
            return 0.15
        value = math.log10(total + 1.0) / 12.0
        return max(0.15, min(value, 1.0))

    def update_node(self, node: EconomicNode) -> None:
        node.netflow_usd = node.inflow_usd - node.outflow_usd
        node.pulse = self.calculate(node)

    def update_all(self) -> None:
        for node in GLOBAL_GRAPH.nodes.values():
            self.update_node(node)


PULSE_ENGINE = PulseEngine()


def pulse_alpha(node: EconomicNode) -> float:
    phase = time.time() / PULSE_ENGINE.period
    wave = (math.sin(phase * math.pi * 2.0) + 1.0) * 0.5
    return 0.2 + wave * node.pulse * 0.8


# ==========================================================
# KẾT THÚC ĐOẠN 007
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 008
# ==========================================================

class TimelineEvent(BaseModel):
    id: str
    node_id: str
    timestamp: datetime
    event_type: str
    title: str
    description: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


TIMELINE_EVENTS: Dict[str, List[TimelineEvent]] = defaultdict(list)


def add_timeline_event(
    node_id: str,
    event_type: str,
    title: str,
    description: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> TimelineEvent:
    event = TimelineEvent(
        id=generate_id("event"),
        node_id=node_id,
        timestamp=utc_now(),
        event_type=event_type,
        title=title,
        description=description,
        metadata=metadata or {},
    )
    TIMELINE_EVENTS[node_id].append(event)
    node = get_node(node_id)
    if node is not None:
        node.history.append(event.model_dump(mode="json"))
    return event


def get_timeline(node_id: str) -> List[TimelineEvent]:
    return sorted(
        TIMELINE_EVENTS.get(node_id, []),
        key=lambda item: item.timestamp,
    )


def clear_timeline(node_id: str) -> None:
    TIMELINE_EVENTS.pop(node_id, None)
    node = get_node(node_id)
    if node is not None:
        node.history.clear()


# ==========================================================
# KẾT THÚC ĐOẠN 008
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 009
# ==========================================================

class ViewportState(BaseModel):
    latitude: float = DEFAULT_CENTER[0]
    longitude: float = DEFAULT_CENTER[1]
    zoom: float = DEFAULT_ZOOM
    pitch: float = 0.0
    bearing: float = 0.0


VIEWPORT = ViewportState()


def set_viewport(
    latitude: float,
    longitude: float,
    zoom: float,
    pitch: Optional[float] = None,
    bearing: Optional[float] = None,
) -> None:
    VIEWPORT.latitude = latitude
    VIEWPORT.longitude = longitude
    VIEWPORT.zoom = max(MIN_ZOOM, min(MAX_ZOOM, zoom))
    if pitch is not None:
        VIEWPORT.pitch = pitch
    if bearing is not None:
        VIEWPORT.bearing = bearing


def focus_node(node_id: str) -> bool:
    node = get_node(node_id)
    if node is None:
        return False
    VIEWPORT.latitude = node.latitude
    VIEWPORT.longitude = node.longitude
    st.session_state.selected_node = node_id
    return True


def zoom_in(step: float = 1.0) -> None:
    VIEWPORT.zoom = min(MAX_ZOOM, VIEWPORT.zoom + step)


def zoom_out(step: float = 1.0) -> None:
    VIEWPORT.zoom = max(MIN_ZOOM, VIEWPORT.zoom - step)


def current_view() -> Dict[str, float]:
    return {
        "latitude": VIEWPORT.latitude,
        "longitude": VIEWPORT.longitude,
        "zoom": VIEWPORT.zoom,
        "pitch": VIEWPORT.pitch,
        "bearing": VIEWPORT.bearing,
    }


# ==========================================================
# KẾT THÚC ĐOẠN 009
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 010
# ==========================================================

class SearchEngine:

    def __init__(self) -> None:
        self.index: Dict[str, Set[str]] = defaultdict(set)

    def normalize(self, text: str) -> str:
        return text.strip().lower()

    def index_node(self, node: EconomicNode) -> None:
        words = self.normalize(node.name).split()
        for word in words:
            self.index[word].add(node.id)
        self.index[self.normalize(node.id)].add(node.id)
        if node.country:
            self.index[self.normalize(node.country)].add(node.id)
        if node.region:
            self.index[self.normalize(node.region)].add(node.id)

    def remove_node(self, node_id: str) -> None:
        for key in list(self.index.keys()):
            self.index[key].discard(node_id)
            if not self.index[key]:
                del self.index[key]

    def rebuild(self) -> None:
        self.index.clear()
        for node in GLOBAL_GRAPH.nodes.values():
            self.index_node(node)

    def search(self, keyword: str) -> List[EconomicNode]:
        keyword = self.normalize(keyword)
        result: Set[str] = set()
        for key, values in self.index.items():
            if keyword in key:
                result.update(values)
        return sorted(
            (GLOBAL_GRAPH.nodes[i] for i in result),
            key=lambda item: item.name,
        )


SEARCH_ENGINE = SearchEngine()


def register_node_and_index(node: EconomicNode) -> None:
    register_node(node)
    SEARCH_ENGINE.index_node(node)


# ==========================================================
# KẾT THÚC ĐOẠN 010
# ==========================================================
