# ==========================================================
# WEOS
# PHẦN 001
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pydeck as pdk
import requests

# ==========================================================
# CẤU HÌNH TRANG
# ==========================================================

st.set_page_config(
    page_title="WEOS - World Economic Observation System",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================================
# HẰNG SỐ TOÀN CỤC
# ==========================================================

APP_NAME = "WEOS"
APP_VERSION = "1.0.0"
APP_SUBTITLE = "World Economic Observation System"

COLOR_BACKGROUND = "#05070D"
COLOR_PANEL = "#111827"
COLOR_TEXT = "#FFFFFF"
COLOR_GREEN = "#00FF88"
COLOR_RED = "#FF4D4D"
COLOR_BLUE = "#4DA6FF"
COLOR_BORDER = "#222222"

# ==========================================================
# KHỞI TẠO SESSION STATE
# ==========================================================

if "map_mode" not in st.session_state:
    st.session_state.map_mode = "globe"

if "selected_node" not in st.session_state:
    st.session_state.selected_node = None

if "search_keyword" not in st.session_state:
    st.session_state.search_keyword = ""

# ==========================================================
# CSS TOÀN HỆ THỐNG
# ==========================================================

st.markdown(
    f"""
    <style>

    .stApp {{
        background-color: {COLOR_BACKGROUND};
        color: {COLOR_TEXT};
    }}

    header {{
        visibility: hidden;
    }}

    footer {{
        visibility: hidden;
    }}

    #MainMenu {{
        visibility: hidden;
    }}

    .block-container {{
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        padding-bottom: 1rem;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================================
# KẾT THÚC 001
# ==========================================================
# ==========================================================
# WEOS
# PHẦN 002
# ==========================================================

# ==========================================================
# HEADER
# ==========================================================

col_logo, col_search, col_mode = st.columns([2, 8, 1])

with col_logo:

    st.markdown(
        f"""
        <h2 style="
            color:{COLOR_TEXT};
            margin:0;
            padding:0;
            font-weight:700;
        ">
            🌍 {APP_NAME}
        </h2>

        <div style="
            color:#9CA3AF;
            font-size:14px;
            margin-top:-4px;
        ">
            {APP_SUBTITLE}
        </div>
        """,
        unsafe_allow_html=True
    )

with col_search:

    keyword = st.text_input(
        label="",
        value=st.session_state.search_keyword,
        placeholder="Tìm quốc gia, thành phố, công ty, ngân hàng, ETF...",
        label_visibility="collapsed"
    )

    st.session_state.search_keyword = keyword

with col_mode:

    if st.session_state.map_mode == "globe":

        if st.button(
            "🌍",
            use_container_width=True,
            help="Chuyển sang bản đồ phẳng"
        ):
            st.session_state.map_mode = "map"
            st.rerun()

    else:

        if st.button(
            "🗺️",
            use_container_width=True,
            help="Chuyển sang quả địa cầu"
        ):
            st.session_state.map_mode = "globe"
            st.rerun()

st.divider()

# ==========================================================
# KHU VỰC BẢN ĐỒ CHÍNH
# ==========================================================

map_container = st.container(border=False)

# ==========================================================
# PANEL THÔNG TIN NODE
# ==========================================================

info_panel = st.container(border=False)

# ==========================================================
# CHÚ GIẢI
# ==========================================================

legend_container = st.container(border=False)

# ==========================================================
# KẾT THÚC 002
# ==========================================================
# ==========================================================
# WEOS
# PHẦN 003
# ==========================================================

# ==========================================================
# HÀM TẠO QUẢ ĐỊA CẦU
# ==========================================================

def create_globe():

    figure = go.Figure()

    figure.update_layout(

        paper_bgcolor=COLOR_BACKGROUND,
        plot_bgcolor=COLOR_BACKGROUND,

        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0
        ),

        height=760,

        geo=dict(

            projection_type="orthographic",

            showland=True,
            landcolor="#16202B",

            showocean=True,
            oceancolor="#05070D",

            showcountries=True,
            countrycolor="#555555",

            showcoastlines=True,
            coastlinecolor="#888888",

            showlakes=False,
            showrivers=False,

            showframe=False,

            bgcolor=COLOR_BACKGROUND,

            lataxis=dict(showgrid=False),
            lonaxis=dict(showgrid=False)
        )
    )

    return figure


# ==========================================================
# HIỂN THỊ BẢN ĐỒ
# ==========================================================

with map_container:

    if st.session_state.map_mode == "globe":

        globe = create_globe()

        st.plotly_chart(
            globe,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "scrollZoom": True
            }
        )

    else:

        st.info("Chế độ bản đồ phẳng sẽ được bổ sung ở các phần tiếp theo.")


# ==========================================================
# PANEL THÔNG TIN
# ==========================================================

with info_panel:

    st.markdown("### Thông tin")

    st.info(
        "Chưa có node nào được chọn."
    )


# ==========================================================
# KẾT THÚC 003
# ==========================================================
# ==========================================================
# WEOS
# PHẦN 004
# ==========================================================

# ==========================================================
# DỮ LIỆU NODE MẶC ĐỊNH
# ==========================================================

WORLD_NODES = pd.DataFrame(
    [
        {
            "id": "FED",
            "name": "Federal Reserve",
            "type": "Ngân hàng Trung ương",
            "country": "Hoa Kỳ",
            "lat": 38.8977,
            "lon": -77.0365,
            "color": COLOR_GREEN,
            "size": 10
        },
        {
            "id": "ECB",
            "name": "European Central Bank",
            "type": "Ngân hàng Trung ương",
            "country": "Đức",
            "lat": 50.1109,
            "lon": 8.6821,
            "color": COLOR_GREEN,
            "size": 10
        },
        {
            "id": "PBOC",
            "name": "People's Bank of China",
            "type": "Ngân hàng Trung ương",
            "country": "Trung Quốc",
            "lat": 39.9042,
            "lon": 116.4074,
            "color": COLOR_GREEN,
            "size": 10
        }
    ]
)

# ==========================================================
# THÊM NODE LÊN QUẢ ĐỊA CẦU
# ==========================================================

def add_nodes_to_globe(figure, nodes):

    figure.add_trace(

        go.Scattergeo(

            lon=nodes["lon"],
            lat=nodes["lat"],

            mode="markers",

            text=nodes["name"],

            hovertemplate=
            "<b>%{text}</b><extra></extra>",

            marker=dict(
                size=nodes["size"],
                color=nodes["color"],
                line=dict(
                    width=1,
                    color="#FFFFFF"
                )
            )

        )

    )

    return figure


# ==========================================================
# CẬP NHẬT HIỂN THỊ
# ==========================================================

with map_container:

    if st.session_state.map_mode == "globe":

        globe = create_globe()

        globe = add_nodes_to_globe(
            globe,
            WORLD_NODES
        )

        st.plotly_chart(
            globe,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "scrollZoom": True
            }
        )

    else:

        st.info("Chế độ bản đồ phẳng sẽ được bổ sung ở các phần tiếp theo.")

# ==========================================================
# KẾT THÚC 004
# ==========================================================
# ==========================================================
# WEOS
# PHẦN 005
# ==========================================================

# ==========================================================
# DỮ LIỆU FLOW MẶC ĐỊNH
# ==========================================================

WORLD_FLOWS = [
    {
        "id": "FLOW_001",
        "from": "FED",
        "to": "ECB",
        "color": COLOR_GREEN
    },
    {
        "id": "FLOW_002",
        "from": "ECB",
        "to": "PBOC",
        "color": COLOR_GREEN
    }
]

# ==========================================================
# VẼ CÁC KẾT NỐI
# ==========================================================

def add_flows_to_globe(
    figure,
    nodes,
    flows
):

    lookup = (
        nodes
        .set_index("id")
        .to_dict("index")
    )

    for flow in flows:

        start = lookup.get(flow["from"])
        end = lookup.get(flow["to"])

        if start is None or end is None:
            continue

        figure.add_trace(

            go.Scattergeo(

                lon=[
                    start["lon"],
                    end["lon"]
                ],

                lat=[
                    start["lat"],
                    end["lat"]
                ],

                mode="lines",

                hoverinfo="skip",

                line=dict(
                    color=flow["color"],
                    width=2
                ),

                opacity=0.7,

                showlegend=False

            )

        )

    return figure

# ==========================================================
# CẬP NHẬT HIỂN THỊ
# ==========================================================

with map_container:

    if st.session_state.map_mode == "globe":

        globe = create_globe()

        globe = add_flows_to_globe(
            globe,
            WORLD_NODES,
            WORLD_FLOWS
        )

        globe = add_nodes_to_globe(
            globe,
            WORLD_NODES
        )

        st.plotly_chart(
            globe,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "scrollZoom": True
            }
        )

    else:

        st.info(
            "Chế độ bản đồ phẳng sẽ được bổ sung ở các phần tiếp theo."
        )

# ==========================================================
# KẾT THÚC 005
# ==========================================================
# ==========================================================
# WEOS
# PHẦN 006
# ==========================================================

# ==========================================================
# CHÚ GIẢI (LEGEND)
# ==========================================================

with legend_container:

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div style="
                display:flex;
                align-items:center;
                gap:8px;
            ">
                <div style="
                    width:14px;
                    height:14px;
                    border-radius:50%;
                    background:{COLOR_GREEN};
                "></div>

                <span style="color:{COLOR_TEXT};">
                    Dòng tiền vào
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style="
                display:flex;
                align-items:center;
                gap:8px;
            ">
                <div style="
                    width:14px;
                    height:14px;
                    border-radius:50%;
                    background:{COLOR_RED};
                "></div>

                <span style="color:{COLOR_TEXT};">
                    Dòng tiền ra
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div style="
                display:flex;
                align-items:center;
                gap:8px;
            ">
                <div style="
                    width:18px;
                    height:2px;
                    background:{COLOR_GREEN};
                "></div>

                <span style="color:{COLOR_TEXT};">
                    Flow kinh tế
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div style="
                color:#9CA3AF;
                text-align:right;
            ">
                WEOS {APP_VERSION}
            </div>
            """,
            unsafe_allow_html=True)

# ==========================================================
# THANH TRẠNG THÁI
# ==========================================================

st.caption(
    "🟢 Hệ thống đã khởi tạo thành công | "
    "Node: {} | "
    "Flow: {} | "
    "Chế độ: {}".format(
        len(WORLD_NODES),
        len(WORLD_FLOWS),
        "Quả địa cầu"
        if st.session_state.map_mode == "globe"
        else "Bản đồ"
    )
)

# ==========================================================
# KẾT THÚC 006
# ==========================================================
# ==========================================================
# WEOS
# PHẦN 007
# ==========================================================

# ==========================================================
# HÀM TÌM KIẾM NODE
# ==========================================================

def filter_nodes(nodes, keyword):

    keyword = keyword.strip().lower()

    if keyword == "":
        return nodes

    mask = (
        nodes["name"].str.lower().str.contains(keyword)
        |
        nodes["country"].str.lower().str.contains(keyword)
        |
        nodes["type"].str.lower().str.contains(keyword)
    )

    return nodes.loc[mask].reset_index(drop=True)


# ==========================================================
# LỌC DỮ LIỆU
# ==========================================================

VISIBLE_NODES = filter_nodes(
    WORLD_NODES,
    st.session_state.search_keyword
)

VISIBLE_NODE_IDS = set(
    VISIBLE_NODES["id"]
)

VISIBLE_FLOWS = [

    flow

    for flow in WORLD_FLOWS

    if (
        flow["from"] in VISIBLE_NODE_IDS
        and
        flow["to"] in VISIBLE_NODE_IDS
    )

]


# ==========================================================
# HIỂN THỊ BẢN ĐỒ
# ==========================================================

with map_container:

    if st.session_state.map_mode == "globe":

        globe = create_globe()

        globe = add_flows_to_globe(
            globe,
            VISIBLE_NODES,
            VISIBLE_FLOWS
        )

        globe = add_nodes_to_globe(
            globe,
            VISIBLE_NODES
        )

        st.plotly_chart(
            globe,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "scrollZoom": True
            }
        )

    else:

        st.info(
            "Chế độ bản đồ phẳng sẽ được bổ sung ở các phần tiếp theo."
        )


