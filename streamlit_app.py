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
# ==========================================================
# WEOS
# ĐOẠN 011
# ==========================================================

class FlowEngine:

    def create(
        self,
        source: str,
        target: str,
        flow_type: FlowType,
        amount_usd: float = 0.0,
        color: str = "#00FF99",
        width: float = 1.0,
    ) -> EconomicFlow:
        flow = EconomicFlow(
            id=generate_id("flow"),
            source=source,
            target=target,
            flow_type=flow_type,
            amount_usd=amount_usd,
            color=color,
            width=width,
            updated_at=utc_now(),
        )
        register_flow(flow)
        return flow

    def update_amount(self, flow_id: str, amount_usd: float) -> bool:
        flow = get_flow(flow_id)
        if flow is None:
            return False
        flow.amount_usd = amount_usd
        flow.updated_at = utc_now()
        if GLOBAL_GRAPH.graph.has_edge(flow.source, flow.target):
            GLOBAL_GRAPH.graph[flow.source][flow.target]["amount_usd"] = amount_usd
        return True

    def remove(self, flow_id: str) -> bool:
        flow = get_flow(flow_id)
        if flow is None:
            return False
        if GLOBAL_GRAPH.graph.has_edge(flow.source, flow.target):
            GLOBAL_GRAPH.graph.remove_edge(flow.source, flow.target)
        GLOBAL_GRAPH.flows.pop(flow_id, None)
        return True

    def incoming(self, node_id: str) -> List[EconomicFlow]:
        return [
            flow
            for flow in GLOBAL_GRAPH.flows.values()
            if flow.target == node_id
        ]

    def outgoing(self, node_id: str) -> List[EconomicFlow]:
        return [
            flow
            for flow in GLOBAL_GRAPH.flows.values()
            if flow.source == node_id
        ]

    def refresh_node(self, node_id: str) -> None:
        node = get_node(node_id)
        if node is None:
            return
        node.inflow_usd = sum(f.amount_usd for f in self.incoming(node_id))
        node.outflow_usd = sum(f.amount_usd for f in self.outgoing(node_id))
        PULSE_ENGINE.update_node(node)


FLOW_ENGINE = FlowEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 011
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 012
# ==========================================================

class NodeEngine:

    def create(
        self,
        name: str,
        node_type: NodeType,
        latitude: float,
        longitude: float,
        country: str = "",
        region: str = "",
        parent_id: str = "",
        founded: str = "",
    ) -> EconomicNode:
        node = EconomicNode(
            id=generate_id(node_type.value),
            name=name,
            node_type=node_type,
            latitude=latitude,
            longitude=longitude,
            country=country,
            region=region,
            parent_id=parent_id,
            founded=founded,
        )
        register_node_and_index(node)
        add_timeline_event(
            node.id,
            "created",
            f"{name} created",
        )
        return node

    def delete(self, node_id: str) -> bool:
        node = get_node(node_id)
        if node is None:
            return False
        SEARCH_ENGINE.remove_node(node_id)
        clear_timeline(node_id)
        GLOBAL_GRAPH.nodes.pop(node_id, None)
        if GLOBAL_GRAPH.graph.has_node(node_id):
            GLOBAL_GRAPH.graph.remove_node(node_id)
        return True

    def update_location(
        self,
        node_id: str,
        latitude: float,
        longitude: float,
    ) -> bool:
        node = get_node(node_id)
        if node is None:
            return False
        node.latitude = latitude
        node.longitude = longitude
        return True

    def all(self) -> List[EconomicNode]:
        return list(GLOBAL_GRAPH.nodes.values())

    def visible(self) -> List[EconomicNode]:
        return [n for n in GLOBAL_GRAPH.nodes.values() if n.visible]


NODE_ENGINE = NodeEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 012
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 013
# ==========================================================

class RenderEngine:

    def __init__(self) -> None:
        self.node_layer = None
        self.flow_layer = None

    def node_dataframe(self) -> pd.DataFrame:
        rows = []
        for node in NODE_ENGINE.visible():
            rows.append(
                {
                    "id": node.id,
                    "name": node.name,
                    "type": node.node_type.value,
                    "lat": node.latitude,
                    "lon": node.longitude,
                    "pulse": node.pulse,
                    "inflow": node.inflow_usd,
                    "outflow": node.outflow_usd,
                    "netflow": node.netflow_usd,
                    "color": node.color,
                    "alpha": pulse_alpha(node),
                }
            )
        return pd.DataFrame(rows)

    def flow_dataframe(self) -> pd.DataFrame:
        rows = []
        for flow in GLOBAL_GRAPH.flows.values():
            source = get_node(flow.source)
            target = get_node(flow.target)
            if source is None or target is None:
                continue
            rows.append(
                {
                    "source_lat": source.latitude,
                    "source_lon": source.longitude,
                    "target_lat": target.latitude,
                    "target_lon": target.longitude,
                    "amount_usd": flow.amount_usd,
                    "type": flow.flow_type.value,
                    "color": flow.color,
                    "width": flow.width,
                }
            )
        return pd.DataFrame(rows)

    def refresh(self) -> None:
        WORLD_CLOCK.tick()
        PULSE_ENGINE.update_all()

RENDER_ENGINE = RenderEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 013
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 014
# ==========================================================

class Theme:

    BACKGROUND = "#05070B"
    LAND = "#0D1724"
    OCEAN = "#03060A"
    GRID = "#1B2430"
    TEXT = "#F5F7FA"
    GREEN = "#00FF99"
    GREEN_DARK = "#00C97A"
    RED = "#FF4D6D"
    RED_DARK = "#C81D4F"
    BLUE = "#00C8FF"
    ORANGE = "#FFB547"


THEME = Theme()


def build_deck() -> pdk.Deck:
    nodes = RENDER_ENGINE.node_dataframe()

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=nodes,
        get_position="[lon, lat]",
        get_radius="50000 + pulse * 150000",
        get_fill_color="[0,255,153,255*alpha]",
        pickable=True,
        auto_highlight=True,
    )

    view_state = pdk.ViewState(
        latitude=VIEWPORT.latitude,
        longitude=VIEWPORT.longitude,
        zoom=VIEWPORT.zoom,
        pitch=VIEWPORT.pitch,
        bearing=VIEWPORT.bearing,
    )

    return pdk.Deck(
        map_style=None,
        initial_view_state=view_state,
        layers=[layer],
        tooltip={
            "html": (
                "<b>{name}</b><br/>"
                "Loại: {type}<br/>"
                "Dòng tiền vào: ${inflow}<br/>"
                "Dòng tiền ra: ${outflow}<br/>"
                "Dòng tiền ròng: ${netflow}"
            )
        },
    )

# ==========================================================
# KẾT THÚC ĐOẠN 014
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 015
# ==========================================================

