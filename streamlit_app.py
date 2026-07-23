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