# ==========================================================
# CẬP NHẬT THANH TRẠNG THÁI
# ==========================================================

st.caption(
    "🟢 Hiển thị: {} Node | {} Flow".format(
        len(VISIBLE_NODES),
        len(VISIBLE_FLOWS)
    )
)

# ==========================================================
# KẾT THÚC 007
# ==========================================================
# ==========================================================
# WEOS
# PHẦN 008
# ==========================================================

# ==========================================================
# DỮ LIỆU CHỌN NODE
# ==========================================================

def get_node_by_id(
    nodes,
    node_id
):

    result = nodes.loc[
        nodes["id"] == node_id
    ]

    if result.empty:
        return None

    return result.iloc[0]


# ==========================================================
# TỰ ĐỘNG CHỌN NODE
# ==========================================================

if (
    st.session_state.selected_node is None
    and
    len(VISIBLE_NODES) > 0
):

    st.session_state.selected_node = (
        VISIBLE_NODES.iloc[0]["id"]
    )

elif (
    st.session_state.selected_node
    not in
    VISIBLE_NODE_IDS
):

    if len(VISIBLE_NODES) > 0:

        st.session_state.selected_node = (
            VISIBLE_NODES.iloc[0]["id"]
        )

    else:

        st.session_state.selected_node = None


# ==========================================================
# PANEL THÔNG TIN NODE
# ==========================================================

