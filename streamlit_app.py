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
# ==========================================================
# WEOS
# ĐOẠN 119
# ==========================================================

class EconomicNodeRecord(BaseModel):
    id: str
    name: str
    node_type: str = ""
    country: str = ""
    city: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    economic_weight: float = 0.0
    capital_inflow_usd: float = 0.0
    capital_outflow_usd: float = 0.0
    influence_score: float = 0.0
    connected_nodes: int = 0
    risk_level: float = 0.0
    growth_rate: float = 0.0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


ECONOMIC_NODE_DATABASE: Dict[
    str,
    EconomicNodeRecord,
] = {}


class EconomicNodeEngine:

    def register(
        self,
        record: EconomicNodeRecord,
    ) -> None:
        ECONOMIC_NODE_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[EconomicNodeRecord]:
        return ECONOMIC_NODE_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        ECONOMIC_NODE_DATABASE.pop(record_id, None)

    def update_flow(
        self,
        record_id: str,
        capital_inflow_usd: float,
        capital_outflow_usd: float,
        influence_score: float,
        risk_level: float,
        growth_rate: float,
    ) -> None:
        record = self.get(record_id)

        if record is None:
            return

        record.capital_inflow_usd = capital_inflow_usd
        record.capital_outflow_usd = capital_outflow_usd
        record.influence_score = influence_score
        record.risk_level = risk_level
        record.growth_rate = growth_rate
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[EconomicNodeRecord]:
        return sorted(
            ECONOMIC_NODE_DATABASE.values(),
            key=lambda item: item.influence_score,
            reverse=True,
        )


ECONOMIC_NODE_ENGINE = EconomicNodeEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 119
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 120
# ==========================================================

class CapitalFlowLinkRecord(BaseModel):
    id: str
    source_node: str
    target_node: str
    flow_type: str = ""
    amount_usd: float = 0.0
    direction: str = "in"
    speed: float = 0.0
    intensity: float = 0.0
    color_state: str = ""
    pulse_rate: float = 0.0
    created_time: Optional[datetime] = None
    updated_at: Optional[datetime] = None


CAPITAL_FLOW_LINK_DATABASE: Dict[
    str,
    CapitalFlowLinkRecord,
] = {}


class CapitalFlowLinkEngine:

    def register(
        self,
        record: CapitalFlowLinkRecord,
    ) -> None:
        CAPITAL_FLOW_LINK_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CapitalFlowLinkRecord]:
        return CAPITAL_FLOW_LINK_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        CAPITAL_FLOW_LINK_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        amount_usd: float,
        intensity: float,
        speed: float,
        direction: str,
        color_state: str,
    ) -> None:
        record = self.get(record_id)

        if record is None:
            return

        record.amount_usd = amount_usd
        record.intensity = intensity
        record.speed = speed
        record.direction = direction
        record.color_state = color_state
        record.updated_at = utc_now()

    def all(self) -> List[CapitalFlowLinkRecord]:
        return list(
            CAPITAL_FLOW_LINK_DATABASE.values()
        )


CAPITAL_FLOW_LINK_ENGINE = CapitalFlowLinkEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 120
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 121
# ==========================================================

class IndicatorConnectionRecord(BaseModel):
    id: str
    source_indicator: str
    target_indicator: str
    relationship: str = ""
    impact_level: float = 0.0
    correlation_score: float = 0.0
    delay_days: int = 0
    direction: str = ""
    explanation: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


INDICATOR_CONNECTION_DATABASE: Dict[
    str,
    IndicatorConnectionRecord,
] = {}


class IndicatorConnectionEngine:

    def register(
        self,
        record: IndicatorConnectionRecord,
    ) -> None:
        INDICATOR_CONNECTION_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[IndicatorConnectionRecord]:
        return INDICATOR_CONNECTION_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        INDICATOR_CONNECTION_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        impact_level: float,
        correlation_score: float,
        delay_days: int,
        direction: str,
        explanation: str,
    ) -> None:
        record = self.get(record_id)

        if record is None:
            return

        record.impact_level = impact_level
        record.correlation_score = correlation_score
        record.delay_days = delay_days
        record.direction = direction
        record.explanation = explanation
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[IndicatorConnectionRecord]:
        return sorted(
            INDICATOR_CONNECTION_DATABASE.values(),
            key=lambda item: item.impact_level,
            reverse=True,
        )


INDICATOR_CONNECTION_ENGINE = IndicatorConnectionEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 121
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 122
# ==========================================================

class MacroEventRecord(BaseModel):
    id: str
    event_name: str
    country: str = ""
    category: str = ""
    importance: str = ""
    actual_value: float = 0.0
    forecast_value: float = 0.0
    previous_value: float = 0.0
    market_impact: str = ""
    affected_assets: List[str] = []
    event_time: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


MACRO_EVENT_DATABASE: Dict[
    str,
    MacroEventRecord,
] = {}


class MacroEventEngine:

    def register(
        self,
        record: MacroEventRecord,
    ) -> None:
        MACRO_EVENT_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[MacroEventRecord]:
        return MACRO_EVENT_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        MACRO_EVENT_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        actual_value: float,
        forecast_value: float,
        previous_value: float,
        market_impact: str,
        affected_assets: List[str],
    ) -> None:
        record = self.get(record_id)

        if record is None:
            return

        record.actual_value = actual_value
        record.forecast_value = forecast_value
        record.previous_value = previous_value
        record.market_impact = market_impact
        record.affected_assets = affected_assets
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[MacroEventRecord]:
        return sorted(
            MACRO_EVENT_DATABASE.values(),
            key=lambda item: item.importance,
        )


MACRO_EVENT_ENGINE = MacroEventEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 122
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 123
# ==========================================================

class EconomicForecastRecord(BaseModel):
    id: str
    country: str
    indicator: str
    forecast_period: str = ""
    current_value: float = 0.0
    forecast_value: float = 0.0
    previous_forecast: float = 0.0
    confidence_level: float = 0.0
    upside_probability: float = 0.0
    downside_probability: float = 0.0
    analyst_count: int = 0
    forecast_source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


ECONOMIC_FORECAST_DATABASE: Dict[
    str,
    EconomicForecastRecord,
] = {}


class EconomicForecastEngine:

    def register(
        self,
        record: EconomicForecastRecord,
    ) -> None:
        ECONOMIC_FORECAST_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[EconomicForecastRecord]:
        return ECONOMIC_FORECAST_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        ECONOMIC_FORECAST_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        current_value: float,
        forecast_value: float,
        confidence_level: float,
        upside_probability: float,
        downside_probability: float,
        analyst_count: int,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.current_value = current_value
        record.forecast_value = forecast_value
        record.confidence_level = confidence_level
        record.upside_probability = upside_probability
        record.downside_probability = downside_probability
        record.analyst_count = analyst_count
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[EconomicForecastRecord]:
        return sorted(
            ECONOMIC_FORECAST_DATABASE.values(),
            key=lambda item: item.country,
        )


ECONOMIC_FORECAST_ENGINE = EconomicForecastEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 123
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 124
# ==========================================================

class MarketSentimentRecord(BaseModel):
    id: str
    asset: str
    region: str = ""
    bullish_score: float = 0.0
    bearish_score: float = 0.0
    neutral_score: float = 0.0
    investor_positioning: str = ""
    volatility_expectation: float = 0.0
    risk_appetite_score: float = 0.0
    fear_greed_index: float = 0.0
    news_sentiment_score: float = 0.0
    social_sentiment_score: float = 0.0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


MARKET_SENTIMENT_DATABASE: Dict[
    str,
    MarketSentimentRecord,
] = {}


class MarketSentimentEngine:

    def register(
        self,
        record: MarketSentimentRecord,
    ) -> None:
        MARKET_SENTIMENT_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[MarketSentimentRecord]:
        return MARKET_SENTIMENT_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        MARKET_SENTIMENT_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        bullish_score: float,
        bearish_score: float,
        neutral_score: float,
        volatility_expectation: float,
        risk_appetite_score: float,
        fear_greed_index: float,
        news_sentiment_score: float,
        social_sentiment_score: float,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.bullish_score = bullish_score
        record.bearish_score = bearish_score
        record.neutral_score = neutral_score
        record.volatility_expectation = volatility_expectation
        record.risk_appetite_score = risk_appetite_score
        record.fear_greed_index = fear_greed_index
        record.news_sentiment_score = news_sentiment_score
        record.social_sentiment_score = social_sentiment_score
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[MarketSentimentRecord]:
        return sorted(
            MARKET_SENTIMENT_DATABASE.values(),
            key=lambda item: item.asset,
        )


MARKET_SENTIMENT_ENGINE = MarketSentimentEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 124
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 125
# ==========================================================

class AssetCorrelationRecord(BaseModel):
    id: str
    asset_a: str
    asset_b: str
    correlation_period: str = ""
    correlation_value: float = 0.0
    volatility_a: float = 0.0
    volatility_b: float = 0.0
    beta_value: float = 0.0
    relationship_type: str = ""
    explanation: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


ASSET_CORRELATION_DATABASE: Dict[
    str,
    AssetCorrelationRecord,
] = {}


class AssetCorrelationEngine:

    def register(
        self,
        record: AssetCorrelationRecord,
    ) -> None:
        ASSET_CORRELATION_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[AssetCorrelationRecord]:
        return ASSET_CORRELATION_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        ASSET_CORRELATION_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        correlation_value: float,
        volatility_a: float,
        volatility_b: float,
        beta_value: float,
        relationship_type: str,
        explanation: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.correlation_value = correlation_value
        record.volatility_a = volatility_a
        record.volatility_b = volatility_b
        record.beta_value = beta_value
        record.relationship_type = relationship_type
        record.explanation = explanation
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[AssetCorrelationRecord]:
        return sorted(
            ASSET_CORRELATION_DATABASE.values(),
            key=lambda item: abs(item.correlation_value),
            reverse=True,
        )


ASSET_CORRELATION_ENGINE = AssetCorrelationEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 125
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 126
# ==========================================================

class ETFFlowRecord(BaseModel):
    id: str
    fund_name: str
    ticker: str
    asset_class: str = ""
    region: str = ""
    total_assets_usd: float = 0.0
    daily_inflow_usd: float = 0.0
    daily_outflow_usd: float = 0.0
    net_flow_usd: float = 0.0
    holdings_change_percent: float = 0.0
    investor_sentiment: str = ""
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


ETF_FLOW_DATABASE: Dict[
    str,
    ETFFlowRecord,
] = {}


class ETFFlowEngine:

    def register(
        self,
        record: ETFFlowRecord,
    ) -> None:
        ETF_FLOW_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[ETFFlowRecord]:
        return ETF_FLOW_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        ETF_FLOW_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        total_assets_usd: float,
        daily_inflow_usd: float,
        daily_outflow_usd: float,
        net_flow_usd: float,
        holdings_change_percent: float,
        investor_sentiment: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.total_assets_usd = total_assets_usd
        record.daily_inflow_usd = daily_inflow_usd
        record.daily_outflow_usd = daily_outflow_usd
        record.net_flow_usd = net_flow_usd
        record.holdings_change_percent = holdings_change_percent
        record.investor_sentiment = investor_sentiment
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[ETFFlowRecord]:
        return sorted(
            ETF_FLOW_DATABASE.values(),
            key=lambda item: abs(item.net_flow_usd),
            reverse=True,
        )


ETF_FLOW_ENGINE = ETFFlowEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 126
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 127
# ==========================================================

class GoldETFFlowRecord(BaseModel):
    id: str
    fund_name: str
    ticker: str
    gold_holdings_tonnes: float = 0.0
    gold_value_usd: float = 0.0
    daily_change_tonnes: float = 0.0
    monthly_change_tonnes: float = 0.0
    net_inflow_usd: float = 0.0
    net_outflow_usd: float = 0.0
    investor_demand_score: float = 0.0
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GOLD_ETF_FLOW_DATABASE: Dict[
    str,
    GoldETFFlowRecord,
] = {}


class GoldETFFlowEngine:

    def register(
        self,
        record: GoldETFFlowRecord,
    ) -> None:
        GOLD_ETF_FLOW_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GoldETFFlowRecord]:
        return GOLD_ETF_FLOW_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        GOLD_ETF_FLOW_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        gold_holdings_tonnes: float,
        gold_value_usd: float,
        daily_change_tonnes: float,
        monthly_change_tonnes: float,
        net_inflow_usd: float,
        net_outflow_usd: float,
        investor_demand_score: float,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.gold_holdings_tonnes = gold_holdings_tonnes
        record.gold_value_usd = gold_value_usd
        record.daily_change_tonnes = daily_change_tonnes
        record.monthly_change_tonnes = monthly_change_tonnes
        record.net_inflow_usd = net_inflow_usd
        record.net_outflow_usd = net_outflow_usd
        record.investor_demand_score = investor_demand_score
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[GoldETFFlowRecord]:
        return sorted(
            GOLD_ETF_FLOW_DATABASE.values(),
            key=lambda item: abs(item.net_inflow_usd),
            reverse=True,
        )


GOLD_ETF_FLOW_ENGINE = GoldETFFlowEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 127
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 128
# ==========================================================

class CommodityPriceRecord(BaseModel):
    id: str
    commodity_name: str
    symbol: str = ""
    category: str = ""
    price_usd: float = 0.0
    daily_change_percent: float = 0.0
    weekly_change_percent: float = 0.0
    monthly_change_percent: float = 0.0
    yearly_change_percent: float = 0.0
    trading_volume_usd: float = 0.0
    supply_index: float = 0.0
    demand_index: float = 0.0
    volatility_index: float = 0.0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


COMMODITY_PRICE_DATABASE: Dict[
    str,
    CommodityPriceRecord,
] = {}


class CommodityPriceEngine:

    def register(
        self,
        record: CommodityPriceRecord,
    ) -> None:
        COMMODITY_PRICE_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CommodityPriceRecord]:
        return COMMODITY_PRICE_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        COMMODITY_PRICE_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        price_usd: float,
        daily_change_percent: float,
        weekly_change_percent: float,
        monthly_change_percent: float,
        yearly_change_percent: float,
        trading_volume_usd: float,
        supply_index: float,
        demand_index: float,
        volatility_index: float,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.price_usd = price_usd
        record.daily_change_percent = daily_change_percent
        record.weekly_change_percent = weekly_change_percent
        record.monthly_change_percent = monthly_change_percent
        record.yearly_change_percent = yearly_change_percent
        record.trading_volume_usd = trading_volume_usd
        record.supply_index = supply_index
        record.demand_index = demand_index
        record.volatility_index = volatility_index
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[CommodityPriceRecord]:
        return sorted(
            COMMODITY_PRICE_DATABASE.values(),
            key=lambda item: abs(item.daily_change_percent),
            reverse=True,
        )


COMMODITY_PRICE_ENGINE = CommodityPriceEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 128
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 129
# ==========================================================

class EnergyPriceRecord(BaseModel):
    id: str
    energy_name: str
    symbol: str = ""
    category: str = ""
    price_usd: float = 0.0
    daily_change_percent: float = 0.0
    weekly_change_percent: float = 0.0
    monthly_change_percent: float = 0.0
    yearly_change_percent: float = 0.0
    production_index: float = 0.0
    consumption_index: float = 0.0
    inventory_level: float = 0.0
    geopolitical_risk_score: float = 0.0
    volatility_index: float = 0.0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


ENERGY_PRICE_DATABASE: Dict[
    str,
    EnergyPriceRecord,
] = {}


class EnergyPriceEngine:

    def register(
        self,
        record: EnergyPriceRecord,
    ) -> None:
        ENERGY_PRICE_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[EnergyPriceRecord]:
        return ENERGY_PRICE_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        ENERGY_PRICE_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        price_usd: float,
        daily_change_percent: float,
        weekly_change_percent: float,
        monthly_change_percent: float,
        yearly_change_percent: float,
        production_index: float,
        consumption_index: float,
        inventory_level: float,
        geopolitical_risk_score: float,
        volatility_index: float,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.price_usd = price_usd
        record.daily_change_percent = daily_change_percent
        record.weekly_change_percent = weekly_change_percent
        record.monthly_change_percent = monthly_change_percent
        record.yearly_change_percent = yearly_change_percent
        record.production_index = production_index
        record.consumption_index = consumption_index
        record.inventory_level = inventory_level
        record.geopolitical_risk_score = geopolitical_risk_score
        record.volatility_index = volatility_index
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[EnergyPriceRecord]:
        return sorted(
            ENERGY_PRICE_DATABASE.values(),
            key=lambda item: abs(item.daily_change_percent),
            reverse=True,
        )


ENERGY_PRICE_ENGINE = EnergyPriceEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 129
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 130
# ==========================================================

class InterestRateMarketRecord(BaseModel):
    id: str
    country: str
    central_bank: str = ""
    benchmark_rate: float = 0.0
    two_year_yield: float = 0.0
    five_year_yield: float = 0.0
    ten_year_yield: float = 0.0
    thirty_year_yield: float = 0.0
    yield_curve_slope: float = 0.0
    market_expectation: str = ""
    rate_cut_probability: float = 0.0
    rate_hike_probability: float = 0.0
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


INTEREST_RATE_MARKET_DATABASE: Dict[
    str,
    InterestRateMarketRecord,
] = {}


class InterestRateMarketEngine:

    def register(
        self,
        record: InterestRateMarketRecord,
    ) -> None:
        INTEREST_RATE_MARKET_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[InterestRateMarketRecord]:
        return INTEREST_RATE_MARKET_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        INTEREST_RATE_MARKET_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        benchmark_rate: float,
        two_year_yield: float,
        five_year_yield: float,
        ten_year_yield: float,
        thirty_year_yield: float,
        yield_curve_slope: float,
        rate_cut_probability: float,
        rate_hike_probability: float,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.benchmark_rate = benchmark_rate
        record.two_year_yield = two_year_yield
        record.five_year_yield = five_year_yield
        record.ten_year_yield = ten_year_yield
        record.thirty_year_yield = thirty_year_yield
        record.yield_curve_slope = yield_curve_slope
        record.rate_cut_probability = rate_cut_probability
        record.rate_hike_probability = rate_hike_probability
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[InterestRateMarketRecord]:
        return sorted(
            INTEREST_RATE_MARKET_DATABASE.values(),
            key=lambda item: item.country,
        )


INTEREST_RATE_MARKET_ENGINE = InterestRateMarketEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 130
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 131
# ==========================================================

class CurrencyStrengthRecord(BaseModel):
    id: str
    currency: str
    country: str = ""
    dxy_component: float = 0.0
    relative_strength_score: float = 0.0
    purchasing_power_index: float = 0.0
    inflation_pressure: float = 0.0
    interest_rate_support: float = 0.0
    trade_support: float = 0.0
    capital_flow_support: float = 0.0
    weekly_change_percent: float = 0.0
    monthly_change_percent: float = 0.0
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


CURRENCY_STRENGTH_DATABASE: Dict[
    str,
    CurrencyStrengthRecord,
] = {}


class CurrencyStrengthEngine:

    def register(
        self,
        record: CurrencyStrengthRecord,
    ) -> None:
        CURRENCY_STRENGTH_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CurrencyStrengthRecord]:
        return CURRENCY_STRENGTH_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        CURRENCY_STRENGTH_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        relative_strength_score: float,
        purchasing_power_index: float,
        inflation_pressure: float,
        interest_rate_support: float,
        trade_support: float,
        capital_flow_support: float,
        weekly_change_percent: float,
        monthly_change_percent: float,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.relative_strength_score = (
            relative_strength_score
        )
        record.purchasing_power_index = (
            purchasing_power_index
        )
        record.inflation_pressure = inflation_pressure
        record.interest_rate_support = interest_rate_support
        record.trade_support = trade_support
        record.capital_flow_support = capital_flow_support
        record.weekly_change_percent = weekly_change_percent
        record.monthly_change_percent = monthly_change_percent
        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[CurrencyStrengthRecord]:
        return sorted(
            CURRENCY_STRENGTH_DATABASE.values(),
            key=lambda item: item.relative_strength_score,
            reverse=True,
        )


CURRENCY_STRENGTH_ENGINE = CurrencyStrengthEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 131
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 132
# ==========================================================

class MacroScoreRecord(BaseModel):
    id: str
    country: str
    economic_strength_score: float = 0.0
    inflation_score: float = 0.0
    growth_score: float = 0.0
    employment_score: float = 0.0
    debt_score: float = 0.0
    currency_score: float = 0.0
    financial_stability_score: float = 0.0
    geopolitical_score: float = 0.0
    total_macro_score: float = 0.0
    ranking: int = 0
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


MACRO_SCORE_DATABASE: Dict[
    str,
    MacroScoreRecord,
] = {}


class MacroScoreEngine:

    def register(
        self,
        record: MacroScoreRecord,
    ) -> None:
        MACRO_SCORE_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[MacroScoreRecord]:
        return MACRO_SCORE_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        MACRO_SCORE_DATABASE.pop(record_id, None)

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.total_macro_score = (
            record.economic_strength_score * 0.25
            + record.growth_score * 0.15
            + record.employment_score * 0.15
            + record.inflation_score * 0.10
            + record.debt_score * 0.10
            + record.currency_score * 0.10
            + record.financial_stability_score * 0.10
            + record.geopolitical_score * 0.05
        )

        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def ranking(self) -> List[MacroScoreRecord]:
        return sorted(
            MACRO_SCORE_DATABASE.values(),
            key=lambda item: item.total_macro_score,
            reverse=True,
        )


MACRO_SCORE_ENGINE = MacroScoreEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 132
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 133
# ==========================================================

class RiskScoreRecord(BaseModel):
    id: str
    country: str
    market_risk: float = 0.0
    currency_risk: float = 0.0
    debt_risk: float = 0.0
    inflation_risk: float = 0.0
    political_risk: float = 0.0
    liquidity_risk: float = 0.0
    banking_risk: float = 0.0
    geopolitical_risk: float = 0.0
    total_risk_score: float = 0.0
    risk_level: str = ""
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


RISK_SCORE_DATABASE: Dict[
    str,
    RiskScoreRecord,
] = {}


class RiskScoreEngine:

    def register(
        self,
        record: RiskScoreRecord,
    ) -> None:
        RISK_SCORE_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[RiskScoreRecord]:
        return RISK_SCORE_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        RISK_SCORE_DATABASE.pop(record_id, None)

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.total_risk_score = (
            record.market_risk * 0.20
            + record.currency_risk * 0.15
            + record.debt_risk * 0.15
            + record.inflation_risk * 0.10
            + record.political_risk * 0.15
            + record.liquidity_risk * 0.10
            + record.banking_risk * 0.10
            + record.geopolitical_risk * 0.05
        )

        if record.total_risk_score >= 80:
            record.risk_level = "HIGH"

        elif record.total_risk_score >= 50:
            record.risk_level = "MEDIUM"

        else:
            record.risk_level = "LOW"

        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def ranking(self) -> List[RiskScoreRecord]:
        return sorted(
            RISK_SCORE_DATABASE.values(),
            key=lambda item: item.total_risk_score,
            reverse=True,
        )


RISK_SCORE_ENGINE = RiskScoreEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 133
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 134
# ==========================================================

class EconomicCycleRecord(BaseModel):
    id: str
    country: str
    cycle_phase: str = ""
    expansion_score: float = 0.0
    slowdown_score: float = 0.0
    recession_score: float = 0.0
    recovery_score: float = 0.0
    leading_indicator_score: float = 0.0
    coincident_indicator_score: float = 0.0
    lagging_indicator_score: float = 0.0
    probability_recession: float = 0.0
    probability_expansion: float = 0.0
    analysis_text: str = ""
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


ECONOMIC_CYCLE_DATABASE: Dict[
    str,
    EconomicCycleRecord,
] = {}