def initialize_app() -> None:
    if st.session_state.weos_initialized:
        return
    st.set_page_config(
        page_title=APP_FULL_NAME,
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.session_state.weos_initialized = True


def render_header() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background:{THEME.BACKGROUND};
            color:{THEME.TEXT};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title(APP_NAME)
    st.caption(APP_FULL_NAME)


def render_map() -> None:
    deck = build_deck()
    st.pydeck_chart(deck, use_container_width=True)


def render_sidebar() -> None:
    with st.sidebar:
        st.header("WEOS")
        st.write(f"Nodes: {len(GLOBAL_GRAPH.nodes)}")
        st.write(f"Flows: {len(GLOBAL_GRAPH.flows)}")
        st.write(f"Markets: {len(MARKETS)}")
        st.write(f"Sources: {len(DATA_SOURCES)}")
        keyword = st.text_input("Tìm kiếm")
        if keyword:
            results = SEARCH_ENGINE.search(keyword)
            for node in results:
                if st.button(node.name, key=node.id):
                    focus_node(node.id)


def main() -> None:
    initialize_app()
    RENDER_ENGINE.refresh()
    render_header()
    render_sidebar()
    render_map()


if __name__ == "__main__":
    main()

# ==========================================================
# KẾT THÚC ĐOẠN 015
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 016
# ==========================================================

class BackgroundSyncEngine:

    def __init__(self) -> None:
        self.running = False
        self.tasks: Dict[str, asyncio.Task] = {}

    async def sync_market(self) -> None:
        while self.running:
            await asyncio.sleep(1)

    async def sync_macro(self) -> None:
        while self.running:
            await asyncio.sleep(60)

    async def sync_news(self) -> None:
        while self.running:
            await asyncio.sleep(30)

    async def sync_infrastructure(self) -> None:
        while self.running:
            await asyncio.sleep(3600)

    async def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.tasks["market"] = asyncio.create_task(self.sync_market())
        self.tasks["macro"] = asyncio.create_task(self.sync_macro())
        self.tasks["news"] = asyncio.create_task(self.sync_news())
        self.tasks["infrastructure"] = asyncio.create_task(
            self.sync_infrastructure()
        )

    async def stop(self) -> None:
        self.running = False
        for task in self.tasks.values():
            task.cancel()
        self.tasks.clear()


BACKGROUND_SYNC_ENGINE = BackgroundSyncEngine()


async def ensure_background_started() -> None:
    if not BACKGROUND_SYNC_ENGINE.running:
        await DATA_ENGINE.initialize_http()
        await BACKGROUND_SYNC_ENGINE.start()


# ==========================================================
# KẾT THÚC ĐOẠN 016
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 017
# ==========================================================

class WebSocketManager:

    def __init__(self) -> None:
        self.connections: Dict[str, websockets.ClientConnection] = {}
        self.running = False

    async def connect(self, source: DataSource) -> None:
        if not source.url:
            return
        try:
            connection = await websockets.connect(
                source.url,
                ping_interval=20,
                ping_timeout=20,
                max_size=None,
            )
            self.connections[source.id] = connection
            DATA_ENGINE.mark_live(source.id)
        except Exception:
            DATA_ENGINE.mark_offline(source.id)

    async def disconnect(self, source_id: str) -> None:
        connection = self.connections.pop(source_id, None)
        if connection is not None:
            await connection.close()

    async def disconnect_all(self) -> None:
        for source_id in list(self.connections.keys()):
            await self.disconnect(source_id)

    async def receive(self, source_id: str) -> Optional[Any]:
        connection = self.connections.get(source_id)
        if connection is None:
            return None
        try:
            message = await connection.recv()
            return orjson.loads(message)
        except Exception:
            DATA_ENGINE.mark_offline(source_id)
            return None

    async def send(self, source_id: str, payload: Dict[str, Any]) -> bool:
        connection = self.connections.get(source_id)
        if connection is None:
            return False
        try:
            await connection.send(orjson.dumps(payload))
            return True
        except Exception:
            DATA_ENGINE.mark_offline(source_id)
            return False


WEBSOCKET_MANAGER = WebSocketManager()

# ==========================================================
# KẾT THÚC ĐOẠN 017
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 018
# ==========================================================

class HttpDataFetcher:

    async def get_json(
        self,
        source_id: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> Optional[Any]:
        if ASYNC_CLIENT is None:
            return None
        try:
            response = await ASYNC_CLIENT.get(url, headers=headers)
            response.raise_for_status()
            DATA_ENGINE.mark_live(source_id)
            return response.json()
        except Exception:
            DATA_ENGINE.mark_offline(source_id)
            return None

    async def get_text(
        self,
        source_id: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        if ASYNC_CLIENT is None:
            return None
        try:
            response = await ASYNC_CLIENT.get(url, headers=headers)
            response.raise_for_status()
            DATA_ENGINE.mark_live(source_id)
            return response.text
        except Exception:
            DATA_ENGINE.mark_offline(source_id)
            return None

    async def get_bytes(
        self,
        source_id: str,
        url: str,
    ) -> Optional[bytes]:
        if ASYNC_CLIENT is None:
            return None
        try:
            response = await ASYNC_CLIENT.get(url)
            response.raise_for_status()
            DATA_ENGINE.mark_live(source_id)
            return response.content
        except Exception:
            DATA_ENGINE.mark_offline(source_id)
            return None


HTTP_FETCHER = HttpDataFetcher()

# ==========================================================
# KẾT THÚC ĐOẠN 018
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 019
# ==========================================================

class Scheduler:

    def __init__(self) -> None:
        self.jobs: Dict[str, Dict[str, Any]] = {}

    def add(
        self,
        job_id: str,
        interval: int,
        callback: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.jobs[job_id] = {
            "interval": interval,
            "callback": callback,
            "args": args,
            "kwargs": kwargs,
            "last_run": 0,
        }

    async def run_once(self) -> None:
        now = unix_time()
        for job in self.jobs.values():
            if now - job["last_run"] < job["interval"]:
                continue
            result = job["callback"](
                *job["args"],
                **job["kwargs"],
            )
            if asyncio.iscoroutine(result):
                await result
            job["last_run"] = now

    async def loop(self) -> None:
        while True:
            await self.run_once()
            await asyncio.sleep(1)

    def remove(self, job_id: str) -> None:
        self.jobs.pop(job_id, None)

    def clear(self) -> None:
        self.jobs.clear()


SCHEDULER = Scheduler()

# ==========================================================
# KẾT THÚC ĐOẠN 019
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 020
# ==========================================================

class EventBus:

    def __init__(self) -> None:
        self.listeners: Dict[str, List[Callable[..., Any]]] = defaultdict(list)

    def subscribe(
        self,
        event: str,
        callback: Callable[..., Any],
    ) -> None:
        self.listeners[event].append(callback)

    def unsubscribe(
        self,
        event: str,
        callback: Callable[..., Any],
    ) -> None:
        if event not in self.listeners:
            return
        if callback in self.listeners[event]:
            self.listeners[event].remove(callback)

    async def emit(
        self,
        event: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        callbacks = self.listeners.get(event, [])
        for callback in callbacks:
            result = callback(*args, **kwargs)
            if asyncio.iscoroutine(result):
                await result

    def clear(self) -> None:
        self.listeners.clear()


EVENT_BUS = EventBus()


async def publish_market_update(symbol: str) -> None:
    market = get_market(symbol)
    if market is not None:
        await EVENT_BUS.emit("market_update", market)


async def publish_node_update(node_id: str) -> None:
    node = get_node(node_id)
    if node is not None:
        await EVENT_BUS.emit("node_update", node)


# ==========================================================
# KẾT THÚC ĐOẠN 020
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 021
# ==========================================================

class MetricsEngine:

    def __init__(self) -> None:
        self.metrics: Dict[str, Any] = {}

    def update(self) -> None:
        self.metrics["nodes"] = len(GLOBAL_GRAPH.nodes)
        self.metrics["flows"] = len(GLOBAL_GRAPH.flows)
        self.metrics["markets"] = len(MARKETS)
        self.metrics["sources"] = len(DATA_SOURCES)
        self.metrics["timeline_events"] = sum(
            len(events) for events in TIMELINE_EVENTS.values()
        )
        self.metrics["uptime"] = WORLD_CLOCK.uptime
        self.metrics["frame"] = WORLD_CLOCK.frame
        self.metrics["last_update"] = utc_now()

    def get(self, key: str, default: Any = None) -> Any:
        return self.metrics.get(key, default)

    def snapshot(self) -> Dict[str, Any]:
        self.update()
        return dict(self.metrics)


METRICS_ENGINE = MetricsEngine()


def refresh_metrics() -> None:
    METRICS_ENGINE.update()


# ==========================================================
# KẾT THÚC ĐOẠN 021
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 022
# ==========================================================

class CacheEngine:

    def __init__(self) -> None:
        self.cache = CACHE

    def has(self, key: str) -> bool:
        return key in self.cache

    def get(self, key: str, default: Any = None) -> Any:
        return self.cache.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.cache[key] = value

    def remove(self, key: str) -> None:
        self.cache.pop(key, None)

    def clear(self) -> None:
        self.cache.clear()

    def remember(
        self,
        key: str,
        creator: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if key in self.cache:
            return self.cache[key]
        value = creator(*args, **kwargs)
        self.cache[key] = value
        return value

    async def remember_async(
        self,
        key: str,
        creator: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if key in self.cache:
            return self.cache[key]
        value = creator(*args, **kwargs)
        if asyncio.iscoroutine(value):
            value = await value
        self.cache[key] = value
        return value


CACHE_ENGINE = CacheEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 022
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 023
# ==========================================================

class GeoEngine:

    def distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        return geodesic((lat1, lon1), (lat2, lon2)).kilometers

    def node_distance(
        self,
        node_a: EconomicNode,
        node_b: EconomicNode,
    ) -> float:
        return self.distance(
            node_a.latitude,
            node_a.longitude,
            node_b.latitude,
            node_b.longitude,
        )

    def nearest(
        self,
        latitude: float,
        longitude: float,
        limit: int = 10,
    ) -> List[EconomicNode]:
        items = []
        for node in GLOBAL_GRAPH.nodes.values():
            d = self.distance(
                latitude,
                longitude,
                node.latitude,
                node.longitude,
            )
            items.append((d, node))
        items.sort(key=lambda item: item[0])
        return [item[1] for item in items[:limit]]

    def bounds(self) -> Tuple[float, float, float, float]:
        if not GLOBAL_GRAPH.nodes:
            return (-90.0, -180.0, 90.0, 180.0)
        lats = [n.latitude for n in GLOBAL_GRAPH.nodes.values()]
        lons = [n.longitude for n in GLOBAL_GRAPH.nodes.values()]
        return (
            min(lats),
            min(lons),
            max(lats),
            max(lons),
        )


GEO_ENGINE = GeoEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 023
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 024
# ==========================================================

class DiscoveryEngine:

    def __init__(self) -> None:
        self.discovered: Set[str] = set()

    def exists(self, external_id: str) -> bool:
        return external_id in self.discovered

    def mark(self, external_id: str) -> None:
        self.discovered.add(external_id)

    def discover(
        self,
        external_id: str,
        name: str,
        node_type: NodeType,
        latitude: float,
        longitude: float,
        country: str = "",
        region: str = "",
        founded: str = "",
    ) -> Optional[EconomicNode]:
        if self.exists(external_id):
            return None
        node = NODE_ENGINE.create(
            name=name,
            node_type=node_type,
            latitude=latitude,
            longitude=longitude,
            country=country,
            region=region,
            founded=founded,
        )
        node.metadata["external_id"] = external_id
        node.metadata["discovered_at"] = utc_now().isoformat()
        self.mark(external_id)
        return node

    def count(self) -> int:
        return len(self.discovered)

    def clear(self) -> None:
        self.discovered.clear()


DISCOVERY_ENGINE = DiscoveryEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 024
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 025
# ==========================================================

class IndicatorType(str, Enum):
    GDP = "gdp"
    CPI = "cpi"
    PPI = "ppi"
    PCE = "pce"
    NFP = "nfp"
    ADP = "adp"
    PMI = "pmi"
    ISM = "ism"
    GDP_NOW = "gdp_now"
    UNEMPLOYMENT = "unemployment"
    RETAIL_SALES = "retail_sales"
    INTEREST_RATE = "interest_rate"
    INFLATION = "inflation"
    DXY = "dxy"
    FOREX = "forex"
    BOND_YIELD = "bond_yield"
    ETF_FLOW = "etf_flow"
    GOLD_RESERVE = "gold_reserve"
    FX_RESERVE = "fx_reserve"
    TRADE_BALANCE = "trade_balance"


class EconomicIndicator(BaseModel):
    id: str
    node_id: str
    indicator: IndicatorType
    value: Optional[float] = None
    unit: str = ""
    status: DataStatus = DataStatus.WAITING
    source: str = ""
    updated_at: Optional[datetime] = None


INDICATORS: Dict[str, EconomicIndicator] = {}

# ==========================================================
# KẾT THÚC ĐOẠN 025
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 026
# ==========================================================

class IndicatorEngine:

    def register(
        self,
        node_id: str,
        indicator: IndicatorType,
        unit: str = "",
    ) -> EconomicIndicator:
        key = f"{node_id}:{indicator.value}"
        if key not in INDICATORS:
            INDICATORS[key] = EconomicIndicator(
                id=key,
                node_id=node_id,
                indicator=indicator,
                unit=unit,
            )
        return INDICATORS[key]

    def update(
        self,
        node_id: str,
        indicator: IndicatorType,
        value: float,
        source: str,
    ) -> EconomicIndicator:
        item = self.register(node_id, indicator)
        item.value = value
        item.source = source
        item.status = DataStatus.LIVE
        item.updated_at = utc_now()
        return item

    def get(
        self,
        node_id: str,
        indicator: IndicatorType,
    ) -> Optional[EconomicIndicator]:
        return INDICATORS.get(f"{node_id}:{indicator.value}")

    def all(
        self,
        node_id: str,
    ) -> List[EconomicIndicator]:
        return [
            indicator
            for indicator in INDICATORS.values()
            if indicator.node_id == node_id
        ]


INDICATOR_ENGINE = IndicatorEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 026
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 027
# ==========================================================

class NewsItem(BaseModel):
    id: str
    title: str
    summary: str = ""
    url: str = ""
    source: str = ""
    published_at: Optional[datetime] = None
    countries: List[str] = Field(default_factory=list)
    companies: List[str] = Field(default_factory=list)
    importance: int = 0


NEWS: Dict[str, NewsItem] = {}


class NewsEngine:

    def add(self, item: NewsItem) -> None:
        NEWS[item.id] = item

    def remove(self, news_id: str) -> None:
        NEWS.pop(news_id, None)

    def get(self, news_id: str) -> Optional[NewsItem]:
        return NEWS.get(news_id)

    def latest(self, limit: int = 100) -> List[NewsItem]:
        return sorted(
            NEWS.values(),
            key=lambda item: item.published_at or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )[:limit]

    def clear(self) -> None:
        NEWS.clear()


NEWS_ENGINE = NewsEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 027
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 028
# ==========================================================

class InfrastructureType(str, Enum):
    FACTORY = "factory"
    PORT = "port"
    AIRPORT = "airport"
    DATA_CENTER = "data_center"
    POWER_PLANT = "power_plant"
    MINE = "mine"
    WAREHOUSE = "warehouse"
    LOGISTICS_CENTER = "logistics_center"
    HEADQUARTERS = "headquarters"


class InfrastructureRecord(BaseModel):
    id: str
    external_id: str
    name: str
    infrastructure_type: InfrastructureType
    country: str = ""
    city: str = ""
    latitude: float
    longitude: float
    founded: str = ""
    owner: str = ""
    source: str = ""
    updated_at: Optional[datetime] = None


INFRASTRUCTURES: Dict[str, InfrastructureRecord] = {}


class InfrastructureEngine:

    def register(self, record: InfrastructureRecord) -> None:
        INFRASTRUCTURES[record.id] = record

    def get(self, record_id: str) -> Optional[InfrastructureRecord]:
        return INFRASTRUCTURES.get(record_id)

    def all(self) -> List[InfrastructureRecord]:
        return list(INFRASTRUCTURES.values())

    def remove(self, record_id: str) -> None:
        INFRASTRUCTURES.pop(record_id, None)


INFRASTRUCTURE_ENGINE = InfrastructureEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 028
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 029
# ==========================================================

class CompanyRecord(BaseModel):
    id: str
    name: str
    ticker: str = ""
    country: str = ""
    headquarters: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    sector: str = ""
    industry: str = ""
    market_cap_usd: Optional[float] = None
    employees: Optional[int] = None
    founded: str = ""
    website: str = ""
    source: str = ""
    updated_at: Optional[datetime] = None


COMPANIES: Dict[str, CompanyRecord] = {}


class CompanyEngine:

    def register(self, company: CompanyRecord) -> None:
        COMPANIES[company.id] = company

    def get(self, company_id: str) -> Optional[CompanyRecord]:
        return COMPANIES.get(company_id)

    def remove(self, company_id: str) -> None:
        COMPANIES.pop(company_id, None)

    def all(self) -> List[CompanyRecord]:
        return list(COMPANIES.values())

    def find_by_ticker(self, ticker: str) -> Optional[CompanyRecord]:
        ticker = ticker.upper()
        for company in COMPANIES.values():
            if company.ticker.upper() == ticker:
                return company
        return None


COMPANY_ENGINE = CompanyEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 029
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 030
# ==========================================================

class CountryRecord(BaseModel):
    code: str
    name: str
    capital: str = ""
    continent: str = ""
    currency: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    population: Optional[int] = None
    area_km2: Optional[float] = None
    gdp_usd: Optional[float] = None
    timezone: str = ""
    updated_at: Optional[datetime] = None


COUNTRIES: Dict[str, CountryRecord] = {}


class CountryEngine:

    def register(self, country: CountryRecord) -> None:
        COUNTRIES[country.code.upper()] = country

    def get(self, code: str) -> Optional[CountryRecord]:
        return COUNTRIES.get(code.upper())

    def remove(self, code: str) -> None:
        COUNTRIES.pop(code.upper(), None)

    def all(self) -> List[CountryRecord]:
        return sorted(
            COUNTRIES.values(),
            key=lambda item: item.name,
        )

    def exists(self, code: str) -> bool:
        return code.upper() in COUNTRIES


COUNTRY_ENGINE = CountryEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 030
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 031
# ==========================================================

class RegionRecord(BaseModel):
    id: str
    name: str
    country_code: str
    latitude: float = 0.0
    longitude: float = 0.0
    population: Optional[int] = None
    area_km2: Optional[float] = None
    updated_at: Optional[datetime] = None


REGIONS: Dict[str, RegionRecord] = {}


class RegionEngine:

    def register(self, region: RegionRecord) -> None:
        REGIONS[region.id] = region

    def get(self, region_id: str) -> Optional[RegionRecord]:
        return REGIONS.get(region_id)

    def remove(self, region_id: str) -> None:
        REGIONS.pop(region_id, None)

    def all(self) -> List[RegionRecord]:
        return sorted(
            REGIONS.values(),
            key=lambda item: item.name,
        )

    def by_country(
        self,
        country_code: str,
    ) -> List[RegionRecord]:
        return [
            region
            for region in REGIONS.values()
            if region.country_code.upper() == country_code.upper()
        ]


REGION_ENGINE = RegionEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 031
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 032
# ==========================================================

class CityRecord(BaseModel):
    id: str
    name: str
    region_id: str = ""
    country_code: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    population: Optional[int] = None
    area_km2: Optional[float] = None
    is_capital: bool = False
    updated_at: Optional[datetime] = None


CITIES: Dict[str, CityRecord] = {}


class CityEngine:

    def register(self, city: CityRecord) -> None:
        CITIES[city.id] = city

    def get(self, city_id: str) -> Optional[CityRecord]:
        return CITIES.get(city_id)

    def remove(self, city_id: str) -> None:
        CITIES.pop(city_id, None)

    def all(self) -> List[CityRecord]:
        return sorted(
            CITIES.values(),
            key=lambda item: item.name,
        )

    def by_country(
        self,
        country_code: str,
    ) -> List[CityRecord]:
        return [
            city
            for city in CITIES.values()
            if city.country_code.upper() == country_code.upper()
        ]

    def capitals(self) -> List[CityRecord]:
        return [city for city in CITIES.values() if city.is_capital]


CITY_ENGINE = CityEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 032
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 033
# ==========================================================

class OrganizationRecord(BaseModel):
    id: str
    name: str
    organization_type: str = ""
    country_code: str = ""
    city_id: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    founded: str = ""
    website: str = ""
    source: str = ""
    updated_at: Optional[datetime] = None


ORGANIZATIONS: Dict[str, OrganizationRecord] = {}


class OrganizationEngine:

    def register(self, organization: OrganizationRecord) -> None:
        ORGANIZATIONS[organization.id] = organization

    def get(self, organization_id: str) -> Optional[OrganizationRecord]:
        return ORGANIZATIONS.get(organization_id)

    def remove(self, organization_id: str) -> None:
        ORGANIZATIONS.pop(organization_id, None)

    def all(self) -> List[OrganizationRecord]:
        return sorted(
            ORGANIZATIONS.values(),
            key=lambda item: item.name,
        )

    def by_country(
        self,
        country_code: str,
    ) -> List[OrganizationRecord]:
        return [
            organization
            for organization in ORGANIZATIONS.values()
            if organization.country_code.upper() == country_code.upper()
        ]


ORGANIZATION_ENGINE = OrganizationEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 033
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 034
# ==========================================================

class EconomicCalendarEvent(BaseModel):
    id: str
    country: str
    title: str
    indicator: str
    importance: int = 0
    previous: Optional[float] = None
    forecast: Optional[float] = None
    actual: Optional[float] = None
    unit: str = ""
    release_time: Optional[datetime] = None
    updated_at: Optional[datetime] = None


ECONOMIC_CALENDAR: Dict[str, EconomicCalendarEvent] = {}


class EconomicCalendarEngine:

    def register(self, event: EconomicCalendarEvent) -> None:
        ECONOMIC_CALENDAR[event.id] = event

    def get(self, event_id: str) -> Optional[EconomicCalendarEvent]:
        return ECONOMIC_CALENDAR.get(event_id)

    def remove(self, event_id: str) -> None:
        ECONOMIC_CALENDAR.pop(event_id, None)

    def all(self) -> List[EconomicCalendarEvent]:
        return sorted(
            ECONOMIC_CALENDAR.values(),
            key=lambda item: item.release_time or utc_now(),
        )

    def upcoming(self) -> List[EconomicCalendarEvent]:
        now = utc_now()
        return [
            item
            for item in self.all()
            if item.release_time is not None
            and item.release_time >= now
        ]


ECONOMIC_CALENDAR_ENGINE = EconomicCalendarEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 034
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 035
# ==========================================================

class CurrencyRecord(BaseModel):
    code: str
    name: str
    symbol: str = ""
    country: str = ""
    exchange_rate_usd: Optional[float] = None
    change: float = 0.0
    change_percent: float = 0.0
    updated_at: Optional[datetime] = None


CURRENCIES: Dict[str, CurrencyRecord] = {}


class CurrencyEngine:

    def register(self, currency: CurrencyRecord) -> None:
        CURRENCIES[currency.code.upper()] = currency

    def get(self, code: str) -> Optional[CurrencyRecord]:
        return CURRENCIES.get(code.upper())

    def update_rate(
        self,
        code: str,
        rate: float,
        change: float,
        change_percent: float,
    ) -> None:
        currency = self.get(code)
        if currency is None:
            currency = CurrencyRecord(
                code=code.upper(),
                name=code.upper(),
            )
            self.register(currency)
        currency.exchange_rate_usd = rate
        currency.change = change
        currency.change_percent = change_percent
        currency.updated_at = utc_now()

    def all(self) -> List[CurrencyRecord]:
        return sorted(
            CURRENCIES.values(),
            key=lambda item: item.code,
        )


CURRENCY_ENGINE = CurrencyEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 035
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 036
# ==========================================================

class CommodityType(str, Enum):
    GOLD = "gold"
    SILVER = "silver"
    OIL_WTI = "oil_wti"
    OIL_BRENT = "oil_brent"
    NATURAL_GAS = "natural_gas"
    COPPER = "copper"
    ALUMINUM = "aluminum"
    IRON_ORE = "iron_ore"
    LITHIUM = "lithium"
    COAL = "coal"


class CommodityRecord(BaseModel):
    symbol: str
    commodity: CommodityType
    price: float = 0.0
    currency: str = "USD"
    unit: str = ""
    change: float = 0.0
    change_percent: float = 0.0
    updated_at: Optional[datetime] = None


COMMODITIES: Dict[str, CommodityRecord] = {}


class CommodityEngine:

    def register(self, commodity: CommodityRecord) -> None:
        COMMODITIES[commodity.symbol.upper()] = commodity

    def get(self, symbol: str) -> Optional[CommodityRecord]:
        return COMMODITIES.get(symbol.upper())

    def update(
        self,
        symbol: str,
        price: float,
        change: float,
        change_percent: float,
    ) -> None:
        item = self.get(symbol)
        if item is None:
            return
        item.price = price
        item.change = change
        item.change_percent = change_percent
        item.updated_at = utc_now()

    def all(self) -> List[CommodityRecord]:
        return sorted(COMMODITIES.values(), key=lambda item: item.symbol)


COMMODITY_ENGINE = CommodityEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 036
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 037
# ==========================================================

class MarketIndexRecord(BaseModel):
    symbol: str
    name: str
    country: str = ""
    price: float = 0.0
    change: float = 0.0
    change_percent: float = 0.0
    currency: str = "USD"
    updated_at: Optional[datetime] = None


MARKET_INDICES: Dict[str, MarketIndexRecord] = {}


class MarketIndexEngine:

    def register(self, index: MarketIndexRecord) -> None:
        MARKET_INDICES[index.symbol.upper()] = index

    def get(self, symbol: str) -> Optional[MarketIndexRecord]:
        return MARKET_INDICES.get(symbol.upper())

    def update(
        self,
        symbol: str,
        price: float,
        change: float,
        change_percent: float,
    ) -> None:
        index = self.get(symbol)
        if index is None:
            return
        index.price = price
        index.change = change
        index.change_percent = change_percent
        index.updated_at = utc_now()

    def all(self) -> List[MarketIndexRecord]:
        return sorted(
            MARKET_INDICES.values(),
            key=lambda item: item.symbol,
        )


MARKET_INDEX_ENGINE = MarketIndexEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 037
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 038
# ==========================================================

class BondRecord(BaseModel):
    symbol: str
    country: str
    maturity: str
    yield_percent: float = 0.0
    change: float = 0.0
    currency: str = ""
    updated_at: Optional[datetime] = None


BONDS: Dict[str, BondRecord] = {}


class BondEngine:

    def register(self, bond: BondRecord) -> None:
        BONDS[bond.symbol.upper()] = bond

    def get(self, symbol: str) -> Optional[BondRecord]:
        return BONDS.get(symbol.upper())

    def update(
        self,
        symbol: str,
        yield_percent: float,
        change: float,
    ) -> None:
        bond = self.get(symbol)
        if bond is None:
            return
        bond.yield_percent = yield_percent
        bond.change = change
        bond.updated_at = utc_now()

    def all(self) -> List[BondRecord]:
        return sorted(
            BONDS.values(),
            key=lambda item: item.symbol,
        )

    def by_country(
        self,
        country: str,
    ) -> List[BondRecord]:
        return [
            bond
            for bond in BONDS.values()
            if bond.country.lower() == country.lower()
        ]


BOND_ENGINE = BondEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 038
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 039
# ==========================================================

class ETFRecord(BaseModel):
    symbol: str
    name: str
    issuer: str = ""
    category: str = ""
    aum_usd: Optional[float] = None
    price: float = 0.0
    nav: float = 0.0
    flow_usd: float = 0.0
    holdings: int = 0
    updated_at: Optional[datetime] = None


ETFS: Dict[str, ETFRecord] = {}


class ETFEngine:

    def register(self, etf: ETFRecord) -> None:
        ETFS[etf.symbol.upper()] = etf

    def get(self, symbol: str) -> Optional[ETFRecord]:
        return ETFS.get(symbol.upper())

    def update(
        self,
        symbol: str,
        price: float,
        nav: float,
        flow_usd: float,
    ) -> None:
        etf = self.get(symbol)
        if etf is None:
            return
        etf.price = price
        etf.nav = nav
        etf.flow_usd = flow_usd
        etf.updated_at = utc_now()

    def all(self) -> List[ETFRecord]:
        return sorted(
            ETFS.values(),
            key=lambda item: item.symbol,
        )


ETF_ENGINE = ETFEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 039
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 040
# ==========================================================

class LogisticsRoute(BaseModel):
    id: str
    origin_node: str
    destination_node: str
    transport_mode: str
    distance_km: float = 0.0
    capacity: float = 0.0
    flow_usd: float = 0.0
    status: str = "active"
    updated_at: Optional[datetime] = None


LOGISTICS_ROUTES: Dict[str, LogisticsRoute] = {}


class LogisticsEngine:

    def register(self, route: LogisticsRoute) -> None:
        LOGISTICS_ROUTES[route.id] = route

    def get(self, route_id: str) -> Optional[LogisticsRoute]:
        return LOGISTICS_ROUTES.get(route_id)

    def update_flow(
        self,
        route_id: str,
        flow_usd: float,
    ) -> None:
        route = self.get(route_id)
        if route is None:
            return
        route.flow_usd = flow_usd
        route.updated_at = utc_now()

    def remove(self, route_id: str) -> None:
        LOGISTICS_ROUTES.pop(route_id, None)

    def all(self) -> List[LogisticsRoute]:
        return sorted(
            LOGISTICS_ROUTES.values(),
            key=lambda item: item.id,
        )

    def by_node(self, node_id: str) -> List[LogisticsRoute]:
        return [
            route
            for route in LOGISTICS_ROUTES.values()
            if route.origin_node == node_id
            or route.destination_node == node_id
        ]


LOGISTICS_ENGINE = LogisticsEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 040
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 041
# ==========================================================

class SupplyChainRecord(BaseModel):
    id: str
    supplier_node: str
    customer_node: str
    product: str = ""
    annual_value_usd: float = 0.0
    volume: float = 0.0
    unit: str = ""
    status: str = "active"
    updated_at: Optional[datetime] = None


SUPPLY_CHAINS: Dict[str, SupplyChainRecord] = {}


class SupplyChainEngine:

    def register(self, record: SupplyChainRecord) -> None:
        SUPPLY_CHAINS[record.id] = record

    def get(self, record_id: str) -> Optional[SupplyChainRecord]:
        return SUPPLY_CHAINS.get(record_id)

    def update_value(
        self,
        record_id: str,
        annual_value_usd: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return
        record.annual_value_usd = annual_value_usd
        record.updated_at = utc_now()

    def remove(self, record_id: str) -> None:
        SUPPLY_CHAINS.pop(record_id, None)

    def all(self) -> List[SupplyChainRecord]:
        return sorted(
            SUPPLY_CHAINS.values(),
            key=lambda item: item.id,
        )

    def by_node(self, node_id: str) -> List[SupplyChainRecord]:
        return [
            record
            for record in SUPPLY_CHAINS.values()
            if record.supplier_node == node_id
            or record.customer_node == node_id
        ]


SUPPLY_CHAIN_ENGINE = SupplyChainEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 041
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 042
# ==========================================================

class EnergyAssetType(str, Enum):
    OIL_FIELD = "oil_field"
    GAS_FIELD = "gas_field"
    REFINERY = "refinery"
    POWER_PLANT = "power_plant"
    SOLAR = "solar"
    WIND = "wind"
    HYDRO = "hydro"
    NUCLEAR = "nuclear"


class EnergyAsset(BaseModel):
    id: str
    name: str
    asset_type: EnergyAssetType
    country: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    capacity: float = 0.0
    capacity_unit: str = ""
    production: float = 0.0
    production_unit: str = ""
    status: str = "active"
    updated_at: Optional[datetime] = None


ENERGY_ASSETS: Dict[str, EnergyAsset] = {}


class EnergyEngine:

    def register(self, asset: EnergyAsset) -> None:
        ENERGY_ASSETS[asset.id] = asset

    def get(self, asset_id: str) -> Optional[EnergyAsset]:
        return ENERGY_ASSETS.get(asset_id)

    def remove(self, asset_id: str) -> None:
        ENERGY_ASSETS.pop(asset_id, None)

    def update_production(
        self,
        asset_id: str,
        production: float,
    ) -> None:
        asset = self.get(asset_id)
        if asset is None:
            return
        asset.production = production
        asset.updated_at = utc_now()

    def all(self) -> List[EnergyAsset]:
        return sorted(
            ENERGY_ASSETS.values(),
            key=lambda item: item.name,
        )


ENERGY_ENGINE = EnergyEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 042
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 043
# ==========================================================

class PortRecord(BaseModel):
    id: str
    name: str
    country: str = ""
    city: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    port_type: str = ""
    annual_capacity: float = 0.0
    capacity_unit: str = ""
    throughput: float = 0.0
    throughput_unit: str = ""
    status: str = "active"
    updated_at: Optional[datetime] = None


PORTS: Dict[str, PortRecord] = {}


class PortEngine:

    def register(self, port: PortRecord) -> None:
        PORTS[port.id] = port

    def get(self, port_id: str) -> Optional[PortRecord]:
        return PORTS.get(port_id)

    def remove(self, port_id: str) -> None:
        PORTS.pop(port_id, None)

    def update_throughput(
        self,
        port_id: str,
        throughput: float,
    ) -> None:
        port = self.get(port_id)
        if port is None:
            return
        port.throughput = throughput
        port.updated_at = utc_now()

    def all(self) -> List[PortRecord]:
        return sorted(
            PORTS.values(),
            key=lambda item: item.name,
        )


PORT_ENGINE = PortEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 043
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 044
# ==========================================================

class AirportRecord(BaseModel):
    id: str
    name: str
    iata: str = ""
    icao: str = ""
    country: str = ""
    city: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    annual_passengers: float = 0.0
    annual_cargo_tons: float = 0.0
    runways: int = 0
    status: str = "active"
    updated_at: Optional[datetime] = None


AIRPORTS: Dict[str, AirportRecord] = {}


class AirportEngine:

    def register(self, airport: AirportRecord) -> None:
        AIRPORTS[airport.id] = airport

    def get(self, airport_id: str) -> Optional[AirportRecord]:
        return AIRPORTS.get(airport_id)

    def remove(self, airport_id: str) -> None:
        AIRPORTS.pop(airport_id, None)

    def update_statistics(
        self,
        airport_id: str,
        passengers: float,
        cargo_tons: float,
    ) -> None:
        airport = self.get(airport_id)
        if airport is None:
            return
        airport.annual_passengers = passengers
        airport.annual_cargo_tons = cargo_tons
        airport.updated_at = utc_now()

    def all(self) -> List[AirportRecord]:
        return sorted(
            AIRPORTS.values(),
            key=lambda item: item.name,
        )


AIRPORT_ENGINE = AirportEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 044
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 045
# ==========================================================

class BankRecord(BaseModel):
    id: str
    name: str
    country: str = ""
    city: str = ""
    bank_type: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    assets_usd: float = 0.0
    deposits_usd: float = 0.0
    market_value_usd: float = 0.0
    founded: str = ""
    website: str = ""
    updated_at: Optional[datetime] = None


BANKS: Dict[str, BankRecord] = {}


class BankEngine:

    def register(self, bank: BankRecord) -> None:
        BANKS[bank.id] = bank

    def get(self, bank_id: str) -> Optional[BankRecord]:
        return BANKS.get(bank_id)

    def remove(self, bank_id: str) -> None:
        BANKS.pop(bank_id, None)

    def update_assets(
        self,
        bank_id: str,
        assets_usd: float,
        deposits_usd: float,
    ) -> None:
        bank = self.get(bank_id)
        if bank is None:
            return
        bank.assets_usd = assets_usd
        bank.deposits_usd = deposits_usd
        bank.updated_at = utc_now()

    def all(self) -> List[BankRecord]:
        return sorted(
            BANKS.values(),
            key=lambda item: item.name,
        )


BANK_ENGINE = BankEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 045
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 046
# ==========================================================

class CentralBankRecord(BaseModel):
    id: str
    name: str
    country: str
    currency: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    interest_rate: Optional[float] = None
    balance_sheet_usd: Optional[float] = None
    gold_reserves_tonnes: Optional[float] = None
    fx_reserves_usd: Optional[float] = None
    updated_at: Optional[datetime] = None


CENTRAL_BANKS: Dict[str, CentralBankRecord] = {}


class CentralBankEngine:

    def register(self, bank: CentralBankRecord) -> None:
        CENTRAL_BANKS[bank.id] = bank

    def get(self, bank_id: str) -> Optional[CentralBankRecord]:
        return CENTRAL_BANKS.get(bank_id)

    def remove(self, bank_id: str) -> None:
        CENTRAL_BANKS.pop(bank_id, None)

    def update(
        self,
        bank_id: str,
        interest_rate: Optional[float],
        balance_sheet_usd: Optional[float],
        gold_reserves_tonnes: Optional[float],
        fx_reserves_usd: Optional[float],
    ) -> None:
        bank = self.get(bank_id)
        if bank is None:
            return
        bank.interest_rate = interest_rate
        bank.balance_sheet_usd = balance_sheet_usd
        bank.gold_reserves_tonnes = gold_reserves_tonnes
        bank.fx_reserves_usd = fx_reserves_usd
        bank.updated_at = utc_now()

    def all(self) -> List[CentralBankRecord]:
        return sorted(
            CENTRAL_BANKS.values(),
            key=lambda item: item.name,
        )


CENTRAL_BANK_ENGINE = CentralBankEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 046
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 047
# ==========================================================

class ExchangeRecord(BaseModel):
    id: str
    name: str
    country: str = ""
    city: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    timezone: str = ""
    currency: str = ""
    market_cap_usd: float = 0.0
    daily_volume_usd: float = 0.0
    listed_companies: int = 0
    status: str = "open"
    updated_at: Optional[datetime] = None


EXCHANGES: Dict[str, ExchangeRecord] = {}


class ExchangeEngine:

    def register(self, exchange: ExchangeRecord) -> None:
        EXCHANGES[exchange.id] = exchange

    def get(self, exchange_id: str) -> Optional[ExchangeRecord]:
        return EXCHANGES.get(exchange_id)

    def remove(self, exchange_id: str) -> None:
        EXCHANGES.pop(exchange_id, None)

    def update(
        self,
        exchange_id: str,
        market_cap_usd: float,
        daily_volume_usd: float,
        listed_companies: int,
    ) -> None:
        exchange = self.get(exchange_id)
        if exchange is None:
            return
        exchange.market_cap_usd = market_cap_usd
        exchange.daily_volume_usd = daily_volume_usd
        exchange.listed_companies = listed_companies
        exchange.updated_at = utc_now()

    def all(self) -> List[ExchangeRecord]:
        return sorted(
            EXCHANGES.values(),
            key=lambda item: item.name,
        )


EXCHANGE_ENGINE = ExchangeEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 047
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 048
# ==========================================================

class MineRecord(BaseModel):
    id: str
    name: str
    country: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    mineral: str = ""
    owner: str = ""
    annual_production: float = 0.0
    production_unit: str = ""
    reserves: float = 0.0
    reserve_unit: str = ""
    status: str = "active"
    updated_at: Optional[datetime] = None


MINES: Dict[str, MineRecord] = {}


class MineEngine:

    def register(self, mine: MineRecord) -> None:
        MINES[mine.id] = mine

    def get(self, mine_id: str) -> Optional[MineRecord]:
        return MINES.get(mine_id)

    def remove(self, mine_id: str) -> None:
        MINES.pop(mine_id, None)

    def update(
        self,
        mine_id: str,
        annual_production: float,
        reserves: float,
    ) -> None:
        mine = self.get(mine_id)
        if mine is None:
            return
        mine.annual_production = annual_production
        mine.reserves = reserves
        mine.updated_at = utc_now()

    def all(self) -> List[MineRecord]:
        return sorted(
            MINES.values(),
            key=lambda item: item.name,
        )


MINE_ENGINE = MineEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 048
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 049
# ==========================================================

class DataCenterRecord(BaseModel):
    id: str
    name: str
    operator: str = ""
    country: str = ""
    city: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    tier: str = ""
    rack_count: int = 0
    power_mw: float = 0.0
    floor_area_m2: float = 0.0
    status: str = "active"
    updated_at: Optional[datetime] = None


DATA_CENTERS: Dict[str, DataCenterRecord] = {}


class DataCenterEngine:

    def register(self, center: DataCenterRecord) -> None:
        DATA_CENTERS[center.id] = center

    def get(self, center_id: str) -> Optional[DataCenterRecord]:
        return DATA_CENTERS.get(center_id)

    def remove(self, center_id: str) -> None:
        DATA_CENTERS.pop(center_id, None)

    def update(
        self,
        center_id: str,
        rack_count: int,
        power_mw: float,
        floor_area_m2: float,
    ) -> None:
        center = self.get(center_id)
        if center is None:
            return
        center.rack_count = rack_count
        center.power_mw = power_mw
        center.floor_area_m2 = floor_area_m2
        center.updated_at = utc_now()

    def all(self) -> List[DataCenterRecord]:
        return sorted(
            DATA_CENTERS.values(),
            key=lambda item: item.name,
        )


DATA_CENTER_ENGINE = DataCenterEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 049
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 050
# ==========================================================

class FactoryRecord(BaseModel):
    id: str
    name: str
    company_id: str = ""
    country: str = ""
    city: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    industry: str = ""
    employees: int = 0
    production_capacity: float = 0.0
    capacity_unit: str = ""
    annual_revenue_usd: float = 0.0
    annual_output: float = 0.0
    output_unit: str = ""
    status: str = "active"
    updated_at: Optional[datetime] = None


FACTORIES: Dict[str, FactoryRecord] = {}


class FactoryEngine:

    def register(self, factory: FactoryRecord) -> None:
        FACTORIES[factory.id] = factory

    def get(self, factory_id: str) -> Optional[FactoryRecord]:
        return FACTORIES.get(factory_id)

    def remove(self, factory_id: str) -> None:
        FACTORIES.pop(factory_id, None)

    def update(
        self,
        factory_id: str,
        employees: int,
        annual_revenue_usd: float,
        annual_output: float,
    ) -> None:
        factory = self.get(factory_id)
        if factory is None:
            return
        factory.employees = employees
        factory.annual_revenue_usd = annual_revenue_usd
        factory.annual_output = annual_output
        factory.updated_at = utc_now()

    def all(self) -> List[FactoryRecord]:
        return sorted(
            FACTORIES.values(),
            key=lambda item: item.name,
        )


FACTORY_ENGINE = FactoryEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 050
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 051
# ==========================================================

class WarehouseRecord(BaseModel):
    id: str
    name: str
    company_id: str = ""
    country: str = ""
    city: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    warehouse_type: str = ""
    area_m2: float = 0.0
    storage_capacity: float = 0.0
    capacity_unit: str = ""
    utilization_percent: float = 0.0
    status: str = "active"
    updated_at: Optional[datetime] = None


WAREHOUSES: Dict[str, WarehouseRecord] = {}


class WarehouseEngine:

    def register(self, warehouse: WarehouseRecord) -> None:
        WAREHOUSES[warehouse.id] = warehouse

    def get(self, warehouse_id: str) -> Optional[WarehouseRecord]:
        return WAREHOUSES.get(warehouse_id)

    def remove(self, warehouse_id: str) -> None:
        WAREHOUSES.pop(warehouse_id, None)

    def update(
        self,
        warehouse_id: str,
        area_m2: float,
        storage_capacity: float,
        utilization_percent: float,
    ) -> None:
        warehouse = self.get(warehouse_id)
        if warehouse is None:
            return
        warehouse.area_m2 = area_m2
        warehouse.storage_capacity = storage_capacity
        warehouse.utilization_percent = utilization_percent
        warehouse.updated_at = utc_now()

    def all(self) -> List[WarehouseRecord]:
        return sorted(
            WAREHOUSES.values(),
            key=lambda item: item.name,
        )


WAREHOUSE_ENGINE = WarehouseEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 051
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 052
# ==========================================================

class RailwayRecord(BaseModel):
    id: str
    name: str
    country: str = ""
    operator: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    railway_type: str = ""
    total_length_km: float = 0.0
    freight_tons_year: float = 0.0
    passengers_year: float = 0.0
    status: str = "active"
    updated_at: Optional[datetime] = None


RAILWAYS: Dict[str, RailwayRecord] = {}


class RailwayEngine:

    def register(self, railway: RailwayRecord) -> None:
        RAILWAYS[railway.id] = railway

    def get(self, railway_id: str) -> Optional[RailwayRecord]:
        return RAILWAYS.get(railway_id)

    def remove(self, railway_id: str) -> None:
        RAILWAYS.pop(railway_id, None)

    def update(
        self,
        railway_id: str,
        total_length_km: float,
        freight_tons_year: float,
        passengers_year: float,
    ) -> None:
        railway = self.get(railway_id)
        if railway is None:
            return
        railway.total_length_km = total_length_km
        railway.freight_tons_year = freight_tons_year
        railway.passengers_year = passengers_year
        railway.updated_at = utc_now()

    def all(self) -> List[RailwayRecord]:
        return sorted(
            RAILWAYS.values(),
            key=lambda item: item.name,
        )


RAILWAY_ENGINE = RailwayEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 052
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 053
# ==========================================================

class HighwayRecord(BaseModel):
    id: str
    name: str
    country: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    highway_type: str = ""
    total_length_km: float = 0.0
    lane_count: int = 0
    annual_traffic: float = 0.0
    toll_revenue_usd: float = 0.0
    status: str = "active"
    updated_at: Optional[datetime] = None


HIGHWAYS: Dict[str, HighwayRecord] = {}


class HighwayEngine:

    def register(self, highway: HighwayRecord) -> None:
        HIGHWAYS[highway.id] = highway

    def get(self, highway_id: str) -> Optional[HighwayRecord]:
        return HIGHWAYS.get(highway_id)

    def remove(self, highway_id: str) -> None:
        HIGHWAYS.pop(highway_id, None)

    def update(
        self,
        highway_id: str,
        total_length_km: float,
        annual_traffic: float,
        toll_revenue_usd: float,
    ) -> None:
        highway = self.get(highway_id)
        if highway is None:
            return
        highway.total_length_km = total_length_km
        highway.annual_traffic = annual_traffic
        highway.toll_revenue_usd = toll_revenue_usd
        highway.updated_at = utc_now()

    def all(self) -> List[HighwayRecord]:
        return sorted(
            HIGHWAYS.values(),
            key=lambda item: item.name,
        )


HIGHWAY_ENGINE = HighwayEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 053
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 054
# ==========================================================

class PipelineRecord(BaseModel):
    id: str
    name: str
    country: str = ""
    operator: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    pipeline_type: str = ""
    total_length_km: float = 0.0
    capacity_per_day: float = 0.0
    capacity_unit: str = ""
    source: str = ""
    destination: str = ""
    status: str = "active"
    updated_at: Optional[datetime] = None


PIPELINES: Dict[str, PipelineRecord] = {}


class PipelineEngine:

    def register(self, pipeline: PipelineRecord) -> None:
        PIPELINES[pipeline.id] = pipeline

    def get(self, pipeline_id: str) -> Optional[PipelineRecord]:
        return PIPELINES.get(pipeline_id)

    def remove(self, pipeline_id: str) -> None:
        PIPELINES.pop(pipeline_id, None)

    def update(
        self,
        pipeline_id: str,
        total_length_km: float,
        capacity_per_day: float,
        status: str,
    ) -> None:
        pipeline = self.get(pipeline_id)
        if pipeline is None:
            return
        pipeline.total_length_km = total_length_km
        pipeline.capacity_per_day = capacity_per_day
        pipeline.status = status
        pipeline.updated_at = utc_now()

    def all(self) -> List[PipelineRecord]:
        return sorted(
            PIPELINES.values(),
            key=lambda item: item.name,
        )


PIPELINE_ENGINE = PipelineEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 054
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 055
# ==========================================================

class ShippingLaneRecord(BaseModel):
    id: str
    name: str
    ocean: str = ""
    source_port: str = ""
    destination_port: str = ""
    distance_km: float = 0.0
    annual_cargo_tons: float = 0.0
    annual_ship_count: int = 0
    average_transit_days: float = 0.0
    risk_level: str = "low"
    status: str = "active"
    updated_at: Optional[datetime] = None


SHIPPING_LANES: Dict[str, ShippingLaneRecord] = {}


class ShippingLaneEngine:

    def register(self, lane: ShippingLaneRecord) -> None:
        SHIPPING_LANES[lane.id] = lane

    def get(self, lane_id: str) -> Optional[ShippingLaneRecord]:
        return SHIPPING_LANES.get(lane_id)

    def remove(self, lane_id: str) -> None:
        SHIPPING_LANES.pop(lane_id, None)

    def update(
        self,
        lane_id: str,
        annual_cargo_tons: float,
        annual_ship_count: int,
        average_transit_days: float,
    ) -> None:
        lane = self.get(lane_id)
        if lane is None:
            return
        lane.annual_cargo_tons = annual_cargo_tons
        lane.annual_ship_count = annual_ship_count
        lane.average_transit_days = average_transit_days
        lane.updated_at = utc_now()

    def all(self) -> List[ShippingLaneRecord]:
        return sorted(
            SHIPPING_LANES.values(),
            key=lambda item: item.name,
        )


SHIPPING_LANE_ENGINE = ShippingLaneEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 055
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 056
# ==========================================================

class SatelliteRecord(BaseModel):
    id: str
    name: str
    operator: str = ""
    country: str = ""
    orbit: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    altitude_km: float = 0.0
    launch_date: str = ""
    purpose: str = ""
    status: str = "active"
    updated_at: Optional[datetime] = None


SATELLITES: Dict[str, SatelliteRecord] = {}


class SatelliteEngine:

    def register(self, satellite: SatelliteRecord) -> None:
        SATELLITES[satellite.id] = satellite

    def get(self, satellite_id: str) -> Optional[SatelliteRecord]:
        return SATELLITES.get(satellite_id)

    def remove(self, satellite_id: str) -> None:
        SATELLITES.pop(satellite_id, None)

    def update(
        self,
        satellite_id: str,
        latitude: float,
        longitude: float,
        altitude_km: float,
        status: str,
    ) -> None:
        satellite = self.get(satellite_id)
        if satellite is None:
            return
        satellite.latitude = latitude
        satellite.longitude = longitude
        satellite.altitude_km = altitude_km
        satellite.status = status
        satellite.updated_at = utc_now()

    def all(self) -> List[SatelliteRecord]:
        return sorted(
            SATELLITES.values(),
            key=lambda item: item.name,
        )


SATELLITE_ENGINE = SatelliteEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 056
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 057
# ==========================================================

class CableRecord(BaseModel):
    id: str
    name: str
    cable_type: str = ""
    owner: str = ""
    source: str = ""
    destination: str = ""
    length_km: float = 0.0
    bandwidth_tbps: float = 0.0
    landing_points: int = 0
    status: str = "active"
    updated_at: Optional[datetime] = None


CABLES: Dict[str, CableRecord] = {}


class CableEngine:

    def register(self, cable: CableRecord) -> None:
        CABLES[cable.id] = cable

    def get(self, cable_id: str) -> Optional[CableRecord]:
        return CABLES.get(cable_id)

    def remove(self, cable_id: str) -> None:
        CABLES.pop(cable_id, None)

    def update(
        self,
        cable_id: str,
        bandwidth_tbps: float,
        landing_points: int,
        status: str,
    ) -> None:
        cable = self.get(cable_id)
        if cable is None:
            return
        cable.bandwidth_tbps = bandwidth_tbps
        cable.landing_points = landing_points
        cable.status = status
        cable.updated_at = utc_now()

    def all(self) -> List[CableRecord]:
        return sorted(
            CABLES.values(),
            key=lambda item: item.name,
        )


CABLE_ENGINE = CableEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 057
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 058
# ==========================================================

class FiberNetworkRecord(BaseModel):
    id: str
    name: str
    operator: str = ""
    country: str = ""
    network_type: str = ""
    total_length_km: float = 0.0
    cities_connected: int = 0
    bandwidth_tbps: float = 0.0
    redundancy_level: str = ""
    status: str = "active"
    updated_at: Optional[datetime] = None


FIBER_NETWORKS: Dict[str, FiberNetworkRecord] = {}


class FiberNetworkEngine:

    def register(self, network: FiberNetworkRecord) -> None:
        FIBER_NETWORKS[network.id] = network

    def get(self, network_id: str) -> Optional[FiberNetworkRecord]:
        return FIBER_NETWORKS.get(network_id)

    def remove(self, network_id: str) -> None:
        FIBER_NETWORKS.pop(network_id, None)

    def update(
        self,
        network_id: str,
        total_length_km: float,
        cities_connected: int,
        bandwidth_tbps: float,
    ) -> None:
        network = self.get(network_id)
        if network is None:
            return
        network.total_length_km = total_length_km
        network.cities_connected = cities_connected
        network.bandwidth_tbps = bandwidth_tbps
        network.updated_at = utc_now()

    def all(self) -> List[FiberNetworkRecord]:
        return sorted(
            FIBER_NETWORKS.values(),
            key=lambda item: item.name,
        )


FIBER_NETWORK_ENGINE = FiberNetworkEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 058
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 059
# ==========================================================

class PowerGridRecord(BaseModel):
    id: str
    name: str
    country: str = ""
    operator: str = ""
    grid_type: str = ""
    voltage_kv: float = 0.0
    total_length_km: float = 0.0
    capacity_mw: float = 0.0
    connected_regions: int = 0
    reliability_percent: float = 0.0
    status: str = "active"
    updated_at: Optional[datetime] = None


POWER_GRIDS: Dict[str, PowerGridRecord] = {}


class PowerGridEngine:

    def register(self, grid: PowerGridRecord) -> None:
        POWER_GRIDS[grid.id] = grid

    def get(self, grid_id: str) -> Optional[PowerGridRecord]:
        return POWER_GRIDS.get(grid_id)

    def remove(self, grid_id: str) -> None:
        POWER_GRIDS.pop(grid_id, None)

    def update(
        self,
        grid_id: str,
        total_length_km: float,
        capacity_mw: float,
        reliability_percent: float,
    ) -> None:
        grid = self.get(grid_id)
        if grid is None:
            return
        grid.total_length_km = total_length_km
        grid.capacity_mw = capacity_mw
        grid.reliability_percent = reliability_percent
        grid.updated_at = utc_now()

    def all(self) -> List[PowerGridRecord]:
        return sorted(
            POWER_GRIDS.values(),
            key=lambda item: item.name,
        )


POWER_GRID_ENGINE = PowerGridEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 059
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 060
# ==========================================================

class PowerPlantRecord(BaseModel):
    id: str
    name: str
    country: str = ""
    city: str = ""
    operator: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    plant_type: str = ""
    fuel: str = ""
    capacity_mw: float = 0.0
    annual_generation_gwh: float = 0.0
    carbon_emission_tons: float = 0.0
    status: str = "active"
    updated_at: Optional[datetime] = None


POWER_PLANTS: Dict[str, PowerPlantRecord] = {}


class PowerPlantEngine:

    def register(self, plant: PowerPlantRecord) -> None:
        POWER_PLANTS[plant.id] = plant

    def get(self, plant_id: str) -> Optional[PowerPlantRecord]:
        return POWER_PLANTS.get(plant_id)

    def remove(self, plant_id: str) -> None:
        POWER_PLANTS.pop(plant_id, None)

    def update(
        self,
        plant_id: str,
        capacity_mw: float,
        annual_generation_gwh: float,
        carbon_emission_tons: float,
    ) -> None:
        plant = self.get(plant_id)
        if plant is None:
            return
        plant.capacity_mw = capacity_mw
        plant.annual_generation_gwh = annual_generation_gwh
        plant.carbon_emission_tons = carbon_emission_tons
        plant.updated_at = utc_now()

    def all(self) -> List[PowerPlantRecord]:
        return sorted(
            POWER_PLANTS.values(),
            key=lambda item: item.name,
        )


POWER_PLANT_ENGINE = PowerPlantEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 060
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 061
# ==========================================================

class GDPRecord(BaseModel):
    id: str
    country: str
    nominal_gdp_usd: float = 0.0
    real_gdp_growth: float = 0.0
    gdp_per_capita: float = 0.0
    quarter: str = ""
    year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GDP_DATABASE: Dict[str, GDPRecord] = {}


class GDPEngine:

    def register(self, record: GDPRecord) -> None:
        GDP_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[GDPRecord]:
        return GDP_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        GDP_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        nominal_gdp_usd: float,
        real_gdp_growth: float,
        gdp_per_capita: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.nominal_gdp_usd = nominal_gdp_usd
        record.real_gdp_growth = real_gdp_growth
        record.gdp_per_capita = gdp_per_capita
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[GDPRecord]:
        return sorted(
            GDP_DATABASE.values(),
            key=lambda item: item.country,
        )


GDP_ENGINE = GDPEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 061
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 062
# ==========================================================

class CPIRecord(BaseModel):
    id: str
    country: str
    headline_cpi: float = 0.0
    core_cpi: float = 0.0
    monthly_change: float = 0.0
    yearly_change: float = 0.0
    month: str = ""
    year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


CPI_DATABASE: Dict[str, CPIRecord] = {}


class CPIEngine:

    def register(self, record: CPIRecord) -> None:
        CPI_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[CPIRecord]:
        return CPI_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        CPI_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        headline_cpi: float,
        core_cpi: float,
        monthly_change: float,
        yearly_change: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.headline_cpi = headline_cpi
        record.core_cpi = core_cpi
        record.monthly_change = monthly_change
        record.yearly_change = yearly_change
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[CPIRecord]:
        return sorted(
            CPI_DATABASE.values(),
            key=lambda item: item.country,
        )


CPI_ENGINE = CPIEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 062
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 063
# ==========================================================

class PPIRecord(BaseModel):
    id: str
    country: str
    headline_ppi: float = 0.0
    core_ppi: float = 0.0
    monthly_change: float = 0.0
    yearly_change: float = 0.0
    month: str = ""
    year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


PPI_DATABASE: Dict[str, PPIRecord] = {}


class PPIEngine:

    def register(self, record: PPIRecord) -> None:
        PPI_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[PPIRecord]:
        return PPI_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        PPI_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        headline_ppi: float,
        core_ppi: float,
        monthly_change: float,
        yearly_change: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.headline_ppi = headline_ppi
        record.core_ppi = core_ppi
        record.monthly_change = monthly_change
        record.yearly_change = yearly_change
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[PPIRecord]:
        return sorted(
            PPI_DATABASE.values(),
            key=lambda item: item.country,
        )


PPI_ENGINE = PPIEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 063
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 064
# ==========================================================

class PCERecord(BaseModel):
    id: str
    country: str
    headline_pce: float = 0.0
    core_pce: float = 0.0
    monthly_change: float = 0.0
    yearly_change: float = 0.0
    month: str = ""
    year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


PCE_DATABASE: Dict[str, PCERecord] = {}


class PCEEngine:

    def register(self, record: PCERecord) -> None:
        PCE_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[PCERecord]:
        return PCE_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        PCE_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        headline_pce: float,
        core_pce: float,
        monthly_change: float,
        yearly_change: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.headline_pce = headline_pce
        record.core_pce = core_pce
        record.monthly_change = monthly_change
        record.yearly_change = yearly_change
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[PCERecord]:
        return sorted(
            PCE_DATABASE.values(),
            key=lambda item: item.country,
        )


PCE_ENGINE = PCEEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 064
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 065
# ==========================================================

class NFPRecord(BaseModel):
    id: str
    country: str
    actual: float = 0.0
    forecast: float = 0.0
    previous: float = 0.0
    unemployment_rate: float = 0.0
    average_hourly_earnings: float = 0.0
    report_month: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


NFP_DATABASE: Dict[str, NFPRecord] = {}


class NFPEngine:

    def register(self, record: NFPRecord) -> None:
        NFP_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[NFPRecord]:
        return NFP_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        NFP_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        actual: float,
        forecast: float,
        previous: float,
        unemployment_rate: float,
        average_hourly_earnings: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.actual = actual
        record.forecast = forecast
        record.previous = previous
        record.unemployment_rate = unemployment_rate
        record.average_hourly_earnings = average_hourly_earnings
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[NFPRecord]:
        return sorted(
            NFP_DATABASE.values(),
            key=lambda item: item.country,
        )


NFP_ENGINE = NFPEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 065
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 066
# ==========================================================

class InterestRateRecord(BaseModel):
    id: str
    country: str
    central_bank: str = ""
    policy_rate: float = 0.0
    previous_rate: float = 0.0
    change_bps: float = 0.0
    decision_date: str = ""
    next_meeting: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


INTEREST_RATE_DATABASE: Dict[str, InterestRateRecord] = {}


class InterestRateEngine:

    def register(self, record: InterestRateRecord) -> None:
        INTEREST_RATE_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[InterestRateRecord]:
        return INTEREST_RATE_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        INTEREST_RATE_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        policy_rate: float,
        previous_rate: float,
        change_bps: float,
        next_meeting: str,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.policy_rate = policy_rate
        record.previous_rate = previous_rate
        record.change_bps = change_bps
        record.next_meeting = next_meeting
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[InterestRateRecord]:
        return sorted(
            INTEREST_RATE_DATABASE.values(),
            key=lambda item: item.country,
        )


INTEREST_RATE_ENGINE = InterestRateEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 066
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 067
# ==========================================================

class UnemploymentRecord(BaseModel):
    id: str
    country: str
    unemployment_rate: float = 0.0
    labor_force: float = 0.0
    employed_population: float = 0.0
    unemployed_population: float = 0.0
    youth_unemployment_rate: float = 0.0
    report_month: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


UNEMPLOYMENT_DATABASE: Dict[str, UnemploymentRecord] = {}


class UnemploymentEngine:

    def register(self, record: UnemploymentRecord) -> None:
        UNEMPLOYMENT_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[UnemploymentRecord]:
        return UNEMPLOYMENT_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        UNEMPLOYMENT_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        unemployment_rate: float,
        labor_force: float,
        employed_population: float,
        unemployed_population: float,
        youth_unemployment_rate: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.unemployment_rate = unemployment_rate
        record.labor_force = labor_force
        record.employed_population = employed_population
        record.unemployed_population = unemployed_population
        record.youth_unemployment_rate = youth_unemployment_rate
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[UnemploymentRecord]:
        return sorted(
            UNEMPLOYMENT_DATABASE.values(),
            key=lambda item: item.country,
        )


UNEMPLOYMENT_ENGINE = UnemploymentEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 067
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 068
# ==========================================================

class InflationRecord(BaseModel):
    id: str
    country: str
    inflation_rate: float = 0.0
    target_rate: float = 0.0
    food_inflation: float = 0.0
    energy_inflation: float = 0.0
    services_inflation: float = 0.0
    report_month: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


INFLATION_DATABASE: Dict[str, InflationRecord] = {}


class InflationEngine:

    def register(self, record: InflationRecord) -> None:
        INFLATION_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[InflationRecord]:
        return INFLATION_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        INFLATION_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        inflation_rate: float,
        target_rate: float,
        food_inflation: float,
        energy_inflation: float,
        services_inflation: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.inflation_rate = inflation_rate
        record.target_rate = target_rate
        record.food_inflation = food_inflation
        record.energy_inflation = energy_inflation
        record.services_inflation = services_inflation
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[InflationRecord]:
        return sorted(
            INFLATION_DATABASE.values(),
            key=lambda item: item.country,
        )


INFLATION_ENGINE = InflationEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 068
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 069
# ==========================================================

class TradeBalanceRecord(BaseModel):
    id: str
    country: str
    exports_usd: float = 0.0
    imports_usd: float = 0.0
    trade_balance_usd: float = 0.0
    export_growth: float = 0.0
    import_growth: float = 0.0
    report_month: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


TRADE_BALANCE_DATABASE: Dict[str, TradeBalanceRecord] = {}


class TradeBalanceEngine:

    def register(self, record: TradeBalanceRecord) -> None:
        TRADE_BALANCE_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[TradeBalanceRecord]:
        return TRADE_BALANCE_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        TRADE_BALANCE_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        exports_usd: float,
        imports_usd: float,
        trade_balance_usd: float,
        export_growth: float,
        import_growth: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.exports_usd = exports_usd
        record.imports_usd = imports_usd
        record.trade_balance_usd = trade_balance_usd
        record.export_growth = export_growth
        record.import_growth = import_growth
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[TradeBalanceRecord]:
        return sorted(
            TRADE_BALANCE_DATABASE.values(),
            key=lambda item: item.country,
        )


TRADE_BALANCE_ENGINE = TradeBalanceEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 069
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 070
# ==========================================================

class ForeignReserveRecord(BaseModel):
    id: str
    country: str
    total_reserves_usd: float = 0.0
    gold_reserves_usd: float = 0.0
    foreign_currency_usd: float = 0.0
    imf_position_usd: float = 0.0
    sdr_usd: float = 0.0
    reserve_month: str = ""
    reserve_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


FOREIGN_RESERVE_DATABASE: Dict[str, ForeignReserveRecord] = {}


class ForeignReserveEngine:

    def register(self, record: ForeignReserveRecord) -> None:
        FOREIGN_RESERVE_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[ForeignReserveRecord]:
        return FOREIGN_RESERVE_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        FOREIGN_RESERVE_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        total_reserves_usd: float,
        gold_reserves_usd: float,
        foreign_currency_usd: float,
        imf_position_usd: float,
        sdr_usd: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.total_reserves_usd = total_reserves_usd
        record.gold_reserves_usd = gold_reserves_usd
        record.foreign_currency_usd = foreign_currency_usd
        record.imf_position_usd = imf_position_usd
        record.sdr_usd = sdr_usd
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[ForeignReserveRecord]:
        return sorted(
            FOREIGN_RESERVE_DATABASE.values(),
            key=lambda item: item.country,
        )


FOREIGN_RESERVE_ENGINE = ForeignReserveEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 070
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 071
# ==========================================================

class PublicDebtRecord(BaseModel):
    id: str
    country: str
    total_debt_usd: float = 0.0
    debt_to_gdp: float = 0.0
    domestic_debt_usd: float = 0.0
    external_debt_usd: float = 0.0
    interest_payment_usd: float = 0.0
    report_period: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


PUBLIC_DEBT_DATABASE: Dict[str, PublicDebtRecord] = {}


class PublicDebtEngine:

    def register(self, record: PublicDebtRecord) -> None:
        PUBLIC_DEBT_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[PublicDebtRecord]:
        return PUBLIC_DEBT_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        PUBLIC_DEBT_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        total_debt_usd: float,
        debt_to_gdp: float,
        domestic_debt_usd: float,
        external_debt_usd: float,
        interest_payment_usd: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.total_debt_usd = total_debt_usd
        record.debt_to_gdp = debt_to_gdp
        record.domestic_debt_usd = domestic_debt_usd
        record.external_debt_usd = external_debt_usd
        record.interest_payment_usd = interest_payment_usd
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[PublicDebtRecord]:
        return sorted(
            PUBLIC_DEBT_DATABASE.values(),
            key=lambda item: item.country,
        )


PUBLIC_DEBT_ENGINE = PublicDebtEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 071
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 072
# ==========================================================

class CurrentAccountRecord(BaseModel):
    id: str
    country: str
    current_account_usd: float = 0.0
    current_account_percent_gdp: float = 0.0
    goods_balance_usd: float = 0.0
    services_balance_usd: float = 0.0
    primary_income_usd: float = 0.0
    secondary_income_usd: float = 0.0
    report_period: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


CURRENT_ACCOUNT_DATABASE: Dict[str, CurrentAccountRecord] = {}


class CurrentAccountEngine:

    def register(self, record: CurrentAccountRecord) -> None:
        CURRENT_ACCOUNT_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[CurrentAccountRecord]:
        return CURRENT_ACCOUNT_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        CURRENT_ACCOUNT_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        current_account_usd: float,
        current_account_percent_gdp: float,
        goods_balance_usd: float,
        services_balance_usd: float,
        primary_income_usd: float,
        secondary_income_usd: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.current_account_usd = current_account_usd
        record.current_account_percent_gdp = current_account_percent_gdp
        record.goods_balance_usd = goods_balance_usd
        record.services_balance_usd = services_balance_usd
        record.primary_income_usd = primary_income_usd
        record.secondary_income_usd = secondary_income_usd
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[CurrentAccountRecord]:
        return sorted(
            CURRENT_ACCOUNT_DATABASE.values(),
            key=lambda item: item.country,
        )


CURRENT_ACCOUNT_ENGINE = CurrentAccountEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 072
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 073
# ==========================================================

class FDIRecord(BaseModel):
    id: str
    country: str
    inward_fdi_usd: float = 0.0
    outward_fdi_usd: float = 0.0
    net_fdi_usd: float = 0.0
    greenfield_projects: int = 0
    merger_acquisition_usd: float = 0.0
    report_period: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


FDI_DATABASE: Dict[str, FDIRecord] = {}


class FDIEngine:

    def register(self, record: FDIRecord) -> None:
        FDI_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[FDIRecord]:
        return FDI_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        FDI_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        inward_fdi_usd: float,
        outward_fdi_usd: float,
        net_fdi_usd: float,
        greenfield_projects: int,
        merger_acquisition_usd: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.inward_fdi_usd = inward_fdi_usd
        record.outward_fdi_usd = outward_fdi_usd
        record.net_fdi_usd = net_fdi_usd
        record.greenfield_projects = greenfield_projects
        record.merger_acquisition_usd = merger_acquisition_usd
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[FDIRecord]:
        return sorted(
            FDI_DATABASE.values(),
            key=lambda item: item.country,
        )


FDI_ENGINE = FDIEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 073
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 074
# ==========================================================

class PMIRecord(BaseModel):
    id: str
    country: str
    manufacturing_pmi: float = 0.0
    services_pmi: float = 0.0
    composite_pmi: float = 0.0
    new_orders: float = 0.0
    employment_index: float = 0.0
    report_month: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


PMI_DATABASE: Dict[str, PMIRecord] = {}


class PMIEngine:

    def register(self, record: PMIRecord) -> None:
        PMI_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[PMIRecord]:
        return PMI_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        PMI_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        manufacturing_pmi: float,
        services_pmi: float,
        composite_pmi: float,
        new_orders: float,
        employment_index: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.manufacturing_pmi = manufacturing_pmi
        record.services_pmi = services_pmi
        record.composite_pmi = composite_pmi
        record.new_orders = new_orders
        record.employment_index = employment_index
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[PMIRecord]:
        return sorted(
            PMI_DATABASE.values(),
            key=lambda item: item.country,
        )


PMI_ENGINE = PMIEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 074
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 075
# ==========================================================

class RetailSalesRecord(BaseModel):
    id: str
    country: str
    retail_sales_index: float = 0.0
    monthly_change: float = 0.0
    yearly_change: float = 0.0
    core_retail_sales: float = 0.0
    ecommerce_share: float = 0.0
    report_month: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


RETAIL_SALES_DATABASE: Dict[str, RetailSalesRecord] = {}


class RetailSalesEngine:

    def register(self, record: RetailSalesRecord) -> None:
        RETAIL_SALES_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[RetailSalesRecord]:
        return RETAIL_SALES_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        RETAIL_SALES_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        retail_sales_index: float,
        monthly_change: float,
        yearly_change: float,
        core_retail_sales: float,
        ecommerce_share: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.retail_sales_index = retail_sales_index
        record.monthly_change = monthly_change
        record.yearly_change = yearly_change
        record.core_retail_sales = core_retail_sales
        record.ecommerce_share = ecommerce_share
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[RetailSalesRecord]:
        return sorted(
            RETAIL_SALES_DATABASE.values(),
            key=lambda item: item.country,
        )


RETAIL_SALES_ENGINE = RetailSalesEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 075
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 076
# ==========================================================

class IndustrialProductionRecord(BaseModel):
    id: str
    country: str
    industrial_production_index: float = 0.0
    manufacturing_output: float = 0.0
    mining_output: float = 0.0
    utilities_output: float = 0.0
    monthly_change: float = 0.0
    yearly_change: float = 0.0
    report_month: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


INDUSTRIAL_PRODUCTION_DATABASE: Dict[str, IndustrialProductionRecord] = {}


class IndustrialProductionEngine:

    def register(self, record: IndustrialProductionRecord) -> None:
        INDUSTRIAL_PRODUCTION_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[IndustrialProductionRecord]:
        return INDUSTRIAL_PRODUCTION_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        INDUSTRIAL_PRODUCTION_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        industrial_production_index: float,
        manufacturing_output: float,
        mining_output: float,
        utilities_output: float,
        monthly_change: float,
        yearly_change: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.industrial_production_index = industrial_production_index
        record.manufacturing_output = manufacturing_output
        record.mining_output = mining_output
        record.utilities_output = utilities_output
        record.monthly_change = monthly_change
        record.yearly_change = yearly_change
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[IndustrialProductionRecord]:
        return sorted(
            INDUSTRIAL_PRODUCTION_DATABASE.values(),
            key=lambda item: item.country,
        )


INDUSTRIAL_PRODUCTION_ENGINE = IndustrialProductionEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 076
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 077
# ==========================================================

class HousingRecord(BaseModel):
    id: str
    country: str
    house_price_index: float = 0.0
    new_home_sales: float = 0.0
    existing_home_sales: float = 0.0
    building_permits: float = 0.0
    housing_starts: float = 0.0
    mortgage_rate: float = 0.0
    report_month: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


HOUSING_DATABASE: Dict[str, HousingRecord] = {}


class HousingEngine:

    def register(self, record: HousingRecord) -> None:
        HOUSING_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[HousingRecord]:
        return HOUSING_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        HOUSING_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        house_price_index: float,
        new_home_sales: float,
        existing_home_sales: float,
        building_permits: float,
        housing_starts: float,
        mortgage_rate: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.house_price_index = house_price_index
        record.new_home_sales = new_home_sales
        record.existing_home_sales = existing_home_sales
        record.building_permits = building_permits
        record.housing_starts = housing_starts
        record.mortgage_rate = mortgage_rate
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[HousingRecord]:
        return sorted(
            HOUSING_DATABASE.values(),
            key=lambda item: item.country,
        )


HOUSING_ENGINE = HousingEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 077
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 078
# ==========================================================

class ConsumerConfidenceRecord(BaseModel):
    id: str
    country: str
    consumer_confidence_index: float = 0.0
    business_confidence_index: float = 0.0
    economic_sentiment_index: float = 0.0
    future_expectation_index: float = 0.0
    current_condition_index: float = 0.0
    report_month: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


CONSUMER_CONFIDENCE_DATABASE: Dict[str, ConsumerConfidenceRecord] = {}


class ConsumerConfidenceEngine:

    def register(self, record: ConsumerConfidenceRecord) -> None:
        CONSUMER_CONFIDENCE_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[ConsumerConfidenceRecord]:
        return CONSUMER_CONFIDENCE_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        CONSUMER_CONFIDENCE_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        consumer_confidence_index: float,
        business_confidence_index: float,
        economic_sentiment_index: float,
        future_expectation_index: float,
        current_condition_index: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.consumer_confidence_index = consumer_confidence_index
        record.business_confidence_index = business_confidence_index
        record.economic_sentiment_index = economic_sentiment_index
        record.future_expectation_index = future_expectation_index
        record.current_condition_index = current_condition_index
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[ConsumerConfidenceRecord]:
        return sorted(
            CONSUMER_CONFIDENCE_DATABASE.values(),
            key=lambda item: item.country,
        )


CONSUMER_CONFIDENCE_ENGINE = ConsumerConfidenceEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 078
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 079
# ==========================================================

class BusinessConfidenceRecord(BaseModel):
    id: str
    country: str
    manufacturing_confidence: float = 0.0
    services_confidence: float = 0.0
    construction_confidence: float = 0.0
    retail_confidence: float = 0.0
    business_expectation: float = 0.0
    report_month: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


BUSINESS_CONFIDENCE_DATABASE: Dict[str, BusinessConfidenceRecord] = {}


class BusinessConfidenceEngine:

    def register(self, record: BusinessConfidenceRecord) -> None:
        BUSINESS_CONFIDENCE_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[BusinessConfidenceRecord]:
        return BUSINESS_CONFIDENCE_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        BUSINESS_CONFIDENCE_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        manufacturing_confidence: float,
        services_confidence: float,
        construction_confidence: float,
        retail_confidence: float,
        business_expectation: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.manufacturing_confidence = manufacturing_confidence
        record.services_confidence = services_confidence
        record.construction_confidence = construction_confidence
        record.retail_confidence = retail_confidence
        record.business_expectation = business_expectation
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[BusinessConfidenceRecord]:
        return sorted(
            BUSINESS_CONFIDENCE_DATABASE.values(),
            key=lambda item: item.country,
        )


BUSINESS_CONFIDENCE_ENGINE = BusinessConfidenceEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 079
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 080
# ==========================================================

class FiscalBalanceRecord(BaseModel):
    id: str
    country: str
    government_revenue_usd: float = 0.0
    government_expenditure_usd: float = 0.0
    fiscal_balance_usd: float = 0.0
    fiscal_balance_percent_gdp: float = 0.0
    primary_balance_usd: float = 0.0
    public_investment_usd: float = 0.0
    report_period: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


FISCAL_BALANCE_DATABASE: Dict[str, FiscalBalanceRecord] = {}


class FiscalBalanceEngine:

    def register(self, record: FiscalBalanceRecord) -> None:
        FISCAL_BALANCE_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[FiscalBalanceRecord]:
        return FISCAL_BALANCE_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        FISCAL_BALANCE_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        government_revenue_usd: float,
        government_expenditure_usd: float,
        fiscal_balance_usd: float,
        fiscal_balance_percent_gdp: float,
        primary_balance_usd: float,
        public_investment_usd: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.government_revenue_usd = government_revenue_usd
        record.government_expenditure_usd = government_expenditure_usd
        record.fiscal_balance_usd = fiscal_balance_usd
        record.fiscal_balance_percent_gdp = fiscal_balance_percent_gdp
        record.primary_balance_usd = primary_balance_usd
        record.public_investment_usd = public_investment_usd
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[FiscalBalanceRecord]:
        return sorted(
            FISCAL_BALANCE_DATABASE.values(),
            key=lambda item: item.country,
        )


FISCAL_BALANCE_ENGINE = FiscalBalanceEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 080
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 081
# ==========================================================

class MoneySupplyRecord(BaseModel):
    id: str
    country: str
    m0: float = 0.0
    m1: float = 0.0
    m2: float = 0.0
    m3: float = 0.0
    monthly_growth: float = 0.0
    yearly_growth: float = 0.0
    report_month: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


MONEY_SUPPLY_DATABASE: Dict[str, MoneySupplyRecord] = {}


class MoneySupplyEngine:

    def register(self, record: MoneySupplyRecord) -> None:
        MONEY_SUPPLY_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[MoneySupplyRecord]:
        return MONEY_SUPPLY_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        MONEY_SUPPLY_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        m0: float,
        m1: float,
        m2: float,
        m3: float,
        monthly_growth: float,
        yearly_growth: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.m0 = m0
        record.m1 = m1
        record.m2 = m2
        record.m3 = m3
        record.monthly_growth = monthly_growth
        record.yearly_growth = yearly_growth
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[MoneySupplyRecord]:
        return sorted(
            MONEY_SUPPLY_DATABASE.values(),
            key=lambda item: item.country,
        )


MONEY_SUPPLY_ENGINE = MoneySupplyEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 081
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 082
# ==========================================================

class GovernmentBudgetRecord(BaseModel):
    id: str
    country: str
    total_revenue_usd: float = 0.0
    total_expenditure_usd: float = 0.0
    budget_deficit_usd: float = 0.0
    deficit_percent_gdp: float = 0.0
    tax_revenue_usd: float = 0.0
    public_spending_usd: float = 0.0
    report_period: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GOVERNMENT_BUDGET_DATABASE: Dict[str, GovernmentBudgetRecord] = {}


class GovernmentBudgetEngine:

    def register(self, record: GovernmentBudgetRecord) -> None:
        GOVERNMENT_BUDGET_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[GovernmentBudgetRecord]:
        return GOVERNMENT_BUDGET_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        GOVERNMENT_BUDGET_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        total_revenue_usd: float,
        total_expenditure_usd: float,
        budget_deficit_usd: float,
        deficit_percent_gdp: float,
        tax_revenue_usd: float,
        public_spending_usd: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.total_revenue_usd = total_revenue_usd
        record.total_expenditure_usd = total_expenditure_usd
        record.budget_deficit_usd = budget_deficit_usd
        record.deficit_percent_gdp = deficit_percent_gdp
        record.tax_revenue_usd = tax_revenue_usd
        record.public_spending_usd = public_spending_usd
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[GovernmentBudgetRecord]:
        return sorted(
            GOVERNMENT_BUDGET_DATABASE.values(),
            key=lambda item: item.country,
        )


GOVERNMENT_BUDGET_ENGINE = GovernmentBudgetEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 082
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 083
# ==========================================================

class PopulationRecord(BaseModel):
    id: str
    country: str
    total_population: int = 0
    working_age_population: int = 0
    labor_force: int = 0
    urban_population: int = 0
    rural_population: int = 0
    population_growth: float = 0.0
    median_age: float = 0.0
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


POPULATION_DATABASE: Dict[str, PopulationRecord] = {}


class PopulationEngine:

    def register(self, record: PopulationRecord) -> None:
        POPULATION_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[PopulationRecord]:
        return POPULATION_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        POPULATION_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        total_population: int,
        working_age_population: int,
        labor_force: int,
        urban_population: int,
        rural_population: int,
        population_growth: float,
        median_age: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.total_population = total_population
        record.working_age_population = working_age_population
        record.labor_force = labor_force
        record.urban_population = urban_population
        record.rural_population = rural_population
        record.population_growth = population_growth
        record.median_age = median_age
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[PopulationRecord]:
        return sorted(
            POPULATION_DATABASE.values(),
            key=lambda item: item.country,
        )


POPULATION_ENGINE = PopulationEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 083
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 084
# ==========================================================

class LaborCostRecord(BaseModel):
    id: str
    country: str
    average_monthly_wage_usd: float = 0.0
    minimum_wage_usd: float = 0.0
    hourly_wage_usd: float = 0.0
    labor_cost_index: float = 0.0
    productivity_index: float = 0.0
    unit_labor_cost: float = 0.0
    report_period: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


LABOR_COST_DATABASE: Dict[str, LaborCostRecord] = {}


class LaborCostEngine:

    def register(self, record: LaborCostRecord) -> None:
        LABOR_COST_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[LaborCostRecord]:
        return LABOR_COST_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        LABOR_COST_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        average_monthly_wage_usd: float,
        minimum_wage_usd: float,
        hourly_wage_usd: float,
        labor_cost_index: float,
        productivity_index: float,
        unit_labor_cost: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.average_monthly_wage_usd = average_monthly_wage_usd
        record.minimum_wage_usd = minimum_wage_usd
        record.hourly_wage_usd = hourly_wage_usd
        record.labor_cost_index = labor_cost_index
        record.productivity_index = productivity_index
        record.unit_labor_cost = unit_labor_cost
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[LaborCostRecord]:
        return sorted(
            LABOR_COST_DATABASE.values(),
            key=lambda item: item.country,
        )


LABOR_COST_ENGINE = LaborCostEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 084
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 085
# ==========================================================

class ProductivityRecord(BaseModel):
    id: str
    country: str
    gdp_per_worker_usd: float = 0.0
    gdp_per_hour_usd: float = 0.0
    productivity_growth: float = 0.0
    manufacturing_productivity: float = 0.0
    services_productivity: float = 0.0
    agriculture_productivity: float = 0.0
    report_period: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


PRODUCTIVITY_DATABASE: Dict[str, ProductivityRecord] = {}


class ProductivityEngine:

    def register(self, record: ProductivityRecord) -> None:
        PRODUCTIVITY_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[ProductivityRecord]:
        return PRODUCTIVITY_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        PRODUCTIVITY_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        gdp_per_worker_usd: float,
        gdp_per_hour_usd: float,
        productivity_growth: float,
        manufacturing_productivity: float,
        services_productivity: float,
        agriculture_productivity: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.gdp_per_worker_usd = gdp_per_worker_usd
        record.gdp_per_hour_usd = gdp_per_hour_usd
        record.productivity_growth = productivity_growth
        record.manufacturing_productivity = manufacturing_productivity
        record.services_productivity = services_productivity
        record.agriculture_productivity = agriculture_productivity
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[ProductivityRecord]:
        return sorted(
            PRODUCTIVITY_DATABASE.values(),
            key=lambda item: item.country,
        )


PRODUCTIVITY_ENGINE = ProductivityEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 085
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 086
# ==========================================================

class HouseholdDebtRecord(BaseModel):
    id: str
    country: str
    household_debt_usd: float = 0.0
    household_debt_to_gdp: float = 0.0
    household_debt_to_income: float = 0.0
    mortgage_debt_usd: float = 0.0
    consumer_credit_usd: float = 0.0
    debt_service_ratio: float = 0.0
    report_period: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


HOUSEHOLD_DEBT_DATABASE: Dict[str, HouseholdDebtRecord] = {}


class HouseholdDebtEngine:

    def register(self, record: HouseholdDebtRecord) -> None:
        HOUSEHOLD_DEBT_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[HouseholdDebtRecord]:
        return HOUSEHOLD_DEBT_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        HOUSEHOLD_DEBT_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        household_debt_usd: float,
        household_debt_to_gdp: float,
        household_debt_to_income: float,
        mortgage_debt_usd: float,
        consumer_credit_usd: float,
        debt_service_ratio: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.household_debt_usd = household_debt_usd
        record.household_debt_to_gdp = household_debt_to_gdp
        record.household_debt_to_income = household_debt_to_income
        record.mortgage_debt_usd = mortgage_debt_usd
        record.consumer_credit_usd = consumer_credit_usd
        record.debt_service_ratio = debt_service_ratio
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[HouseholdDebtRecord]:
        return sorted(
            HOUSEHOLD_DEBT_DATABASE.values(),
            key=lambda item: item.country,
        )


HOUSEHOLD_DEBT_ENGINE = HouseholdDebtEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 086
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 087
# ==========================================================

class CorporateDebtRecord(BaseModel):
    id: str
    country: str
    corporate_debt_usd: float = 0.0
    corporate_debt_to_gdp: float = 0.0
    investment_grade_debt_usd: float = 0.0
    high_yield_debt_usd: float = 0.0
    default_rate: float = 0.0
    average_borrowing_rate: float = 0.0
    report_period: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


CORPORATE_DEBT_DATABASE: Dict[str, CorporateDebtRecord] = {}


class CorporateDebtEngine:

    def register(self, record: CorporateDebtRecord) -> None:
        CORPORATE_DEBT_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[CorporateDebtRecord]:
        return CORPORATE_DEBT_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        CORPORATE_DEBT_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        corporate_debt_usd: float,
        corporate_debt_to_gdp: float,
        investment_grade_debt_usd: float,
        high_yield_debt_usd: float,
        default_rate: float,
        average_borrowing_rate: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.corporate_debt_usd = corporate_debt_usd
        record.corporate_debt_to_gdp = corporate_debt_to_gdp
        record.investment_grade_debt_usd = investment_grade_debt_usd
        record.high_yield_debt_usd = high_yield_debt_usd
        record.default_rate = default_rate
        record.average_borrowing_rate = average_borrowing_rate
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[CorporateDebtRecord]:
        return sorted(
            CORPORATE_DEBT_DATABASE.values(),
            key=lambda item: item.country,
        )


CORPORATE_DEBT_ENGINE = CorporateDebtEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 087
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 088
# ==========================================================

class BankingSystemRecord(BaseModel):
    id: str
    country: str
    total_bank_assets_usd: float = 0.0
    total_bank_deposits_usd: float = 0.0
    total_bank_loans_usd: float = 0.0
    non_performing_loan_ratio: float = 0.0
    capital_adequacy_ratio: float = 0.0
    liquidity_coverage_ratio: float = 0.0
    report_period: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


BANKING_SYSTEM_DATABASE: Dict[str, BankingSystemRecord] = {}


class BankingSystemEngine:

    def register(self, record: BankingSystemRecord) -> None:
        BANKING_SYSTEM_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[BankingSystemRecord]:
        return BANKING_SYSTEM_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        BANKING_SYSTEM_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        total_bank_assets_usd: float,
        total_bank_deposits_usd: float,
        total_bank_loans_usd: float,
        non_performing_loan_ratio: float,
        capital_adequacy_ratio: float,
        liquidity_coverage_ratio: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.total_bank_assets_usd = total_bank_assets_usd
        record.total_bank_deposits_usd = total_bank_deposits_usd
        record.total_bank_loans_usd = total_bank_loans_usd
        record.non_performing_loan_ratio = non_performing_loan_ratio
        record.capital_adequacy_ratio = capital_adequacy_ratio
        record.liquidity_coverage_ratio = liquidity_coverage_ratio
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[BankingSystemRecord]:
        return sorted(
            BANKING_SYSTEM_DATABASE.values(),
            key=lambda item: item.country,
        )


BANKING_SYSTEM_ENGINE = BankingSystemEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 088
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 089
# ==========================================================

class CreditRatingRecord(BaseModel):
    id: str
    country: str
    sovereign_rating_sp: str = ""
    sovereign_rating_moodys: str = ""
    sovereign_rating_fitch: str = ""
    outlook: str = ""
    cds_5y_bps: float = 0.0
    risk_score: float = 0.0
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


CREDIT_RATING_DATABASE: Dict[str, CreditRatingRecord] = {}


class CreditRatingEngine:

    def register(self, record: CreditRatingRecord) -> None:
        CREDIT_RATING_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[CreditRatingRecord]:
        return CREDIT_RATING_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        CREDIT_RATING_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        sovereign_rating_sp: str,
        sovereign_rating_moodys: str,
        sovereign_rating_fitch: str,
        outlook: str,
        cds_5y_bps: float,
        risk_score: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.sovereign_rating_sp = sovereign_rating_sp
        record.sovereign_rating_moodys = sovereign_rating_moodys
        record.sovereign_rating_fitch = sovereign_rating_fitch
        record.outlook = outlook
        record.cds_5y_bps = cds_5y_bps
        record.risk_score = risk_score
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[CreditRatingRecord]:
        return sorted(
            CREDIT_RATING_DATABASE.values(),
            key=lambda item: item.country,
        )


CREDIT_RATING_ENGINE = CreditRatingEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 089
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 090
# ==========================================================

class SovereignFundRecord(BaseModel):
    id: str
    country: str
    fund_name: str = ""
    assets_under_management_usd: float = 0.0
    equity_allocation_percent: float = 0.0
    bond_allocation_percent: float = 0.0
    real_estate_percent: float = 0.0
    alternative_assets_percent: float = 0.0
    annual_return_percent: float = 0.0
    inception_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


SOVEREIGN_FUND_DATABASE: Dict[str, SovereignFundRecord] = {}


class SovereignFundEngine:

    def register(self, record: SovereignFundRecord) -> None:
        SOVEREIGN_FUND_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[SovereignFundRecord]:
        return SOVEREIGN_FUND_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        SOVEREIGN_FUND_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        assets_under_management_usd: float,
        equity_allocation_percent: float,
        bond_allocation_percent: float,
        real_estate_percent: float,
        alternative_assets_percent: float,
        annual_return_percent: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.assets_under_management_usd = assets_under_management_usd
        record.equity_allocation_percent = equity_allocation_percent
        record.bond_allocation_percent = bond_allocation_percent
        record.real_estate_percent = real_estate_percent
        record.alternative_assets_percent = alternative_assets_percent
        record.annual_return_percent = annual_return_percent
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[SovereignFundRecord]:
        return sorted(
            SOVEREIGN_FUND_DATABASE.values(),
            key=lambda item: item.country,
        )


SOVEREIGN_FUND_ENGINE = SovereignFundEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 090
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 091
# ==========================================================

class GoldReserveRecord(BaseModel):
    id: str
    country: str
    gold_reserve_tonnes: float = 0.0
    gold_reserve_value_usd: float = 0.0
    reserve_share_percent: float = 0.0
    annual_change_tonnes: float = 0.0
    monthly_change_tonnes: float = 0.0
    ranking: int = 0
    report_month: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GOLD_RESERVE_DATABASE: Dict[str, GoldReserveRecord] = {}


class GoldReserveEngine:

    def register(self, record: GoldReserveRecord) -> None:
        GOLD_RESERVE_DATABASE[record.id] = record

    def get(self, record_id: str) -> Optional[GoldReserveRecord]:
        return GOLD_RESERVE_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        GOLD_RESERVE_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        gold_reserve_tonnes: float,
        gold_reserve_value_usd: float,
        reserve_share_percent: float,
        annual_change_tonnes: float,
        monthly_change_tonnes: float,
        ranking: int,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.gold_reserve_tonnes = gold_reserve_tonnes
        record.gold_reserve_value_usd = gold_reserve_value_usd
        record.reserve_share_percent = reserve_share_percent
        record.annual_change_tonnes = annual_change_tonnes
        record.monthly_change_tonnes = monthly_change_tonnes
        record.ranking = ranking
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[GoldReserveRecord]:
        return sorted(
            GOLD_RESERVE_DATABASE.values(),
            key=lambda item: item.country,
        )


GOLD_RESERVE_ENGINE = GoldReserveEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 091
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 092
# ==========================================================

class ForeignExchangeReserveRecord(BaseModel):
    id: str
    country: str
    usd_percent: float = 0.0
    eur_percent: float = 0.0
    cny_percent: float = 0.0
    jpy_percent: float = 0.0
    gbp_percent: float = 0.0
    other_percent: float = 0.0
    total_reserve_usd: float = 0.0
    report_period: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


FOREIGN_EXCHANGE_RESERVE_DATABASE: Dict[str, ForeignExchangeReserveRecord] = {}


class ForeignExchangeReserveEngine:

    def register(self, record: ForeignExchangeReserveRecord) -> None:
        FOREIGN_EXCHANGE_RESERVE_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[ForeignExchangeReserveRecord]:
        return FOREIGN_EXCHANGE_RESERVE_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        FOREIGN_EXCHANGE_RESERVE_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        usd_percent: float,
        eur_percent: float,
        cny_percent: float,
        jpy_percent: float,
        gbp_percent: float,
        other_percent: float,
        total_reserve_usd: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.usd_percent = usd_percent
        record.eur_percent = eur_percent
        record.cny_percent = cny_percent
        record.jpy_percent = jpy_percent
        record.gbp_percent = gbp_percent
        record.other_percent = other_percent
        record.total_reserve_usd = total_reserve_usd
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[ForeignExchangeReserveRecord]:
        return sorted(
            FOREIGN_EXCHANGE_RESERVE_DATABASE.values(),
            key=lambda item: item.country,
        )


FOREIGN_EXCHANGE_RESERVE_ENGINE = ForeignExchangeReserveEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 092
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 093
# ==========================================================

class CapitalFlowRecord(BaseModel):
    id: str
    country: str
    portfolio_inflow_usd: float = 0.0
    portfolio_outflow_usd: float = 0.0
    direct_investment_inflow_usd: float = 0.0
    direct_investment_outflow_usd: float = 0.0
    other_investment_usd: float = 0.0
    net_capital_flow_usd: float = 0.0
    report_period: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


CAPITAL_FLOW_DATABASE: Dict[str, CapitalFlowRecord] = {}


class CapitalFlowEngine:

    def register(self, record: CapitalFlowRecord) -> None:
        CAPITAL_FLOW_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CapitalFlowRecord]:
        return CAPITAL_FLOW_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        CAPITAL_FLOW_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        portfolio_inflow_usd: float,
        portfolio_outflow_usd: float,
        direct_investment_inflow_usd: float,
        direct_investment_outflow_usd: float,
        other_investment_usd: float,
        net_capital_flow_usd: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.portfolio_inflow_usd = portfolio_inflow_usd
        record.portfolio_outflow_usd = portfolio_outflow_usd
        record.direct_investment_inflow_usd = direct_investment_inflow_usd
        record.direct_investment_outflow_usd = direct_investment_outflow_usd
        record.other_investment_usd = other_investment_usd
        record.net_capital_flow_usd = net_capital_flow_usd
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[CapitalFlowRecord]:
        return sorted(
            CAPITAL_FLOW_DATABASE.values(),
            key=lambda item: item.country,
        )


CAPITAL_FLOW_ENGINE = CapitalFlowEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 093
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 094
# ==========================================================

class ExchangeRateRecord(BaseModel):
    id: str
    base_currency: str
    quote_currency: str
    exchange_rate: float = 0.0
    daily_change_percent: float = 0.0
    weekly_change_percent: float = 0.0
    monthly_change_percent: float = 0.0
    yearly_change_percent: float = 0.0
    volatility_30d: float = 0.0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


EXCHANGE_RATE_DATABASE: Dict[str, ExchangeRateRecord] = {}


class ExchangeRateEngine:

    def register(self, record: ExchangeRateRecord) -> None:
        EXCHANGE_RATE_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[ExchangeRateRecord]:
        return EXCHANGE_RATE_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        EXCHANGE_RATE_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        exchange_rate: float,
        daily_change_percent: float,
        weekly_change_percent: float,
        monthly_change_percent: float,
        yearly_change_percent: float,
        volatility_30d: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.exchange_rate = exchange_rate
        record.daily_change_percent = daily_change_percent
        record.weekly_change_percent = weekly_change_percent
        record.monthly_change_percent = monthly_change_percent
        record.yearly_change_percent = yearly_change_percent
        record.volatility_30d = volatility_30d
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[ExchangeRateRecord]:
        return sorted(
            EXCHANGE_RATE_DATABASE.values(),
            key=lambda item: (
                item.base_currency,
                item.quote_currency,
            ),
        )


EXCHANGE_RATE_ENGINE = ExchangeRateEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 094
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 095
# ==========================================================

class BalanceOfPaymentsRecord(BaseModel):
    id: str
    country: str
    current_account_usd: float = 0.0
    capital_account_usd: float = 0.0
    financial_account_usd: float = 0.0
    reserve_assets_change_usd: float = 0.0
    net_errors_omissions_usd: float = 0.0
    overall_balance_usd: float = 0.0
    report_period: str = ""
    report_year: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


BALANCE_OF_PAYMENTS_DATABASE: Dict[
    str,
    BalanceOfPaymentsRecord,
] = {}


class BalanceOfPaymentsEngine:

    def register(self, record: BalanceOfPaymentsRecord) -> None:
        BALANCE_OF_PAYMENTS_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[BalanceOfPaymentsRecord]:
        return BALANCE_OF_PAYMENTS_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        BALANCE_OF_PAYMENTS_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        current_account_usd: float,
        capital_account_usd: float,
        financial_account_usd: float,
        reserve_assets_change_usd: float,
        net_errors_omissions_usd: float,
        overall_balance_usd: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.current_account_usd = current_account_usd
        record.capital_account_usd = capital_account_usd
        record.financial_account_usd = financial_account_usd
        record.reserve_assets_change_usd = reserve_assets_change_usd
        record.net_errors_omissions_usd = net_errors_omissions_usd
        record.overall_balance_usd = overall_balance_usd
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[BalanceOfPaymentsRecord]:
        return sorted(
            BALANCE_OF_PAYMENTS_DATABASE.values(),
            key=lambda item: item.country,
        )


BALANCE_OF_PAYMENTS_ENGINE = BalanceOfPaymentsEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 095
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 096
# ==========================================================

class GovernmentBondRecord(BaseModel):
    id: str
    country: str
    maturity: str = ""
    yield_percent: float = 0.0
    coupon_percent: float = 0.0
    issue_size_usd: float = 0.0
    outstanding_usd: float = 0.0
    duration: float = 0.0
    modified_duration: float = 0.0
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GOVERNMENT_BOND_DATABASE: Dict[str, GovernmentBondRecord] = {}


class GovernmentBondEngine:

    def register(self, record: GovernmentBondRecord) -> None:
        GOVERNMENT_BOND_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GovernmentBondRecord]:
        return GOVERNMENT_BOND_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        GOVERNMENT_BOND_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        yield_percent: float,
        coupon_percent: float,
        issue_size_usd: float,
        outstanding_usd: float,
        duration: float,
        modified_duration: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.yield_percent = yield_percent
        record.coupon_percent = coupon_percent
        record.issue_size_usd = issue_size_usd
        record.outstanding_usd = outstanding_usd
        record.duration = duration
        record.modified_duration = modified_duration
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[GovernmentBondRecord]:
        return sorted(
            GOVERNMENT_BOND_DATABASE.values(),
            key=lambda item: (
                item.country,
                item.maturity,
            ),
        )


GOVERNMENT_BOND_ENGINE = GovernmentBondEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 096
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 097
# ==========================================================

class CreditSpreadRecord(BaseModel):
    id: str
    country: str
    investment_grade_spread_bps: float = 0.0
    high_yield_spread_bps: float = 0.0
    sovereign_spread_bps: float = 0.0
    emerging_market_spread_bps: float = 0.0
    corporate_spread_bps: float = 0.0
    risk_premium_percent: float = 0.0
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


CREDIT_SPREAD_DATABASE: Dict[str, CreditSpreadRecord] = {}


class CreditSpreadEngine:

    def register(self, record: CreditSpreadRecord) -> None:
        CREDIT_SPREAD_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CreditSpreadRecord]:
        return CREDIT_SPREAD_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        CREDIT_SPREAD_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        investment_grade_spread_bps: float,
        high_yield_spread_bps: float,
        sovereign_spread_bps: float,
        emerging_market_spread_bps: float,
        corporate_spread_bps: float,
        risk_premium_percent: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.investment_grade_spread_bps = (
            investment_grade_spread_bps
        )
        record.high_yield_spread_bps = high_yield_spread_bps
        record.sovereign_spread_bps = sovereign_spread_bps
        record.emerging_market_spread_bps = (
            emerging_market_spread_bps
        )
        record.corporate_spread_bps = corporate_spread_bps
        record.risk_premium_percent = risk_premium_percent
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[CreditSpreadRecord]:
        return sorted(
            CREDIT_SPREAD_DATABASE.values(),
            key=lambda item: item.country,
        )


CREDIT_SPREAD_ENGINE = CreditSpreadEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 097
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 098
# ==========================================================

class StockMarketRecord(BaseModel):
    id: str
    country: str
    exchange: str
    index_name: str
    index_value: float = 0.0
    daily_change_percent: float = 0.0
    weekly_change_percent: float = 0.0
    monthly_change_percent: float = 0.0
    market_cap_usd: float = 0.0
    volume_usd: float = 0.0
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


STOCK_MARKET_DATABASE: Dict[str, StockMarketRecord] = {}


class StockMarketEngine:

    def register(self, record: StockMarketRecord) -> None:
        STOCK_MARKET_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[StockMarketRecord]:
        return STOCK_MARKET_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        STOCK_MARKET_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        index_value: float,
        daily_change_percent: float,
        weekly_change_percent: float,
        monthly_change_percent: float,
        market_cap_usd: float,
        volume_usd: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.index_value = index_value
        record.daily_change_percent = daily_change_percent
        record.weekly_change_percent = weekly_change_percent
        record.monthly_change_percent = monthly_change_percent
        record.market_cap_usd = market_cap_usd
        record.volume_usd = volume_usd
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[StockMarketRecord]:
        return sorted(
            STOCK_MARKET_DATABASE.values(),
            key=lambda item: (
                item.country,
                item.index_name,
            ),
        )


STOCK_MARKET_ENGINE = StockMarketEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 098
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 099
# ==========================================================

class CryptocurrencyRecord(BaseModel):
    id: str
    symbol: str
    name: str
    price_usd: float = 0.0
    market_cap_usd: float = 0.0
    volume_24h_usd: float = 0.0
    circulating_supply: float = 0.0
    max_supply: float = 0.0
    dominance_percent: float = 0.0
    daily_change_percent: float = 0.0
    weekly_change_percent: float = 0.0
    monthly_change_percent: float = 0.0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


CRYPTOCURRENCY_DATABASE: Dict[str, CryptocurrencyRecord] = {}


class CryptocurrencyEngine:

    def register(self, record: CryptocurrencyRecord) -> None:
        CRYPTOCURRENCY_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CryptocurrencyRecord]:
        return CRYPTOCURRENCY_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        CRYPTOCURRENCY_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        price_usd: float,
        market_cap_usd: float,
        volume_24h_usd: float,
        circulating_supply: float,
        max_supply: float,
        dominance_percent: float,
        daily_change_percent: float,
        weekly_change_percent: float,
        monthly_change_percent: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.price_usd = price_usd
        record.market_cap_usd = market_cap_usd
        record.volume_24h_usd = volume_24h_usd
        record.circulating_supply = circulating_supply
        record.max_supply = max_supply
        record.dominance_percent = dominance_percent
        record.daily_change_percent = daily_change_percent
        record.weekly_change_percent = weekly_change_percent
        record.monthly_change_percent = monthly_change_percent
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[CryptocurrencyRecord]:
        return sorted(
            CRYPTOCURRENCY_DATABASE.values(),
            key=lambda item: item.market_cap_usd,
            reverse=True,
        )


CRYPTOCURRENCY_ENGINE = CryptocurrencyEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 099
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 100
# ==========================================================

class TradeFlowRecord(BaseModel):
    id: str
    exporter: str
    importer: str
    commodity: str
    hs_code: str = ""
    export_value_usd: float = 0.0
    import_value_usd: float = 0.0
    trade_balance_usd: float = 0.0
    quantity: float = 0.0
    unit: str = ""
    transport_mode: str = ""
    report_period: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


TRADE_FLOW_DATABASE: Dict[str, TradeFlowRecord] = {}


class TradeFlowEngine:

    def register(self, record: TradeFlowRecord) -> None:
        TRADE_FLOW_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[TradeFlowRecord]:
        return TRADE_FLOW_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        TRADE_FLOW_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        export_value_usd: float,
        import_value_usd: float,
        trade_balance_usd: float,
        quantity: float,
        transport_mode: str,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.export_value_usd = export_value_usd
        record.import_value_usd = import_value_usd
        record.trade_balance_usd = trade_balance_usd
        record.quantity = quantity
        record.transport_mode = transport_mode
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[TradeFlowRecord]:
        return sorted(
            TRADE_FLOW_DATABASE.values(),
            key=lambda item: (
                item.exporter,
                item.importer,
                item.commodity,
            ),
        )


TRADE_FLOW_ENGINE = TradeFlowEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 100
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 101
# ==========================================================

class ShippingRecord(BaseModel):
    id: str
    vessel_name: str
    imo_number: str = ""
    mmsi: str = ""
    flag_country: str = ""
    ship_type: str = ""
    operator: str = ""
    current_port: str = ""
    destination_port: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    speed_knots: float = 0.0
    course_degree: float = 0.0
    cargo_type: str = ""
    cargo_capacity_ton: float = 0.0
    eta: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


SHIPPING_DATABASE: Dict[str, ShippingRecord] = {}


class ShippingEngine:

    def register(self, record: ShippingRecord) -> None:
        SHIPPING_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[ShippingRecord]:
        return SHIPPING_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        SHIPPING_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        current_port: str,
        destination_port: str,
        latitude: float,
        longitude: float,
        speed_knots: float,
        course_degree: float,
        eta: str,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.current_port = current_port
        record.destination_port = destination_port
        record.latitude = latitude
        record.longitude = longitude
        record.speed_knots = speed_knots
        record.course_degree = course_degree
        record.eta = eta
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[ShippingRecord]:
        return sorted(
            SHIPPING_DATABASE.values(),
            key=lambda item: item.vessel_name,
        )


SHIPPING_ENGINE = ShippingEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 101
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 102
# ==========================================================

class FlightRecord(BaseModel):
    id: str
    flight_number: str
    airline: str
    aircraft_type: str = ""
    aircraft_registration: str = ""
    departure_airport: str = ""
    arrival_airport: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    altitude_ft: float = 0.0
    ground_speed_kmh: float = 0.0
    heading_degree: float = 0.0
    flight_status: str = ""
    scheduled_departure: str = ""
    scheduled_arrival: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


FLIGHT_DATABASE: Dict[str, FlightRecord] = {}


class FlightEngine:

    def register(self, record: FlightRecord) -> None:
        FLIGHT_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[FlightRecord]:
        return FLIGHT_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        FLIGHT_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        latitude: float,
        longitude: float,
        altitude_ft: float,
        ground_speed_kmh: float,
        heading_degree: float,
        flight_status: str,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.latitude = latitude
        record.longitude = longitude
        record.altitude_ft = altitude_ft
        record.ground_speed_kmh = ground_speed_kmh
        record.heading_degree = heading_degree
        record.flight_status = flight_status
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[FlightRecord]:
        return sorted(
            FLIGHT_DATABASE.values(),
            key=lambda item: item.flight_number,
        )


FLIGHT_ENGINE = FlightEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 102
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 103
# ==========================================================

class RailwayTrafficRecord(BaseModel):
    id: str
    country: str
    railway_operator: str
    route_name: str = ""
    origin_station: str = ""
    destination_station: str = ""
    train_type: str = ""
    train_count: int = 0
    freight_ton: float = 0.0
    passenger_count: int = 0
    average_speed_kmh: float = 0.0
    route_length_km: float = 0.0
    report_period: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


RAILWAY_TRAFFIC_DATABASE: Dict[
    str,
    RailwayTrafficRecord,
] = {}


class RailwayTrafficEngine:

    def register(self, record: RailwayTrafficRecord) -> None:
        RAILWAY_TRAFFIC_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[RailwayTrafficRecord]:
        return RAILWAY_TRAFFIC_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        RAILWAY_TRAFFIC_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        train_count: int,
        freight_ton: float,
        passenger_count: int,
        average_speed_kmh: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.train_count = train_count
        record.freight_ton = freight_ton
        record.passenger_count = passenger_count
        record.average_speed_kmh = average_speed_kmh
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[RailwayTrafficRecord]:
        return sorted(
            RAILWAY_TRAFFIC_DATABASE.values(),
            key=lambda item: (
                item.country,
                item.route_name,
            ),
        )


RAILWAY_TRAFFIC_ENGINE = RailwayTrafficEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 103
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 104
# ==========================================================

class RoadTrafficRecord(BaseModel):
    id: str
    country: str
    road_name: str
    road_type: str = ""
    start_location: str = ""
    end_location: str = ""
    vehicle_count: int = 0
    truck_count: int = 0
    bus_count: int = 0
    average_speed_kmh: float = 0.0
    congestion_percent: float = 0.0
    freight_ton: float = 0.0
    report_period: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


ROAD_TRAFFIC_DATABASE: Dict[
    str,
    RoadTrafficRecord,
] = {}


class RoadTrafficEngine:

    def register(self, record: RoadTrafficRecord) -> None:
        ROAD_TRAFFIC_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[RoadTrafficRecord]:
        return ROAD_TRAFFIC_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        ROAD_TRAFFIC_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        vehicle_count: int,
        truck_count: int,
        bus_count: int,
        average_speed_kmh: float,
        congestion_percent: float,
        freight_ton: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.vehicle_count = vehicle_count
        record.truck_count = truck_count
        record.bus_count = bus_count
        record.average_speed_kmh = average_speed_kmh
        record.congestion_percent = congestion_percent
        record.freight_ton = freight_ton
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[RoadTrafficRecord]:
        return sorted(
            ROAD_TRAFFIC_DATABASE.values(),
            key=lambda item: (
                item.country,
                item.road_name,
            ),
        )


ROAD_TRAFFIC_ENGINE = RoadTrafficEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 104
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 105
# ==========================================================

class EnergyFlowRecord(BaseModel):
    id: str
    exporter: str
    importer: str
    energy_type: str
    pipeline: str = ""
    transport_method: str = ""
    quantity: float = 0.0
    unit: str = ""
    value_usd: float = 0.0
    price_per_unit: float = 0.0
    capacity: float = 0.0
    utilization_percent: float = 0.0
    report_period: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


ENERGY_FLOW_DATABASE: Dict[str, EnergyFlowRecord] = {}


class EnergyFlowEngine:

    def register(self, record: EnergyFlowRecord) -> None:
        ENERGY_FLOW_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[EnergyFlowRecord]:
        return ENERGY_FLOW_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        ENERGY_FLOW_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        quantity: float,
        value_usd: float,
        price_per_unit: float,
        capacity: float,
        utilization_percent: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.quantity = quantity
        record.value_usd = value_usd
        record.price_per_unit = price_per_unit
        record.capacity = capacity
        record.utilization_percent = utilization_percent
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[EnergyFlowRecord]:
        return sorted(
            ENERGY_FLOW_DATABASE.values(),
            key=lambda item: (
                item.exporter,
                item.importer,
                item.energy_type,
            ),
        )


ENERGY_FLOW_ENGINE = EnergyFlowEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 105
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 106
# ==========================================================

class CommodityFlowRecord(BaseModel):
    id: str
    exporter: str
    importer: str
    commodity: str
    category: str = ""
    quantity: float = 0.0
    unit: str = ""
    value_usd: float = 0.0
    average_price: float = 0.0
    shipping_method: str = ""
    origin_port: str = ""
    destination_port: str = ""
    report_period: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


COMMODITY_FLOW_DATABASE: Dict[
    str,
    CommodityFlowRecord,
] = {}


class CommodityFlowEngine:

    def register(self, record: CommodityFlowRecord) -> None:
        COMMODITY_FLOW_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CommodityFlowRecord]:
        return COMMODITY_FLOW_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        COMMODITY_FLOW_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        quantity: float,
        value_usd: float,
        average_price: float,
        shipping_method: str,
        origin_port: str,
        destination_port: str,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.quantity = quantity
        record.value_usd = value_usd
        record.average_price = average_price
        record.shipping_method = shipping_method
        record.origin_port = origin_port
        record.destination_port = destination_port
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[CommodityFlowRecord]:
        return sorted(
            COMMODITY_FLOW_DATABASE.values(),
            key=lambda item: (
                item.exporter,
                item.importer,
                item.commodity,
            ),
        )


COMMODITY_FLOW_ENGINE = CommodityFlowEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 106
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 107
# ==========================================================

class SupplyChainRecord(BaseModel):
    id: str
    company: str
    supplier: str
    customer: str
    product: str
    industry: str = ""
    origin_country: str = ""
    destination_country: str = ""
    production_capacity: float = 0.0
    inventory_level: float = 0.0
    lead_time_days: float = 0.0
    annual_trade_value_usd: float = 0.0
    risk_score: float = 0.0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


SUPPLY_CHAIN_DATABASE: Dict[
    str,
    SupplyChainRecord,
] = {}


class SupplyChainEngine:

    def register(self, record: SupplyChainRecord) -> None:
        SUPPLY_CHAIN_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[SupplyChainRecord]:
        return SUPPLY_CHAIN_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        SUPPLY_CHAIN_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        production_capacity: float,
        inventory_level: float,
        lead_time_days: float,
        annual_trade_value_usd: float,
        risk_score: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.production_capacity = production_capacity
        record.inventory_level = inventory_level
        record.lead_time_days = lead_time_days
        record.annual_trade_value_usd = annual_trade_value_usd
        record.risk_score = risk_score
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[SupplyChainRecord]:
        return sorted(
            SUPPLY_CHAIN_DATABASE.values(),
            key=lambda item: (
                item.company,
                item.product,
            ),
        )


SUPPLY_CHAIN_ENGINE = SupplyChainEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 107
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 108
# ==========================================================

class ManufacturingRecord(BaseModel):
    id: str
    company: str
    factory: str
    country: str
    city: str = ""
    product: str = ""
    industry: str = ""
    annual_capacity: float = 0.0
    current_output: float = 0.0
    capacity_utilization: float = 0.0
    employee_count: int = 0
    annual_revenue_usd: float = 0.0
    export_ratio: float = 0.0
    carbon_emission_ton: float = 0.0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


MANUFACTURING_DATABASE: Dict[
    str,
    ManufacturingRecord,
] = {}


class ManufacturingEngine:

    def register(self, record: ManufacturingRecord) -> None:
        MANUFACTURING_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[ManufacturingRecord]:
        return MANUFACTURING_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        MANUFACTURING_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        annual_capacity: float,
        current_output: float,
        capacity_utilization: float,
        employee_count: int,
        annual_revenue_usd: float,
        export_ratio: float,
        carbon_emission_ton: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.annual_capacity = annual_capacity
        record.current_output = current_output
        record.capacity_utilization = capacity_utilization
        record.employee_count = employee_count
        record.annual_revenue_usd = annual_revenue_usd
        record.export_ratio = export_ratio
        record.carbon_emission_ton = carbon_emission_ton
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[ManufacturingRecord]:
        return sorted(
            MANUFACTURING_DATABASE.values(),
            key=lambda item: (
                item.company,
                item.factory,
            ),
        )


MANUFACTURING_ENGINE = ManufacturingEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 108
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 109
# ==========================================================

class InventoryRecord(BaseModel):
    id: str
    company: str
    warehouse: str
    country: str
    city: str = ""
    product: str = ""
    category: str = ""
    quantity: float = 0.0
    unit: str = ""
    inventory_value_usd: float = 0.0
    daily_inflow: float = 0.0
    daily_outflow: float = 0.0
    turnover_days: float = 0.0
    utilization_percent: float = 0.0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


INVENTORY_DATABASE: Dict[
    str,
    InventoryRecord,
] = {}


class InventoryEngine:

    def register(self, record: InventoryRecord) -> None:
        INVENTORY_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[InventoryRecord]:
        return INVENTORY_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        INVENTORY_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        quantity: float,
        inventory_value_usd: float,
        daily_inflow: float,
        daily_outflow: float,
        turnover_days: float,
        utilization_percent: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.quantity = quantity
        record.inventory_value_usd = inventory_value_usd
        record.daily_inflow = daily_inflow
        record.daily_outflow = daily_outflow
        record.turnover_days = turnover_days
        record.utilization_percent = utilization_percent
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[InventoryRecord]:
        return sorted(
            INVENTORY_DATABASE.values(),
            key=lambda item: (
                item.company,
                item.warehouse,
            ),
        )


INVENTORY_ENGINE = InventoryEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 109
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 110
# ==========================================================

class RetailRecord(BaseModel):
    id: str
    company: str
    store: str
    country: str
    city: str = ""
    category: str = ""
    address: str = ""
    employee_count: int = 0
    daily_customer_count: int = 0
    daily_sales_usd: float = 0.0
    monthly_sales_usd: float = 0.0
    annual_sales_usd: float = 0.0
    inventory_value_usd: float = 0.0
    average_transaction_usd: float = 0.0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


RETAIL_DATABASE: Dict[
    str,
    RetailRecord,
] = {}


class RetailEngine:

    def register(self, record: RetailRecord) -> None:
        RETAIL_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[RetailRecord]:
        return RETAIL_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        RETAIL_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        employee_count: int,
        daily_customer_count: int,
        daily_sales_usd: float,
        monthly_sales_usd: float,
        annual_sales_usd: float,
        inventory_value_usd: float,
        average_transaction_usd: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.employee_count = employee_count
        record.daily_customer_count = daily_customer_count
        record.daily_sales_usd = daily_sales_usd
        record.monthly_sales_usd = monthly_sales_usd
        record.annual_sales_usd = annual_sales_usd
        record.inventory_value_usd = inventory_value_usd
        record.average_transaction_usd = average_transaction_usd
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[RetailRecord]:
        return sorted(
            RETAIL_DATABASE.values(),
            key=lambda item: (
                item.company,
                item.store,
            ),
        )


RETAIL_ENGINE = RetailEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 110
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 111
# ==========================================================

class BankingRecord(BaseModel):
    id: str
    bank_name: str
    country: str
    headquarters: str = ""
    total_assets_usd: float = 0.0
    total_deposits_usd: float = 0.0
    total_loans_usd: float = 0.0
    total_equity_usd: float = 0.0
    net_income_usd: float = 0.0
    tier1_capital_ratio: float = 0.0
    liquidity_ratio: float = 0.0
    nonperforming_loan_ratio: float = 0.0
    branch_count: int = 0
    employee_count: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


BANKING_DATABASE: Dict[str, BankingRecord] = {}


class BankingEngine:

    def register(self, record: BankingRecord) -> None:
        BANKING_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[BankingRecord]:
        return BANKING_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        BANKING_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        total_assets_usd: float,
        total_deposits_usd: float,
        total_loans_usd: float,
        total_equity_usd: float,
        net_income_usd: float,
        tier1_capital_ratio: float,
        liquidity_ratio: float,
        nonperforming_loan_ratio: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.total_assets_usd = total_assets_usd
        record.total_deposits_usd = total_deposits_usd
        record.total_loans_usd = total_loans_usd
        record.total_equity_usd = total_equity_usd
        record.net_income_usd = net_income_usd
        record.tier1_capital_ratio = tier1_capital_ratio
        record.liquidity_ratio = liquidity_ratio
        record.nonperforming_loan_ratio = nonperforming_loan_ratio
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[BankingRecord]:
        return sorted(
            BANKING_DATABASE.values(),
            key=lambda item: (
                item.country,
                item.bank_name,
            ),
        )


BANKING_ENGINE = BankingEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 111
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 112
# ==========================================================

class InsuranceRecord(BaseModel):
    id: str
    company: str
    country: str
    headquarters: str = ""
    insurance_type: str = ""
    total_assets_usd: float = 0.0
    total_premium_usd: float = 0.0
    total_claims_usd: float = 0.0
    investment_assets_usd: float = 0.0
    net_income_usd: float = 0.0
    solvency_ratio: float = 0.0
    customer_count: int = 0
    employee_count: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


INSURANCE_DATABASE: Dict[
    str,
    InsuranceRecord,
] = {}


class InsuranceEngine:

    def register(self, record: InsuranceRecord) -> None:
        INSURANCE_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[InsuranceRecord]:
        return INSURANCE_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        INSURANCE_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        total_assets_usd: float,
        total_premium_usd: float,
        total_claims_usd: float,
        investment_assets_usd: float,
        net_income_usd: float,
        solvency_ratio: float,
        customer_count: int,
        employee_count: int,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.total_assets_usd = total_assets_usd
        record.total_premium_usd = total_premium_usd
        record.total_claims_usd = total_claims_usd
        record.investment_assets_usd = investment_assets_usd
        record.net_income_usd = net_income_usd
        record.solvency_ratio = solvency_ratio
        record.customer_count = customer_count
        record.employee_count = employee_count
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[InsuranceRecord]:
        return sorted(
            INSURANCE_DATABASE.values(),
            key=lambda item: (
                item.country,
                item.company,
            ),
        )


INSURANCE_ENGINE = InsuranceEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 112
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 113
# ==========================================================

class InvestmentFundRecord(BaseModel):
    id: str
    fund_name: str
    country: str
    fund_type: str = ""
    asset_under_management_usd: float = 0.0
    equity_holdings_usd: float = 0.0
    bond_holdings_usd: float = 0.0
    commodity_holdings_usd: float = 0.0
    real_estate_holdings_usd: float = 0.0
    crypto_holdings_usd: float = 0.0
    cash_position_usd: float = 0.0
    investor_count: int = 0
    annual_return_percent: float = 0.0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


INVESTMENT_FUND_DATABASE: Dict[
    str,
    InvestmentFundRecord,
] = {}


class InvestmentFundEngine:

    def register(self, record: InvestmentFundRecord) -> None:
        INVESTMENT_FUND_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[InvestmentFundRecord]:
        return INVESTMENT_FUND_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        INVESTMENT_FUND_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        asset_under_management_usd: float,
        equity_holdings_usd: float,
        bond_holdings_usd: float,
        commodity_holdings_usd: float,
        real_estate_holdings_usd: float,
        crypto_holdings_usd: float,
        cash_position_usd: float,
        annual_return_percent: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.asset_under_management_usd = (
            asset_under_management_usd
        )
        record.equity_holdings_usd = equity_holdings_usd
        record.bond_holdings_usd = bond_holdings_usd
        record.commodity_holdings_usd = commodity_holdings_usd
        record.real_estate_holdings_usd = (
            real_estate_holdings_usd
        )
        record.crypto_holdings_usd = crypto_holdings_usd
        record.cash_position_usd = cash_position_usd
        record.annual_return_percent = annual_return_percent
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[InvestmentFundRecord]:
        return sorted(
            INVESTMENT_FUND_DATABASE.values(),
            key=lambda item: (
                item.country,
                item.fund_name,
            ),
        )


INVESTMENT_FUND_ENGINE = InvestmentFundEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 113
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 114
# ==========================================================

class VentureCapitalRecord(BaseModel):
    id: str
    fund_name: str
    country: str
    investment_stage: str = ""
    total_capital_usd: float = 0.0
    invested_capital_usd: float = 0.0
    portfolio_company_count: int = 0
    technology_focus: str = ""
    healthcare_focus: float = 0.0
    ai_focus: float = 0.0
    energy_focus: float = 0.0
    annual_investment_usd: float = 0.0
    exit_value_usd: float = 0.0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


VENTURE_CAPITAL_DATABASE: Dict[
    str,
    VentureCapitalRecord,
] = {}


class VentureCapitalEngine:

    def register(self, record: VentureCapitalRecord) -> None:
        VENTURE_CAPITAL_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[VentureCapitalRecord]:
        return VENTURE_CAPITAL_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        VENTURE_CAPITAL_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        total_capital_usd: float,
        invested_capital_usd: float,
        portfolio_company_count: int,
        annual_investment_usd: float,
        exit_value_usd: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.total_capital_usd = total_capital_usd
        record.invested_capital_usd = invested_capital_usd
        record.portfolio_company_count = portfolio_company_count
        record.annual_investment_usd = annual_investment_usd
        record.exit_value_usd = exit_value_usd
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[VentureCapitalRecord]:
        return sorted(
            VENTURE_CAPITAL_DATABASE.values(),
            key=lambda item: (
                item.country,
                item.fund_name,
            ),
        )


VENTURE_CAPITAL_ENGINE = VentureCapitalEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 114
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 115
# ==========================================================

class PrivateEquityRecord(BaseModel):
    id: str
    fund_name: str
    country: str
    strategy: str = ""
    assets_under_management_usd: float = 0.0
    invested_companies: int = 0
    acquisition_value_usd: float = 0.0
    exit_value_usd: float = 0.0
    portfolio_value_usd: float = 0.0
    sector_focus: str = ""
    average_holding_years: float = 0.0
    employee_count: int = 0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


PRIVATE_EQUITY_DATABASE: Dict[
    str,
    PrivateEquityRecord,
] = {}


class PrivateEquityEngine:

    def register(self, record: PrivateEquityRecord) -> None:
        PRIVATE_EQUITY_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[PrivateEquityRecord]:
        return PRIVATE_EQUITY_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        PRIVATE_EQUITY_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        assets_under_management_usd: float,
        invested_companies: int,
        acquisition_value_usd: float,
        exit_value_usd: float,
        portfolio_value_usd: float,
        average_holding_years: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.assets_under_management_usd = (
            assets_under_management_usd
        )
        record.invested_companies = invested_companies
        record.acquisition_value_usd = acquisition_value_usd
        record.exit_value_usd = exit_value_usd
        record.portfolio_value_usd = portfolio_value_usd
        record.average_holding_years = average_holding_years
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[PrivateEquityRecord]:
        return sorted(
            PRIVATE_EQUITY_DATABASE.values(),
            key=lambda item: (
                item.country,
                item.fund_name,
            ),
        )


PRIVATE_EQUITY_ENGINE = PrivateEquityEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 115
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 116
# ==========================================================

class RealEstateAssetRecord(BaseModel):
    id: str
    owner: str
    country: str
    city: str = ""
    asset_type: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    area_m2: float = 0.0
    estimated_value_usd: float = 0.0
    rental_income_usd: float = 0.0
    occupancy_rate: float = 0.0
    development_status: str = ""
    transaction_volume_usd: float = 0.0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


REAL_ESTATE_DATABASE: Dict[
    str,
    RealEstateAssetRecord,
] = {}


class RealEstateEngine:

    def register(self, record: RealEstateAssetRecord) -> None:
        REAL_ESTATE_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[RealEstateAssetRecord]:
        return REAL_ESTATE_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        REAL_ESTATE_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        estimated_value_usd: float,
        rental_income_usd: float,
        occupancy_rate: float,
        transaction_volume_usd: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.estimated_value_usd = estimated_value_usd
        record.rental_income_usd = rental_income_usd
        record.occupancy_rate = occupancy_rate
        record.transaction_volume_usd = transaction_volume_usd
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[RealEstateAssetRecord]:
        return sorted(
            REAL_ESTATE_DATABASE.values(),
            key=lambda item: (
                item.country,
                item.city,
            ),
        )


REAL_ESTATE_ENGINE = RealEstateEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 116
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 117
# ==========================================================

class CompanyRecord(BaseModel):
    id: str
    name: str
    country: str
    headquarters_city: str = ""
    industry: str = ""
    sector: str = ""
    founded_year: int = 0
    employees: int = 0
    annual_revenue_usd: float = 0.0
    market_cap_usd: float = 0.0
    total_assets_usd: float = 0.0
    debt_usd: float = 0.0
    profit_usd: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    website: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


COMPANY_DATABASE: Dict[str, CompanyRecord] = {}


class CompanyEngine:

    def register(self, record: CompanyRecord) -> None:
        COMPANY_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CompanyRecord]:
        return COMPANY_DATABASE.get(record_id)

    def remove(self, record_id: str) -> None:
        COMPANY_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        employees: int,
        annual_revenue_usd: float,
        market_cap_usd: float,
        total_assets_usd: float,
        debt_usd: float,
        profit_usd: float,
    ) -> None:
        record = self.get(record_id)
        if record is None:
            return

        record.employees = employees
        record.annual_revenue_usd = annual_revenue_usd
        record.market_cap_usd = market_cap_usd
        record.total_assets_usd = total_assets_usd
        record.debt_usd = debt_usd
        record.profit_usd = profit_usd
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[CompanyRecord]:
        return sorted(
            COMPANY_DATABASE.values(),
            key=lambda item: (
                item.country,
                item.name,
            ),
        )


COMPANY_ENGINE = CompanyEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 117
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 118
# ==========================================================

class CompanyLocationRecord(BaseModel):
    id: str
    company_id: str
    company_name: str
    location_type: str = ""
    country: str = ""
    city: str = ""
    address: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    employees: int = 0
    annual_output: float = 0.0
    output_unit: str = ""
    investment_usd: float = 0.0
    cash_flow_in_usd: float = 0.0
    cash_flow_out_usd: float = 0.0
    growth_rate: float = 0.0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


COMPANY_LOCATION_DATABASE: Dict[
    str,
    CompanyLocationRecord,
] = {}


class CompanyLocationEngine:

    def register(
        self,
        record: CompanyLocationRecord,
    ) -> None:
        COMPANY_LOCATION_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CompanyLocationRecord]:
        return COMPANY_LOCATION_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        COMPANY_LOCATION_DATABASE.pop(record_id, None)

    def update_flow(
        self,
        record_id: str,
        cash_flow_in_usd: float,
        cash_flow_out_usd: float,
        growth_rate: float,
        employees: int,
    ) -> None:
        record = self.get(record_id)

        if record is None:
            return

        record.cash_flow_in_usd = cash_flow_in_usd
        record.cash_flow_out_usd = cash_flow_out_usd
        record.growth_rate = growth_rate
        record.employees = employees
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[CompanyLocationRecord]:
        return sorted(
            COMPANY_LOCATION_DATABASE.values(),
            key=lambda item: (
                item.country,
                item.company_name,
            ),
        )


COMPANY_LOCATION_ENGINE = CompanyLocationEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 118
# ==========================================================