with info_panel:

    st.markdown("### Thông tin Node")

    if st.session_state.selected_node is None:

        st.info("Không có dữ liệu.")

    else:

        node = get_node_by_id(
            WORLD_NODES,
            st.session_state.selected_node
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Tên",
                node["name"]
            )

            st.metric(
                "Loại",
                node["type"]
            )

        with col2:

            st.metric(
                "Quốc gia",
                node["country"]
            )

            st.metric(
                "ID",
                node["id"]
            )

        st.markdown("---")

        st.markdown(
            "**Dòng tiền vào:** REAL DATA REQUIRED"
        )

        st.markdown(
            "**Dòng tiền ra:** REAL DATA REQUIRED"
        )

        st.markdown(
            "**Dòng tiền ròng:** REAL DATA REQUIRED"
        )

        st.markdown(
            "**Cập nhật lần cuối:** WAITING REAL DATA"
        )

        st.markdown(
            "**Nguồn dữ liệu:** WAITING REAL DATA"
        )

# ==========================================================
# KẾT THÚC 008
# ==========================================================
# ==========================================================
# WEOS
# PHẦN 009
# ==========================================================

# ==========================================================
# THỐNG KÊ HỆ THỐNG
# ==========================================================

def build_system_statistics(
    nodes,
    flows
):

    return {

        "total_nodes": len(nodes),

        "total_flows": len(flows),

        "countries": nodes["country"].nunique(),

        "node_types": nodes["type"].nunique()

    }