class EconomicCycleEngine:

    def register(
        self,
        record: EconomicCycleRecord,
    ) -> None:
        ECONOMIC_CYCLE_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[EconomicCycleRecord]:
        return ECONOMIC_CYCLE_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        ECONOMIC_CYCLE_DATABASE.pop(record_id, None)

    def analyze(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        scores = {
            "EXPANSION": record.expansion_score,
            "SLOWDOWN": record.slowdown_score,
            "RECESSION": record.recession_score,
            "RECOVERY": record.recovery_score,
        }

        record.cycle_phase = max(
            scores,
            key=scores.get,
        )

        total = sum(scores.values())

        if total > 0:
            record.probability_expansion = (
                record.expansion_score / total
            )

            record.probability_recession = (
                record.recession_score / total
            )

        record.analysis_text = (
            f"Economic cycle phase: "
            f"{record.cycle_phase}"
        )

        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def all(self) -> List[EconomicCycleRecord]:
        return sorted(
            ECONOMIC_CYCLE_DATABASE.values(),
            key=lambda item: item.country,
        )


ECONOMIC_CYCLE_ENGINE = EconomicCycleEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 134
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 135
# ==========================================================

class MacroSignalRecord(BaseModel):
    id: str
    country: str
    signal_name: str
    signal_type: str = ""
    value: float = 0.0
    weight: float = 0.0
    direction: str = ""
    impact_score: float = 0.0
    confidence_score: float = 0.0
    explanation: str = ""
    generated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


MACRO_SIGNAL_DATABASE: Dict[
    str,
    MacroSignalRecord,
] = {}


class MacroSignalEngine:

    def register(
        self,
        record: MacroSignalRecord,
    ) -> None:
        MACRO_SIGNAL_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[MacroSignalRecord]:
        return MACRO_SIGNAL_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        MACRO_SIGNAL_DATABASE.pop(record_id, None)

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.impact_score = (
            record.value
            * record.weight
            * record.confidence_score
        )

        if record.impact_score > 0:
            record.direction = "POSITIVE"

        elif record.impact_score < 0:
            record.direction = "NEGATIVE"

        else:
            record.direction = "NEUTRAL"

        record.explanation = (
            f"{record.signal_name} "
            f"creates {record.direction} impact "
            f"with score {record.impact_score}"
        )

        record.status = DataStatus.REALTIME
        record.generated_time = utc_now()
        record.updated_at = utc_now()

    def all(self) -> List[MacroSignalRecord]:
        return sorted(
            MACRO_SIGNAL_DATABASE.values(),
            key=lambda item: abs(item.impact_score),
            reverse=True,
        )


MACRO_SIGNAL_ENGINE = MacroSignalEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 135
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 136
# ==========================================================

class MarketImpactRecord(BaseModel):
    id: str
    event_name: str
    asset: str
    country: str = ""
    impact_direction: str = ""
    impact_strength: float = 0.0
    probability: float = 0.0
    expected_move_percent: float = 0.0
    volatility_effect: float = 0.0
    liquidity_effect: float = 0.0
    explanation: str = ""
    generated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


MARKET_IMPACT_DATABASE: Dict[
    str,
    MarketImpactRecord,
] = {}


class MarketImpactEngine:

    def register(
        self,
        record: MarketImpactRecord,
    ) -> None:
        MARKET_IMPACT_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[MarketImpactRecord]:
        return MARKET_IMPACT_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        MARKET_IMPACT_DATABASE.pop(record_id, None)

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.impact_strength = (
            record.probability
            * (
                abs(record.expected_move_percent)
                + record.volatility_effect
                + record.liquidity_effect
            )
        )

        if record.expected_move_percent > 0:
            record.impact_direction = "BULLISH"

        elif record.expected_move_percent < 0:
            record.impact_direction = "BEARISH"

        else:
            record.impact_direction = "NEUTRAL"

        record.explanation = (
            f"{record.event_name} impacts "
            f"{record.asset} with "
            f"{record.impact_direction} bias"
        )

        record.generated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(self) -> List[MarketImpactRecord]:
        return sorted(
            MARKET_IMPACT_DATABASE.values(),
            key=lambda item: item.impact_strength,
            reverse=True,
        )


MARKET_IMPACT_ENGINE = MarketImpactEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 136
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 137
# ==========================================================

class AssetFlowPredictionRecord(BaseModel):
    id: str
    asset: str
    source_region: str = ""
    destination_region: str = ""
    prediction_period: str = ""
    expected_inflow_usd: float = 0.0
    expected_outflow_usd: float = 0.0
    confidence_score: float = 0.0
    macro_support_score: float = 0.0
    liquidity_score: float = 0.0
    risk_adjustment_score: float = 0.0
    final_prediction_score: float = 0.0
    prediction_direction: str = ""
    explanation: str = ""
    generated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


ASSET_FLOW_PREDICTION_DATABASE: Dict[
    str,
    AssetFlowPredictionRecord,
] = {}


class AssetFlowPredictionEngine:

    def register(
        self,
        record: AssetFlowPredictionRecord,
    ) -> None:
        ASSET_FLOW_PREDICTION_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[AssetFlowPredictionRecord]:
        return ASSET_FLOW_PREDICTION_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        ASSET_FLOW_PREDICTION_DATABASE.pop(record_id, None)

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        net_flow = (
            record.expected_inflow_usd
            - record.expected_outflow_usd
        )

        record.final_prediction_score = (
            record.confidence_score * 0.25
            + record.macro_support_score * 0.30
            + record.liquidity_score * 0.20
            + record.risk_adjustment_score * 0.25
        )

        if net_flow > 0:
            record.prediction_direction = "INFLOW"

        elif net_flow < 0:
            record.prediction_direction = "OUTFLOW"

        else:
            record.prediction_direction = "NEUTRAL"

        record.explanation = (
            f"Predicted capital movement for "
            f"{record.asset}: "
            f"{record.prediction_direction}"
        )

        record.generated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(self) -> List[AssetFlowPredictionRecord]:
        return sorted(
            ASSET_FLOW_PREDICTION_DATABASE.values(),
            key=lambda item: item.final_prediction_score,
            reverse=True,
        )


ASSET_FLOW_PREDICTION_ENGINE = AssetFlowPredictionEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 137
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 138
# ==========================================================

class MacroScenarioRecord(BaseModel):
    id: str
    scenario_name: str
    country: str = ""
    scenario_type: str = ""
    probability: float = 0.0
    growth_impact: float = 0.0
    inflation_impact: float = 0.0
    currency_impact: float = 0.0
    bond_impact: float = 0.0
    equity_impact: float = 0.0
    gold_impact: float = 0.0
    risk_level: str = ""
    explanation: str = ""
    generated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


MACRO_SCENARIO_DATABASE: Dict[
    str,
    MacroScenarioRecord,
] = {}


class MacroScenarioEngine:

    def register(
        self,
        record: MacroScenarioRecord,
    ) -> None:
        MACRO_SCENARIO_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[MacroScenarioRecord]:
        return MACRO_SCENARIO_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        MACRO_SCENARIO_DATABASE.pop(record_id, None)

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        impact_values = [
            abs(record.growth_impact),
            abs(record.inflation_impact),
            abs(record.currency_impact),
            abs(record.bond_impact),
            abs(record.equity_impact),
            abs(record.gold_impact),
        ]

        total_impact = sum(impact_values)

        if total_impact >= 70:
            record.risk_level = "HIGH"

        elif total_impact >= 35:
            record.risk_level = "MEDIUM"

        else:
            record.risk_level = "LOW"

        record.explanation = (
            f"Scenario {record.scenario_name} "
            f"has probability "
            f"{record.probability}% with "
            f"{record.risk_level} impact"
        )

        record.generated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(self) -> List[MacroScenarioRecord]:
        return sorted(
            MACRO_SCENARIO_DATABASE.values(),
            key=lambda item: item.probability,
            reverse=True,
        )


MACRO_SCENARIO_ENGINE = MacroScenarioEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 138
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 139
# ==========================================================

class AIAnalysisRecord(BaseModel):
    id: str
    analysis_type: str
    target: str
    country: str = ""
    asset: str = ""
    input_data: Dict[str, Any] = {}
    prediction: str = ""
    confidence_score: float = 0.0
    bullish_probability: float = 0.0
    bearish_probability: float = 0.0
    neutral_probability: float = 0.0
    reasoning: str = ""
    generated_time: Optional[datetime] = None
    model_version: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


AI_ANALYSIS_DATABASE: Dict[
    str,
    AIAnalysisRecord,
] = {}


class AIAnalysisEngine:

    def register(
        self,
        record: AIAnalysisRecord,
    ) -> None:
        AI_ANALYSIS_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[AIAnalysisRecord]:
        return AI_ANALYSIS_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        AI_ANALYSIS_DATABASE.pop(record_id, None)

    def analyze(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        highest_probability = max(
            record.bullish_probability,
            record.bearish_probability,
            record.neutral_probability,
        )

        if highest_probability == record.bullish_probability:
            record.prediction = "BULLISH"

        elif highest_probability == record.bearish_probability:
            record.prediction = "BEARISH"

        else:
            record.prediction = "NEUTRAL"

        record.confidence_score = highest_probability

        record.reasoning = (
            f"AI analysis for {record.target}: "
            f"{record.prediction} "
            f"with confidence "
            f"{record.confidence_score}"
        )

        record.generated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def all(self) -> List[AIAnalysisRecord]:
        return sorted(
            AI_ANALYSIS_DATABASE.values(),
            key=lambda item: item.confidence_score,
            reverse=True,
        )


AI_ANALYSIS_ENGINE = AIAnalysisEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 139
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 140
# ==========================================================

class NewsAnalysisRecord(BaseModel):
    id: str
    headline: str
    source_name: str = ""
    country: str = ""
    category: str = ""
    related_assets: List[str] = []
    sentiment_score: float = 0.0
    importance_score: float = 0.0
    market_impact_score: float = 0.0
    positive_keywords: List[str] = []
    negative_keywords: List[str] = []
    ai_summary: str = ""
    publication_time: Optional[datetime] = None
    analyzed_time: Optional[datetime] = None
    source_url: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


NEWS_ANALYSIS_DATABASE: Dict[
    str,
    NewsAnalysisRecord,
] = {}


class NewsAnalysisEngine:

    def register(
        self,
        record: NewsAnalysisRecord,
    ) -> None:
        NEWS_ANALYSIS_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[NewsAnalysisRecord]:
        return NEWS_ANALYSIS_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        NEWS_ANALYSIS_DATABASE.pop(record_id, None)

    def analyze(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        sentiment = (
            len(record.positive_keywords)
            -
            len(record.negative_keywords)
        )

        record.sentiment_score = sentiment

        record.market_impact_score = (
            record.importance_score
            *
            abs(record.sentiment_score)
        )

        if record.sentiment_score > 0:
            record.ai_summary = (
                f"Positive impact detected "
                f"for {record.related_assets}"
            )

        elif record.sentiment_score < 0:
            record.ai_summary = (
                f"Negative impact detected "
                f"for {record.related_assets}"
            )

        else:
            record.ai_summary = (
                "Neutral market impact"
            )

        record.analyzed_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(self) -> List[NewsAnalysisRecord]:
        return sorted(
            NEWS_ANALYSIS_DATABASE.values(),
            key=lambda item: item.market_impact_score,
            reverse=True,
        )


NEWS_ANALYSIS_ENGINE = NewsAnalysisEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 140
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 141
# ==========================================================

class DataQualityRecord(BaseModel):
    id: str
    dataset_name: str
    source_name: str = ""
    completeness_score: float = 0.0
    accuracy_score: float = 0.0
    freshness_score: float = 0.0
    reliability_score: float = 0.0
    total_quality_score: float = 0.0
    missing_fields: int = 0
    duplicate_records: int = 0
    last_check_time: Optional[datetime] = None
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


DATA_QUALITY_DATABASE: Dict[
    str,
    DataQualityRecord,
] = {}


class DataQualityEngine:

    def register(
        self,
        record: DataQualityRecord,
    ) -> None:
        DATA_QUALITY_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[DataQualityRecord]:
        return DATA_QUALITY_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        DATA_QUALITY_DATABASE.pop(record_id, None)

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.total_quality_score = (
            record.completeness_score * 0.25
            + record.accuracy_score * 0.30
            + record.freshness_score * 0.25
            + record.reliability_score * 0.20
        )

        record.last_check_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(self) -> List[DataQualityRecord]:
        return sorted(
            DATA_QUALITY_DATABASE.values(),
            key=lambda item: item.total_quality_score,
            reverse=True,
        )


DATA_QUALITY_ENGINE = DataQualityEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 141
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 142
# ==========================================================

class DataSourceRecord(BaseModel):
    id: str
    source_name: str
    source_type: str = ""
    provider: str = ""
    api_endpoint: str = ""
    update_frequency: str = ""
    supported_data: List[str] = []
    reliability_score: float = 0.0
    response_time_ms: float = 0.0
    last_sync_time: Optional[datetime] = None
    connection_status: str = ""
    error_count: int = 0
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


DATA_SOURCE_DATABASE: Dict[
    str,
    DataSourceRecord,
] = {}


class DataSourceEngine:

    def register(
        self,
        record: DataSourceRecord,
    ) -> None:
        DATA_SOURCE_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[DataSourceRecord]:
        return DATA_SOURCE_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        DATA_SOURCE_DATABASE.pop(record_id, None)

    def update_status(
        self,
        record_id: str,
        connection_status: str,
        response_time_ms: float,
        error_count: int,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.connection_status = connection_status
        record.response_time_ms = response_time_ms
        record.error_count = error_count
        record.last_sync_time = utc_now()
        record.updated_at = utc_now()

        if connection_status == "CONNECTED":
            record.status = DataStatus.REALTIME

        else:
            record.status = DataStatus.ERROR

    def all(self) -> List[DataSourceRecord]:
        return sorted(
            DATA_SOURCE_DATABASE.values(),
            key=lambda item: item.reliability_score,
            reverse=True,
        )


DATA_SOURCE_ENGINE = DataSourceEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 142
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 143
# ==========================================================

class DataSyncRecord(BaseModel):
    id: str
    source_id: str
    dataset_name: str
    sync_type: str = ""
    records_received: int = 0
    records_updated: int = 0
    records_failed: int = 0
    sync_duration_seconds: float = 0.0
    sync_frequency: str = ""
    last_sync_time: Optional[datetime] = None
    next_sync_time: Optional[datetime] = None
    sync_status: str = ""
    error_message: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


DATA_SYNC_DATABASE: Dict[
    str,
    DataSyncRecord,
] = {}


class DataSyncEngine:

    def register(
        self,
        record: DataSyncRecord,
    ) -> None:
        DATA_SYNC_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[DataSyncRecord]:
        return DATA_SYNC_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        DATA_SYNC_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        records_received: int,
        records_updated: int,
        records_failed: int,
        sync_duration_seconds: float,
        sync_status: str,
        error_message: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.records_received = records_received
        record.records_updated = records_updated
        record.records_failed = records_failed
        record.sync_duration_seconds = sync_duration_seconds
        record.sync_status = sync_status
        record.error_message = error_message
        record.last_sync_time = utc_now()
        record.updated_at = utc_now()

        if sync_status == "SUCCESS":
            record.status = DataStatus.REALTIME

        elif sync_status == "FAILED":
            record.status = DataStatus.ERROR

        else:
            record.status = DataStatus.WAITING

    def all(self) -> List[DataSyncRecord]:
        return sorted(
            DATA_SYNC_DATABASE.values(),
            key=lambda item: item.last_sync_time
            or datetime.min,
            reverse=True,
        )


DATA_SYNC_ENGINE = DataSyncEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 143
# ==========================================================v
# ==========================================================
# WEOS
# ĐOẠN 144
# ==========================================================

class APIConnectorRecord(BaseModel):
    id: str
    name: str
    provider: str = ""
    api_type: str = ""
    endpoint: str = ""
    authentication_type: str = ""
    request_limit: int = 0
    requests_used: int = 0
    response_time_ms: float = 0.0
    last_request_time: Optional[datetime] = None
    connection_status: str = ""
    error_message: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


API_CONNECTOR_DATABASE: Dict[
    str,
    APIConnectorRecord,
] = {}


class APIConnectorEngine:

    def register(
        self,
        record: APIConnectorRecord,
    ) -> None:
        API_CONNECTOR_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[APIConnectorRecord]:
        return API_CONNECTOR_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        API_CONNECTOR_DATABASE.pop(record_id, None)

    def update_connection(
        self,
        record_id: str,
        connection_status: str,
        response_time_ms: float,
        error_message: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.connection_status = connection_status
        record.response_time_ms = response_time_ms
        record.error_message = error_message
        record.last_request_time = utc_now()
        record.updated_at = utc_now()

        if connection_status == "CONNECTED":
            record.status = DataStatus.REALTIME

        elif connection_status == "ERROR":
            record.status = DataStatus.ERROR

        else:
            record.status = DataStatus.WAITING

    def usage(
        self,
        record_id: str,
    ) -> float:

        record = self.get(record_id)

        if record is None:
            return 0.0

        if record.request_limit == 0:
            return 0.0

        return (
            record.requests_used
            /
            record.request_limit
        ) * 100

    def all(self) -> List[APIConnectorRecord]:
        return sorted(
            API_CONNECTOR_DATABASE.values(),
            key=lambda item: item.response_time_ms,
        )


API_CONNECTOR_ENGINE = APIConnectorEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 144
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 145
# ==========================================================

class RealtimeStreamRecord(BaseModel):
    id: str
    stream_name: str
    data_type: str = ""
    source: str = ""
    update_interval_seconds: int = 0
    messages_received: int = 0
    messages_processed: int = 0
    messages_failed: int = 0
    latency_ms: float = 0.0
    throughput_per_second: float = 0.0
    stream_status: str = ""
    last_message_time: Optional[datetime] = None
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


REALTIME_STREAM_DATABASE: Dict[
    str,
    RealtimeStreamRecord,
] = {}


class RealtimeStreamEngine:

    def register(
        self,
        record: RealtimeStreamRecord,
    ) -> None:
        REALTIME_STREAM_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[RealtimeStreamRecord]:
        return REALTIME_STREAM_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        REALTIME_STREAM_DATABASE.pop(record_id, None)

    def update(
        self,
        record_id: str,
        messages_received: int,
        messages_processed: int,
        messages_failed: int,
        latency_ms: float,
        throughput_per_second: float,
        stream_status: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.messages_received = messages_received
        record.messages_processed = messages_processed
        record.messages_failed = messages_failed
        record.latency_ms = latency_ms
        record.throughput_per_second = throughput_per_second
        record.stream_status = stream_status
        record.last_message_time = utc_now()
        record.updated_at = utc_now()

        if stream_status == "ACTIVE":
            record.status = DataStatus.REALTIME

        elif stream_status == "ERROR":
            record.status = DataStatus.ERROR

        else:
            record.status = DataStatus.WAITING

    def health_score(
        self,
        record_id: str,
    ) -> float:

        record = self.get(record_id)

        if record is None:
            return 0.0

        latency_score = max(
            0,
            100 - record.latency_ms / 10
        )

        failure_score = 100

        if record.messages_received > 0:
            failure_score = (
                1 -
                (
                    record.messages_failed
                    /
                    record.messages_received
                )
            ) * 100

        return (
            latency_score * 0.4
            +
            failure_score * 0.6
        )

    def all(self) -> List[RealtimeStreamRecord]:
        return sorted(
            REALTIME_STREAM_DATABASE.values(),
            key=lambda item: item.latency_ms,
        )


REALTIME_STREAM_ENGINE = RealtimeStreamEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 145
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 146
# ==========================================================

class CacheRecord(BaseModel):
    id: str
    cache_name: str
    data_type: str = ""
    storage_type: str = ""
    key_count: int = 0
    memory_usage_mb: float = 0.0
    hit_count: int = 0
    miss_count: int = 0
    hit_rate_percent: float = 0.0
    ttl_seconds: int = 0
    last_refresh_time: Optional[datetime] = None
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


CACHE_DATABASE: Dict[
    str,
    CacheRecord,
] = {}


class CacheEngine:

    def register(
        self,
        record: CacheRecord,
    ) -> None:
        CACHE_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CacheRecord]:
        return CACHE_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        CACHE_DATABASE.pop(record_id, None)

    def update_usage(
        self,
        record_id: str,
        key_count: int,
        memory_usage_mb: float,
        hit_count: int,
        miss_count: int,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.key_count = key_count
        record.memory_usage_mb = memory_usage_mb
        record.hit_count = hit_count
        record.miss_count = miss_count

        total_requests = (
            hit_count + miss_count
        )

        if total_requests > 0:
            record.hit_rate_percent = (
                hit_count
                /
                total_requests
            ) * 100

        record.last_refresh_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def clear(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.key_count = 0
        record.memory_usage_mb = 0.0
        record.hit_count = 0
        record.miss_count = 0
        record.hit_rate_percent = 0.0
        record.updated_at = utc_now()

    def all(self) -> List[CacheRecord]:
        return sorted(
            CACHE_DATABASE.values(),
            key=lambda item: item.hit_rate_percent,
            reverse=True,
        )


CACHE_ENGINE = CacheEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 146
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 147
# ==========================================================

class DatabaseRecord(BaseModel):
    id: str
    database_name: str
    database_type: str = ""
    host: str = ""
    port: int = 0
    table_count: int = 0
    record_count: int = 0
    storage_size_gb: float = 0.0
    query_per_second: float = 0.0
    connection_count: int = 0
    max_connection: int = 0
    backup_status: str = ""
    last_backup_time: Optional[datetime] = None
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


DATABASE_MONITOR_DATABASE: Dict[
    str,
    DatabaseRecord,
] = {}


class DatabaseEngine:

    def register(
        self,
        record: DatabaseRecord,
    ) -> None:
        DATABASE_MONITOR_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[DatabaseRecord]:
        return DATABASE_MONITOR_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        DATABASE_MONITOR_DATABASE.pop(record_id, None)

    def update_metrics(
        self,
        record_id: str,
        record_count: int,
        storage_size_gb: float,
        query_per_second: float,
        connection_count: int,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.record_count = record_count
        record.storage_size_gb = storage_size_gb
        record.query_per_second = query_per_second
        record.connection_count = connection_count
        record.updated_at = utc_now()

        record.status = DataStatus.REALTIME

    def health_score(
        self,
        record_id: str,
    ) -> float:

        record = self.get(record_id)

        if record is None:
            return 0.0

        connection_score = 100

        if record.max_connection > 0:
            usage = (
                record.connection_count
                /
                record.max_connection
            )

            connection_score = (
                1 - usage
            ) * 100

        return max(
            0,
            connection_score,
        )

    def all(self) -> List[DatabaseRecord]:
        return sorted(
            DATABASE_MONITOR_DATABASE.values(),
            key=lambda item: item.database_name,
        )


DATABASE_ENGINE = DatabaseEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 147
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 148
# ==========================================================

class SystemHealthRecord(BaseModel):
    id: str
    service_name: str
    service_type: str = ""
    cpu_usage_percent: float = 0.0
    memory_usage_percent: float = 0.0
    disk_usage_percent: float = 0.0
    network_usage_percent: float = 0.0
    response_time_ms: float = 0.0
    uptime_percent: float = 0.0
    error_rate_percent: float = 0.0
    active_users: int = 0
    health_score: float = 0.0
    last_check_time: Optional[datetime] = None
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


SYSTEM_HEALTH_DATABASE: Dict[
    str,
    SystemHealthRecord,
] = {}


class SystemHealthEngine:

    def register(
        self,
        record: SystemHealthRecord,
    ) -> None:
        SYSTEM_HEALTH_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[SystemHealthRecord]:
        return SYSTEM_HEALTH_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        SYSTEM_HEALTH_DATABASE.pop(record_id, None)

    def calculate_health(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        performance_score = (
            100
            -
            (
                record.cpu_usage_percent * 0.2
                +
                record.memory_usage_percent * 0.2
                +
                record.disk_usage_percent * 0.1
                +
                record.error_rate_percent * 0.3
                +
                record.response_time_ms * 0.01
            )
        )

        uptime_score = (
            record.uptime_percent * 0.2
        )

        record.health_score = max(
            0,
            min(
                100,
                performance_score * 0.8
                +
                uptime_score,
            ),
        )

        record.last_check_time = utc_now()
        record.updated_at = utc_now()

        if record.health_score >= 80:
            record.status = DataStatus.REALTIME

        elif record.health_score >= 50:
            record.status = DataStatus.WAITING

        else:
            record.status = DataStatus.ERROR

    def ranking(self) -> List[SystemHealthRecord]:
        return sorted(
            SYSTEM_HEALTH_DATABASE.values(),
            key=lambda item: item.health_score,
            reverse=True,
        )


SYSTEM_HEALTH_ENGINE = SystemHealthEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 148
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 149
# ==========================================================

class UserActivityRecord(BaseModel):
    id: str
    user_id: str
    session_id: str = ""
    activity_type: str = ""
    page_name: str = ""
    action_name: str = ""
    duration_seconds: float = 0.0
    device_type: str = ""
    location_country: str = ""
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


USER_ACTIVITY_DATABASE: Dict[
    str,
    UserActivityRecord,
] = {}


class UserActivityEngine:

    def register(
        self,
        record: UserActivityRecord,
    ) -> None:
        USER_ACTIVITY_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[UserActivityRecord]:
        return USER_ACTIVITY_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        USER_ACTIVITY_DATABASE.pop(record_id, None)

    def track(
        self,
        record_id: str,
        activity_type: str,
        page_name: str,
        action_name: str,
        duration_seconds: float,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.activity_type = activity_type
        record.page_name = page_name
        record.action_name = action_name
        record.duration_seconds = duration_seconds
        record.timestamp = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def activity_summary(
        self,
        user_id: str,
    ) -> Dict[str, int]:

        result = {}

        for item in USER_ACTIVITY_DATABASE.values():

            if item.user_id == user_id:

                if item.activity_type not in result:
                    result[item.activity_type] = 0

                result[item.activity_type] += 1

        return result

    def all(self) -> List[UserActivityRecord]:
        return sorted(
            USER_ACTIVITY_DATABASE.values(),
            key=lambda item: item.timestamp
            or datetime.min,
            reverse=True,
        )


USER_ACTIVITY_ENGINE = UserActivityEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 149
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 150
# ==========================================================

class AlertRecord(BaseModel):
    id: str
    alert_type: str
    target: str
    severity: str = ""
    title: str = ""
    message: str = ""
    trigger_value: float = 0.0
    current_value: float = 0.0
    threshold_value: float = 0.0
    affected_assets: List[str] = []
    affected_countries: List[str] = []
    created_time: Optional[datetime] = None
    resolved_time: Optional[datetime] = None
    alert_status: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


ALERT_DATABASE: Dict[
    str,
    AlertRecord,
] = {}


class AlertEngine:

    def register(
        self,
        record: AlertRecord,
    ) -> None:
        ALERT_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[AlertRecord]:
        return ALERT_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        ALERT_DATABASE.pop(record_id, None)

    def trigger(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        difference = (
            record.current_value
            -
            record.threshold_value
        )

        if abs(difference) >= abs(
            record.trigger_value
        ):
            record.alert_status = "TRIGGERED"

        else:
            record.alert_status = "NORMAL"

        record.created_time = utc_now()
        record.updated_at = utc_now()

        if record.alert_status == "TRIGGERED":
            record.status = DataStatus.REALTIME

        else:
            record.status = DataStatus.WAITING

    def active_alerts(self) -> List[AlertRecord]:
        return sorted(
            [
                item
                for item in ALERT_DATABASE.values()
                if item.alert_status == "TRIGGERED"
            ],
            key=lambda item: item.severity,
        )


ALERT_ENGINE = AlertEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 150
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 151
# ==========================================================

class DecisionSignalRecord(BaseModel):
    id: str
    target: str
    target_type: str = ""
    signal_direction: str = ""
    confidence_score: float = 0.0
    macro_score: float = 0.0
    technical_score: float = 0.0
    sentiment_score: float = 0.0
    liquidity_score: float = 0.0
    risk_score: float = 0.0
    final_score: float = 0.0
    recommendation: str = ""
    explanation: str = ""
    generated_time: Optional[datetime] = None
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


DECISION_SIGNAL_DATABASE: Dict[
    str,
    DecisionSignalRecord,
] = {}


class DecisionSignalEngine:

    def register(
        self,
        record: DecisionSignalRecord,
    ) -> None:
        DECISION_SIGNAL_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[DecisionSignalRecord]:
        return DECISION_SIGNAL_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        DECISION_SIGNAL_DATABASE.pop(record_id, None)

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.final_score = (
            record.macro_score * 0.30
            +
            record.technical_score * 0.20
            +
            record.sentiment_score * 0.20
            +
            record.liquidity_score * 0.15
            -
            record.risk_score * 0.15
        )

        if record.final_score >= 70:
            record.signal_direction = "BULLISH"
            record.recommendation = "POSITIVE"

        elif record.final_score <= 30:
            record.signal_direction = "BEARISH"
            record.recommendation = "NEGATIVE"

        else:
            record.signal_direction = "NEUTRAL"
            record.recommendation = "WAIT"

        record.confidence_score = abs(
            record.final_score - 50
        ) * 2

        record.explanation = (
            f"Decision signal for "
            f"{record.target}: "
            f"{record.signal_direction}"
        )

        record.generated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(self) -> List[DecisionSignalRecord]:
        return sorted(
            DECISION_SIGNAL_DATABASE.values(),
            key=lambda item: item.confidence_score,
            reverse=True,
        )


DECISION_SIGNAL_ENGINE = DecisionSignalEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 151
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 152
# ==========================================================

class CorrelationNetworkRecord(BaseModel):
    id: str
    source_asset: str
    target_asset: str
    correlation_value: float = 0.0
    relationship_type: str = ""
    time_period: str = ""
    strength_score: float = 0.0
    positive_relation: bool = False
    impact_direction: str = ""
    explanation: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


CORRELATION_NETWORK_DATABASE: Dict[
    str,
    CorrelationNetworkRecord,
] = {}


class CorrelationNetworkEngine:

    def register(
        self,
        record: CorrelationNetworkRecord,
    ) -> None:
        CORRELATION_NETWORK_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CorrelationNetworkRecord]:
        return CORRELATION_NETWORK_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        CORRELATION_NETWORK_DATABASE.pop(record_id, None)

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.strength_score = abs(
            record.correlation_value
        ) * 100

        if record.correlation_value > 0:
            record.positive_relation = True
            record.impact_direction = "SAME_DIRECTION"

        elif record.correlation_value < 0:
            record.positive_relation = False
            record.impact_direction = "OPPOSITE_DIRECTION"

        else:
            record.positive_relation = False
            record.impact_direction = "NO_RELATION"

        record.relationship_type = (
            f"{record.source_asset} -> "
            f"{record.target_asset}"
        )

        record.explanation = (
            f"Correlation strength between "
            f"{record.source_asset} and "
            f"{record.target_asset}: "
            f"{record.strength_score}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def strongest_links(
        self,
    ) -> List[CorrelationNetworkRecord]:

        return sorted(
            CORRELATION_NETWORK_DATABASE.values(),
            key=lambda item: item.strength_score,
            reverse=True,
        )


CORRELATION_NETWORK_ENGINE = CorrelationNetworkEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 152
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 153
# ==========================================================

class CausalRelationshipRecord(BaseModel):
    id: str
    cause_factor: str
    effect_factor: str
    relationship_type: str = ""
    impact_strength: float = 0.0
    delay_period_days: int = 0
    confidence_score: float = 0.0
    affected_assets: List[str] = []
    affected_regions: List[str] = []
    explanation: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


CAUSAL_RELATIONSHIP_DATABASE: Dict[
    str,
    CausalRelationshipRecord,
] = {}


class CausalRelationshipEngine:

    def register(
        self,
        record: CausalRelationshipRecord,
    ) -> None:
        CAUSAL_RELATIONSHIP_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CausalRelationshipRecord]:
        return CAUSAL_RELATIONSHIP_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        CAUSAL_RELATIONSHIP_DATABASE.pop(record_id, None)

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.impact_strength = (
            record.confidence_score
            *
            abs(record.impact_strength)
        )

        if record.impact_strength >= 70:
            record.relationship_type = "STRONG"

        elif record.impact_strength >= 40:
            record.relationship_type = "MODERATE"

        else:
            record.relationship_type = "WEAK"

        record.explanation = (
            f"{record.cause_factor} affects "
            f"{record.effect_factor} "
            f"with delay "
            f"{record.delay_period_days} days"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def strongest_relationships(
        self,
    ) -> List[CausalRelationshipRecord]:

        return sorted(
            CAUSAL_RELATIONSHIP_DATABASE.values(),
            key=lambda item: item.impact_strength,
            reverse=True,
        )


CAUSAL_RELATIONSHIP_ENGINE = CausalRelationshipEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 153
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 154
# ==========================================================

class KnowledgeGraphNodeRecord(BaseModel):
    id: str
    node_name: str
    node_type: str = ""
    category: str = ""
    country: str = ""
    importance_score: float = 0.0
    influence_score: float = 0.0
    connection_count: int = 0
    description: str = ""
    metadata: Dict[str, Any] = {}
    created_time: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: DataStatus = DataStatus.WAITING


KNOWLEDGE_GRAPH_NODE_DATABASE: Dict[
    str,
    KnowledgeGraphNodeRecord,
] = {}


class KnowledgeGraphNodeEngine:

    def register(
        self,
        record: KnowledgeGraphNodeRecord,
    ) -> None:
        KNOWLEDGE_GRAPH_NODE_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[KnowledgeGraphNodeRecord]:
        return KNOWLEDGE_GRAPH_NODE_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        KNOWLEDGE_GRAPH_NODE_DATABASE.pop(
            record_id,
            None,
        )

    def update_influence(
        self,
        record_id: str,
        influence_score: float,
        connection_count: int,
        importance_score: float,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.influence_score = influence_score
        record.connection_count = connection_count
        record.importance_score = importance_score
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[KnowledgeGraphNodeRecord]:

        return sorted(
            KNOWLEDGE_GRAPH_NODE_DATABASE.values(),
            key=lambda item: item.influence_score,
            reverse=True,
        )


KNOWLEDGE_GRAPH_NODE_ENGINE = KnowledgeGraphNodeEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 154
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 155
# ==========================================================

class KnowledgeGraphEdgeRecord(BaseModel):
    id: str
    source_node: str
    target_node: str
    relationship_type: str = ""
    relationship_weight: float = 0.0
    influence_direction: str = ""
    confidence_score: float = 0.0
    explanation: str = ""
    created_time: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: DataStatus = DataStatus.WAITING


KNOWLEDGE_GRAPH_EDGE_DATABASE: Dict[
    str,
    KnowledgeGraphEdgeRecord,
] = {}


class KnowledgeGraphEdgeEngine:

    def register(
        self,
        record: KnowledgeGraphEdgeRecord,
    ) -> None:
        KNOWLEDGE_GRAPH_EDGE_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[KnowledgeGraphEdgeRecord]:
        return KNOWLEDGE_GRAPH_EDGE_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        KNOWLEDGE_GRAPH_EDGE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.relationship_weight = (
            record.confidence_score
            *
            abs(record.relationship_weight)
        )

        if record.relationship_weight >= 70:
            record.influence_direction = "STRONG"

        elif record.relationship_weight >= 40:
            record.influence_direction = "MEDIUM"

        else:
            record.influence_direction = "WEAK"

        record.explanation = (
            f"{record.source_node} "
            f"connects to "
            f"{record.target_node} "
            f"through "
            f"{record.relationship_type}"
        )

        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def strongest_connections(
        self,
    ) -> List[KnowledgeGraphEdgeRecord]:

        return sorted(
            KNOWLEDGE_GRAPH_EDGE_DATABASE.values(),
            key=lambda item: item.relationship_weight,
            reverse=True,
        )


KNOWLEDGE_GRAPH_EDGE_ENGINE = KnowledgeGraphEdgeEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 155
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 156
# ==========================================================

class MoneyFlowNodeRecord(BaseModel):
    id: str
    node_name: str
    node_type: str = ""
    country: str = ""
    asset_class: str = ""
    inflow_usd: float = 0.0
    outflow_usd: float = 0.0
    net_flow_usd: float = 0.0
    flow_velocity: float = 0.0
    flow_strength: float = 0.0
    investor_activity_score: float = 0.0
    risk_adjusted_flow_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


MONEY_FLOW_NODE_DATABASE: Dict[
    str,
    MoneyFlowNodeRecord,
] = {}


class MoneyFlowNodeEngine:

    def register(
        self,
        record: MoneyFlowNodeRecord,
    ) -> None:
        MONEY_FLOW_NODE_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[MoneyFlowNodeRecord]:
        return MONEY_FLOW_NODE_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        MONEY_FLOW_NODE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.net_flow_usd = (
            record.inflow_usd
            -
            record.outflow_usd
        )

        record.flow_strength = (
            abs(record.net_flow_usd)
            *
            record.investor_activity_score
        )

        record.risk_adjusted_flow_score = (
            record.flow_strength
            *
            (
                1
                -
                record.flow_velocity
            )
        )

        if record.net_flow_usd > 0:
            record.asset_class = (
                record.asset_class
                +
                "_INFLOW"
            )

        elif record.net_flow_usd < 0:
            record.asset_class = (
                record.asset_class
                +
                "_OUTFLOW"
            )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[MoneyFlowNodeRecord]:

        return sorted(
            MONEY_FLOW_NODE_DATABASE.values(),
            key=lambda item: item.flow_strength,
            reverse=True,
        )


MONEY_FLOW_NODE_ENGINE = MoneyFlowNodeEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 156
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 157
# ==========================================================

class MoneyFlowEdgeRecord(BaseModel):
    id: str
    source_node: str
    target_node: str
    flow_type: str = ""
    amount_usd: float = 0.0
    velocity: float = 0.0
    intensity: float = 0.0
    confidence_score: float = 0.0
    direction: str = ""
    risk_level: float = 0.0
    explanation: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


MONEY_FLOW_EDGE_DATABASE: Dict[
    str,
    MoneyFlowEdgeRecord,
] = {}


class MoneyFlowEdgeEngine:

    def register(
        self,
        record: MoneyFlowEdgeRecord,
    ) -> None:
        MONEY_FLOW_EDGE_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[MoneyFlowEdgeRecord]:
        return MONEY_FLOW_EDGE_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        MONEY_FLOW_EDGE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.intensity = (
            abs(record.amount_usd)
            *
            record.velocity
            *
            record.confidence_score
        )

        if record.amount_usd > 0:
            record.direction = "INFLOW"

        elif record.amount_usd < 0:
            record.direction = "OUTFLOW"

        else:
            record.direction = "STABLE"

        if record.risk_level >= 70:
            risk_state = "HIGH_RISK"

        elif record.risk_level >= 40:
            risk_state = "MEDIUM_RISK"

        else:
            risk_state = "LOW_RISK"

        record.explanation = (
            f"Capital flow {record.direction} "
            f"between {record.source_node} "
            f"and {record.target_node}, "
            f"state: {risk_state}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def strongest_flows(
        self,
    ) -> List[MoneyFlowEdgeRecord]:

        return sorted(
            MONEY_FLOW_EDGE_DATABASE.values(),
            key=lambda item: item.intensity,
            reverse=True,
        )


MONEY_FLOW_EDGE_ENGINE = MoneyFlowEdgeEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 157
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 158
# ==========================================================

class GlobalFlowNetworkRecord(BaseModel):
    id: str
    network_name: str
    total_nodes: int = 0
    total_edges: int = 0
    total_capital_usd: float = 0.0
    active_flows: int = 0
    strongest_region: str = ""
    weakest_region: str = ""
    dominant_asset: str = ""
    average_flow_velocity: float = 0.0
    network_risk_score: float = 0.0
    calculated_time: Optional[datetime] = None
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_FLOW_NETWORK_DATABASE: Dict[
    str,
    GlobalFlowNetworkRecord,
] = {}


class GlobalFlowNetworkEngine:

    def register(
        self,
        record: GlobalFlowNetworkRecord,
    ) -> None:
        GLOBAL_FLOW_NETWORK_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalFlowNetworkRecord]:
        return GLOBAL_FLOW_NETWORK_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        GLOBAL_FLOW_NETWORK_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        if record.total_edges > 0:
            record.average_flow_velocity = (
                record.active_flows
                /
                record.total_edges
            )

        risk_components = [
            record.network_risk_score,
            record.average_flow_velocity * 100,
        ]

        record.network_risk_score = (
            sum(risk_components)
            /
            len(risk_components)
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def summary(
        self,
    ) -> List[GlobalFlowNetworkRecord]:

        return sorted(
            GLOBAL_FLOW_NETWORK_DATABASE.values(),
            key=lambda item: item.total_capital_usd,
            reverse=True,
        )


GLOBAL_FLOW_NETWORK_ENGINE = GlobalFlowNetworkEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 158
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 159
# ==========================================================

class RegionalEconomicFlowRecord(BaseModel):
    id: str
    region_name: str
    country_count: int = 0
    total_gdp_usd: float = 0.0
    capital_inflow_usd: float = 0.0
    capital_outflow_usd: float = 0.0
    net_flow_usd: float = 0.0
    trade_volume_usd: float = 0.0
    investment_volume_usd: float = 0.0
    economic_power_score: float = 0.0
    growth_momentum_score: float = 0.0
    risk_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


REGIONAL_ECONOMIC_FLOW_DATABASE: Dict[
    str,
    RegionalEconomicFlowRecord,
] = {}


class RegionalEconomicFlowEngine:

    def register(
        self,
        record: RegionalEconomicFlowRecord,
    ) -> None:
        REGIONAL_ECONOMIC_FLOW_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[RegionalEconomicFlowRecord]:
        return REGIONAL_ECONOMIC_FLOW_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        REGIONAL_ECONOMIC_FLOW_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.net_flow_usd = (
            record.capital_inflow_usd
            -
            record.capital_outflow_usd
        )

        record.economic_power_score = (
            (
                record.total_gdp_usd
                /
                1000000000000
            )
            +
            (
                record.trade_volume_usd
                /
                1000000000000
            )
        )

        record.growth_momentum_score = (
            record.investment_volume_usd
            /
            1000000000
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[RegionalEconomicFlowRecord]:

        return sorted(
            REGIONAL_ECONOMIC_FLOW_DATABASE.values(),
            key=lambda item: item.economic_power_score,
            reverse=True,
        )


REGIONAL_ECONOMIC_FLOW_ENGINE = RegionalEconomicFlowEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 159
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 160
# ==========================================================

class CountryEconomicProfileRecord(BaseModel):
    id: str
    country: str
    region: str = ""
    population: int = 0
    gdp_usd: float = 0.0
    gdp_per_capita_usd: float = 0.0
    inflation_rate: float = 0.0
    unemployment_rate: float = 0.0
    debt_to_gdp_ratio: float = 0.0
    currency: str = ""
    currency_strength_score: float = 0.0
    economic_power_score: float = 0.0
    stability_score: float = 0.0
    investment_attractiveness_score: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


COUNTRY_PROFILE_DATABASE: Dict[
    str,
    CountryEconomicProfileRecord,
] = {}


class CountryEconomicProfileEngine:

    def register(
        self,
        record: CountryEconomicProfileRecord,
    ) -> None:
        COUNTRY_PROFILE_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CountryEconomicProfileRecord]:
        return COUNTRY_PROFILE_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        COUNTRY_PROFILE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate_score(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        gdp_score = min(
            record.gdp_usd
            /
            1000000000000
            *
            10,
            100,
        )

        inflation_score = max(
            0,
            100 - abs(record.inflation_rate) * 5,
        )

        unemployment_score = max(
            0,
            100 - record.unemployment_rate * 5,
        )

        debt_score = max(
            0,
            100 - record.debt_to_gdp_ratio * 0.5,
        )

        record.economic_power_score = (
            gdp_score * 0.35
            +
            inflation_score * 0.20
            +
            unemployment_score * 0.20
            +
            debt_score * 0.25
        )

        record.investment_attractiveness_score = (
            record.economic_power_score * 0.5
            +
            record.stability_score * 0.5
        )

        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def ranking(
        self,
    ) -> List[CountryEconomicProfileRecord]:

        return sorted(
            COUNTRY_PROFILE_DATABASE.values(),
            key=lambda item: item.economic_power_score,
            reverse=True,
        )


COUNTRY_ECONOMIC_PROFILE_ENGINE = CountryEconomicProfileEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 160
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 161
# ==========================================================

class CountryRiskProfileRecord(BaseModel):
    id: str
    country: str
    political_stability_score: float = 0.0
    economic_stability_score: float = 0.0
    financial_stability_score: float = 0.0
    currency_risk_score: float = 0.0
    debt_risk_score: float = 0.0
    trade_risk_score: float = 0.0
    geopolitical_risk_score: float = 0.0
    total_risk_score: float = 0.0
    risk_category: str = ""
    investment_grade: str = ""
    analysis_text: str = ""
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


COUNTRY_RISK_PROFILE_DATABASE: Dict[
    str,
    CountryRiskProfileRecord,
] = {}


class CountryRiskProfileEngine:

    def register(
        self,
        record: CountryRiskProfileRecord,
    ) -> None:
        COUNTRY_RISK_PROFILE_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CountryRiskProfileRecord]:
        return COUNTRY_RISK_PROFILE_DATABASE.get(record_id)

    def remove(
        self,
        record_id: str,
    ) -> None:
        COUNTRY_RISK_PROFILE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.total_risk_score = (
            record.political_stability_score * 0.15
            +
            record.economic_stability_score * 0.20
            +
            record.financial_stability_score * 0.20
            +
            record.currency_risk_score * 0.10
            +
            record.debt_risk_score * 0.15
            +
            record.trade_risk_score * 0.10
            +
            record.geopolitical_risk_score * 0.10
        )

        if record.total_risk_score >= 75:
            record.risk_category = "HIGH"

        elif record.total_risk_score >= 45:
            record.risk_category = "MEDIUM"

        else:
            record.risk_category = "LOW"

        if record.total_risk_score >= 80:
            record.investment_grade = "AAA"

        elif record.total_risk_score >= 60:
            record.investment_grade = "BBB"

        else:
            record.investment_grade = "SPECULATIVE"

        record.analysis_text = (
            f"{record.country} risk profile: "
            f"{record.risk_category}"
        )

        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def ranking(
        self,
    ) -> List[CountryRiskProfileRecord]:

        return sorted(
            COUNTRY_RISK_PROFILE_DATABASE.values(),
            key=lambda item: item.total_risk_score,
            reverse=True,
        )


COUNTRY_RISK_PROFILE_ENGINE = CountryRiskProfileEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 161
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 162
# ==========================================================

class CountryTradeProfileRecord(BaseModel):
    id: str
    country: str
    total_export_usd: float = 0.0
    total_import_usd: float = 0.0
    trade_balance_usd: float = 0.0
    export_growth_rate: float = 0.0
    import_growth_rate: float = 0.0
    main_export_products: List[str] = []
    main_import_products: List[str] = []
    trade_partner_count: int = 0
    trade_dependency_score: float = 0.0
    global_trade_power_score: float = 0.0
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


COUNTRY_TRADE_PROFILE_DATABASE: Dict[
    str,
    CountryTradeProfileRecord,
] = {}


class CountryTradeProfileEngine:

    def register(
        self,
        record: CountryTradeProfileRecord,
    ) -> None:
        COUNTRY_TRADE_PROFILE_DATABASE[record.id] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CountryTradeProfileRecord]:

        return COUNTRY_TRADE_PROFILE_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        COUNTRY_TRADE_PROFILE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.trade_balance_usd = (
            record.total_export_usd
            -
            record.total_import_usd
        )

        export_score = min(
            (
                record.total_export_usd
                /
                100000000000
            ),
            100,
        )

        partner_score = min(
            record.trade_partner_count
            /
            2,
            100,
        )

        growth_score = (
            record.export_growth_rate
            +
            record.import_growth_rate
        )

        record.global_trade_power_score = (
            export_score * 0.45
            +
            partner_score * 0.30
            +
            growth_score * 0.25
        )

        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def ranking(
        self,
    ) -> List[CountryTradeProfileRecord]:

        return sorted(
            COUNTRY_TRADE_PROFILE_DATABASE.values(),
            key=lambda item:
            item.global_trade_power_score,
            reverse=True,
        )


COUNTRY_TRADE_PROFILE_ENGINE = CountryTradeProfileEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 162
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 163
# ==========================================================

class CountryInvestmentProfileRecord(BaseModel):
    id: str
    country: str
    foreign_direct_investment_usd: float = 0.0
    portfolio_investment_usd: float = 0.0
    infrastructure_investment_usd: float = 0.0
    technology_investment_usd: float = 0.0
    annual_investment_growth: float = 0.0
    investor_confidence_score: float = 0.0
    market_access_score: float = 0.0
    labor_quality_score: float = 0.0
    infrastructure_score: float = 0.0
    investment_attractiveness_score: float = 0.0
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


COUNTRY_INVESTMENT_PROFILE_DATABASE: Dict[
    str,
    CountryInvestmentProfileRecord,
] = {}


class CountryInvestmentProfileEngine:

    def register(
        self,
        record: CountryInvestmentProfileRecord,
    ) -> None:
        COUNTRY_INVESTMENT_PROFILE_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CountryInvestmentProfileRecord]:

        return COUNTRY_INVESTMENT_PROFILE_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        COUNTRY_INVESTMENT_PROFILE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        investment_scale = min(
            record.foreign_direct_investment_usd
            /
            100000000000,
            100,
        )

        capital_growth_score = (
            record.annual_investment_growth
            *
            5
        )

        record.investment_attractiveness_score = (
            investment_scale * 0.30
            +
            record.investor_confidence_score * 0.20
            +
            record.market_access_score * 0.15
            +
            record.labor_quality_score * 0.15
            +
            record.infrastructure_score * 0.10
            +
            capital_growth_score * 0.10
        )

        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def ranking(
        self,
    ) -> List[CountryInvestmentProfileRecord]:

        return sorted(
            COUNTRY_INVESTMENT_PROFILE_DATABASE.values(),
            key=lambda item:
            item.investment_attractiveness_score,
            reverse=True,
        )


COUNTRY_INVESTMENT_PROFILE_ENGINE = (
    CountryInvestmentProfileEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 163
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 164
# ==========================================================

class CountryLaborProfileRecord(BaseModel):
    id: str
    country: str
    labor_force_population: int = 0
    employment_rate: float = 0.0
    unemployment_rate: float = 0.0
    wage_level_usd: float = 0.0
    productivity_score: float = 0.0
    education_score: float = 0.0
    skill_level_score: float = 0.0
    labor_cost_competitiveness: float = 0.0
    automation_level: float = 0.0
    labor_market_score: float = 0.0
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


COUNTRY_LABOR_PROFILE_DATABASE: Dict[
    str,
    CountryLaborProfileRecord,
] = {}


class CountryLaborProfileEngine:

    def register(
        self,
        record: CountryLaborProfileRecord,
    ) -> None:
        COUNTRY_LABOR_PROFILE_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CountryLaborProfileRecord]:

        return COUNTRY_LABOR_PROFILE_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        COUNTRY_LABOR_PROFILE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        employment_score = (
            record.employment_rate
            *
            100
        )

        unemployment_score = max(
            0,
            100 -
            (
                record.unemployment_rate
                *
                5
            ),
        )

        productivity_component = (
            record.productivity_score
            *
            0.30
        )

        education_component = (
            record.education_score
            *
            0.20
        )

        skill_component = (
            record.skill_level_score
            *
            0.20
        )

        automation_component = (
            record.automation_level
            *
            0.10
        )

        record.labor_market_score = (
            employment_score * 0.10
            +
            unemployment_score * 0.10
            +
            productivity_component
            +
            education_component
            +
            skill_component
            +
            record.labor_cost_competitiveness
            * 0.10
            +
            automation_component
        )

        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def ranking(
        self,
    ) -> List[CountryLaborProfileRecord]:

        return sorted(
            COUNTRY_LABOR_PROFILE_DATABASE.values(),
            key=lambda item:
            item.labor_market_score,
            reverse=True,
        )


COUNTRY_LABOR_PROFILE_ENGINE = (
    CountryLaborProfileEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 164
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 165
# ==========================================================

class CountryInnovationProfileRecord(BaseModel):
    id: str
    country: str
    research_spending_usd: float = 0.0
    patent_count: int = 0
    technology_export_usd: float = 0.0
    startup_count: int = 0
    venture_capital_usd: float = 0.0
    ai_development_score: float = 0.0
    digital_infrastructure_score: float = 0.0
    university_quality_score: float = 0.0
    innovation_capacity_score: float = 0.0
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


COUNTRY_INNOVATION_PROFILE_DATABASE: Dict[
    str,
    CountryInnovationProfileRecord,
] = {}


class CountryInnovationProfileEngine:

    def register(
        self,
        record: CountryInnovationProfileRecord,
    ) -> None:
        COUNTRY_INNOVATION_PROFILE_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CountryInnovationProfileRecord]:

        return COUNTRY_INNOVATION_PROFILE_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        COUNTRY_INNOVATION_PROFILE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        research_score = min(
            record.research_spending_usd
            /
            10000000000,
            100,
        )

        patent_score = min(
            record.patent_count
            /
            1000,
            100,
        )

        startup_score = min(
            record.startup_count
            /
            10000,
            100,
        )

        venture_score = min(
            record.venture_capital_usd
            /
            10000000000,
            100,
        )

        technology_score = min(
            record.technology_export_usd
            /
            100000000000,
            100,
        )

        record.innovation_capacity_score = (
            research_score * 0.20
            +
            patent_score * 0.20
            +
            technology_score * 0.15
            +
            startup_score * 0.15
            +
            venture_score * 0.10
            +
            record.ai_development_score * 0.10
            +
            record.digital_infrastructure_score * 0.05
            +
            record.university_quality_score * 0.05
        )

        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def ranking(
        self,
    ) -> List[CountryInnovationProfileRecord]:

        return sorted(
            COUNTRY_INNOVATION_PROFILE_DATABASE.values(),
            key=lambda item:
            item.innovation_capacity_score,
            reverse=True,
        )


COUNTRY_INNOVATION_PROFILE_ENGINE = (
    CountryInnovationProfileEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 165
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 166
# ==========================================================

class CountryEnergyProfileRecord(BaseModel):
    id: str
    country: str
    oil_production_barrel: float = 0.0
    gas_production_m3: float = 0.0
    coal_production_ton: float = 0.0
    renewable_capacity_mw: float = 0.0
    energy_consumption_mwh: float = 0.0
    energy_import_usd: float = 0.0
    energy_export_usd: float = 0.0
    energy_security_score: float = 0.0
    renewable_transition_score: float = 0.0
    energy_dependency_score: float = 0.0
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


COUNTRY_ENERGY_PROFILE_DATABASE: Dict[
    str,
    CountryEnergyProfileRecord,
] = {}


class CountryEnergyProfileEngine:

    def register(
        self,
        record: CountryEnergyProfileRecord,
    ) -> None:
        COUNTRY_ENERGY_PROFILE_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CountryEnergyProfileRecord]:

        return COUNTRY_ENERGY_PROFILE_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        COUNTRY_ENERGY_PROFILE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        production_score = min(
            (
                record.oil_production_barrel
                /
                1000000
            ),
            100,
        )

        gas_score = min(
            (
                record.gas_production_m3
                /
                10000000000
            ),
            100,
        )

        renewable_score = min(
            (
                record.renewable_capacity_mw
                /
                10000
            ),
            100,
        )

        dependency_penalty = min(
            (
                record.energy_import_usd
                /
                100000000000
            ),
            100,
        )

        record.energy_security_score = (
            production_score * 0.35
            +
            gas_score * 0.20
            +
            renewable_score * 0.25
            +
            (
                100
                -
                dependency_penalty
            )
            * 0.20
        )

        record.energy_dependency_score = (
            dependency_penalty
        )

        record.renewable_transition_score = (
            renewable_score
        )

        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def ranking(
        self,
    ) -> List[CountryEnergyProfileRecord]:

        return sorted(
            COUNTRY_ENERGY_PROFILE_DATABASE.values(),
            key=lambda item:
            item.energy_security_score,
            reverse=True,
        )


COUNTRY_ENERGY_PROFILE_ENGINE = (
    CountryEnergyProfileEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 166
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 167
# ==========================================================

class CountryTechnologyProfileRecord(BaseModel):
    id: str
    country: str
    internet_penetration_rate: float = 0.0
    smartphone_usage_rate: float = 0.0
    cloud_adoption_score: float = 0.0
    ai_readiness_score: float = 0.0
    cybersecurity_score: float = 0.0
    digital_payment_score: float = 0.0
    technology_export_usd: float = 0.0
    technology_import_usd: float = 0.0
    digital_economy_score: float = 0.0
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


COUNTRY_TECHNOLOGY_PROFILE_DATABASE: Dict[
    str,
    CountryTechnologyProfileRecord,
] = {}


class CountryTechnologyProfileEngine:

    def register(
        self,
        record: CountryTechnologyProfileRecord,
    ) -> None:
        COUNTRY_TECHNOLOGY_PROFILE_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CountryTechnologyProfileRecord]:

        return COUNTRY_TECHNOLOGY_PROFILE_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        COUNTRY_TECHNOLOGY_PROFILE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        export_score = min(
            record.technology_export_usd
            /
            100000000000,
            100,
        )

        import_score = min(
            record.technology_import_usd
            /
            100000000000,
            100,
        )

        record.digital_economy_score = (
            record.internet_penetration_rate
            * 0.15
            +
            record.smartphone_usage_rate
            * 0.10
            +
            record.cloud_adoption_score
            * 0.15
            +
            record.ai_readiness_score
            * 0.20
            +
            record.cybersecurity_score
            * 0.15
            +
            record.digital_payment_score
            * 0.10
            +
            export_score
            * 0.10
            +
            import_score
            * 0.05
        )

        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def ranking(
        self,
    ) -> List[CountryTechnologyProfileRecord]:

        return sorted(
            COUNTRY_TECHNOLOGY_PROFILE_DATABASE.values(),
            key=lambda item:
            item.digital_economy_score,
            reverse=True,
        )


COUNTRY_TECHNOLOGY_PROFILE_ENGINE = (
    CountryTechnologyProfileEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 167
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 168
# ==========================================================

class CountryFinancialProfileRecord(BaseModel):
    id: str
    country: str
    banking_asset_usd: float = 0.0
    stock_market_cap_usd: float = 0.0
    bond_market_size_usd: float = 0.0
    foreign_reserve_usd: float = 0.0
    financial_depth_score: float = 0.0
    banking_stability_score: float = 0.0
    capital_market_score: float = 0.0
    liquidity_score: float = 0.0
    foreign_investor_access_score: float = 0.0
    financial_power_score: float = 0.0
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


COUNTRY_FINANCIAL_PROFILE_DATABASE: Dict[
    str,
    CountryFinancialProfileRecord,
] = {}


class CountryFinancialProfileEngine:

    def register(
        self,
        record: CountryFinancialProfileRecord,
    ) -> None:
        COUNTRY_FINANCIAL_PROFILE_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CountryFinancialProfileRecord]:

        return COUNTRY_FINANCIAL_PROFILE_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        COUNTRY_FINANCIAL_PROFILE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        banking_score = min(
            record.banking_asset_usd
            /
            100000000000,
            100,
        )

        market_score = min(
            (
                record.stock_market_cap_usd
                +
                record.bond_market_size_usd
            )
            /
            200000000000,
            100,
        )

        reserve_score = min(
            record.foreign_reserve_usd
            /
            100000000000,
            100,
        )

        record.financial_power_score = (
            banking_score * 0.25
            +
            market_score * 0.30
            +
            reserve_score * 0.15
            +
            record.financial_depth_score * 0.10
            +
            record.banking_stability_score * 0.10
            +
            record.liquidity_score * 0.05
            +
            record.foreign_investor_access_score * 0.05
        )

        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def ranking(
        self,
    ) -> List[CountryFinancialProfileRecord]:

        return sorted(
            COUNTRY_FINANCIAL_PROFILE_DATABASE.values(),
            key=lambda item:
            item.financial_power_score,
            reverse=True,
        )


COUNTRY_FINANCIAL_PROFILE_ENGINE = (
    CountryFinancialProfileEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 168
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 169
# ==========================================================

class CountryMilitaryProfileRecord(BaseModel):
    id: str
    country: str
    defense_budget_usd: float = 0.0
    active_personnel: int = 0
    military_technology_score: float = 0.0
    strategic_position_score: float = 0.0
    defense_industry_score: float = 0.0
    alliance_strength_score: float = 0.0
    cybersecurity_military_score: float = 0.0
    military_power_score: float = 0.0
    geopolitical_influence_score: float = 0.0
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


COUNTRY_MILITARY_PROFILE_DATABASE: Dict[
    str,
    CountryMilitaryProfileRecord,
] = {}


class CountryMilitaryProfileEngine:

    def register(
        self,
        record: CountryMilitaryProfileRecord,
    ) -> None:

        COUNTRY_MILITARY_PROFILE_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CountryMilitaryProfileRecord]:

        return COUNTRY_MILITARY_PROFILE_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        COUNTRY_MILITARY_PROFILE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        budget_score = min(
            record.defense_budget_usd
            /
            100000000000,
            100,
        )

        personnel_score = min(
            record.active_personnel
            /
            1000000
            *
            100,
            100,
        )

        record.military_power_score = (
            budget_score * 0.25
            +
            personnel_score * 0.10
            +
            record.military_technology_score * 0.25
            +
            record.defense_industry_score * 0.15
            +
            record.strategic_position_score * 0.10
            +
            record.alliance_strength_score * 0.10
            +
            record.cybersecurity_military_score * 0.05
        )

        record.geopolitical_influence_score = (
            record.military_power_score * 0.60
            +
            record.strategic_position_score * 0.40
        )

        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def ranking(
        self,
    ) -> List[CountryMilitaryProfileRecord]:

        return sorted(
            COUNTRY_MILITARY_PROFILE_DATABASE.values(),
            key=lambda item:
            item.military_power_score,
            reverse=True,
        )


COUNTRY_MILITARY_PROFILE_ENGINE = (
    CountryMilitaryProfileEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 169
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 170
# ==========================================================

class CountryGeopoliticalProfileRecord(BaseModel):
    id: str
    country: str
    diplomatic_influence_score: float = 0.0
    alliance_network_score: float = 0.0
    trade_influence_score: float = 0.0
    economic_influence_score: float = 0.0
    military_influence_score: float = 0.0
    technology_influence_score: float = 0.0
    cultural_influence_score: float = 0.0
    geopolitical_power_score: float = 0.0
    influence_category: str = ""
    analysis_text: str = ""
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


COUNTRY_GEOPOLITICAL_PROFILE_DATABASE: Dict[
    str,
    CountryGeopoliticalProfileRecord,
] = {}


class CountryGeopoliticalProfileEngine:

    def register(
        self,
        record: CountryGeopoliticalProfileRecord,
    ) -> None:

        COUNTRY_GEOPOLITICAL_PROFILE_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CountryGeopoliticalProfileRecord]:

        return COUNTRY_GEOPOLITICAL_PROFILE_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        COUNTRY_GEOPOLITICAL_PROFILE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.geopolitical_power_score = (
            record.diplomatic_influence_score * 0.20
            +
            record.alliance_network_score * 0.15
            +
            record.trade_influence_score * 0.15
            +
            record.economic_influence_score * 0.20
            +
            record.military_influence_score * 0.15
            +
            record.technology_influence_score * 0.10
            +
            record.cultural_influence_score * 0.05
        )

        if record.geopolitical_power_score >= 80:
            record.influence_category = "GLOBAL_POWER"

        elif record.geopolitical_power_score >= 50:
            record.influence_category = "REGIONAL_POWER"

        else:
            record.influence_category = "LIMITED_INFLUENCE"

        record.analysis_text = (
            f"{record.country} geopolitical "
            f"influence level: "
            f"{record.influence_category}"
        )

        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def ranking(
        self,
    ) -> List[CountryGeopoliticalProfileRecord]:

        return sorted(
            COUNTRY_GEOPOLITICAL_PROFILE_DATABASE.values(),
            key=lambda item:
            item.geopolitical_power_score,
            reverse=True,
        )


COUNTRY_GEOPOLITICAL_PROFILE_ENGINE = (
    CountryGeopoliticalProfileEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 170
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 171
# ==========================================================

class GlobalPowerIndexRecord(BaseModel):
    id: str
    country: str
    economic_power: float = 0.0
    military_power: float = 0.0
    technology_power: float = 0.0
    financial_power: float = 0.0
    diplomatic_power: float = 0.0
    energy_power: float = 0.0
    innovation_power: float = 0.0
    total_power_score: float = 0.0
    global_rank: int = 0
    power_category: str = ""
    report_date: str = ""
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_POWER_INDEX_DATABASE: Dict[
    str,
    GlobalPowerIndexRecord,
] = {}


class GlobalPowerIndexEngine:

    def register(
        self,
        record: GlobalPowerIndexRecord,
    ) -> None:

        GLOBAL_POWER_INDEX_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalPowerIndexRecord]:

        return GLOBAL_POWER_INDEX_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_POWER_INDEX_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.total_power_score = (
            record.economic_power * 0.25
            +
            record.military_power * 0.15
            +
            record.technology_power * 0.15
            +
            record.financial_power * 0.15
            +
            record.diplomatic_power * 0.10
            +
            record.energy_power * 0.10
            +
            record.innovation_power * 0.10
        )

        if record.total_power_score >= 85:
            record.power_category = "SUPER_POWER"

        elif record.total_power_score >= 65:
            record.power_category = "MAJOR_POWER"

        elif record.total_power_score >= 40:
            record.power_category = "REGIONAL_POWER"

        else:
            record.power_category = "EMERGING"

        record.status = DataStatus.REALTIME
        record.updated_at = utc_now()

    def ranking(
        self,
    ) -> List[GlobalPowerIndexRecord]:

        return sorted(
            GLOBAL_POWER_INDEX_DATABASE.values(),
            key=lambda item:
            item.total_power_score,
            reverse=True,
        )


GLOBAL_POWER_INDEX_ENGINE = GlobalPowerIndexEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 171
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 172
# ==========================================================

class GlobalInfluenceNetworkRecord(BaseModel):
    id: str
    country: str
    economic_links: int = 0
    diplomatic_links: int = 0
    trade_links: int = 0
    technology_links: int = 0
    financial_links: int = 0
    energy_links: int = 0
    total_connections: int = 0
    influence_score: float = 0.0
    network_centrality_score: float = 0.0
    influence_rank: int = 0
    influence_category: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_INFLUENCE_NETWORK_DATABASE: Dict[
    str,
    GlobalInfluenceNetworkRecord,
] = {}


class GlobalInfluenceNetworkEngine:

    def register(
        self,
        record: GlobalInfluenceNetworkRecord,
    ) -> None:

        GLOBAL_INFLUENCE_NETWORK_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalInfluenceNetworkRecord]:

        return GLOBAL_INFLUENCE_NETWORK_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_INFLUENCE_NETWORK_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.total_connections = (
            record.economic_links
            +
            record.diplomatic_links
            +
            record.trade_links
            +
            record.technology_links
            +
            record.financial_links
            +
            record.energy_links
        )

        record.network_centrality_score = (
            record.total_connections
            /
            100
        )

        record.influence_score = (
            record.economic_links * 0.25
            +
            record.financial_links * 0.20
            +
            record.trade_links * 0.20
            +
            record.technology_links * 0.15
            +
            record.diplomatic_links * 0.10
            +
            record.energy_links * 0.10
        )

        if record.influence_score >= 80:
            record.influence_category = (
                "GLOBAL_HUB"
            )

        elif record.influence_score >= 50:
            record.influence_category = (
                "REGIONAL_HUB"
            )

        else:
            record.influence_category = (
                "LOCAL_NODE"
            )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalInfluenceNetworkRecord]:

        return sorted(
            GLOBAL_INFLUENCE_NETWORK_DATABASE.values(),
            key=lambda item:
            item.influence_score,
            reverse=True,
        )


GLOBAL_INFLUENCE_NETWORK_ENGINE = (
    GlobalInfluenceNetworkEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 172
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 173
# ==========================================================

class GlobalSupplyChainNodeRecord(BaseModel):
    id: str
    company_or_country: str
    node_type: str = ""
    industry: str = ""
    country: str = ""
    production_capacity: float = 0.0
    export_capacity_usd: float = 0.0
    import_dependency_usd: float = 0.0
    supply_chain_importance: float = 0.0
    disruption_risk_score: float = 0.0
    alternative_source_count: int = 0
    strategic_importance_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_SUPPLY_CHAIN_NODE_DATABASE: Dict[
    str,
    GlobalSupplyChainNodeRecord,
] = {}


class GlobalSupplyChainNodeEngine:

    def register(
        self,
        record: GlobalSupplyChainNodeRecord,
    ) -> None:

        GLOBAL_SUPPLY_CHAIN_NODE_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalSupplyChainNodeRecord]:

        return GLOBAL_SUPPLY_CHAIN_NODE_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_SUPPLY_CHAIN_NODE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        production_score = min(
            record.production_capacity
            /
            1000000,
            100,
        )

        export_score = min(
            record.export_capacity_usd
            /
            100000000000,
            100,
        )

        dependency_penalty = min(
            record.import_dependency_usd
            /
            100000000000,
            100,
        )

        alternative_score = min(
            record.alternative_source_count
            *
            10,
            100,
        )

        record.strategic_importance_score = (
            production_score * 0.25
            +
            export_score * 0.25
            +
            record.supply_chain_importance * 0.25
            +
            alternative_score * 0.10
            -
            dependency_penalty * 0.15
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalSupplyChainNodeRecord]:

        return sorted(
            GLOBAL_SUPPLY_CHAIN_NODE_DATABASE.values(),
            key=lambda item:
            item.strategic_importance_score,
            reverse=True,
        )


GLOBAL_SUPPLY_CHAIN_NODE_ENGINE = (
    GlobalSupplyChainNodeEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 173
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 174
# ==========================================================

class SupplyChainEdgeRecord(BaseModel):
    id: str
    source_node: str
    target_node: str
    product_category: str = ""
    trade_value_usd: float = 0.0
    dependency_level: float = 0.0
    transport_distance_km: float = 0.0
    shipping_time_days: float = 0.0
    disruption_probability: float = 0.0
    flow_strength: float = 0.0
    risk_adjusted_flow_score: float = 0.0
    relationship_status: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


SUPPLY_CHAIN_EDGE_DATABASE: Dict[
    str,
    SupplyChainEdgeRecord,
] = {}


class SupplyChainEdgeEngine:

    def register(
        self,
        record: SupplyChainEdgeRecord,
    ) -> None:

        SUPPLY_CHAIN_EDGE_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[SupplyChainEdgeRecord]:

        return SUPPLY_CHAIN_EDGE_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        SUPPLY_CHAIN_EDGE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.flow_strength = (
            record.trade_value_usd
            /
            1000000000
        )

        record.risk_adjusted_flow_score = (
            record.flow_strength
            *
            (
                1
                -
                record.disruption_probability
            )
            *
            record.dependency_level
        )

        if record.disruption_probability >= 0.7:
            record.relationship_status = (
                "HIGH_RISK"
            )

        elif record.disruption_probability >= 0.3:
            record.relationship_status = (
                "MEDIUM_RISK"
            )

        else:
            record.relationship_status = (
                "STABLE"
            )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[SupplyChainEdgeRecord]:

        return sorted(
            SUPPLY_CHAIN_EDGE_DATABASE.values(),
            key=lambda item:
            item.risk_adjusted_flow_score,
            reverse=True,
        )


SUPPLY_CHAIN_EDGE_ENGINE = (
    SupplyChainEdgeEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 174
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 175
# ==========================================================

class GlobalCommodityFlowRecord(BaseModel):
    id: str
    commodity: str
    source_country: str = ""
    destination_country: str = ""
    export_volume: float = 0.0
    import_volume: float = 0.0
    trade_value_usd: float = 0.0
    supply_share_percent: float = 0.0
    demand_share_percent: float = 0.0
    price_impact_score: float = 0.0
    disruption_risk_score: float = 0.0
    flow_strength: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_COMMODITY_FLOW_DATABASE: Dict[
    str,
    GlobalCommodityFlowRecord,
] = {}


class GlobalCommodityFlowEngine:

    def register(
        self,
        record: GlobalCommodityFlowRecord,
    ) -> None:

        GLOBAL_COMMODITY_FLOW_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalCommodityFlowRecord]:

        return GLOBAL_COMMODITY_FLOW_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_COMMODITY_FLOW_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        volume_score = (
            record.export_volume
            +
            record.import_volume
        )

        trade_score = (
            record.trade_value_usd
            /
            1000000000
        )

        record.flow_strength = (
            volume_score * 0.40
            +
            trade_score * 0.30
            +
            record.supply_share_percent * 0.15
            +
            record.demand_share_percent * 0.15
        )

        record.price_impact_score = (
            record.flow_strength
            *
            (
                1
                +
                record.disruption_risk_score
            )
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalCommodityFlowRecord]:

        return sorted(
            GLOBAL_COMMODITY_FLOW_DATABASE.values(),
            key=lambda item:
            item.flow_strength,
            reverse=True,
        )


GLOBAL_COMMODITY_FLOW_ENGINE = (
    GlobalCommodityFlowEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 175
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 176
# ==========================================================

class GlobalEnergyFlowRecord(BaseModel):
    id: str
    energy_type: str
    source_country: str = ""
    destination_country: str = ""
    production_volume: float = 0.0
    consumption_volume: float = 0.0
    trade_value_usd: float = 0.0
    strategic_importance: float = 0.0
    supply_risk_score: float = 0.0
    demand_growth_score: float = 0.0
    energy_flow_strength: float = 0.0
    price_impact_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_ENERGY_FLOW_DATABASE: Dict[
    str,
    GlobalEnergyFlowRecord,
] = {}


class GlobalEnergyFlowEngine:

    def register(
        self,
        record: GlobalEnergyFlowRecord,
    ) -> None:

        GLOBAL_ENERGY_FLOW_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalEnergyFlowRecord]:

        return GLOBAL_ENERGY_FLOW_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_ENERGY_FLOW_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        production_score = (
            record.production_volume
            /
            1000000
        )

        consumption_score = (
            record.consumption_volume
            /
            1000000
        )

        trade_score = (
            record.trade_value_usd
            /
            1000000000
        )

        record.energy_flow_strength = (
            production_score * 0.30
            +
            consumption_score * 0.20
            +
            trade_score * 0.25
            +
            record.strategic_importance * 0.25
        )

        record.price_impact_score = (
            record.energy_flow_strength
            *
            (
                1
                +
                record.supply_risk_score
                +
                record.demand_growth_score
            )
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalEnergyFlowRecord]:

        return sorted(
            GLOBAL_ENERGY_FLOW_DATABASE.values(),
            key=lambda item:
            item.energy_flow_strength,
            reverse=True,
        )


GLOBAL_ENERGY_FLOW_ENGINE = (
    GlobalEnergyFlowEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 176
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 177
# ==========================================================

class GlobalCurrencyFlowRecord(BaseModel):
    id: str
    currency: str
    source_country: str = ""
    destination_country: str = ""
    transaction_volume_usd: float = 0.0
    reserve_usage_usd: float = 0.0
    forex_demand_score: float = 0.0
    exchange_rate_pressure: float = 0.0
    liquidity_flow_score: float = 0.0
    currency_influence_score: float = 0.0
    flow_direction: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_CURRENCY_FLOW_DATABASE: Dict[
    str,
    GlobalCurrencyFlowRecord,
] = {}


class GlobalCurrencyFlowEngine:

    def register(
        self,
        record: GlobalCurrencyFlowRecord,
    ) -> None:

        GLOBAL_CURRENCY_FLOW_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalCurrencyFlowRecord]:

        return GLOBAL_CURRENCY_FLOW_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_CURRENCY_FLOW_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        transaction_score = (
            record.transaction_volume_usd
            /
            100000000000
        )

        reserve_score = (
            record.reserve_usage_usd
            /
            100000000000
        )

        record.liquidity_flow_score = (
            transaction_score * 0.40
            +
            reserve_score * 0.20
            +
            record.forex_demand_score * 0.20
            +
            record.exchange_rate_pressure * 0.20
        )

        record.currency_influence_score = (
            record.liquidity_flow_score
            *
            100
        )

        if record.transaction_volume_usd > 0:
            record.flow_direction = "INFLOW"

        elif record.transaction_volume_usd < 0:
            record.flow_direction = "OUTFLOW"

        else:
            record.flow_direction = "STABLE"

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalCurrencyFlowRecord]:

        return sorted(
            GLOBAL_CURRENCY_FLOW_DATABASE.values(),
            key=lambda item:
            item.currency_influence_score,
            reverse=True,
        )


GLOBAL_CURRENCY_FLOW_ENGINE = (
    GlobalCurrencyFlowEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 177
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 178
# ==========================================================

class GlobalCapitalMarketRecord(BaseModel):
    id: str
    market_name: str
    country: str = ""
    market_type: str = ""
    total_market_size_usd: float = 0.0
    daily_trading_volume_usd: float = 0.0
    foreign_capital_inflow_usd: float = 0.0
    foreign_capital_outflow_usd: float = 0.0
    liquidity_score: float = 0.0
    volatility_score: float = 0.0
    investor_confidence_score: float = 0.0
    market_strength_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_CAPITAL_MARKET_DATABASE: Dict[
    str,
    GlobalCapitalMarketRecord,
] = {}


class GlobalCapitalMarketEngine:

    def register(
        self,
        record: GlobalCapitalMarketRecord,
    ) -> None:

        GLOBAL_CAPITAL_MARKET_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalCapitalMarketRecord]:

        return GLOBAL_CAPITAL_MARKET_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_CAPITAL_MARKET_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        market_size_score = min(
            record.total_market_size_usd
            /
            1000000000000,
            100,
        )

        volume_score = min(
            record.daily_trading_volume_usd
            /
            10000000000,
            100,
        )

        flow_balance = (
            record.foreign_capital_inflow_usd
            -
            record.foreign_capital_outflow_usd
        )

        flow_score = min(
            max(
                flow_balance
                /
                10000000000,
                0,
            ),
            100,
        )

        record.market_strength_score = (
            market_size_score * 0.30
            +
            volume_score * 0.20
            +
            flow_score * 0.20
            +
            record.liquidity_score * 0.15
            +
            record.investor_confidence_score * 0.15
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalCapitalMarketRecord]:

        return sorted(
            GLOBAL_CAPITAL_MARKET_DATABASE.values(),
            key=lambda item:
            item.market_strength_score,
            reverse=True,
        )


GLOBAL_CAPITAL_MARKET_ENGINE = (
    GlobalCapitalMarketEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 178
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 179
# ==========================================================

class GlobalBondMarketRecord(BaseModel):
    id: str
    bond_market_name: str
    country: str = ""
    bond_type: str = ""
    total_debt_value_usd: float = 0.0
    government_bond_value_usd: float = 0.0
    corporate_bond_value_usd: float = 0.0
    foreign_holder_value_usd: float = 0.0
    yield_level: float = 0.0
    yield_change: float = 0.0
    credit_quality_score: float = 0.0
    liquidity_score: float = 0.0
    risk_score: float = 0.0
    bond_market_strength_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_BOND_MARKET_DATABASE: Dict[
    str,
    GlobalBondMarketRecord,
] = {}


class GlobalBondMarketEngine:

    def register(
        self,
        record: GlobalBondMarketRecord,
    ) -> None:

        GLOBAL_BOND_MARKET_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalBondMarketRecord]:

        return GLOBAL_BOND_MARKET_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_BOND_MARKET_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        size_score = min(
            record.total_debt_value_usd
            /
            1000000000000,
            100,
        )

        foreign_score = min(
            record.foreign_holder_value_usd
            /
            100000000000,
            100,
        )

        yield_stability_score = max(
            0,
            100 -
            abs(record.yield_change) * 10,
        )

        record.bond_market_strength_score = (
            size_score * 0.30
            +
            foreign_score * 0.15
            +
            record.credit_quality_score * 0.25
            +
            record.liquidity_score * 0.15
            +
            yield_stability_score * 0.15
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalBondMarketRecord]:

        return sorted(
            GLOBAL_BOND_MARKET_DATABASE.values(),
            key=lambda item:
            item.bond_market_strength_score,
            reverse=True,
        )


GLOBAL_BOND_MARKET_ENGINE = (
    GlobalBondMarketEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 179
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 180
# ==========================================================

class GlobalEquityMarketRecord(BaseModel):
    id: str
    market_name: str
    country: str = ""
    index_symbol: str = ""
    market_cap_usd: float = 0.0
    daily_volume_usd: float = 0.0
    foreign_investment_usd: float = 0.0
    earnings_growth_rate: float = 0.0
    valuation_score: float = 0.0
    liquidity_score: float = 0.0
    investor_sentiment_score: float = 0.0
    volatility_score: float = 0.0
    equity_strength_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_EQUITY_MARKET_DATABASE: Dict[
    str,
    GlobalEquityMarketRecord,
] = {}


class GlobalEquityMarketEngine:

    def register(
        self,
        record: GlobalEquityMarketRecord,
    ) -> None:

        GLOBAL_EQUITY_MARKET_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalEquityMarketRecord]:

        return GLOBAL_EQUITY_MARKET_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_EQUITY_MARKET_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        market_size_score = min(
            record.market_cap_usd
            /
            1000000000000,
            100,
        )

        volume_score = min(
            record.daily_volume_usd
            /
            10000000000,
            100,
        )

        foreign_flow_score = min(
            record.foreign_investment_usd
            /
            100000000000,
            100,
        )

        growth_score = min(
            record.earnings_growth_rate
            *
            5,
            100,
        )

        record.equity_strength_score = (
            market_size_score * 0.25
            +
            volume_score * 0.15
            +
            foreign_flow_score * 0.15
            +
            growth_score * 0.20
            +
            record.valuation_score * 0.10
            +
            record.liquidity_score * 0.10
            +
            record.investor_sentiment_score * 0.05
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalEquityMarketRecord]:

        return sorted(
            GLOBAL_EQUITY_MARKET_DATABASE.values(),
            key=lambda item:
            item.equity_strength_score,
            reverse=True,
        )


GLOBAL_EQUITY_MARKET_ENGINE = (
    GlobalEquityMarketEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 180
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 181
# ==========================================================

class GlobalCryptoMarketRecord(BaseModel):
    id: str
    asset_name: str
    symbol: str = ""
    market_cap_usd: float = 0.0
    daily_volume_usd: float = 0.0
    circulating_supply: float = 0.0
    total_supply: float = 0.0
    whale_activity_score: float = 0.0
    institutional_flow_usd: float = 0.0
    retail_activity_score: float = 0.0
    volatility_score: float = 0.0
    adoption_score: float = 0.0
    crypto_strength_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_CRYPTO_MARKET_DATABASE: Dict[
    str,
    GlobalCryptoMarketRecord,
] = {}


class GlobalCryptoMarketEngine:

    def register(
        self,
        record: GlobalCryptoMarketRecord,
    ) -> None:

        GLOBAL_CRYPTO_MARKET_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalCryptoMarketRecord]:

        return GLOBAL_CRYPTO_MARKET_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_CRYPTO_MARKET_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        market_size_score = min(
            record.market_cap_usd
            /
            1000000000000,
            100,
        )

        volume_score = min(
            record.daily_volume_usd
            /
            50000000000,
            100,
        )

        institutional_score = min(
            record.institutional_flow_usd
            /
            10000000000,
            100,
        )

        supply_score = 0

        if record.total_supply > 0:
            supply_score = (
                record.circulating_supply
                /
                record.total_supply
            ) * 100

        record.crypto_strength_score = (
            market_size_score * 0.20
            +
            volume_score * 0.15
            +
            institutional_score * 0.20
            +
            record.whale_activity_score * 0.15
            +
            record.retail_activity_score * 0.10
            +
            record.adoption_score * 0.15
            +
            supply_score * 0.05
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalCryptoMarketRecord]:

        return sorted(
            GLOBAL_CRYPTO_MARKET_DATABASE.values(),
            key=lambda item:
            item.crypto_strength_score,
            reverse=True,
        )


GLOBAL_CRYPTO_MARKET_ENGINE = (
    GlobalCryptoMarketEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 181
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 182
# ==========================================================

class GlobalAlternativeAssetRecord(BaseModel):
    id: str
    asset_name: str
    asset_type: str = ""
    region: str = ""
    total_value_usd: float = 0.0
    transaction_volume_usd: float = 0.0
    investor_demand_score: float = 0.0
    liquidity_score: float = 0.0
    risk_score: float = 0.0
    growth_score: float = 0.0
    institutional_interest_score: float = 0.0
    alternative_asset_strength_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_ALTERNATIVE_ASSET_DATABASE: Dict[
    str,
    GlobalAlternativeAssetRecord,
] = {}


class GlobalAlternativeAssetEngine:

    def register(
        self,
        record: GlobalAlternativeAssetRecord,
    ) -> None:

        GLOBAL_ALTERNATIVE_ASSET_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalAlternativeAssetRecord]:

        return GLOBAL_ALTERNATIVE_ASSET_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_ALTERNATIVE_ASSET_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        value_score = min(
            record.total_value_usd
            /
            100000000000,
            100,
        )

        volume_score = min(
            record.transaction_volume_usd
            /
            10000000000,
            100,
        )

        record.alternative_asset_strength_score = (
            value_score * 0.20
            +
            volume_score * 0.15
            +
            record.investor_demand_score * 0.20
            +
            record.liquidity_score * 0.10
            +
            record.growth_score * 0.15
            +
            record.institutional_interest_score * 0.20
            -
            record.risk_score * 0.10
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalAlternativeAssetRecord]:

        return sorted(
            GLOBAL_ALTERNATIVE_ASSET_DATABASE.values(),
            key=lambda item:
            item.alternative_asset_strength_score,
            reverse=True,
        )


GLOBAL_ALTERNATIVE_ASSET_ENGINE = (
    GlobalAlternativeAssetEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 182
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 183
# ==========================================================

class GlobalRealEstateMarketRecord(BaseModel):
    id: str
    market_name: str
    country: str = ""
    city: str = ""
    property_type: str = ""
    total_market_value_usd: float = 0.0
    transaction_volume_usd: float = 0.0
    rental_yield_percent: float = 0.0
    price_growth_rate: float = 0.0
    foreign_buyer_activity_score: float = 0.0
    construction_activity_score: float = 0.0
    vacancy_rate: float = 0.0
    real_estate_strength_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_REAL_ESTATE_DATABASE: Dict[
    str,
    GlobalRealEstateMarketRecord,
] = {}


class GlobalRealEstateMarketEngine:

    def register(
        self,
        record: GlobalRealEstateMarketRecord,
    ) -> None:

        GLOBAL_REAL_ESTATE_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalRealEstateMarketRecord]:

        return GLOBAL_REAL_ESTATE_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_REAL_ESTATE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        market_size_score = min(
            record.total_market_value_usd
            /
            1000000000000,
            100,
        )

        transaction_score = min(
            record.transaction_volume_usd
            /
            100000000000,
            100,
        )

        growth_score = min(
            record.price_growth_rate
            *
            5,
            100,
        )

        vacancy_score = max(
            0,
            100 -
            (
                record.vacancy_rate
                *
                5
            ),
        )

        record.real_estate_strength_score = (
            market_size_score * 0.25
            +
            transaction_score * 0.20
            +
            record.rental_yield_percent * 0.10
            +
            growth_score * 0.15
            +
            record.foreign_buyer_activity_score * 0.10
            +
            record.construction_activity_score * 0.10
            +
            vacancy_score * 0.10
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalRealEstateMarketRecord]:

        return sorted(
            GLOBAL_REAL_ESTATE_DATABASE.values(),
            key=lambda item:
            item.real_estate_strength_score,
            reverse=True,
        )


GLOBAL_REAL_ESTATE_MARKET_ENGINE = (
    GlobalRealEstateMarketEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 183
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 184
# ==========================================================

class GlobalHousingMarketRecord(BaseModel):
    id: str
    country: str
    city: str = ""
    average_home_price_usd: float = 0.0
    mortgage_rate: float = 0.0
    housing_supply_index: float = 0.0
    housing_demand_index: float = 0.0
    affordability_score: float = 0.0
    household_debt_ratio: float = 0.0
    construction_growth_rate: float = 0.0
    foreign_property_demand_score: float = 0.0
    housing_market_strength_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_HOUSING_MARKET_DATABASE: Dict[
    str,
    GlobalHousingMarketRecord,
] = {}


class GlobalHousingMarketEngine:

    def register(
        self,
        record: GlobalHousingMarketRecord,
    ) -> None:

        GLOBAL_HOUSING_MARKET_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalHousingMarketRecord]:

        return GLOBAL_HOUSING_MARKET_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_HOUSING_MARKET_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        demand_supply_score = (
            record.housing_demand_index
            -
            record.housing_supply_index
            +
            50
        )

        debt_penalty = max(
            0,
            100 -
            (
                record.household_debt_ratio
                *
                0.5
            ),
        )

        mortgage_score = max(
            0,
            100 -
            (
                record.mortgage_rate
                *
                5
            ),
        )

        record.housing_market_strength_score = (
            demand_supply_score * 0.25
            +
            record.affordability_score * 0.20
            +
            debt_penalty * 0.20
            +
            mortgage_score * 0.15
            +
            record.construction_growth_rate * 0.10
            +
            record.foreign_property_demand_score * 0.10
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalHousingMarketRecord]:

        return sorted(
            GLOBAL_HOUSING_MARKET_DATABASE.values(),
            key=lambda item:
            item.housing_market_strength_score,
            reverse=True,
        )


GLOBAL_HOUSING_MARKET_ENGINE = (
    GlobalHousingMarketEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 184
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 185
# ==========================================================

class GlobalConsumerMarketRecord(BaseModel):
    id: str
    country: str
    consumer_spending_usd: float = 0.0
    retail_sales_growth_rate: float = 0.0
    household_income_growth_rate: float = 0.0
    consumer_confidence_score: float = 0.0
    savings_rate: float = 0.0
    household_debt_ratio: float = 0.0
    e_commerce_growth_score: float = 0.0
    consumption_power_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_CONSUMER_MARKET_DATABASE: Dict[
    str,
    GlobalConsumerMarketRecord,
] = {}


class GlobalConsumerMarketEngine:

    def register(
        self,
        record: GlobalConsumerMarketRecord,
    ) -> None:

        GLOBAL_CONSUMER_MARKET_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalConsumerMarketRecord]:

        return GLOBAL_CONSUMER_MARKET_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_CONSUMER_MARKET_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        spending_score = min(
            record.consumer_spending_usd
            /
            100000000000,
            100,
        )

        income_score = min(
            record.household_income_growth_rate
            *
            5,
            100,
        )

        debt_penalty = max(
            0,
            100 -
            (
                record.household_debt_ratio
                *
                0.5
            ),
        )

        record.consumption_power_score = (
            spending_score * 0.30
            +
            record.retail_sales_growth_rate * 0.15
            +
            income_score * 0.15
            +
            record.consumer_confidence_score * 0.20
            +
            record.e_commerce_growth_score * 0.10
            +
            debt_penalty * 0.10
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalConsumerMarketRecord]:

        return sorted(
            GLOBAL_CONSUMER_MARKET_DATABASE.values(),
            key=lambda item:
            item.consumption_power_score,
            reverse=True,
        )


GLOBAL_CONSUMER_MARKET_ENGINE = (
    GlobalConsumerMarketEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 185
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 186
# ==========================================================

class GlobalIndustrialProductionRecord(BaseModel):
    id: str
    country: str
    industry_sector: str = ""
    industrial_output_usd: float = 0.0
    manufacturing_capacity: float = 0.0
    production_growth_rate: float = 0.0
    factory_utilization_rate: float = 0.0
    automation_score: float = 0.0
    export_competitiveness_score: float = 0.0
    supply_chain_integration_score: float = 0.0
    industrial_strength_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_INDUSTRIAL_PRODUCTION_DATABASE: Dict[
    str,
    GlobalIndustrialProductionRecord,
] = {}


class GlobalIndustrialProductionEngine:

    def register(
        self,
        record: GlobalIndustrialProductionRecord,
    ) -> None:

        GLOBAL_INDUSTRIAL_PRODUCTION_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalIndustrialProductionRecord]:

        return GLOBAL_INDUSTRIAL_PRODUCTION_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_INDUSTRIAL_PRODUCTION_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        output_score = min(
            record.industrial_output_usd
            /
            100000000000,
            100,
        )

        capacity_score = (
            record.manufacturing_capacity
        )

        growth_score = min(
            record.production_growth_rate
            *
            5,
            100,
        )

        record.industrial_strength_score = (
            output_score * 0.25
            +
            capacity_score * 0.20
            +
            growth_score * 0.15
            +
            record.factory_utilization_rate * 0.10
            +
            record.automation_score * 0.10
            +
            record.export_competitiveness_score * 0.10
            +
            record.supply_chain_integration_score * 0.10
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalIndustrialProductionRecord]:

        return sorted(
            GLOBAL_INDUSTRIAL_PRODUCTION_DATABASE.values(),
            key=lambda item:
            item.industrial_strength_score,
            reverse=True,
        )


GLOBAL_INDUSTRIAL_PRODUCTION_ENGINE = (
    GlobalIndustrialProductionEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 186
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 187
# ==========================================================

class GlobalAgricultureMarketRecord(BaseModel):
    id: str
    country: str
    agriculture_sector: str = ""
    farmland_area_hectare: float = 0.0
    crop_production_ton: float = 0.0
    livestock_production_ton: float = 0.0
    agriculture_export_usd: float = 0.0
    food_security_score: float = 0.0
    productivity_score: float = 0.0
    technology_usage_score: float = 0.0
    climate_risk_score: float = 0.0
    agriculture_strength_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_AGRICULTURE_DATABASE: Dict[
    str,
    GlobalAgricultureMarketRecord,
] = {}


class GlobalAgricultureMarketEngine:

    def register(
        self,
        record: GlobalAgricultureMarketRecord,
    ) -> None:

        GLOBAL_AGRICULTURE_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalAgricultureMarketRecord]:

        return GLOBAL_AGRICULTURE_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_AGRICULTURE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        land_score = min(
            record.farmland_area_hectare
            /
            10000000,
            100,
        )

        production_score = min(
            (
                record.crop_production_ton
                +
                record.livestock_production_ton
            )
            /
            10000000,
            100,
        )

        export_score = min(
            record.agriculture_export_usd
            /
            10000000000,
            100,
        )

        record.agriculture_strength_score = (
            land_score * 0.15
            +
            production_score * 0.25
            +
            export_score * 0.20
            +
            record.food_security_score * 0.15
            +
            record.productivity_score * 0.10
            +
            record.technology_usage_score * 0.10
            -
            record.climate_risk_score * 0.05
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalAgricultureMarketRecord]:

        return sorted(
            GLOBAL_AGRICULTURE_DATABASE.values(),
            key=lambda item:
            item.agriculture_strength_score,
            reverse=True,
        )


GLOBAL_AGRICULTURE_ENGINE = (
    GlobalAgricultureMarketEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 187
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 188
# ==========================================================

class GlobalClimateRiskRecord(BaseModel):
    id: str
    country: str
    temperature_change_celsius: float = 0.0
    extreme_weather_frequency: float = 0.0
    flood_risk_score: float = 0.0
    drought_risk_score: float = 0.0
    climate_policy_score: float = 0.0
    renewable_transition_score: float = 0.0
    carbon_emission_ton: float = 0.0
    climate_resilience_score: float = 0.0
    economic_impact_score: float = 0.0
    climate_risk_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_CLIMATE_RISK_DATABASE: Dict[
    str,
    GlobalClimateRiskRecord,
] = {}


class GlobalClimateRiskEngine:

    def register(
        self,
        record: GlobalClimateRiskRecord,
    ) -> None:

        GLOBAL_CLIMATE_RISK_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalClimateRiskRecord]:

        return GLOBAL_CLIMATE_RISK_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_CLIMATE_RISK_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        weather_risk = (
            record.extreme_weather_frequency
            +
            record.flood_risk_score
            +
            record.drought_risk_score
        ) / 3

        emission_penalty = min(
            record.carbon_emission_ton
            /
            100000000,
            100,
        )

        record.climate_risk_score = (
            weather_risk * 0.40
            +
            emission_penalty * 0.20
            -
            record.climate_policy_score * 0.15
            -
            record.renewable_transition_score * 0.15
            -
            record.climate_resilience_score * 0.10
        )

        record.economic_impact_score = (
            record.climate_risk_score
            *
            (
                1
                +
                abs(
                    record.temperature_change_celsius
                )
            )
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalClimateRiskRecord]:

        return sorted(
            GLOBAL_CLIMATE_RISK_DATABASE.values(),
            key=lambda item:
            item.climate_risk_score,
            reverse=True,
        )


GLOBAL_CLIMATE_RISK_ENGINE = (
    GlobalClimateRiskEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 188
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 189
# ==========================================================

class GlobalHealthSystemRecord(BaseModel):
    id: str
    country: str
    healthcare_expenditure_usd: float = 0.0
    hospital_capacity_score: float = 0.0
    doctor_density_score: float = 0.0
    medical_technology_score: float = 0.0
    pharmaceutical_industry_score: float = 0.0
    life_expectancy_years: float = 0.0
    healthcare_access_score: float = 0.0
    pandemic_response_score: float = 0.0
    health_system_strength_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_HEALTH_SYSTEM_DATABASE: Dict[
    str,
    GlobalHealthSystemRecord,
] = {}


class GlobalHealthSystemEngine:

    def register(
        self,
        record: GlobalHealthSystemRecord,
    ) -> None:

        GLOBAL_HEALTH_SYSTEM_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalHealthSystemRecord]:

        return GLOBAL_HEALTH_SYSTEM_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_HEALTH_SYSTEM_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        spending_score = min(
            record.healthcare_expenditure_usd
            /
            100000000000,
            100,
        )

        life_score = min(
            record.life_expectancy_years
            /
            1.0,
            100,
        )

        record.health_system_strength_score = (
            spending_score * 0.20
            +
            record.hospital_capacity_score * 0.15
            +
            record.doctor_density_score * 0.15
            +
            record.medical_technology_score * 0.15
            +
            record.pharmaceutical_industry_score * 0.10
            +
            life_score * 0.10
            +
            record.healthcare_access_score * 0.10
            +
            record.pandemic_response_score * 0.05
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalHealthSystemRecord]:

        return sorted(
            GLOBAL_HEALTH_SYSTEM_DATABASE.values(),
            key=lambda item:
            item.health_system_strength_score,
            reverse=True,
        )


GLOBAL_HEALTH_SYSTEM_ENGINE = (
    GlobalHealthSystemEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 189
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 190
# ==========================================================

class GlobalEducationSystemRecord(BaseModel):
    id: str
    country: str
    education_spending_usd: float = 0.0
    literacy_rate: float = 0.0
    university_quality_score: float = 0.0
    research_capacity_score: float = 0.0
    international_student_score: float = 0.0
    skill_development_score: float = 0.0
    innovation_education_score: float = 0.0
    workforce_quality_score: float = 0.0
    education_strength_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_EDUCATION_SYSTEM_DATABASE: Dict[
    str,
    GlobalEducationSystemRecord,
] = {}


class GlobalEducationSystemEngine:

    def register(
        self,
        record: GlobalEducationSystemRecord,
    ) -> None:

        GLOBAL_EDUCATION_SYSTEM_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalEducationSystemRecord]:

        return GLOBAL_EDUCATION_SYSTEM_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_EDUCATION_SYSTEM_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        spending_score = min(
            record.education_spending_usd
            /
            50000000000,
            100,
        )

        record.workforce_quality_score = (
            record.literacy_rate * 0.15
            +
            record.university_quality_score * 0.20
            +
            record.research_capacity_score * 0.20
            +
            record.skill_development_score * 0.20
            +
            record.innovation_education_score * 0.10
            +
            spending_score * 0.10
            +
            record.international_student_score * 0.05
        )

        record.education_strength_score = (
            record.workforce_quality_score
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalEducationSystemRecord]:

        return sorted(
            GLOBAL_EDUCATION_SYSTEM_DATABASE.values(),
            key=lambda item:
            item.education_strength_score,
            reverse=True,
        )


GLOBAL_EDUCATION_SYSTEM_ENGINE = (
    GlobalEducationSystemEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 190
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 191
# ==========================================================

class GlobalScienceResearchRecord(BaseModel):
    id: str
    country: str
    research_spending_usd: float = 0.0
    scientific_publications: int = 0
    international_collaboration_score: float = 0.0
    researcher_count: int = 0
    laboratory_capacity_score: float = 0.0
    breakthrough_research_score: float = 0.0
    patent_generation_score: float = 0.0
    science_influence_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_SCIENCE_RESEARCH_DATABASE: Dict[
    str,
    GlobalScienceResearchRecord,
] = {}


class GlobalScienceResearchEngine:

    def register(
        self,
        record: GlobalScienceResearchRecord,
    ) -> None:

        GLOBAL_SCIENCE_RESEARCH_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalScienceResearchRecord]:

        return GLOBAL_SCIENCE_RESEARCH_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_SCIENCE_RESEARCH_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        research_budget_score = min(
            record.research_spending_usd
            /
            10000000000,
            100,
        )

        publication_score = min(
            record.scientific_publications
            /
            100000,
            100,
        )

        researcher_score = min(
            record.researcher_count
            /
            100000,
            100,
        )

        record.science_influence_score = (
            research_budget_score * 0.20
            +
            publication_score * 0.20
            +
            researcher_score * 0.15
            +
            record.international_collaboration_score * 0.15
            +
            record.laboratory_capacity_score * 0.10
            +
            record.breakthrough_research_score * 0.10
            +
            record.patent_generation_score * 0.10
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalScienceResearchRecord]:

        return sorted(
            GLOBAL_SCIENCE_RESEARCH_DATABASE.values(),
            key=lambda item:
            item.science_influence_score,
            reverse=True,
        )


GLOBAL_SCIENCE_RESEARCH_ENGINE = (
    GlobalScienceResearchEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 191
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 192
# ==========================================================

class GlobalPatentInnovationRecord(BaseModel):
    id: str
    country: str
    patent_filing_count: int = 0
    patent_grant_count: int = 0
    technology_sector: str = ""
    corporate_research_score: float = 0.0
    university_research_score: float = 0.0
    international_patent_score: float = 0.0
    intellectual_property_value_usd: float = 0.0
    innovation_market_score: float = 0.0
    patent_influence_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_PATENT_INNOVATION_DATABASE: Dict[
    str,
    GlobalPatentInnovationRecord,
] = {}


class GlobalPatentInnovationEngine:

    def register(
        self,
        record: GlobalPatentInnovationRecord,
    ) -> None:

        GLOBAL_PATENT_INNOVATION_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalPatentInnovationRecord]:

        return GLOBAL_PATENT_INNOVATION_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_PATENT_INNOVATION_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        filing_score = min(
            record.patent_filing_count
            /
            100000,
            100,
        )

        grant_score = min(
            record.patent_grant_count
            /
            50000,
            100,
        )

        ip_value_score = min(
            record.intellectual_property_value_usd
            /
            100000000000,
            100,
        )

        record.patent_influence_score = (
            filing_score * 0.20
            +
            grant_score * 0.20
            +
            record.corporate_research_score * 0.15
            +
            record.university_research_score * 0.15
            +
            record.international_patent_score * 0.10
            +
            record.innovation_market_score * 0.10
            +
            ip_value_score * 0.10
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalPatentInnovationRecord]:

        return sorted(
            GLOBAL_PATENT_INNOVATION_DATABASE.values(),
            key=lambda item:
            item.patent_influence_score,
            reverse=True,
        )


GLOBAL_PATENT_INNOVATION_ENGINE = (
    GlobalPatentInnovationEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 192
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 193
# ==========================================================

class GlobalArtificialIntelligenceProfileRecord(BaseModel):
    id: str
    country: str
    ai_research_score: float = 0.0
    ai_company_count: int = 0
    ai_investment_usd: float = 0.0
    computing_capacity_score: float = 0.0
    semiconductor_access_score: float = 0.0
    ai_talent_score: float = 0.0
    data_availability_score: float = 0.0
    ai_policy_score: float = 0.0
    ai_power_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_AI_PROFILE_DATABASE: Dict[
    str,
    GlobalArtificialIntelligenceProfileRecord,
] = {}


class GlobalArtificialIntelligenceProfileEngine:

    def register(
        self,
        record: GlobalArtificialIntelligenceProfileRecord,
    ) -> None:

        GLOBAL_AI_PROFILE_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalArtificialIntelligenceProfileRecord]:

        return GLOBAL_AI_PROFILE_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_AI_PROFILE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        investment_score = min(
            record.ai_investment_usd
            /
            10000000000,
            100,
        )

        company_score = min(
            record.ai_company_count
            /
            1000,
            100,
        )

        record.ai_power_score = (
            record.ai_research_score * 0.20
            +
            company_score * 0.10
            +
            investment_score * 0.15
            +
            record.computing_capacity_score * 0.15
            +
            record.semiconductor_access_score * 0.10
            +
            record.ai_talent_score * 0.15
            +
            record.data_availability_score * 0.10
            +
            record.ai_policy_score * 0.05
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalArtificialIntelligenceProfileRecord]:

        return sorted(
            GLOBAL_AI_PROFILE_DATABASE.values(),
            key=lambda item:
            item.ai_power_score,
            reverse=True,
        )


GLOBAL_AI_PROFILE_ENGINE = (
    GlobalArtificialIntelligenceProfileEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 193
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 194
# ==========================================================

class GlobalSemiconductorMarketRecord(BaseModel):
    id: str
    country: str
    semiconductor_revenue_usd: float = 0.0
    chip_manufacturing_capacity: float = 0.0
    advanced_chip_score: float = 0.0
    fabrication_technology_score: float = 0.0
    semiconductor_export_usd: float = 0.0
    supply_chain_position_score: float = 0.0
    research_capability_score: float = 0.0
    strategic_importance_score: float = 0.0
    semiconductor_power_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_SEMICONDUCTOR_DATABASE: Dict[
    str,
    GlobalSemiconductorMarketRecord,
] = {}


class GlobalSemiconductorMarketEngine:

    def register(
        self,
        record: GlobalSemiconductorMarketRecord,
    ) -> None:

        GLOBAL_SEMICONDUCTOR_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalSemiconductorMarketRecord]:

        return GLOBAL_SEMICONDUCTOR_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_SEMICONDUCTOR_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        revenue_score = min(
            record.semiconductor_revenue_usd
            /
            100000000000,
            100,
        )

        export_score = min(
            record.semiconductor_export_usd
            /
            50000000000,
            100,
        )

        record.semiconductor_power_score = (
            revenue_score * 0.20
            +
            record.chip_manufacturing_capacity * 0.20
            +
            record.advanced_chip_score * 0.15
            +
            record.fabrication_technology_score * 0.15
            +
            export_score * 0.10
            +
            record.supply_chain_position_score * 0.10
            +
            record.research_capability_score * 0.05
            +
            record.strategic_importance_score * 0.05
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalSemiconductorMarketRecord]:

        return sorted(
            GLOBAL_SEMICONDUCTOR_DATABASE.values(),
            key=lambda item:
            item.semiconductor_power_score,
            reverse=True,
        )


GLOBAL_SEMICONDUCTOR_ENGINE = (
    GlobalSemiconductorMarketEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 194
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 195
# ==========================================================

class GlobalTechnologyCompetitionRecord(BaseModel):
    id: str
    country: str
    technology_sector: str = ""
    technology_company_count: int = 0
    technology_market_value_usd: float = 0.0
    research_investment_usd: float = 0.0
    startup_ecosystem_score: float = 0.0
    talent_availability_score: float = 0.0
    global_market_share_score: float = 0.0
    innovation_speed_score: float = 0.0
    technology_competitiveness_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_TECHNOLOGY_COMPETITION_DATABASE: Dict[
    str,
    GlobalTechnologyCompetitionRecord,
] = {}


class GlobalTechnologyCompetitionEngine:

    def register(
        self,
        record: GlobalTechnologyCompetitionRecord,
    ) -> None:

        GLOBAL_TECHNOLOGY_COMPETITION_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalTechnologyCompetitionRecord]:

        return GLOBAL_TECHNOLOGY_COMPETITION_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_TECHNOLOGY_COMPETITION_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        company_score = min(
            record.technology_company_count
            /
            10000,
            100,
        )

        market_score = min(
            record.technology_market_value_usd
            /
            1000000000000,
            100,
        )

        research_score = min(
            record.research_investment_usd
            /
            100000000000,
            100,
        )

        record.technology_competitiveness_score = (
            company_score * 0.10
            +
            market_score * 0.20
            +
            research_score * 0.20
            +
            record.startup_ecosystem_score * 0.15
            +
            record.talent_availability_score * 0.15
            +
            record.global_market_share_score * 0.10
            +
            record.innovation_speed_score * 0.10
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalTechnologyCompetitionRecord]:

        return sorted(
            GLOBAL_TECHNOLOGY_COMPETITION_DATABASE.values(),
            key=lambda item:
            item.technology_competitiveness_score,
            reverse=True,
        )


GLOBAL_TECHNOLOGY_COMPETITION_ENGINE = (
    GlobalTechnologyCompetitionEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 195
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 196
# ==========================================================

class GlobalDataIntelligenceRecord(BaseModel):
    id: str
    data_domain: str
    country: str = ""
    organization: str = ""
    data_volume: float = 0.0
    data_quality_score: float = 0.0
    data_processing_power_score: float = 0.0
    analytics_capability_score: float = 0.0
    artificial_intelligence_usage_score: float = 0.0
    data_accessibility_score: float = 0.0
    intelligence_value_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_DATA_INTELLIGENCE_DATABASE: Dict[
    str,
    GlobalDataIntelligenceRecord,
] = {}


class GlobalDataIntelligenceEngine:

    def register(
        self,
        record: GlobalDataIntelligenceRecord,
    ) -> None:

        GLOBAL_DATA_INTELLIGENCE_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalDataIntelligenceRecord]:

        return GLOBAL_DATA_INTELLIGENCE_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_DATA_INTELLIGENCE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.intelligence_value_score = (
            record.data_quality_score * 0.20
            +
            record.data_processing_power_score * 0.20
            +
            record.analytics_capability_score * 0.20
            +
            record.artificial_intelligence_usage_score * 0.20
            +
            record.data_accessibility_score * 0.20
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalDataIntelligenceRecord]:

        return sorted(
            GLOBAL_DATA_INTELLIGENCE_DATABASE.values(),
            key=lambda item:
            item.intelligence_value_score,
            reverse=True,
        )


GLOBAL_DATA_INTELLIGENCE_ENGINE = (
    GlobalDataIntelligenceEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 196
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 197
# ==========================================================

class GlobalCyberSecurityRecord(BaseModel):
    id: str
    country: str
    cyber_defense_score: float = 0.0
    cyber_attack_frequency: float = 0.0
    security_infrastructure_score: float = 0.0
    data_protection_score: float = 0.0
    cyber_talent_score: float = 0.0
    government_security_score: float = 0.0
    private_sector_security_score: float = 0.0
    cyber_power_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_CYBER_SECURITY_DATABASE: Dict[
    str,
    GlobalCyberSecurityRecord,
] = {}


class GlobalCyberSecurityEngine:

    def register(
        self,
        record: GlobalCyberSecurityRecord,
    ) -> None:

        GLOBAL_CYBER_SECURITY_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalCyberSecurityRecord]:

        return GLOBAL_CYBER_SECURITY_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_CYBER_SECURITY_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        attack_penalty = max(
            0,
            100 -
            (
                record.cyber_attack_frequency
                *
                5
            ),
        )

        record.cyber_power_score = (
            record.cyber_defense_score * 0.20
            +
            record.security_infrastructure_score * 0.20
            +
            record.data_protection_score * 0.15
            +
            record.cyber_talent_score * 0.15
            +
            record.government_security_score * 0.10
            +
            record.private_sector_security_score * 0.10
            +
            attack_penalty * 0.10
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalCyberSecurityRecord]:

        return sorted(
            GLOBAL_CYBER_SECURITY_DATABASE.values(),
            key=lambda item:
            item.cyber_power_score,
            reverse=True,
        )


GLOBAL_CYBER_SECURITY_ENGINE = (
    GlobalCyberSecurityEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 197
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 198
# ==========================================================

class GlobalDigitalEconomyRecord(BaseModel):
    id: str
    country: str
    digital_market_value_usd: float = 0.0
    internet_users: int = 0
    e_commerce_volume_usd: float = 0.0
    digital_payment_volume_usd: float = 0.0
    software_export_usd: float = 0.0
    cloud_market_score: float = 0.0
    digital_infrastructure_score: float = 0.0
    digital_skill_score: float = 0.0
    digital_economy_power_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_DIGITAL_ECONOMY_DATABASE: Dict[
    str,
    GlobalDigitalEconomyRecord,
] = {}


class GlobalDigitalEconomyEngine:

    def register(
        self,
        record: GlobalDigitalEconomyRecord,
    ) -> None:

        GLOBAL_DIGITAL_ECONOMY_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalDigitalEconomyRecord]:

        return GLOBAL_DIGITAL_ECONOMY_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_DIGITAL_ECONOMY_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        market_score = min(
            record.digital_market_value_usd
            /
            100000000000,
            100,
        )

        ecommerce_score = min(
            record.e_commerce_volume_usd
            /
            100000000000,
            100,
        )

        payment_score = min(
            record.digital_payment_volume_usd
            /
            100000000000,
            100,
        )

        software_score = min(
            record.software_export_usd
            /
            50000000000,
            100,
        )

        record.digital_economy_power_score = (
            market_score * 0.20
            +
            ecommerce_score * 0.15
            +
            payment_score * 0.15
            +
            software_score * 0.15
            +
            record.cloud_market_score * 0.10
            +
            record.digital_infrastructure_score * 0.15
            +
            record.digital_skill_score * 0.10
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalDigitalEconomyRecord]:

        return sorted(
            GLOBAL_DIGITAL_ECONOMY_DATABASE.values(),
            key=lambda item:
            item.digital_economy_power_score,
            reverse=True,
        )


GLOBAL_DIGITAL_ECONOMY_ENGINE = (
    GlobalDigitalEconomyEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 198
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 199
# ==========================================================

class GlobalInfrastructureNetworkRecord(BaseModel):
    id: str
    country: str
    transportation_score: float = 0.0
    port_capacity_score: float = 0.0
    airport_network_score: float = 0.0
    railway_network_score: float = 0.0
    energy_grid_score: float = 0.0
    communication_network_score: float = 0.0
    infrastructure_investment_usd: float = 0.0
    infrastructure_quality_score: float = 0.0
    infrastructure_power_score: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_INFRASTRUCTURE_DATABASE: Dict[
    str,
    GlobalInfrastructureNetworkRecord,
] = {}


class GlobalInfrastructureNetworkEngine:

    def register(
        self,
        record: GlobalInfrastructureNetworkRecord,
    ) -> None:

        GLOBAL_INFRASTRUCTURE_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalInfrastructureNetworkRecord]:

        return GLOBAL_INFRASTRUCTURE_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_INFRASTRUCTURE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        investment_score = min(
            record.infrastructure_investment_usd
            /
            100000000000,
            100,
        )

        record.infrastructure_quality_score = (
            record.transportation_score * 0.15
            +
            record.port_capacity_score * 0.15
            +
            record.airport_network_score * 0.10
            +
            record.railway_network_score * 0.15
            +
            record.energy_grid_score * 0.15
            +
            record.communication_network_score * 0.10
            +
            investment_score * 0.20
        )

        record.infrastructure_power_score = (
            record.infrastructure_quality_score
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalInfrastructureNetworkRecord]:

        return sorted(
            GLOBAL_INFRASTRUCTURE_DATABASE.values(),
            key=lambda item:
            item.infrastructure_power_score,
            reverse=True,
        )


GLOBAL_INFRASTRUCTURE_ENGINE = (
    GlobalInfrastructureNetworkEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 199
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 200
# ==========================================================

class GlobalLogisticsNetworkRecord(BaseModel):
    id: str
    country: str
    logistics_performance_score: float = 0.0
    shipping_capacity_score: float = 0.0
    warehouse_capacity_score: float = 0.0
    customs_efficiency_score: float = 0.0
    supply_chain_speed_score: float = 0.0
    logistics_cost_score: float = 0.0
    international_connectivity_score: float = 0.0
    logistics_power_score: float = 0.0
    cargo_volume_ton: float = 0.0
    trade_route_count: int = 0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_LOGISTICS_NETWORK_DATABASE: Dict[
    str,
    GlobalLogisticsNetworkRecord,
] = {}


class GlobalLogisticsNetworkEngine:

    def register(
        self,
        record: GlobalLogisticsNetworkRecord,
    ) -> None:

        GLOBAL_LOGISTICS_NETWORK_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalLogisticsNetworkRecord]:

        return GLOBAL_LOGISTICS_NETWORK_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_LOGISTICS_NETWORK_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        cargo_score = min(
            record.cargo_volume_ton
            /
            10000000,
            100,
        )

        route_score = min(
            record.trade_route_count
            /
            100,
            100,
        )

        record.logistics_power_score = (
            record.logistics_performance_score
            * 0.20
            +
            record.shipping_capacity_score
            * 0.15
            +
            record.warehouse_capacity_score
            * 0.10
            +
            record.customs_efficiency_score
            * 0.10
            +
            record.supply_chain_speed_score
            * 0.15
            +
            record.logistics_cost_score
            * 0.10
            +
            record.international_connectivity_score
            * 0.10
            +
            cargo_score
            * 0.05
            +
            route_score
            * 0.05
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalLogisticsNetworkRecord]:

        return sorted(
            GLOBAL_LOGISTICS_NETWORK_DATABASE.values(),
            key=lambda item:
            item.logistics_power_score,
            reverse=True,
        )


GLOBAL_LOGISTICS_NETWORK_ENGINE = (
    GlobalLogisticsNetworkEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 200
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 201
# ==========================================================

class GlobalMoneyFlowMapNodeRecord(BaseModel):
    id: str
    node_name: str
    node_type: str = ""
    country: str = ""
    region: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    economic_power_score: float = 0.0
    financial_power_score: float = 0.0
    capital_inflow_usd: float = 0.0
    capital_outflow_usd: float = 0.0
    net_capital_flow_usd: float = 0.0
    asset_focus: List[str] = []
    activity_level: float = 0.0
    visualization_size: float = 0.0
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_MONEY_FLOW_NODE_DATABASE: Dict[
    str,
    GlobalMoneyFlowMapNodeRecord,
] = {}


class GlobalMoneyFlowMapNodeEngine:

    def register(
        self,
        record: GlobalMoneyFlowMapNodeRecord,
    ) -> None:

        GLOBAL_MONEY_FLOW_NODE_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalMoneyFlowMapNodeRecord]:

        return GLOBAL_MONEY_FLOW_NODE_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_MONEY_FLOW_NODE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.net_capital_flow_usd = (
            record.capital_inflow_usd
            -
            record.capital_outflow_usd
        )

        record.activity_level = (
            abs(
                record.net_capital_flow_usd
            )
            /
            1000000000
        )

        record.visualization_size = (
            record.economic_power_score * 0.5
            +
            record.financial_power_score * 0.5
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalMoneyFlowMapNodeRecord]:

        return sorted(
            GLOBAL_MONEY_FLOW_NODE_DATABASE.values(),
            key=lambda item:
            item.activity_level,
            reverse=True,
        )


GLOBAL_MONEY_FLOW_NODE_ENGINE = (
    GlobalMoneyFlowMapNodeEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 201
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 202
# ==========================================================

class GlobalMoneyFlowMapEdgeRecord(BaseModel):
    id: str
    source_node: str
    target_node: str
    asset_type: str = ""
    flow_direction: str = ""
    capital_amount_usd: float = 0.0
    flow_speed: float = 0.0
    flow_strength: float = 0.0
    institutional_score: float = 0.0
    retail_score: float = 0.0
    risk_score: float = 0.0
    visualization_intensity: float = 0.0
    line_color_signal: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_MONEY_FLOW_EDGE_DATABASE: Dict[
    str,
    GlobalMoneyFlowMapEdgeRecord,
] = {}


class GlobalMoneyFlowMapEdgeEngine:

    def register(
        self,
        record: GlobalMoneyFlowMapEdgeRecord,
    ) -> None:

        GLOBAL_MONEY_FLOW_EDGE_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalMoneyFlowMapEdgeRecord]:

        return GLOBAL_MONEY_FLOW_EDGE_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_MONEY_FLOW_EDGE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.flow_strength = (
            abs(record.capital_amount_usd)
            /
            1000000000
            *
            record.flow_speed
        )

        record.visualization_intensity = (
            record.flow_strength * 0.50
            +
            record.institutional_score * 0.30
            +
            record.retail_score * 0.20
        )

        if record.capital_amount_usd > 0:
            record.flow_direction = "INFLOW"
            record.line_color_signal = "GREEN"

        elif record.capital_amount_usd < 0:
            record.flow_direction = "OUTFLOW"
            record.line_color_signal = "RED"

        else:
            record.flow_direction = "NEUTRAL"
            record.line_color_signal = "GRAY"

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def strongest_flows(
        self,
    ) -> List[GlobalMoneyFlowMapEdgeRecord]:

        return sorted(
            GLOBAL_MONEY_FLOW_EDGE_DATABASE.values(),
            key=lambda item:
            item.visualization_intensity,
            reverse=True,
        )


GLOBAL_MONEY_FLOW_EDGE_ENGINE = (
    GlobalMoneyFlowMapEdgeEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 202
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 203
# ==========================================================

class AssetRotationRecord(BaseModel):
    id: str
    asset_class: str
    previous_allocation_percent: float = 0.0
    current_allocation_percent: float = 0.0
    capital_change_usd: float = 0.0
    momentum_score: float = 0.0
    risk_adjusted_score: float = 0.0
    investor_sentiment_score: float = 0.0
    institutional_flow_score: float = 0.0
    rotation_direction: str = ""
    rotation_strength: float = 0.0
    explanation: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


ASSET_ROTATION_DATABASE: Dict[
    str,
    AssetRotationRecord,
] = {}


class AssetRotationEngine:

    def register(
        self,
        record: AssetRotationRecord,
    ) -> None:

        ASSET_ROTATION_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[AssetRotationRecord]:

        return ASSET_ROTATION_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        ASSET_ROTATION_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.capital_change_usd = (
            (
                record.current_allocation_percent
                -
                record.previous_allocation_percent
            )
            *
            1000000000
            /
            100
        )

        record.rotation_strength = (
            abs(
                record.capital_change_usd
            )
            *
            0.40
            +
            record.momentum_score
            *
            0.20
            +
            record.investor_sentiment_score
            *
            0.20
            +
            record.institutional_flow_score
            *
            0.20
        )

        if record.capital_change_usd > 0:
            record.rotation_direction = (
                "CAPITAL_INFLOW"
            )

        elif record.capital_change_usd < 0:
            record.rotation_direction = (
                "CAPITAL_OUTFLOW"
            )

        else:
            record.rotation_direction = (
                "NO_ROTATION"
            )

        record.explanation = (
            f"{record.asset_class} rotation: "
            f"{record.rotation_direction}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[AssetRotationRecord]:

        return sorted(
            ASSET_ROTATION_DATABASE.values(),
            key=lambda item:
            item.rotation_strength,
            reverse=True,
        )


ASSET_ROTATION_ENGINE = AssetRotationEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 203
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 204
# ==========================================================

class DollarCycleRecord(BaseModel):
    id: str
    cycle_phase: str = ""
    dxy_value: float = 0.0
    dxy_change_percent: float = 0.0
    fed_policy_score: float = 0.0
    interest_rate_score: float = 0.0
    inflation_pressure_score: float = 0.0
    global_liquidity_score: float = 0.0
    risk_sentiment_score: float = 0.0
    dollar_strength_score: float = 0.0
    affected_assets: List[str] = []
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


DOLLAR_CYCLE_DATABASE: Dict[
    str,
    DollarCycleRecord,
] = {}


class DollarCycleEngine:

    def register(
        self,
        record: DollarCycleRecord,
    ) -> None:

        DOLLAR_CYCLE_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[DollarCycleRecord]:

        return DOLLAR_CYCLE_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        DOLLAR_CYCLE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.dollar_strength_score = (
            record.dxy_value * 0.20
            +
            record.fed_policy_score * 0.20
            +
            record.interest_rate_score * 0.20
            +
            record.inflation_pressure_score * 0.15
            +
            record.global_liquidity_score * 0.15
            +
            record.risk_sentiment_score * 0.10
        )

        if record.dollar_strength_score >= 75:
            record.cycle_phase = (
                "STRONG_DOLLAR_CYCLE"
            )

        elif record.dollar_strength_score >= 50:
            record.cycle_phase = (
                "BALANCED_DOLLAR_CYCLE"
            )

        else:
            record.cycle_phase = (
                "WEAK_DOLLAR_CYCLE"
            )

        record.analysis_text = (
            f"Dollar cycle phase: "
            f"{record.cycle_phase}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[DollarCycleRecord]:

        return sorted(
            DOLLAR_CYCLE_DATABASE.values(),
            key=lambda item:
            item.dollar_strength_score,
            reverse=True,
        )


DOLLAR_CYCLE_ENGINE = DollarCycleEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 204
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 205
# ==========================================================

class GoldMarketFlowRecord(BaseModel):
    id: str
    gold_price_usd: float = 0.0
    gold_etf_flow_usd: float = 0.0
    central_bank_purchase_ton: float = 0.0
    jewelry_demand_ton: float = 0.0
    investment_demand_ton: float = 0.0
    real_yield_score: float = 0.0
    dollar_pressure_score: float = 0.0
    inflation_expectation_score: float = 0.0
    geopolitical_risk_score: float = 0.0
    gold_flow_strength: float = 0.0
    gold_market_signal: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GOLD_MARKET_FLOW_DATABASE: Dict[
    str,
    GoldMarketFlowRecord,
] = {}


class GoldMarketFlowEngine:

    def register(
        self,
        record: GoldMarketFlowRecord,
    ) -> None:

        GOLD_MARKET_FLOW_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GoldMarketFlowRecord]:

        return GOLD_MARKET_FLOW_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GOLD_MARKET_FLOW_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.gold_flow_strength = (
            record.gold_etf_flow_usd
            /
            1000000000
            *
            0.20
            +
            record.central_bank_purchase_ton
            *
            0.15
            +
            record.investment_demand_ton
            *
            0.10
            +
            record.real_yield_score
            *
            0.20
            +
            record.dollar_pressure_score
            *
            0.15
            +
            record.inflation_expectation_score
            *
            0.10
            +
            record.geopolitical_risk_score
            *
            0.10
        )

        if record.gold_flow_strength >= 70:
            record.gold_market_signal = (
                "BULLISH_GOLD_FLOW"
            )

        elif record.gold_flow_strength <= 30:
            record.gold_market_signal = (
                "BEARISH_GOLD_FLOW"
            )

        else:
            record.gold_market_signal = (
                "NEUTRAL_GOLD_FLOW"
            )

        record.analysis_text = (
            f"Gold market signal: "
            f"{record.gold_market_signal}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GoldMarketFlowRecord]:

        return sorted(
            GOLD_MARKET_FLOW_DATABASE.values(),
            key=lambda item:
            item.gold_flow_strength,
            reverse=True,
        )


GOLD_MARKET_FLOW_ENGINE = (
    GoldMarketFlowEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 205
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 206
# ==========================================================

class ETFMoneyFlowRecord(BaseModel):
    id: str
    etf_name: str
    ticker: str = ""
    asset_class: str = ""
    region: str = ""
    total_assets_usd: float = 0.0
    daily_inflow_usd: float = 0.0
    daily_outflow_usd: float = 0.0
    weekly_flow_usd: float = 0.0
    monthly_flow_usd: float = 0.0
    institutional_interest_score: float = 0.0
    retail_interest_score: float = 0.0
    momentum_score: float = 0.0
    etf_flow_strength: float = 0.0
    flow_signal: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


ETF_MONEY_FLOW_DATABASE: Dict[
    str,
    ETFMoneyFlowRecord,
] = {}


class ETFMoneyFlowEngine:

    def register(
        self,
        record: ETFMoneyFlowRecord,
    ) -> None:

        ETF_MONEY_FLOW_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[ETFMoneyFlowRecord]:

        return ETF_MONEY_FLOW_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        ETF_MONEY_FLOW_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        net_daily_flow = (
            record.daily_inflow_usd
            -
            record.daily_outflow_usd
        )

        record.etf_flow_strength = (
            net_daily_flow
            /
            1000000000
            *
            0.30
            +
            record.weekly_flow_usd
            /
            10000000000
            *
            0.20
            +
            record.monthly_flow_usd
            /
            50000000000
            *
            0.20
            +
            record.institutional_interest_score
            *
            0.15
            +
            record.retail_interest_score
            *
            0.05
            +
            record.momentum_score
            *
            0.10
        )

        if record.etf_flow_strength >= 70:
            record.flow_signal = (
                "STRONG_CAPITAL_INFLOW"
            )

        elif record.etf_flow_strength <= 30:
            record.flow_signal = (
                "CAPITAL_OUTFLOW"
            )

        else:
            record.flow_signal = (
                "BALANCED_FLOW"
            )

        record.analysis_text = (
            f"{record.etf_name}: "
            f"{record.flow_signal}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[ETFMoneyFlowRecord]:

        return sorted(
            ETF_MONEY_FLOW_DATABASE.values(),
            key=lambda item:
            item.etf_flow_strength,
            reverse=True,
        )


ETF_MONEY_FLOW_ENGINE = ETFMoneyFlowEngine()

# ==========================================================
# KẾT THÚC ĐOẠN 206
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 207
# ==========================================================

class InstitutionalCapitalFlowRecord(BaseModel):
    id: str
    institution_name: str
    institution_type: str = ""
    country: str = ""
    asset_class: str = ""
    managed_assets_usd: float = 0.0
    capital_inflow_usd: float = 0.0
    capital_outflow_usd: float = 0.0
    portfolio_allocation_change: float = 0.0
    risk_preference_score: float = 0.0
    market_confidence_score: float = 0.0
    institutional_flow_strength: float = 0.0
    flow_direction: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


INSTITUTIONAL_CAPITAL_FLOW_DATABASE: Dict[
    str,
    InstitutionalCapitalFlowRecord,
] = {}


class InstitutionalCapitalFlowEngine:

    def register(
        self,
        record: InstitutionalCapitalFlowRecord,
    ) -> None:

        INSTITUTIONAL_CAPITAL_FLOW_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[InstitutionalCapitalFlowRecord]:

        return INSTITUTIONAL_CAPITAL_FLOW_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        INSTITUTIONAL_CAPITAL_FLOW_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        net_flow = (
            record.capital_inflow_usd
            -
            record.capital_outflow_usd
        )

        asset_scale_score = min(
            record.managed_assets_usd
            /
            100000000000,
            100,
        )

        record.institutional_flow_strength = (
            net_flow
            /
            10000000000
            *
            0.30
            +
            asset_scale_score
            *
            0.20
            +
            record.portfolio_allocation_change
            *
            0.20
            +
            record.risk_preference_score
            *
            0.15
            +
            record.market_confidence_score
            *
            0.15
        )

        if net_flow > 0:
            record.flow_direction = (
                "INSTITUTIONAL_ACCUMULATION"
            )

        elif net_flow < 0:
            record.flow_direction = (
                "INSTITUTIONAL_DISTRIBUTION"
            )

        else:
            record.flow_direction = (
                "NEUTRAL"
            )

        record.analysis_text = (
            f"{record.institution_name}: "
            f"{record.flow_direction}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[InstitutionalCapitalFlowRecord]:

        return sorted(
            INSTITUTIONAL_CAPITAL_FLOW_DATABASE.values(),
            key=lambda item:
            item.institutional_flow_strength,
            reverse=True,
        )


INSTITUTIONAL_CAPITAL_FLOW_ENGINE = (
    InstitutionalCapitalFlowEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 207
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 208
# ==========================================================

class GlobalHedgeFundFlowRecord(BaseModel):
    id: str
    fund_name: str
    fund_type: str = ""
    headquarters_country: str = ""
    strategy: str = ""
    total_assets_usd: float = 0.0
    long_position_usd: float = 0.0
    short_position_usd: float = 0.0
    leverage_ratio: float = 0.0
    risk_appetite_score: float = 0.0
    market_exposure_score: float = 0.0
    net_position_usd: float = 0.0
    hedge_fund_flow_score: float = 0.0
    market_signal: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_HEDGE_FUND_FLOW_DATABASE: Dict[
    str,
    GlobalHedgeFundFlowRecord,
] = {}


class GlobalHedgeFundFlowEngine:

    def register(
        self,
        record: GlobalHedgeFundFlowRecord,
    ) -> None:

        GLOBAL_HEDGE_FUND_FLOW_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalHedgeFundFlowRecord]:

        return GLOBAL_HEDGE_FUND_FLOW_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_HEDGE_FUND_FLOW_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.net_position_usd = (
            record.long_position_usd
            -
            record.short_position_usd
        )

        asset_scale_score = min(
            record.total_assets_usd
            /
            100000000000,
            100,
        )

        record.hedge_fund_flow_score = (
            record.net_position_usd
            /
            10000000000
            *
            0.30
            +
            asset_scale_score
            *
            0.20
            +
            record.leverage_ratio
            *
            0.15
            +
            record.risk_appetite_score
            *
            0.15
            +
            record.market_exposure_score
            *
            0.20
        )

        if record.net_position_usd > 0:
            record.market_signal = (
                "RISK_ON_ACCUMULATION"
            )

        elif record.net_position_usd < 0:
            record.market_signal = (
                "RISK_OFF_POSITIONING"
            )

        else:
            record.market_signal = (
                "NEUTRAL_POSITIONING"
            )

        record.analysis_text = (
            f"{record.fund_name}: "
            f"{record.market_signal}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalHedgeFundFlowRecord]:

        return sorted(
            GLOBAL_HEDGE_FUND_FLOW_DATABASE.values(),
            key=lambda item:
            item.hedge_fund_flow_score,
            reverse=True,
        )


GLOBAL_HEDGE_FUND_FLOW_ENGINE = (
    GlobalHedgeFundFlowEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 208
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 209
# ==========================================================

class CentralBankPolicyFlowRecord(BaseModel):
    id: str
    central_bank_name: str
    country: str = ""
    policy_type: str = ""
    interest_rate: float = 0.0
    balance_sheet_usd: float = 0.0
    asset_purchase_usd: float = 0.0
    liquidity_injection_usd: float = 0.0
    liquidity_withdrawal_usd: float = 0.0
    monetary_policy_score: float = 0.0
    market_impact_score: float = 0.0
    policy_direction: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


CENTRAL_BANK_POLICY_FLOW_DATABASE: Dict[
    str,
    CentralBankPolicyFlowRecord,
] = {}


class CentralBankPolicyFlowEngine:

    def register(
        self,
        record: CentralBankPolicyFlowRecord,
    ) -> None:

        CENTRAL_BANK_POLICY_FLOW_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CentralBankPolicyFlowRecord]:

        return CENTRAL_BANK_POLICY_FLOW_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        CENTRAL_BANK_POLICY_FLOW_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        liquidity_flow = (
            record.liquidity_injection_usd
            -
            record.liquidity_withdrawal_usd
        )

        balance_score = min(
            record.balance_sheet_usd
            /
            1000000000000,
            100,
        )

        record.monetary_policy_score = (
            liquidity_flow
            /
            10000000000
            *
            0.35
            +
            balance_score
            *
            0.20
            +
            record.asset_purchase_usd
            /
            10000000000
            *
            0.20
            +
            record.market_impact_score
            *
            0.25
        )

        if liquidity_flow > 0:
            record.policy_direction = (
                "EASING_LIQUIDITY"
            )

        elif liquidity_flow < 0:
            record.policy_direction = (
                "TIGHTENING_LIQUIDITY"
            )

        else:
            record.policy_direction = (
                "NEUTRAL_POLICY"
            )

        record.analysis_text = (
            f"{record.central_bank_name}: "
            f"{record.policy_direction}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[CentralBankPolicyFlowRecord]:

        return sorted(
            CENTRAL_BANK_POLICY_FLOW_DATABASE.values(),
            key=lambda item:
            item.monetary_policy_score,
            reverse=True,
        )


CENTRAL_BANK_POLICY_FLOW_ENGINE = (
    CentralBankPolicyFlowEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 209
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 210
# ==========================================================

class GlobalLiquidityConditionRecord(BaseModel):
    id: str
    region: str
    global_money_supply_usd: float = 0.0
    m2_growth_rate: float = 0.0
    central_bank_balance_change: float = 0.0
    credit_growth_rate: float = 0.0
    bond_market_liquidity_score: float = 0.0
    equity_market_liquidity_score: float = 0.0
    currency_liquidity_score: float = 0.0
    liquidity_cycle_score: float = 0.0
    liquidity_status: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_LIQUIDITY_CONDITION_DATABASE: Dict[
    str,
    GlobalLiquidityConditionRecord,
] = {}


class GlobalLiquidityConditionEngine:

    def register(
        self,
        record: GlobalLiquidityConditionRecord,
    ) -> None:

        GLOBAL_LIQUIDITY_CONDITION_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalLiquidityConditionRecord]:

        return GLOBAL_LIQUIDITY_CONDITION_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_LIQUIDITY_CONDITION_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        money_supply_score = (
            record.m2_growth_rate
            *
            5
        )

        central_bank_score = (
            record.central_bank_balance_change
            *
            5
        )

        record.liquidity_cycle_score = (
            money_supply_score * 0.25
            +
            central_bank_score * 0.25
            +
            record.credit_growth_rate * 0.20
            +
            record.bond_market_liquidity_score * 0.10
            +
            record.equity_market_liquidity_score * 0.10
            +
            record.currency_liquidity_score * 0.10
        )

        if record.liquidity_cycle_score >= 70:
            record.liquidity_status = (
                "ABUNDANT_LIQUIDITY"
            )

        elif record.liquidity_cycle_score >= 40:
            record.liquidity_status = (
                "NORMAL_LIQUIDITY"
            )

        else:
            record.liquidity_status = (
                "TIGHT_LIQUIDITY"
            )

        record.analysis_text = (
            f"Liquidity condition: "
            f"{record.liquidity_status}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalLiquidityConditionRecord]:

        return sorted(
            GLOBAL_LIQUIDITY_CONDITION_DATABASE.values(),
            key=lambda item:
            item.liquidity_cycle_score,
            reverse=True,
        )


GLOBAL_LIQUIDITY_CONDITION_ENGINE = (
    GlobalLiquidityConditionEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 210
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 211
# ==========================================================

class MarketRegimeDetectionRecord(BaseModel):
    id: str
    market_name: str
    asset_class: str = ""
    trend_score: float = 0.0
    volatility_score: float = 0.0
    liquidity_score: float = 0.0
    momentum_score: float = 0.0
    macro_support_score: float = 0.0
    risk_sentiment_score: float = 0.0
    regime_score: float = 0.0
    current_regime: str = ""
    confidence_score: float = 0.0
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


MARKET_REGIME_DATABASE: Dict[
    str,
    MarketRegimeDetectionRecord,
] = {}


class MarketRegimeDetectionEngine:

    def register(
        self,
        record: MarketRegimeDetectionRecord,
    ) -> None:

        MARKET_REGIME_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[MarketRegimeDetectionRecord]:

        return MARKET_REGIME_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        MARKET_REGIME_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.regime_score = (
            record.trend_score * 0.20
            +
            record.volatility_score * 0.15
            +
            record.liquidity_score * 0.15
            +
            record.momentum_score * 0.15
            +
            record.macro_support_score * 0.20
            +
            record.risk_sentiment_score * 0.15
        )

        record.confidence_score = (
            abs(
                record.regime_score - 50
            )
            *
            2
        )

        if record.regime_score >= 75:
            record.current_regime = (
                "BULL_MARKET_REGIME"
            )

        elif record.regime_score >= 55:
            record.current_regime = (
                "RISK_ON_REGIME"
            )

        elif record.regime_score >= 35:
            record.current_regime = (
                "NEUTRAL_REGIME"
            )

        else:
            record.current_regime = (
                "BEAR_MARKET_REGIME"
            )

        record.analysis_text = (
            f"{record.market_name}: "
            f"{record.current_regime}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[MarketRegimeDetectionRecord]:

        return sorted(
            MARKET_REGIME_DATABASE.values(),
            key=lambda item:
            item.regime_score,
            reverse=True,
        )


MARKET_REGIME_ENGINE = (
    MarketRegimeDetectionEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 211
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 212
# ==========================================================

class EconomicCycleDetectionRecord(BaseModel):
    id: str
    country: str
    gdp_growth_rate: float = 0.0
    inflation_rate: float = 0.0
    unemployment_rate: float = 0.0
    interest_rate_level: float = 0.0
    consumer_activity_score: float = 0.0
    industrial_activity_score: float = 0.0
    credit_cycle_score: float = 0.0
    economic_cycle_score: float = 0.0
    current_cycle: str = ""
    confidence_score: float = 0.0
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


ECONOMIC_CYCLE_DATABASE: Dict[
    str,
    EconomicCycleDetectionRecord,
] = {}


class EconomicCycleDetectionEngine:

    def register(
        self,
        record: EconomicCycleDetectionRecord,
    ) -> None:

        ECONOMIC_CYCLE_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[EconomicCycleDetectionRecord]:

        return ECONOMIC_CYCLE_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        ECONOMIC_CYCLE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        inflation_score = max(
            0,
            100 -
            (
                abs(
                    record.inflation_rate
                    -
                    2
                )
                *
                20
            ),
        )

        employment_score = max(
            0,
            100 -
            (
                record.unemployment_rate
                *
                5
            ),
        )

        record.economic_cycle_score = (
            record.gdp_growth_rate
            *
            10
            *
            0.20
            +
            inflation_score
            *
            0.15
            +
            employment_score
            *
            0.15
            +
            record.consumer_activity_score
            *
            0.15
            +
            record.industrial_activity_score
            *
            0.15
            +
            record.credit_cycle_score
            *
            0.20
        )

        record.confidence_score = (
            abs(
                record.economic_cycle_score
                -
                50
            )
            *
            2
        )

        if record.economic_cycle_score >= 75:
            record.current_cycle = (
                "EXPANSION_CYCLE"
            )

        elif record.economic_cycle_score >= 55:
            record.current_cycle = (
                "RECOVERY_CYCLE"
            )

        elif record.economic_cycle_score >= 35:
            record.current_cycle = (
                "SLOWDOWN_CYCLE"
            )

        else:
            record.current_cycle = (
                "RECESSION_RISK"
            )

        record.analysis_text = (
            f"{record.country}: "
            f"{record.current_cycle}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[EconomicCycleDetectionRecord]:

        return sorted(
            ECONOMIC_CYCLE_DATABASE.values(),
            key=lambda item:
            item.economic_cycle_score,
            reverse=True,
        )


ECONOMIC_CYCLE_ENGINE = (
    EconomicCycleDetectionEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 212
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 213
# ==========================================================

class EconomicScenarioSimulationRecord(BaseModel):
    id: str
    scenario_name: str
    country: str = ""
    scenario_type: str = ""
    gdp_change_percent: float = 0.0
    inflation_change_percent: float = 0.0
    interest_rate_change_percent: float = 0.0
    unemployment_change_percent: float = 0.0
    currency_impact_score: float = 0.0
    stock_market_impact_score: float = 0.0
    bond_market_impact_score: float = 0.0
    gold_market_impact_score: float = 0.0
    probability_score: float = 0.0
    scenario_impact_score: float = 0.0
    conclusion: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


ECONOMIC_SCENARIO_DATABASE: Dict[
    str,
    EconomicScenarioSimulationRecord,
] = {}


class EconomicScenarioSimulationEngine:

    def register(
        self,
        record: EconomicScenarioSimulationRecord,
    ) -> None:

        ECONOMIC_SCENARIO_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[EconomicScenarioSimulationRecord]:

        return ECONOMIC_SCENARIO_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        ECONOMIC_SCENARIO_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        growth_component = (
            record.gdp_change_percent
            *
            10
        )

        inflation_component = (
            abs(
                record.inflation_change_percent
            )
            *
            5
        )

        rate_component = (
            abs(
                record.interest_rate_change_percent
            )
            *
            5
        )

        employment_component = (
            abs(
                record.unemployment_change_percent
            )
            *
            5
        )

        record.scenario_impact_score = (
            growth_component * 0.20
            +
            inflation_component * 0.20
            +
            rate_component * 0.15
            +
            employment_component * 0.15
            +
            record.currency_impact_score * 0.10
            +
            record.stock_market_impact_score * 0.05
            +
            record.bond_market_impact_score * 0.05
            +
            record.gold_market_impact_score * 0.10
        )

        if record.scenario_impact_score >= 70:
            record.conclusion = (
                "HIGH_MARKET_IMPACT"
            )

        elif record.scenario_impact_score >= 40:
            record.conclusion = (
                "MEDIUM_MARKET_IMPACT"
            )

        else:
            record.conclusion = (
                "LOW_MARKET_IMPACT"
            )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[EconomicScenarioSimulationRecord]:

        return sorted(
            ECONOMIC_SCENARIO_DATABASE.values(),
            key=lambda item:
            item.scenario_impact_score,
            reverse=True,
        )


ECONOMIC_SCENARIO_ENGINE = (
    EconomicScenarioSimulationEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 213
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 214
# ==========================================================

class CrisisDetectionRecord(BaseModel):
    id: str
    region: str
    economic_stress_score: float = 0.0
    financial_stability_score: float = 0.0
    currency_pressure_score: float = 0.0
    debt_risk_score: float = 0.0
    geopolitical_tension_score: float = 0.0
    market_volatility_score: float = 0.0
    liquidity_stress_score: float = 0.0
    crisis_probability_score: float = 0.0
    crisis_level: str = ""
    warning_signal: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


CRISIS_DETECTION_DATABASE: Dict[
    str,
    CrisisDetectionRecord,
] = {}


class CrisisDetectionEngine:

    def register(
        self,
        record: CrisisDetectionRecord,
    ) -> None:

        CRISIS_DETECTION_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[CrisisDetectionRecord]:

        return CRISIS_DETECTION_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        CRISIS_DETECTION_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.crisis_probability_score = (
            record.economic_stress_score * 0.15
            +
            record.financial_stability_score * 0.15
            +
            record.currency_pressure_score * 0.15
            +
            record.debt_risk_score * 0.15
            +
            record.geopolitical_tension_score * 0.15
            +
            record.market_volatility_score * 0.10
            +
            record.liquidity_stress_score * 0.15
        )

        if record.crisis_probability_score >= 80:
            record.crisis_level = (
                "CRITICAL"
            )
            record.warning_signal = (
                "RED_ALERT"
            )

        elif record.crisis_probability_score >= 60:
            record.crisis_level = (
                "HIGH_RISK"
            )
            record.warning_signal = (
                "ORANGE_ALERT"
            )

        elif record.crisis_probability_score >= 40:
            record.crisis_level = (
                "WATCH"
            )
            record.warning_signal = (
                "YELLOW_ALERT"
            )

        else:
            record.crisis_level = (
                "STABLE"
            )
            record.warning_signal = (
                "NO_ALERT"
            )

        record.analysis_text = (
            f"{record.region}: "
            f"{record.crisis_level}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[CrisisDetectionRecord]:

        return sorted(
            CRISIS_DETECTION_DATABASE.values(),
            key=lambda item:
            item.crisis_probability_score,
            reverse=True,
        )


CRISIS_DETECTION_ENGINE = (
    CrisisDetectionEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 214
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 215
# ==========================================================

class MarketShockDetectionRecord(BaseModel):
    id: str
    market_name: str
    asset_class: str = ""
    price_change_percent: float = 0.0
    volume_change_percent: float = 0.0
    volatility_change_percent: float = 0.0
    liquidity_change_score: float = 0.0
    investor_panic_score: float = 0.0
    institutional_reaction_score: float = 0.0
    macro_event_score: float = 0.0
    shock_probability_score: float = 0.0
    shock_level: str = ""
    warning_signal: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


MARKET_SHOCK_DATABASE: Dict[
    str,
    MarketShockDetectionRecord,
] = {}


class MarketShockDetectionEngine:

    def register(
        self,
        record: MarketShockDetectionRecord,
    ) -> None:

        MARKET_SHOCK_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[MarketShockDetectionRecord]:

        return MARKET_SHOCK_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        MARKET_SHOCK_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        price_stress = abs(
            record.price_change_percent
        ) * 5

        volume_stress = abs(
            record.volume_change_percent
        ) * 3

        volatility_stress = abs(
            record.volatility_change_percent
        ) * 3

        record.shock_probability_score = (
            price_stress * 0.20
            +
            volume_stress * 0.15
            +
            volatility_stress * 0.15
            +
            record.liquidity_change_score * 0.15
            +
            record.investor_panic_score * 0.15
            +
            record.institutional_reaction_score * 0.10
            +
            record.macro_event_score * 0.10
        )

        if record.shock_probability_score >= 80:
            record.shock_level = (
                "EXTREME_SHOCK"
            )
            record.warning_signal = (
                "RED_ALERT"
            )

        elif record.shock_probability_score >= 60:
            record.shock_level = (
                "HIGH_VOLATILITY"
            )
            record.warning_signal = (
                "ORANGE_ALERT"
            )

        elif record.shock_probability_score >= 40:
            record.shock_level = (
                "MARKET_STRESS"
            )
            record.warning_signal = (
                "YELLOW_ALERT"
            )

        else:
            record.shock_level = (
                "NORMAL"
            )
            record.warning_signal = (
                "NO_ALERT"
            )

        record.analysis_text = (
            f"{record.market_name}: "
            f"{record.shock_level}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[MarketShockDetectionRecord]:

        return sorted(
            MARKET_SHOCK_DATABASE.values(),
            key=lambda item:
            item.shock_probability_score,
            reverse=True,
        )


MARKET_SHOCK_ENGINE = (
    MarketShockDetectionEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 215
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 216
# ==========================================================

class GlobalRiskHeatmapRecord(BaseModel):
    id: str
    region: str
    country: str = ""
    economic_risk_score: float = 0.0
    financial_risk_score: float = 0.0
    currency_risk_score: float = 0.0
    political_risk_score: float = 0.0
    climate_risk_score: float = 0.0
    supply_chain_risk_score: float = 0.0
    market_risk_score: float = 0.0
    total_risk_score: float = 0.0
    risk_color_level: str = ""
    risk_category: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_RISK_HEATMAP_DATABASE: Dict[
    str,
    GlobalRiskHeatmapRecord,
] = {}


class GlobalRiskHeatmapEngine:

    def register(
        self,
        record: GlobalRiskHeatmapRecord,
    ) -> None:

        GLOBAL_RISK_HEATMAP_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalRiskHeatmapRecord]:

        return GLOBAL_RISK_HEATMAP_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_RISK_HEATMAP_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.total_risk_score = (
            record.economic_risk_score * 0.20
            +
            record.financial_risk_score * 0.15
            +
            record.currency_risk_score * 0.15
            +
            record.political_risk_score * 0.15
            +
            record.climate_risk_score * 0.10
            +
            record.supply_chain_risk_score * 0.15
            +
            record.market_risk_score * 0.10
        )

        if record.total_risk_score >= 75:
            record.risk_color_level = "RED"
            record.risk_category = "HIGH_RISK"

        elif record.total_risk_score >= 50:
            record.risk_color_level = "ORANGE"
            record.risk_category = "MEDIUM_RISK"

        elif record.total_risk_score >= 25:
            record.risk_color_level = "YELLOW"
            record.risk_category = "LOW_RISK"

        else:
            record.risk_color_level = "GREEN"
            record.risk_category = "STABLE"

        record.analysis_text = (
            f"{record.country}: "
            f"{record.risk_category}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalRiskHeatmapRecord]:

        return sorted(
            GLOBAL_RISK_HEATMAP_DATABASE.values(),
            key=lambda item:
            item.total_risk_score,
            reverse=True,
        )


GLOBAL_RISK_HEATMAP_ENGINE = (
    GlobalRiskHeatmapEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 216
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 217
# ==========================================================

class GlobalInvestmentOpportunityRecord(BaseModel):
    id: str
    country: str
    sector: str = ""
    market_size_usd: float = 0.0
    growth_potential_score: float = 0.0
    investor_interest_score: float = 0.0
    economic_stability_score: float = 0.0
    regulatory_environment_score: float = 0.0
    technology_advantage_score: float = 0.0
    risk_discount_score: float = 0.0
    opportunity_score: float = 0.0
    opportunity_level: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_INVESTMENT_OPPORTUNITY_DATABASE: Dict[
    str,
    GlobalInvestmentOpportunityRecord,
] = {}


class GlobalInvestmentOpportunityEngine:

    def register(
        self,
        record: GlobalInvestmentOpportunityRecord,
    ) -> None:

        GLOBAL_INVESTMENT_OPPORTUNITY_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalInvestmentOpportunityRecord]:

        return GLOBAL_INVESTMENT_OPPORTUNITY_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_INVESTMENT_OPPORTUNITY_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        market_score = min(
            record.market_size_usd
            /
            100000000000,
            100,
        )

        record.opportunity_score = (
            market_score * 0.20
            +
            record.growth_potential_score * 0.20
            +
            record.investor_interest_score * 0.15
            +
            record.economic_stability_score * 0.15
            +
            record.regulatory_environment_score * 0.10
            +
            record.technology_advantage_score * 0.10
            -
            record.risk_discount_score * 0.10
        )

        if record.opportunity_score >= 75:
            record.opportunity_level = (
                "HIGH_OPPORTUNITY"
            )

        elif record.opportunity_score >= 50:
            record.opportunity_level = (
                "MEDIUM_OPPORTUNITY"
            )

        else:
            record.opportunity_level = (
                "LOW_OPPORTUNITY"
            )

        record.analysis_text = (
            f"{record.country} - "
            f"{record.sector}: "
            f"{record.opportunity_level}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalInvestmentOpportunityRecord]:

        return sorted(
            GLOBAL_INVESTMENT_OPPORTUNITY_DATABASE.values(),
            key=lambda item:
            item.opportunity_score,
            reverse=True,
        )


GLOBAL_INVESTMENT_OPPORTUNITY_ENGINE = (
    GlobalInvestmentOpportunityEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 217
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 218
# ==========================================================

class GlobalPortfolioAllocationRecord(BaseModel):
    id: str
    investor_type: str
    region: str = ""
    asset_class: str = ""
    equity_allocation: float = 0.0
    bond_allocation: float = 0.0
    gold_allocation: float = 0.0
    crypto_allocation: float = 0.0
    real_estate_allocation: float = 0.0
    cash_allocation: float = 0.0
    risk_preference_score: float = 0.0
    macro_view_score: float = 0.0
    allocation_change_score: float = 0.0
    portfolio_signal: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_PORTFOLIO_ALLOCATION_DATABASE: Dict[
    str,
    GlobalPortfolioAllocationRecord,
] = {}


class GlobalPortfolioAllocationEngine:

    def register(
        self,
        record: GlobalPortfolioAllocationRecord,
    ) -> None:

        GLOBAL_PORTFOLIO_ALLOCATION_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalPortfolioAllocationRecord]:

        return GLOBAL_PORTFOLIO_ALLOCATION_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_PORTFOLIO_ALLOCATION_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        defensive_assets = (
            record.bond_allocation
            +
            record.gold_allocation
            +
            record.cash_allocation
        )

        growth_assets = (
            record.equity_allocation
            +
            record.crypto_allocation
            +
            record.real_estate_allocation
        )

        record.allocation_change_score = (
            growth_assets
            -
            defensive_assets
        )

        portfolio_score = (
            record.risk_preference_score * 0.25
            +
            record.macro_view_score * 0.35
            +
            record.allocation_change_score * 0.40
        )

        if portfolio_score >= 60:
            record.portfolio_signal = (
                "RISK_ON_ALLOCATION"
            )

        elif portfolio_score <= 40:
            record.portfolio_signal = (
                "RISK_OFF_ALLOCATION"
            )

        else:
            record.portfolio_signal = (
                "BALANCED_ALLOCATION"
            )

        record.analysis_text = (
            f"{record.investor_type}: "
            f"{record.portfolio_signal}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalPortfolioAllocationRecord]:

        return sorted(
            GLOBAL_PORTFOLIO_ALLOCATION_DATABASE.values(),
            key=lambda item:
            item.allocation_change_score,
            reverse=True,
        )


GLOBAL_PORTFOLIO_ALLOCATION_ENGINE = (
    GlobalPortfolioAllocationEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 218
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 219
# ==========================================================

class GlobalInvestorSentimentRecord(BaseModel):
    id: str
    market_name: str
    asset_class: str = ""
    retail_sentiment_score: float = 0.0
    institutional_sentiment_score: float = 0.0
    social_media_sentiment_score: float = 0.0
    news_sentiment_score: float = 0.0
    volatility_fear_score: float = 0.0
    optimism_score: float = 0.0
    pessimism_score: float = 0.0
    overall_sentiment_score: float = 0.0
    sentiment_state: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_INVESTOR_SENTIMENT_DATABASE: Dict[
    str,
    GlobalInvestorSentimentRecord,
] = {}


class GlobalInvestorSentimentEngine:

    def register(
        self,
        record: GlobalInvestorSentimentRecord,
    ) -> None:

        GLOBAL_INVESTOR_SENTIMENT_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalInvestorSentimentRecord]:

        return GLOBAL_INVESTOR_SENTIMENT_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_INVESTOR_SENTIMENT_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.overall_sentiment_score = (
            record.retail_sentiment_score * 0.15
            +
            record.institutional_sentiment_score * 0.25
            +
            record.social_media_sentiment_score * 0.15
            +
            record.news_sentiment_score * 0.20
            +
            record.optimism_score * 0.15
            -
            record.volatility_fear_score * 0.05
            -
            record.pessimism_score * 0.05
        )

        if record.overall_sentiment_score >= 70:
            record.sentiment_state = (
                "EXTREME_OPTIMISM"
            )

        elif record.overall_sentiment_score >= 55:
            record.sentiment_state = (
                "POSITIVE_SENTIMENT"
            )

        elif record.overall_sentiment_score >= 40:
            record.sentiment_state = (
                "NEUTRAL_SENTIMENT"
            )

        else:
            record.sentiment_state = (
                "NEGATIVE_SENTIMENT"
            )

        record.analysis_text = (
            f"{record.market_name}: "
            f"{record.sentiment_state}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalInvestorSentimentRecord]:

        return sorted(
            GLOBAL_INVESTOR_SENTIMENT_DATABASE.values(),
            key=lambda item:
            item.overall_sentiment_score,
            reverse=True,
        )


GLOBAL_INVESTOR_SENTIMENT_ENGINE = (
    GlobalInvestorSentimentEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 219
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 220
# ==========================================================

class GlobalMarketCorrelationRecord(BaseModel):
    id: str
    asset_a: str
    asset_b: str = ""
    correlation_period: str = ""
    price_correlation: float = 0.0
    volatility_correlation: float = 0.0
    liquidity_correlation: float = 0.0
    macro_correlation: float = 0.0
    flow_correlation: float = 0.0
    total_correlation_score: float = 0.0
    relationship_type: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_MARKET_CORRELATION_DATABASE: Dict[
    str,
    GlobalMarketCorrelationRecord,
] = {}


class GlobalMarketCorrelationEngine:

    def register(
        self,
        record: GlobalMarketCorrelationRecord,
    ) -> None:

        GLOBAL_MARKET_CORRELATION_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalMarketCorrelationRecord]:

        return GLOBAL_MARKET_CORRELATION_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_MARKET_CORRELATION_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.total_correlation_score = (
            record.price_correlation * 0.25
            +
            record.volatility_correlation * 0.15
            +
            record.liquidity_correlation * 0.20
            +
            record.macro_correlation * 0.20
            +
            record.flow_correlation * 0.20
        )

        if record.total_correlation_score >= 75:
            record.relationship_type = (
                "STRONG_RELATIONSHIP"
            )

        elif record.total_correlation_score >= 50:
            record.relationship_type = (
                "MODERATE_RELATIONSHIP"
            )

        else:
            record.relationship_type = (
                "WEAK_RELATIONSHIP"
            )

        record.analysis_text = (
            f"{record.asset_a} ↔ "
            f"{record.asset_b}: "
            f"{record.relationship_type}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalMarketCorrelationRecord]:

        return sorted(
            GLOBAL_MARKET_CORRELATION_DATABASE.values(),
            key=lambda item:
            item.total_correlation_score,
            reverse=True,
        )


GLOBAL_MARKET_CORRELATION_ENGINE = (
    GlobalMarketCorrelationEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 220
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 221
# ==========================================================

class GlobalMacroSignalRecord(BaseModel):
    id: str
    signal_name: str
    category: str = ""
    indicator_name: str = ""
    current_value: float = 0.0
    previous_value: float = 0.0
    change_percent: float = 0.0
    impact_score: float = 0.0
    confidence_score: float = 0.0
    market_direction: str = ""
    affected_assets: List[str] = []
    signal_strength: float = 0.0
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_MACRO_SIGNAL_DATABASE: Dict[
    str,
    GlobalMacroSignalRecord,
] = {}


class GlobalMacroSignalEngine:

    def register(
        self,
        record: GlobalMacroSignalRecord,
    ) -> None:

        GLOBAL_MACRO_SIGNAL_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalMacroSignalRecord]:

        return GLOBAL_MACRO_SIGNAL_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_MACRO_SIGNAL_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        if record.previous_value != 0:
            record.change_percent = (
                (
                    record.current_value
                    -
                    record.previous_value
                )
                /
                abs(
                    record.previous_value
                )
            )
            * 100

        record.signal_strength = (
            abs(
                record.change_percent
            )
            *
            0.30
            +
            record.impact_score
            *
            0.40
            +
            record.confidence_score
            *
            0.30
        )

        if record.change_percent > 0:
            record.market_direction = (
                "POSITIVE"
            )

        elif record.change_percent < 0:
            record.market_direction = (
                "NEGATIVE"
            )

        else:
            record.market_direction = (
                "NEUTRAL"
            )

        record.analysis_text = (
            f"{record.signal_name}: "
            f"{record.market_direction}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalMacroSignalRecord]:

        return sorted(
            GLOBAL_MACRO_SIGNAL_DATABASE.values(),
            key=lambda item:
            item.signal_strength,
            reverse=True,
        )


GLOBAL_MACRO_SIGNAL_ENGINE = (
    GlobalMacroSignalEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 221
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 222
# ==========================================================

class GlobalEconomicIndicatorRecord(BaseModel):
    id: str
    indicator_name: str
    country: str = ""
    category: str = ""
    current_value: float = 0.0
    previous_value: float = 0.0
    forecast_value: float = 0.0
    deviation_from_forecast: float = 0.0
    market_impact_score: float = 0.0
    gold_impact_score: float = 0.0
    dollar_impact_score: float = 0.0
    stock_market_impact_score: float = 0.0
    bond_market_impact_score: float = 0.0
    indicator_signal: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_ECONOMIC_INDICATOR_DATABASE: Dict[
    str,
    GlobalEconomicIndicatorRecord,
] = {}


class GlobalEconomicIndicatorEngine:

    def register(
        self,
        record: GlobalEconomicIndicatorRecord,
    ) -> None:

        GLOBAL_ECONOMIC_INDICATOR_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalEconomicIndicatorRecord]:

        return GLOBAL_ECONOMIC_INDICATOR_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_ECONOMIC_INDICATOR_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        if record.forecast_value != 0:
            record.deviation_from_forecast = (
                (
                    record.current_value
                    -
                    record.forecast_value
                )
                /
                abs(
                    record.forecast_value
                )
            ) * 100

        record.market_impact_score = (
            abs(
                record.deviation_from_forecast
            )
            *
            0.40
            +
            record.category != ""
            *
            0.10
            +
            record.current_value
            *
            0.50
        )

        if record.deviation_from_forecast > 0:
            record.indicator_signal = (
                "ABOVE_EXPECTATION"
            )

        elif record.deviation_from_forecast < 0:
            record.indicator_signal = (
                "BELOW_EXPECTATION"
            )

        else:
            record.indicator_signal = (
                "IN_LINE_EXPECTATION"
            )

        record.analysis_text = (
            f"{record.indicator_name}: "
            f"{record.indicator_signal}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalEconomicIndicatorRecord]:

        return sorted(
            GLOBAL_ECONOMIC_INDICATOR_DATABASE.values(),
            key=lambda item:
            item.market_impact_score,
            reverse=True,
        )


GLOBAL_ECONOMIC_INDICATOR_ENGINE = (
    GlobalEconomicIndicatorEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 222
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 223
# ==========================================================

class GlobalEconomicEventRecord(BaseModel):
    id: str
    event_name: str
    country: str = ""
    event_category: str = ""
    event_time: str = ""
    previous_value: float = 0.0
    forecast_value: float = 0.0
    actual_value: float = 0.0
    surprise_score: float = 0.0
    market_reaction_score: float = 0.0
    gold_reaction_score: float = 0.0
    dollar_reaction_score: float = 0.0
    volatility_impact_score: float = 0.0
    event_importance: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_ECONOMIC_EVENT_DATABASE: Dict[
    str,
    GlobalEconomicEventRecord,
] = {}


class GlobalEconomicEventEngine:

    def register(
        self,
        record: GlobalEconomicEventRecord,
    ) -> None:

        GLOBAL_ECONOMIC_EVENT_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalEconomicEventRecord]:

        return GLOBAL_ECONOMIC_EVENT_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_ECONOMIC_EVENT_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        if record.forecast_value != 0:
            record.surprise_score = (
                (
                    record.actual_value
                    -
                    record.forecast_value
                )
                /
                abs(
                    record.forecast_value
                )
            ) * 100

        record.market_reaction_score = (
            abs(
                record.surprise_score
            )
            *
            0.35
            +
            record.volatility_impact_score
            *
            0.35
            +
            record.event_category != ""
            *
            0.30
        )

        if record.market_reaction_score >= 70:
            record.event_importance = (
                "HIGH_IMPACT"
            )

        elif record.market_reaction_score >= 40:
            record.event_importance = (
                "MEDIUM_IMPACT"
            )

        else:
            record.event_importance = (
                "LOW_IMPACT"
            )

        record.analysis_text = (
            f"{record.event_name}: "
            f"{record.event_importance}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalEconomicEventRecord]:

        return sorted(
            GLOBAL_ECONOMIC_EVENT_DATABASE.values(),
            key=lambda item:
            item.market_reaction_score,
            reverse=True,
        )


GLOBAL_ECONOMIC_EVENT_ENGINE = (
    GlobalEconomicEventEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 223
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 224
# ==========================================================

class GlobalNewsIntelligenceRecord(BaseModel):
    id: str
    title: str
    source_name: str = ""
    country: str = ""
    category: str = ""
    published_time: Optional[datetime] = None
    sentiment_score: float = 0.0
    market_relevance_score: float = 0.0
    gold_relevance_score: float = 0.0
    dollar_relevance_score: float = 0.0
    geopolitical_score: float = 0.0
    economic_score: float = 0.0
    ai_summary: str = ""
    news_impact_score: float = 0.0
    impact_level: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_NEWS_INTELLIGENCE_DATABASE: Dict[
    str,
    GlobalNewsIntelligenceRecord,
] = {}


class GlobalNewsIntelligenceEngine:

    def register(
        self,
        record: GlobalNewsIntelligenceRecord,
    ) -> None:

        GLOBAL_NEWS_INTELLIGENCE_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalNewsIntelligenceRecord]:

        return GLOBAL_NEWS_INTELLIGENCE_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_NEWS_INTELLIGENCE_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.news_impact_score = (
            record.market_relevance_score * 0.25
            +
            record.gold_relevance_score * 0.15
            +
            record.dollar_relevance_score * 0.15
            +
            record.geopolitical_score * 0.20
            +
            record.economic_score * 0.25
        )

        if record.news_impact_score >= 75:
            record.impact_level = (
                "MAJOR_MARKET_EVENT"
            )

        elif record.news_impact_score >= 50:
            record.impact_level = (
                "IMPORTANT_EVENT"
            )

        else:
            record.impact_level = (
                "LOW_IMPACT_EVENT"
            )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalNewsIntelligenceRecord]:

        return sorted(
            GLOBAL_NEWS_INTELLIGENCE_DATABASE.values(),
            key=lambda item:
            item.news_impact_score,
            reverse=True,
        )


GLOBAL_NEWS_INTELLIGENCE_ENGINE = (
    GlobalNewsIntelligenceEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 224
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 225
# ==========================================================

class GlobalSocialMediaMarketSignalRecord(BaseModel):
    id: str
    platform: str
    topic: str = ""
    region: str = ""
    mention_volume: int = 0
    sentiment_positive_score: float = 0.0
    sentiment_negative_score: float = 0.0
    influencer_activity_score: float = 0.0
    retail_attention_score: float = 0.0
    market_relevance_score: float = 0.0
    viral_probability_score: float = 0.0
    social_signal_strength: float = 0.0
    signal_direction: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_SOCIAL_MEDIA_SIGNAL_DATABASE: Dict[
    str,
    GlobalSocialMediaMarketSignalRecord,
] = {}


class GlobalSocialMediaMarketSignalEngine:

    def register(
        self,
        record: GlobalSocialMediaMarketSignalRecord,
    ) -> None:

        GLOBAL_SOCIAL_MEDIA_SIGNAL_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalSocialMediaMarketSignalRecord]:

        return GLOBAL_SOCIAL_MEDIA_SIGNAL_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_SOCIAL_MEDIA_SIGNAL_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        sentiment_balance = (
            record.sentiment_positive_score
            -
            record.sentiment_negative_score
        )

        mention_score = min(
            record.mention_volume
            /
            100000,
            100,
        )

        record.social_signal_strength = (
            mention_score * 0.20
            +
            sentiment_balance * 0.20
            +
            record.influencer_activity_score * 0.15
            +
            record.retail_attention_score * 0.20
            +
            record.market_relevance_score * 0.15
            +
            record.viral_probability_score * 0.10
        )

        if record.social_signal_strength >= 70:
            record.signal_direction = (
                "BULLISH_SOCIAL_SIGNAL"
            )

        elif record.social_signal_strength <= 30:
            record.signal_direction = (
                "BEARISH_SOCIAL_SIGNAL"
            )

        else:
            record.signal_direction = (
                "NEUTRAL_SOCIAL_SIGNAL"
            )

        record.analysis_text = (
            f"{record.topic}: "
            f"{record.signal_direction}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalSocialMediaMarketSignalRecord]:

        return sorted(
            GLOBAL_SOCIAL_MEDIA_SIGNAL_DATABASE.values(),
            key=lambda item:
            item.social_signal_strength,
            reverse=True,
        )


GLOBAL_SOCIAL_MEDIA_SIGNAL_ENGINE = (
    GlobalSocialMediaMarketSignalEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 225
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 226
# ==========================================================

class GlobalCommodityFlowRecord(BaseModel):
    id: str
    commodity_name: str
    commodity_type: str = ""
    producing_regions: List[str] = []
    consuming_regions: List[str] = []
    production_volume: float = 0.0
    consumption_volume: float = 0.0
    inventory_level: float = 0.0
    supply_change_score: float = 0.0
    demand_change_score: float = 0.0
    price_momentum_score: float = 0.0
    geopolitical_supply_risk_score: float = 0.0
    commodity_flow_strength: float = 0.0
    market_signal: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_COMMODITY_FLOW_DATABASE: Dict[
    str,
    GlobalCommodityFlowRecord,
] = {}


class GlobalCommodityFlowEngine:

    def register(
        self,
        record: GlobalCommodityFlowRecord,
    ) -> None:

        GLOBAL_COMMODITY_FLOW_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalCommodityFlowRecord]:

        return GLOBAL_COMMODITY_FLOW_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_COMMODITY_FLOW_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        supply_demand_balance = (
            record.demand_change_score
            -
            record.supply_change_score
        )

        inventory_pressure = max(
            0,
            100 -
            record.inventory_level
        )

        record.commodity_flow_strength = (
            supply_demand_balance * 0.25
            +
            record.price_momentum_score * 0.20
            +
            inventory_pressure * 0.15
            +
            record.geopolitical_supply_risk_score * 0.20
            +
            abs(
                record.production_volume
                -
                record.consumption_volume
            )
            *
            0.20
        )

        if record.commodity_flow_strength >= 70:
            record.market_signal = (
                "SUPPLY_STRESS_BULLISH"
            )

        elif record.commodity_flow_strength <= 30:
            record.market_signal = (
                "SUPPLY_RELIEF_BEARISH"
            )

        else:
            record.market_signal = (
                "BALANCED_COMMODITY_FLOW"
            )

        record.analysis_text = (
            f"{record.commodity_name}: "
            f"{record.market_signal}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalCommodityFlowRecord]:

        return sorted(
            GLOBAL_COMMODITY_FLOW_DATABASE.values(),
            key=lambda item:
            item.commodity_flow_strength,
            reverse=True,
        )


GLOBAL_COMMODITY_FLOW_ENGINE = (
    GlobalCommodityFlowEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 226
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 227
# ==========================================================

class GlobalEnergyFlowRecord(BaseModel):
    id: str
    energy_type: str
    producing_country: str = ""
    consuming_country: str = ""
    production_volume: float = 0.0
    consumption_volume: float = 0.0
    export_volume: float = 0.0
    import_volume: float = 0.0
    energy_price: float = 0.0
    supply_risk_score: float = 0.0
    demand_growth_score: float = 0.0
    geopolitical_risk_score: float = 0.0
    energy_security_score: float = 0.0
    energy_flow_strength: float = 0.0
    market_signal: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_ENERGY_FLOW_DATABASE: Dict[
    str,
    GlobalEnergyFlowRecord,
] = {}


class GlobalEnergyFlowEngine:

    def register(
        self,
        record: GlobalEnergyFlowRecord,
    ) -> None:

        GLOBAL_ENERGY_FLOW_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalEnergyFlowRecord]:

        return GLOBAL_ENERGY_FLOW_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_ENERGY_FLOW_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        trade_balance = (
            record.export_volume
            -
            record.import_volume
        )

        production_balance = (
            record.production_volume
            -
            record.consumption_volume
        )

        record.energy_flow_strength = (
            abs(trade_balance)
            *
            0.20
            +
            abs(production_balance)
            *
            0.20
            +
            record.energy_price
            *
            0.15
            +
            record.supply_risk_score
            *
            0.15
            +
            record.demand_growth_score
            *
            0.15
            +
            record.geopolitical_risk_score
            *
            0.10
            +
            record.energy_security_score
            *
            0.05
        )

        if record.supply_risk_score >= 70:
            record.market_signal = (
                "ENERGY_SUPPLY_RISK"
            )

        elif record.demand_growth_score >= 70:
            record.market_signal = (
                "ENERGY_DEMAND_EXPANSION"
            )

        else:
            record.market_signal = (
                "NORMAL_ENERGY_FLOW"
            )

        record.analysis_text = (
            f"{record.energy_type}: "
            f"{record.market_signal}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalEnergyFlowRecord]:

        return sorted(
            GLOBAL_ENERGY_FLOW_DATABASE.values(),
            key=lambda item:
            item.energy_flow_strength,
            reverse=True,
        )


GLOBAL_ENERGY_FLOW_ENGINE = (
    GlobalEnergyFlowEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 227
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 228
# ==========================================================

class GlobalCurrencyFlowRecord(BaseModel):
    id: str
    currency_pair: str
    base_currency: str = ""
    quote_currency: str = ""
    exchange_rate: float = 0.0
    exchange_rate_change_percent: float = 0.0
    central_bank_policy_score: float = 0.0
    interest_rate_difference_score: float = 0.0
    trade_flow_score: float = 0.0
    capital_flow_score: float = 0.0
    reserve_currency_score: float = 0.0
    currency_strength_score: float = 0.0
    market_signal: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_CURRENCY_FLOW_DATABASE: Dict[
    str,
    GlobalCurrencyFlowRecord,
] = {}


class GlobalCurrencyFlowEngine:

    def register(
        self,
        record: GlobalCurrencyFlowRecord,
    ) -> None:

        GLOBAL_CURRENCY_FLOW_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalCurrencyFlowRecord]:

        return GLOBAL_CURRENCY_FLOW_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_CURRENCY_FLOW_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.currency_strength_score = (
            record.exchange_rate_change_percent
            *
            0.15
            +
            record.central_bank_policy_score
            *
            0.20
            +
            record.interest_rate_difference_score
            *
            0.20
            +
            record.trade_flow_score
            *
            0.15
            +
            record.capital_flow_score
            *
            0.20
            +
            record.reserve_currency_score
            *
            0.10
        )

        if record.currency_strength_score >= 70:
            record.market_signal = (
                "CURRENCY_STRENGTHENING"
            )

        elif record.currency_strength_score <= 30:
            record.market_signal = (
                "CURRENCY_WEAKENING"
            )

        else:
            record.market_signal = (
                "CURRENCY_BALANCED"
            )

        record.analysis_text = (
            f"{record.currency_pair}: "
            f"{record.market_signal}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalCurrencyFlowRecord]:

        return sorted(
            GLOBAL_CURRENCY_FLOW_DATABASE.values(),
            key=lambda item:
            item.currency_strength_score,
            reverse=True,
        )


GLOBAL_CURRENCY_FLOW_ENGINE = (
    GlobalCurrencyFlowEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 228
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 229
# ==========================================================

class GlobalBondMarketFlowRecord(BaseModel):
    id: str
    country: str
    bond_type: str = ""
    yield_rate: float = 0.0
    yield_change_percent: float = 0.0
    foreign_investment_usd: float = 0.0
    domestic_demand_score: float = 0.0
    inflation_expectation_score: float = 0.0
    interest_rate_expectation_score: float = 0.0
    credit_risk_score: float = 0.0
    liquidity_score: float = 0.0
    bond_flow_strength: float = 0.0
    market_signal: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_BOND_FLOW_DATABASE: Dict[
    str,
    GlobalBondMarketFlowRecord,
] = {}


class GlobalBondMarketFlowEngine:

    def register(
        self,
        record: GlobalBondMarketFlowRecord,
    ) -> None:

        GLOBAL_BOND_FLOW_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalBondMarketFlowRecord]:

        return GLOBAL_BOND_FLOW_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_BOND_FLOW_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        foreign_flow_score = min(
            record.foreign_investment_usd
            /
            10000000000,
            100,
        )

        record.bond_flow_strength = (
            foreign_flow_score * 0.20
            +
            record.domestic_demand_score * 0.15
            +
            record.inflation_expectation_score * 0.15
            +
            record.interest_rate_expectation_score * 0.20
            +
            record.liquidity_score * 0.15
            -
            record.credit_risk_score * 0.15
        )

        if record.bond_flow_strength >= 70:
            record.market_signal = (
                "BOND_ACCUMULATION"
            )

        elif record.bond_flow_strength <= 30:
            record.market_signal = (
                "BOND_SELLING_PRESSURE"
            )

        else:
            record.market_signal = (
                "BOND_BALANCED_FLOW"
            )

        record.analysis_text = (
            f"{record.country} bond market: "
            f"{record.market_signal}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalBondMarketFlowRecord]:

        return sorted(
            GLOBAL_BOND_FLOW_DATABASE.values(),
            key=lambda item:
            item.bond_flow_strength,
            reverse=True,
        )


GLOBAL_BOND_MARKET_FLOW_ENGINE = (
    GlobalBondMarketFlowEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 229
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 230
# ==========================================================

class GlobalEquityMarketFlowRecord(BaseModel):
    id: str
    market_name: str
    country: str = ""
    index_name: str = ""
    market_cap_usd: float = 0.0
    daily_volume_usd: float = 0.0
    foreign_inflow_usd: float = 0.0
    foreign_outflow_usd: float = 0.0
    earnings_growth_score: float = 0.0
    valuation_score: float = 0.0
    liquidity_score: float = 0.0
    investor_confidence_score: float = 0.0
    equity_flow_strength: float = 0.0
    market_signal: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_EQUITY_FLOW_DATABASE: Dict[
    str,
    GlobalEquityMarketFlowRecord,
] = {}


class GlobalEquityMarketFlowEngine:

    def register(
        self,
        record: GlobalEquityMarketFlowRecord,
    ) -> None:

        GLOBAL_EQUITY_FLOW_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalEquityMarketFlowRecord]:

        return GLOBAL_EQUITY_FLOW_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_EQUITY_FLOW_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        foreign_net_flow = (
            record.foreign_inflow_usd
            -
            record.foreign_outflow_usd
        )

        market_size_score = min(
            record.market_cap_usd
            /
            1000000000000,
            100,
        )

        volume_score = min(
            record.daily_volume_usd
            /
            50000000000,
            100,
        )

        record.equity_flow_strength = (
            foreign_net_flow
            /
            10000000000
            *
            0.25
            +
            market_size_score
            *
            0.15
            +
            volume_score
            *
            0.10
            +
            record.earnings_growth_score
            *
            0.20
            +
            record.valuation_score
            *
            0.10
            +
            record.liquidity_score
            *
            0.10
            +
            record.investor_confidence_score
            *
            0.10
        )

        if record.equity_flow_strength >= 70:
            record.market_signal = (
                "EQUITY_ACCUMULATION"
            )

        elif record.equity_flow_strength <= 30:
            record.market_signal = (
                "EQUITY_DISTRIBUTION"
            )

        else:
            record.market_signal = (
                "EQUITY_NEUTRAL"
            )

        record.analysis_text = (
            f"{record.market_name}: "
            f"{record.market_signal}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalEquityMarketFlowRecord]:

        return sorted(
            GLOBAL_EQUITY_FLOW_DATABASE.values(),
            key=lambda item:
            item.equity_flow_strength,
            reverse=True,
        )


GLOBAL_EQUITY_MARKET_FLOW_ENGINE = (
    GlobalEquityMarketFlowEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 230
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 231
# ==========================================================

class GlobalMarketCapitalRotationRecord(BaseModel):
    id: str
    from_asset: str
    to_asset: str
    region: str = ""
    capital_shift_usd: float = 0.0
    shift_speed: float = 0.0
    institutional_participation_score: float = 0.0
    retail_participation_score: float = 0.0
    macro_trigger_score: float = 0.0
    risk_factor_score: float = 0.0
    rotation_strength: float = 0.0
    rotation_signal: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_CAPITAL_ROTATION_DATABASE: Dict[
    str,
    GlobalMarketCapitalRotationRecord,
] = {}


class GlobalMarketCapitalRotationEngine:

    def register(
        self,
        record: GlobalMarketCapitalRotationRecord,
    ) -> None:

        GLOBAL_CAPITAL_ROTATION_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalMarketCapitalRotationRecord]:

        return GLOBAL_CAPITAL_ROTATION_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_CAPITAL_ROTATION_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        capital_score = min(
            abs(
                record.capital_shift_usd
            )
            /
            10000000000,
            100,
        )

        record.rotation_strength = (
            capital_score * 0.30
            +
            record.shift_speed * 0.15
            +
            record.institutional_participation_score * 0.20
            +
            record.retail_participation_score * 0.10
            +
            record.macro_trigger_score * 0.20
            -
            record.risk_factor_score * 0.05
        )

        if record.capital_shift_usd > 0:
            record.rotation_signal = (
                "CAPITAL_MOVING_IN"
            )

        elif record.capital_shift_usd < 0:
            record.rotation_signal = (
                "CAPITAL_MOVING_OUT"
            )

        else:
            record.rotation_signal = (
                "NO_CAPITAL_ROTATION"
            )

        record.analysis_text = (
            f"{record.from_asset} -> "
            f"{record.to_asset}: "
            f"{record.rotation_signal}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalMarketCapitalRotationRecord]:

        return sorted(
            GLOBAL_CAPITAL_ROTATION_DATABASE.values(),
            key=lambda item:
            item.rotation_strength,
            reverse=True,
        )


GLOBAL_CAPITAL_ROTATION_ENGINE = (
    GlobalMarketCapitalRotationEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 231
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 232
# ==========================================================

class GlobalSafeHavenFlowRecord(BaseModel):
    id: str
    asset_name: str
    asset_type: str = ""
    region: str = ""
    safe_haven_demand_score: float = 0.0
    geopolitical_risk_score: float = 0.0
    financial_stress_score: float = 0.0
    currency_instability_score: float = 0.0
    investor_fear_score: float = 0.0
    capital_inflow_usd: float = 0.0
    safe_haven_strength_score: float = 0.0
    market_signal: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_SAFE_HAVEN_FLOW_DATABASE: Dict[
    str,
    GlobalSafeHavenFlowRecord,
] = {}


class GlobalSafeHavenFlowEngine:

    def register(
        self,
        record: GlobalSafeHavenFlowRecord,
    ) -> None:

        GLOBAL_SAFE_HAVEN_FLOW_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalSafeHavenFlowRecord]:

        return GLOBAL_SAFE_HAVEN_FLOW_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_SAFE_HAVEN_FLOW_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        capital_score = min(
            record.capital_inflow_usd
            /
            10000000000,
            100,
        )

        record.safe_haven_strength_score = (
            record.safe_haven_demand_score * 0.20
            +
            record.geopolitical_risk_score * 0.20
            +
            record.financial_stress_score * 0.20
            +
            record.currency_instability_score * 0.15
            +
            record.investor_fear_score * 0.15
            +
            capital_score * 0.10
        )

        if record.safe_haven_strength_score >= 70:
            record.market_signal = (
                "STRONG_SAFE_HAVEN_FLOW"
            )

        elif record.safe_haven_strength_score >= 40:
            record.market_signal = (
                "MODERATE_SAFE_HAVEN_FLOW"
            )

        else:
            record.market_signal = (
                "LOW_SAFE_HAVEN_DEMAND"
            )

        record.analysis_text = (
            f"{record.asset_name}: "
            f"{record.market_signal}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalSafeHavenFlowRecord]:

        return sorted(
            GLOBAL_SAFE_HAVEN_FLOW_DATABASE.values(),
            key=lambda item:
            item.safe_haven_strength_score,
            reverse=True,
        )


GLOBAL_SAFE_HAVEN_FLOW_ENGINE = (
    GlobalSafeHavenFlowEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 232
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 233
# ==========================================================

class GlobalInstitutionalBehaviorRecord(BaseModel):
    id: str
    institution_name: str
    institution_type: str = ""
    region: str = ""
    investment_style: str = ""
    asset_under_management_usd: float = 0.0
    risk_appetite_score: float = 0.0
    liquidity_preference_score: float = 0.0
    growth_preference_score: float = 0.0
    defensive_preference_score: float = 0.0
    recent_capital_change_usd: float = 0.0
    behavior_score: float = 0.0
    behavior_state: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_INSTITUTIONAL_BEHAVIOR_DATABASE: Dict[
    str,
    GlobalInstitutionalBehaviorRecord,
] = {}


class GlobalInstitutionalBehaviorEngine:

    def register(
        self,
        record: GlobalInstitutionalBehaviorRecord,
    ) -> None:

        GLOBAL_INSTITUTIONAL_BEHAVIOR_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalInstitutionalBehaviorRecord]:

        return GLOBAL_INSTITUTIONAL_BEHAVIOR_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_INSTITUTIONAL_BEHAVIOR_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        asset_scale_score = min(
            record.asset_under_management_usd
            /
            100000000000,
            100,
        )

        record.behavior_score = (
            asset_scale_score * 0.20
            +
            record.risk_appetite_score * 0.15
            +
            record.liquidity_preference_score * 0.15
            +
            record.growth_preference_score * 0.15
            +
            record.defensive_preference_score * 0.15
            +
            abs(
                record.recent_capital_change_usd
            )
            /
            10000000000
            *
            0.20
        )

        if (
            record.growth_preference_score
            >
            record.defensive_preference_score
        ):
            record.behavior_state = (
                "GROWTH_SEEKING"
            )

        elif (
            record.defensive_preference_score
            >
            record.growth_preference_score
        ):
            record.behavior_state = (
                "DEFENSIVE_POSITIONING"
            )

        else:
            record.behavior_state = (
                "BALANCED_POSITIONING"
            )

        record.analysis_text = (
            f"{record.institution_name}: "
            f"{record.behavior_state}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalInstitutionalBehaviorRecord]:

        return sorted(
            GLOBAL_INSTITUTIONAL_BEHAVIOR_DATABASE.values(),
            key=lambda item:
            item.behavior_score,
            reverse=True,
        )


GLOBAL_INSTITUTIONAL_BEHAVIOR_ENGINE = (
    GlobalInstitutionalBehaviorEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 233
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 234
# ==========================================================

class GlobalMarketLiquidityFlowRecord(BaseModel):
    id: str
    market_name: str
    asset_class: str = ""
    available_liquidity_usd: float = 0.0
    trading_volume_usd: float = 0.0
    bid_ask_spread_score: float = 0.0
    institutional_liquidity_score: float = 0.0
    retail_liquidity_score: float = 0.0
    central_bank_liquidity_score: float = 0.0
    liquidity_change_percent: float = 0.0
    liquidity_strength_score: float = 0.0
    liquidity_state: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_MARKET_LIQUIDITY_DATABASE: Dict[
    str,
    GlobalMarketLiquidityFlowRecord,
] = {}


class GlobalMarketLiquidityFlowEngine:

    def register(
        self,
        record: GlobalMarketLiquidityFlowRecord,
    ) -> None:

        GLOBAL_MARKET_LIQUIDITY_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalMarketLiquidityFlowRecord]:

        return GLOBAL_MARKET_LIQUIDITY_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_MARKET_LIQUIDITY_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        volume_score = min(
            record.trading_volume_usd
            /
            50000000000,
            100,
        )

        liquidity_score = min(
            record.available_liquidity_usd
            /
            100000000000,
            100,
        )

        record.liquidity_strength_score = (
            liquidity_score * 0.25
            +
            volume_score * 0.20
            +
            record.bid_ask_spread_score * 0.15
            +
            record.institutional_liquidity_score * 0.15
            +
            record.retail_liquidity_score * 0.10
            +
            record.central_bank_liquidity_score * 0.15
        )

        if record.liquidity_change_percent > 0:
            record.liquidity_state = (
                "LIQUIDITY_EXPANSION"
            )

        elif record.liquidity_change_percent < 0:
            record.liquidity_state = (
                "LIQUIDITY_CONTRACTION"
            )

        else:
            record.liquidity_state = (
                "STABLE_LIQUIDITY"
            )

        record.analysis_text = (
            f"{record.market_name}: "
            f"{record.liquidity_state}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalMarketLiquidityFlowRecord]:

        return sorted(
            GLOBAL_MARKET_LIQUIDITY_DATABASE.values(),
            key=lambda item:
            item.liquidity_strength_score,
            reverse=True,
        )


GLOBAL_MARKET_LIQUIDITY_ENGINE = (
    GlobalMarketLiquidityFlowEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 234
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 235
# ==========================================================

class GlobalMoneyFlowPredictionRecord(BaseModel):
    id: str
    source_region: str
    destination_region: str = ""
    asset_class: str = ""
    current_flow_usd: float = 0.0
    historical_pattern_score: float = 0.0
    macro_environment_score: float = 0.0
    liquidity_condition_score: float = 0.0
    investor_behavior_score: float = 0.0
    geopolitical_factor_score: float = 0.0
    predicted_flow_usd: float = 0.0
    prediction_confidence_score: float = 0.0
    prediction_direction: str = ""
    ai_explanation: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_MONEY_FLOW_PREDICTION_DATABASE: Dict[
    str,
    GlobalMoneyFlowPredictionRecord,
] = {}


class GlobalMoneyFlowPredictionEngine:

    def register(
        self,
        record: GlobalMoneyFlowPredictionRecord,
    ) -> None:

        GLOBAL_MONEY_FLOW_PREDICTION_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalMoneyFlowPredictionRecord]:

        return GLOBAL_MONEY_FLOW_PREDICTION_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_MONEY_FLOW_PREDICTION_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        prediction_factor = (
            record.historical_pattern_score * 0.20
            +
            record.macro_environment_score * 0.25
            +
            record.liquidity_condition_score * 0.20
            +
            record.investor_behavior_score * 0.15
            +
            record.geopolitical_factor_score * 0.20
        )

        record.predicted_flow_usd = (
            record.current_flow_usd
            *
            (
                1
                +
                prediction_factor
                /
                100
            )
        )

        record.prediction_confidence_score = (
            abs(
                prediction_factor
                -
                50
            )
            *
            2
        )

        if record.predicted_flow_usd > record.current_flow_usd:
            record.prediction_direction = (
                "FLOW_INCREASE_EXPECTED"
            )

        elif record.predicted_flow_usd < record.current_flow_usd:
            record.prediction_direction = (
                "FLOW_DECREASE_EXPECTED"
            )

        else:
            record.prediction_direction = (
                "FLOW_STABLE_EXPECTED"
            )

        record.ai_explanation = (
            f"Capital flow prediction: "
            f"{record.prediction_direction}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalMoneyFlowPredictionRecord]:

        return sorted(
            GLOBAL_MONEY_FLOW_PREDICTION_DATABASE.values(),
            key=lambda item:
            item.prediction_confidence_score,
            reverse=True,
        )


GLOBAL_MONEY_FLOW_PREDICTION_ENGINE = (
    GlobalMoneyFlowPredictionEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 235
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 236
# ==========================================================

class GlobalCapitalFlowAlertRecord(BaseModel):
    id: str
    alert_name: str
    region: str = ""
    asset_class: str = ""
    flow_change_usd: float = 0.0
    abnormal_flow_score: float = 0.0
    historical_deviation_score: float = 0.0
    market_pressure_score: float = 0.0
    institutional_activity_score: float = 0.0
    alert_probability_score: float = 0.0
    alert_level: str = ""
    alert_signal: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_CAPITAL_FLOW_ALERT_DATABASE: Dict[
    str,
    GlobalCapitalFlowAlertRecord,
] = {}


class GlobalCapitalFlowAlertEngine:

    def register(
        self,
        record: GlobalCapitalFlowAlertRecord,
    ) -> None:

        GLOBAL_CAPITAL_FLOW_ALERT_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalCapitalFlowAlertRecord]:

        return GLOBAL_CAPITAL_FLOW_ALERT_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_CAPITAL_FLOW_ALERT_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        flow_size_score = min(
            abs(
                record.flow_change_usd
            )
            /
            10000000000,
            100,
        )

        record.alert_probability_score = (
            flow_size_score * 0.25
            +
            record.abnormal_flow_score * 0.25
            +
            record.historical_deviation_score * 0.20
            +
            record.market_pressure_score * 0.15
            +
            record.institutional_activity_score * 0.15
        )

        if record.alert_probability_score >= 80:
            record.alert_level = (
                "EXTREME_FLOW_ALERT"
            )
            record.alert_signal = (
                "RED"
            )

        elif record.alert_probability_score >= 60:
            record.alert_level = (
                "HIGH_FLOW_ALERT"
            )
            record.alert_signal = (
                "ORANGE"
            )

        elif record.alert_probability_score >= 40:
            record.alert_level = (
                "WATCH_FLOW"
            )
            record.alert_signal = (
                "YELLOW"
            )

        else:
            record.alert_level = (
                "NORMAL_FLOW"
            )
            record.alert_signal = (
                "GREEN"
            )

        record.analysis_text = (
            f"{record.alert_name}: "
            f"{record.alert_level}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalCapitalFlowAlertRecord]:

        return sorted(
            GLOBAL_CAPITAL_FLOW_ALERT_DATABASE.values(),
            key=lambda item:
            item.alert_probability_score,
            reverse=True,
        )


GLOBAL_CAPITAL_FLOW_ALERT_ENGINE = (
    GlobalCapitalFlowAlertEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 236
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 237
# ==========================================================

class GlobalEconomicPowerIndexRecord(BaseModel):
    id: str
    country: str
    gdp_power_score: float = 0.0
    financial_power_score: float = 0.0
    technology_power_score: float = 0.0
    industrial_power_score: float = 0.0
    trade_power_score: float = 0.0
    energy_power_score: float = 0.0
    innovation_power_score: float = 0.0
    military_power_score: float = 0.0
    economic_power_index: float = 0.0
    global_rank: int = 0
    power_category: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_ECONOMIC_POWER_INDEX_DATABASE: Dict[
    str,
    GlobalEconomicPowerIndexRecord,
] = {}


class GlobalEconomicPowerIndexEngine:

    def register(
        self,
        record: GlobalEconomicPowerIndexRecord,
    ) -> None:

        GLOBAL_ECONOMIC_POWER_INDEX_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalEconomicPowerIndexRecord]:

        return GLOBAL_ECONOMIC_POWER_INDEX_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_ECONOMIC_POWER_INDEX_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.economic_power_index = (
            record.gdp_power_score * 0.20
            +
            record.financial_power_score * 0.15
            +
            record.technology_power_score * 0.15
            +
            record.industrial_power_score * 0.15
            +
            record.trade_power_score * 0.10
            +
            record.energy_power_score * 0.10
            +
            record.innovation_power_score * 0.10
            +
            record.military_power_score * 0.05
        )

        if record.economic_power_index >= 80:
            record.power_category = (
                "GLOBAL_SUPER_POWER"
            )

        elif record.economic_power_index >= 60:
            record.power_category = (
                "MAJOR_ECONOMIC_POWER"
            )

        elif record.economic_power_index >= 40:
            record.power_category = (
                "EMERGING_POWER"
            )

        else:
            record.power_category = (
                "DEVELOPING_ECONOMY"
            )

        record.analysis_text = (
            f"{record.country}: "
            f"{record.power_category}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalEconomicPowerIndexRecord]:

        return sorted(
            GLOBAL_ECONOMIC_POWER_INDEX_DATABASE.values(),
            key=lambda item:
            item.economic_power_index,
            reverse=True,
        )


GLOBAL_ECONOMIC_POWER_INDEX_ENGINE = (
    GlobalEconomicPowerIndexEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 237
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 238
# ==========================================================

class GlobalCountryAttractivenessRecord(BaseModel):
    id: str
    country: str
    investment_environment_score: float = 0.0
    political_stability_score: float = 0.0
    economic_growth_score: float = 0.0
    infrastructure_score: float = 0.0
    workforce_quality_score: float = 0.0
    technology_ecosystem_score: float = 0.0
    market_size_score: float = 0.0
    tax_environment_score: float = 0.0
    foreign_investment_score: float = 0.0
    attractiveness_index: float = 0.0
    attractiveness_level: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_COUNTRY_ATTRACTIVENESS_DATABASE: Dict[
    str,
    GlobalCountryAttractivenessRecord,
] = {}


class GlobalCountryAttractivenessEngine:

    def register(
        self,
        record: GlobalCountryAttractivenessRecord,
    ) -> None:

        GLOBAL_COUNTRY_ATTRACTIVENESS_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalCountryAttractivenessRecord]:

        return GLOBAL_COUNTRY_ATTRACTIVENESS_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_COUNTRY_ATTRACTIVENESS_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.attractiveness_index = (
            record.investment_environment_score * 0.15
            +
            record.political_stability_score * 0.10
            +
            record.economic_growth_score * 0.15
            +
            record.infrastructure_score * 0.15
            +
            record.workforce_quality_score * 0.10
            +
            record.technology_ecosystem_score * 0.10
            +
            record.market_size_score * 0.10
            +
            record.tax_environment_score * 0.05
            +
            record.foreign_investment_score * 0.10
        )

        if record.attractiveness_index >= 80:
            record.attractiveness_level = (
                "PREMIUM_INVESTMENT_DESTINATION"
            )

        elif record.attractiveness_index >= 60:
            record.attractiveness_level = (
                "ATTRACTIVE_MARKET"
            )

        elif record.attractiveness_index >= 40:
            record.attractiveness_level = (
                "MODERATE_ATTRACTIVENESS"
            )

        else:
            record.attractiveness_level = (
                "HIGH_INVESTMENT_BARRIER"
            )

        record.analysis_text = (
            f"{record.country}: "
            f"{record.attractiveness_level}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalCountryAttractivenessRecord]:

        return sorted(
            GLOBAL_COUNTRY_ATTRACTIVENESS_DATABASE.values(),
            key=lambda item:
            item.attractiveness_index,
            reverse=True,
        )


GLOBAL_COUNTRY_ATTRACTIVENESS_ENGINE = (
    GlobalCountryAttractivenessEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 238
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 239
# ==========================================================

class GlobalTradeNetworkRecord(BaseModel):
    id: str
    country: str
    export_value_usd: float = 0.0
    import_value_usd: float = 0.0
    trade_balance_usd: float = 0.0
    trading_partner_count: int = 0
    export_diversification_score: float = 0.0
    supply_chain_position_score: float = 0.0
    trade_dependency_score: float = 0.0
    global_trade_influence_score: float = 0.0
    trade_status: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_TRADE_NETWORK_DATABASE: Dict[
    str,
    GlobalTradeNetworkRecord,
] = {}


class GlobalTradeNetworkEngine:

    def register(
        self,
        record: GlobalTradeNetworkRecord,
    ) -> None:

        GLOBAL_TRADE_NETWORK_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalTradeNetworkRecord]:

        return GLOBAL_TRADE_NETWORK_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_TRADE_NETWORK_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        record.trade_balance_usd = (
            record.export_value_usd
            -
            record.import_value_usd
        )

        trade_size_score = min(
            (
                record.export_value_usd
                +
                record.import_value_usd
            )
            /
            100000000000,
            100,
        )

        partner_score = min(
            record.trading_partner_count
            /
            200,
            100,
        )

        record.global_trade_influence_score = (
            trade_size_score * 0.25
            +
            partner_score * 0.10
            +
            record.export_diversification_score * 0.20
            +
            record.supply_chain_position_score * 0.25
            +
            record.trade_dependency_score * 0.20
        )

        if record.trade_balance_usd > 0:
            record.trade_status = (
                "TRADE_SURPLUS"
            )

        elif record.trade_balance_usd < 0:
            record.trade_status = (
                "TRADE_DEFICIT"
            )

        else:
            record.trade_status = (
                "TRADE_BALANCED"
            )

        record.analysis_text = (
            f"{record.country}: "
            f"{record.trade_status}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalTradeNetworkRecord]:

        return sorted(
            GLOBAL_TRADE_NETWORK_DATABASE.values(),
            key=lambda item:
            item.global_trade_influence_score,
            reverse=True,
        )


GLOBAL_TRADE_NETWORK_ENGINE = (
    GlobalTradeNetworkEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 239
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 240
# ==========================================================

class GlobalForeignInvestmentFlowRecord(BaseModel):
    id: str
    country: str
    investment_type: str = ""
    foreign_direct_investment_usd: float = 0.0
    portfolio_investment_usd: float = 0.0
    technology_transfer_score: float = 0.0
    investor_confidence_score: float = 0.0
    regulatory_quality_score: float = 0.0
    economic_growth_expectation_score: float = 0.0
    geopolitical_risk_score: float = 0.0
    investment_flow_strength: float = 0.0
    investment_signal: str = ""
    analysis_text: str = ""
    calculated_time: Optional[datetime] = None
    source: str = ""
    status: DataStatus = DataStatus.WAITING
    updated_at: Optional[datetime] = None


GLOBAL_FOREIGN_INVESTMENT_FLOW_DATABASE: Dict[
    str,
    GlobalForeignInvestmentFlowRecord,
] = {}


class GlobalForeignInvestmentFlowEngine:

    def register(
        self,
        record: GlobalForeignInvestmentFlowRecord,
    ) -> None:

        GLOBAL_FOREIGN_INVESTMENT_FLOW_DATABASE[
            record.id
        ] = record

    def get(
        self,
        record_id: str,
    ) -> Optional[GlobalForeignInvestmentFlowRecord]:

        return GLOBAL_FOREIGN_INVESTMENT_FLOW_DATABASE.get(
            record_id
        )

    def remove(
        self,
        record_id: str,
    ) -> None:

        GLOBAL_FOREIGN_INVESTMENT_FLOW_DATABASE.pop(
            record_id,
            None,
        )

    def calculate(
        self,
        record_id: str,
    ) -> None:

        record = self.get(record_id)

        if record is None:
            return

        fdi_score = min(
            record.foreign_direct_investment_usd
            /
            10000000000,
            100,
        )

        portfolio_score = min(
            record.portfolio_investment_usd
            /
            5000000000,
            100,
        )

        record.investment_flow_strength = (
            fdi_score * 0.25
            +
            portfolio_score * 0.15
            +
            record.technology_transfer_score * 0.15
            +
            record.investor_confidence_score * 0.20
            +
            record.regulatory_quality_score * 0.10
            +
            record.economic_growth_expectation_score * 0.10
            -
            record.geopolitical_risk_score * 0.05
        )

        if record.investment_flow_strength >= 70:
            record.investment_signal = (
                "STRONG_FOREIGN_CAPITAL_INFLOW"
            )

        elif record.investment_flow_strength >= 40:
            record.investment_signal = (
                "MODERATE_FOREIGN_INVESTMENT"
            )

        else:
            record.investment_signal = (
                "WEAK_INVESTMENT_FLOW"
            )

        record.analysis_text = (
            f"{record.country}: "
            f"{record.investment_signal}"
        )

        record.calculated_time = utc_now()
        record.updated_at = utc_now()
        record.status = DataStatus.REALTIME

    def ranking(
        self,
    ) -> List[GlobalForeignInvestmentFlowRecord]:

        return sorted(
            GLOBAL_FOREIGN_INVESTMENT_FLOW_DATABASE.values(),
            key=lambda item:
            item.investment_flow_strength,
            reverse=True,
        )


GLOBAL_FOREIGN_INVESTMENT_FLOW_ENGINE = (
    GlobalForeignInvestmentFlowEngine()
)

# ==========================================================
# KẾT THÚC ĐOẠN 240
# ==========================================================