SYSTEM_STATISTICS = build_system_statistics(
    WORLD_NODES,
    WORLD_FLOWS
)

# ==========================================================
# SIDEBAR THÔNG TIN HỆ THỐNG
# ==========================================================

with st.sidebar:

    st.markdown("## WEOS")

    st.markdown(
        f"**Phiên bản:** {APP_VERSION}"
    )

    st.markdown("---")

    st.metric(
        "Tổng Node",
        SYSTEM_STATISTICS["total_nodes"]
    )

    st.metric(
        "Tổng Flow",
        SYSTEM_STATISTICS["total_flows"]
    )

    st.metric(
        "Quốc gia",
        SYSTEM_STATISTICS["countries"]
    )

    st.metric(
        "Loại Node",
        SYSTEM_STATISTICS["node_types"]
    )

    st.markdown("---")

    st.success(
        "Hệ thống hoạt động bình thường."
    )

# ==========================================================
# KIỂM TRA DỮ LIỆU
# ==========================================================

if WORLD_NODES.empty:

    st.error(
        "Không có dữ liệu Node."
    )

    st.stop()

if len(WORLD_FLOWS) == 0:

    st.warning(
        "Chưa có dữ liệu Flow."
    )

# ==========================================================
# KẾT THÚC 009
# ==========================================================
