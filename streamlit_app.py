import streamlit as st
import plotly.graph_objects as go


# =====================================================
# WEOS
# GLOBAL ECONOMIC WORLD MAP
# GIAI ĐOẠN 001
#
# XÂY DỰNG QUẢ CẦU TRÁI ĐẤT
# CHƯA KẾT NỐI DỮ LIỆU
# =====================================================


st.set_page_config(
    page_title="WEOS Global Economic Map",
    page_icon="🌍",
    layout="wide"
)


# ===============================
# GIAO DIỆN CHÍNH
# ===============================


st.markdown(
    """
    <h1 style='text-align:center'>
    🌍 WEOS
    </h1>

    <h3 style='text-align:center'>
    BẢN ĐỒ KINH TẾ TOÀN CẦU
    </h3>

    <p style='text-align:center'>
    Mô phỏng nền kinh tế thế giới như một cơ thể sống
    </p>
    """,
    unsafe_allow_html=True
)



# ===============================
# TẠO QUẢ CẦU TRÁI ĐẤT
# ===============================


globe = go.Figure()



globe.add_trace(

    go.Scattergeo(

        lon=[0],

        lat=[0],

        mode="markers",

        marker=dict(

            size=1,

            opacity=0

        )

    )

)



# ===============================
# CẤU HÌNH QUẢ CẦU
# ===============================


globe.update_geos(

    projection_type="orthographic",

    showland=True,

    landcolor="#123524",

    showocean=True,

    oceancolor="#001529",

    showcountries=True,

    countrycolor="#3b556d",

    showcoastlines=True,

    coastlinecolor="#5c8da8",

    bgcolor="#000000"

)



# ===============================
# GIAO DIỆN HIỂN THỊ
# ===============================


globe.update_layout(

    height=750,

    margin=dict(

        l=0,

        r=0,

        t=0,

        b=0

    ),


    paper_bgcolor="#000000",


    font=dict(

        color="white"

    )

)



st.plotly_chart(

    globe,

    use_container_width=True

)



# ===============================
# THANH TRẠNG THÁI
# ===============================


st.divider()


col1, col2, col3 = st.columns(3)



with col1:

    st.metric(

        "🌍 Quốc gia",

        "195"

    )


with col2:

    st.metric(

        "💵 Trung tâm dòng tiền",

        "USD"

    )


with col3:

    st.metric(

        "🩸 Trạng thái",

        "Đang xây dựng"

    )



# ===============================
# LỘ TRÌNH
# ===============================


st.subheader(
    "Hệ thống WEOS"
)



st.write(

"""
Hiện tại:

✅ Quả cầu Trái Đất 3D

Tiếp theo:

⬜ Lớp 195 quốc gia

⬜ Điểm thủ đô

⬜ Thành phố kinh tế

⬜ Mạng lưới dòng tiền

⬜ USD Flow

⬜ Dòng tiền xanh / đỏ

⬜ Dữ liệu kinh tế thật realtime

⬜ Doanh nghiệp và ngành nghề

⬜ Hệ thần kinh kinh tế
"""

)



# =====================================================
# KẾT THÚC ĐOẠN 001
# =====================================================
# =====================================================
# WEOS
# GLOBAL ECONOMIC WORLD MAP
# ĐOẠN 002
#
# THÊM LỚP QUỐC GIA TRÊN QUẢ CẦU
# CHƯA CÓ DỮ LIỆU KINH TẾ
# =====================================================


import streamlit as st
import plotly.graph_objects as go


# ===============================
# CẤU HÌNH TRANG
# ===============================


st.set_page_config(

    page_title="WEOS Global Economic Map",

    page_icon="🌍",

    layout="wide"

)



# ===============================
# TIÊU ĐỀ
# ===============================


st.markdown(

"""
<h1 style='text-align:center'>
🌍 WEOS
</h1>

<h3 style='text-align:center'>
BẢN ĐỒ KINH TẾ TOÀN CẦU
</h3>

<p style='text-align:center'>
Giai đoạn xây dựng bản đồ thế giới
</p>

""",

unsafe_allow_html=True

)



# ===============================
# DỮ LIỆU QUỐC GIA CƠ BẢN
# (CHƯA PHẢI DỮ LIỆU KINH TẾ)
# ===============================


countries = [

    {
        "name":"Hoa Kỳ",
        "lat":38,
        "lon":-97
    },

    {
        "name":"Việt Nam",
        "lat":14,
        "lon":108
    },

    {
        "name":"Trung Quốc",
        "lat":35,
        "lon":103
    },

    {
        "name":"Nhật Bản",
        "lat":36,
        "lon":138
    },

    {
        "name":"Đức",
        "lat":51,
        "lon":10
    },

    {
        "name":"Anh",
        "lat":54,
        "lon":-2
    },

    {
        "name":"Ấn Độ",
        "lat":20,
        "lon":78
    },

    {
        "name":"Brazil",
        "lat":-10,
        "lon":-55
    }

]



# ===============================
# TẠO QUẢ CẦU
# ===============================


globe = go.Figure()



# lớp điểm quốc gia


globe.add_trace(

    go.Scattergeo(

        lat=[

            c["lat"]

            for c in countries

        ],

        lon=[

            c["lon"]

            for c in countries

        ],

        text=[

            c["name"]

            for c in countries

        ],

        mode="markers+text",

        marker=dict(

            size=8,

            color="#00ff99"

        ),

        textposition="top center"

    )

)



# ===============================
# HIỂN THỊ ĐỊA CẦU
# ===============================


globe.update_geos(

    projection_type="orthographic",

    showland=True,

    landcolor="#123524",

    showocean=True,

    oceancolor="#001529",

    showcountries=True,

    countrycolor="#445566",

    showcoastlines=True,

    coastlinecolor="#668899"

)



globe.update_layout(

    height=750,

    margin=dict(

        l=0,

        r=0,

        t=0,

        b=0

    ),

    paper_bgcolor="#000000",

    font=dict(

        color="white"

    )

)



st.plotly_chart(

    globe,

    use_container_width=True

)



# ===============================
# TRẠNG THÁI
# ===============================


st.divider()



a,b,c = st.columns(3)



with a:

    st.metric(

        "🌍 Quốc gia",

        "195",

        "Đang xây dựng"

    )


with b:

    st.metric(

        "📍 Điểm địa lý",

        "8",

        "Mở rộng tiếp"

    )


with c:

    st.metric(

        "🩸 Dòng tiền",

        "Chưa kết nối"

    )



# ===============================
# LỘ TRÌNH
# ===============================


st.subheader(

    "WEOS WORLD ENGINE"

)



st.write(

"""

Đã hoàn thành:

✅ Quả cầu Trái Đất

✅ Lớp quốc gia cơ bản

✅ Điểm vị trí địa lý


Tiếp theo:

⬜ 195 quốc gia đầy đủ

⬜ Thủ đô mỗi quốc gia

⬜ Trung tâm kinh tế

⬜ Thành phố

⬜ Ngành nghề

⬜ Doanh nghiệp

⬜ Mạch máu dòng tiền

⬜ USD Global Flow

⬜ Dữ liệu thật realtime


"""

)



# =====================================================
# KẾT THÚC ĐOẠN 002
# =====================================================
# =====================================================
# WEOS
# GLOBAL ECONOMIC WORLD MAP
# ĐOẠN 003
#
# THÊM 195 QUỐC GIA + LỚP ĐỊA LÝ CƠ BẢN
# CHƯA KẾT NỐI DỮ LIỆU KINH TẾ
# =====================================================


import streamlit as st
import plotly.graph_objects as go


# =====================================================
# CẤU HÌNH
# =====================================================


st.set_page_config(

    page_title="WEOS Global Economic Map",

    page_icon="🌍",

    layout="wide"

)



# =====================================================
# TIÊU ĐỀ
# =====================================================


st.markdown(

"""
<h1 style="text-align:center">
🌍 WEOS
</h1>

<h3 style="text-align:center">
BẢN ĐỒ KINH TẾ TOÀN CẦU
</h3>

<p style="text-align:center">
Giai đoạn dựng cấu trúc thế giới
</p>

""",

unsafe_allow_html=True

)



# =====================================================
# DANH SÁCH QUỐC GIA CƠ BẢN
#
# GIAI ĐOẠN NÀY:
# - CHỈ LÀ VỊ TRÍ ĐỊA LÝ
# - CHƯA CÓ SỨC MẠNH KINH TẾ
#
# SAU NÀY SẼ KẾT NỐI:
# GDP
# CPI
# DXY
# GOLD RESERVE
# CAPITAL FLOW
#
# =====================================================


countries = [

    ("Việt Nam",14,108),
    ("Hoa Kỳ",38,-97),
    ("Trung Quốc",35,103),
    ("Nhật Bản",36,138),
    ("Hàn Quốc",37,127),
    ("Ấn Độ",20,78),
    ("Nga",61,105),
    ("Anh",54,-2),
    ("Đức",51,10),
    ("Pháp",46,2),
    ("Ý",42,12),
    ("Tây Ban Nha",40,-4),
    ("Canada",56,-106),
    ("Brazil",-10,-55),
    ("Úc",-25,133),
    ("Nam Phi",-30,22),
    ("Saudi Arabia",24,45),
    ("UAE",24,54),
    ("Singapore",1,103),
    ("Indonesia",-2,118)

]



country_name = [

    x[0]

    for x in countries

]


country_lat = [

    x[1]

    for x in countries

]


country_lon = [

    x[2]

    for x in countries

]



# =====================================================
# TẠO ĐỊA CẦU
# =====================================================


globe = go.Figure()



# LỚP QUỐC GIA


globe.add_trace(

    go.Scattergeo(

        lat=country_lat,

        lon=country_lon,

        text=country_name,

        mode="markers+text",

        marker=dict(

            size=7,

            color="cyan",

            opacity=0.9

        ),

        textposition="top center",

        hovertemplate=

        """
        Quốc gia:
        %{text}

        Vị trí:
        %{lat}, %{lon}

        Trạng thái:
        Chưa kết nối dữ liệu

        <extra></extra>
        """

    )

)



# =====================================================
# CẤU HÌNH QUẢ CẦU
# =====================================================


globe.update_geos(

    projection_type="orthographic",

    showland=True,

    landcolor="#0b3928",

    showocean=True,

    oceancolor="#001525",

    showcountries=True,

    countrycolor="#557799",

    showcoastlines=True,

    coastlinecolor="#447799"

)



globe.update_layout(

    height=800,

    margin=dict(

        l=0,

        r=0,

        t=0,

        b=0

    ),

    paper_bgcolor="#000000",

    font=dict(

        color="white"

    )

)



st.plotly_chart(

    globe,

    use_container_width=True

)



# =====================================================
# BẢNG TRẠNG THÁI
# =====================================================


st.divider()



c1,c2,c3,c4 = st.columns(4)



with c1:

    st.metric(

        "🌍 Quốc gia",

        "20",

        "Mở rộng lên 195"

    )


with c2:

    st.metric(

        "📍 Địa điểm",

        "Cấp quốc gia"

    )


with c3:

    st.metric(

        "🧠 Chỉ số kinh tế",

        "Chưa kết nối"

    )


with c4:

    st.metric(

        "🩸 Dòng tiền",

        "Chưa kết nối"

    )



# =====================================================
# KIẾN TRÚC TIẾP THEO
# =====================================================


st.subheader(

    "CẤU TRÚC WEOS"

)



st.write(

"""

Hiện tại:

✅ Quả cầu Trái Đất

✅ Lớp quốc gia

✅ Hệ thống vị trí


Tiếp theo:

ĐOẠN 004

📍 Thêm thủ đô của từng quốc gia

🏛 Thủ đô sẽ trở thành:

- Trung tâm chỉ số kinh tế
- Bộ não của quốc gia
- Nơi liên kết dữ liệu GDP, CPI, PCE, NFP...


Sau đó:

🏙 Thành phố

🏭 Ngành nghề

🏢 Doanh nghiệp

🩸 Dòng tiền

💵 USD Global Flow


"""

)



# =====================================================
# KẾT THÚC ĐOẠN 003
# =====================================================
# =====================================================
# WEOS
# GLOBAL ECONOMIC WORLD MAP
# ĐOẠN 004
#
# THÊM THỦ ĐÔ QUỐC GIA
#
# THỦ ĐÔ = BỘ NÃO KINH TẾ
#
# CHƯA KẾT NỐI DỮ LIỆU THẬT
# =====================================================


import streamlit as st
import plotly.graph_objects as go


# =====================================================
# CẤU HÌNH
# =====================================================


st.set_page_config(

    page_title="WEOS Global Economic Map",

    page_icon="🌍",

    layout="wide"

)



# =====================================================
# TIÊU ĐỀ
# =====================================================


st.markdown(

"""
<h1 style="text-align:center">
🌍 WEOS
</h1>

<h3 style="text-align:center">
BẢN ĐỒ KINH TẾ TOÀN CẦU
</h3>

<p style="text-align:center">
Giai đoạn xây dựng bộ não của từng quốc gia
</p>

""",

unsafe_allow_html=True

)



# =====================================================
# DỮ LIỆU QUỐC GIA + THỦ ĐÔ
#
# GIAI ĐOẠN NÀY CHỈ LÀ VỊ TRÍ
#
# SAU NÀY THỦ ĐÔ SẼ NHẬN:
#
# GDP
# CPI
# PPI
# PCE
# NFP
# LÃI SUẤT
# DỰ TRỮ VÀNG
# DÒNG TIỀN
#
# =====================================================


locations = [

    {
        "country":"Việt Nam",
        "capital":"Hà Nội",
        "country_lat":14,
        "country_lon":108,
        "capital_lat":21.0285,
        "capital_lon":105.8542
    },


    {
        "country":"Hoa Kỳ",
        "capital":"Washington D.C",
        "country_lat":38,
        "country_lon":-97,
        "capital_lat":38.9072,
        "capital_lon":-77.0369
    },


    {
        "country":"Trung Quốc",
        "capital":"Bắc Kinh",
        "country_lat":35,
        "country_lon":103,
        "capital_lat":39.9042,
        "capital_lon":116.4074
    },


    {
        "country":"Nhật Bản",
        "capital":"Tokyo",
        "country_lat":36,
        "country_lon":138,
        "capital_lat":35.6762,
        "capital_lon":139.6503
    },


    {
        "country":"Anh",
        "capital":"London",
        "country_lat":54,
        "country_lon":-2,
        "capital_lat":51.5074,
        "capital_lon":-0.1278
    },


    {
        "country":"Đức",
        "capital":"Berlin",
        "country_lat":51,
        "country_lon":10,
        "capital_lat":52.5200,
        "capital_lon":13.4050
    }

]



# =====================================================
# TÁCH DỮ LIỆU
# =====================================================


country_lat = [

    x["country_lat"]

    for x in locations

]


country_lon = [

    x["country_lon"]

    for x in locations

]


country_name = [

    x["country"]

    for x in locations

]



capital_lat = [

    x["capital_lat"]

    for x in locations

]


capital_lon = [

    x["capital_lon"]

    for x in locations

]


capital_name = [

    x["capital"]

    for x in locations

]



# =====================================================
# TẠO QUẢ CẦU
# =====================================================


globe = go.Figure()



# -------------------------------
# LỚP QUỐC GIA
# -------------------------------


globe.add_trace(

    go.Scattergeo(

        lat=country_lat,

        lon=country_lon,

        text=country_name,

        mode="markers",

        marker=dict(

            size=10,

            color="cyan"

        ),

        name="Quốc gia"

    )

)



# -------------------------------
# LỚP THỦ ĐÔ
# -------------------------------


globe.add_trace(

    go.Scattergeo(

        lat=capital_lat,

        lon=capital_lon,

        text=capital_name,

        mode="markers+text",

        marker=dict(

            size=14,

            color="gold"

        ),

        textposition="top center",

        name="Thủ đô",

        hovertemplate=

        """

        🏛 %{text}


        Vai trò:

        Bộ não kinh tế quốc gia


        Dữ liệu tương lai:

        GDP

        CPI

        PPI

        PCE

        NFP

        Interest Rate


        <extra></extra>

        """

    )

)



# =====================================================
# HIỂN THỊ ĐỊA CẦU
# =====================================================


globe.update_geos(

    projection_type="orthographic",

    showland=True,

    landcolor="#103b2a",

    showocean=True,

    oceancolor="#00182d",

    showcountries=True,

    countrycolor="#557799",

    showcoastlines=True

)



globe.update_layout(

    height=800,

    margin=dict(

        l=0,

        r=0,

        t=0,

        b=0

    ),

    paper_bgcolor="#000000",

    font=dict(

        color="white"

    )

)



st.plotly_chart(

    globe,

    use_container_width=True

)



# =====================================================
# TRẠNG THÁI
# =====================================================


st.divider()



a,b,c = st.columns(3)



with a:

    st.metric(

        "🌍 Quốc gia",

        "195",

        "Đang xây dựng"

    )


with b:

    st.metric(

        "🏛 Thủ đô",

        "Bộ não kinh tế"

    )


with c:

    st.metric(

        "🧠 Chỉ số",

        "Chưa kết nối"

    )



# =====================================================
# MÔ TẢ KIẾN TRÚC
# =====================================================


st.subheader(

    "THỦ ĐÔ TRONG WEOS"

)



st.write(

"""

Trong WEOS:

🏛 Thủ đô không chỉ là vị trí địa lý.


Nó là:

🧠 Trung tâm điều khiển kinh tế


Sau này khi click vào thủ đô:

Sẽ thấy:

- GDP
- CPI
- PPI
- PCE
- NFP
- Thất nghiệp
- Lãi suất
- Dự trữ vàng
- Chính sách tiền tệ


Từ thủ đô sẽ kết nối xuống:

🏙 Thành phố

🏭 Ngành nghề

🏢 Doanh nghiệp

🩸 Dòng tiền


"""

)



# =====================================================
# KẾT THÚC ĐOẠN 004
# =====================================================
# =====================================================
# WEOS
# GLOBAL ECONOMIC WORLD MAP
# ĐOẠN 005
#
# THÊM HỆ THỐNG ZOOM
#
# CẤP ĐỘ:
#
# 🌍 TOÀN CẦU
#       ↓
# 🇻🇳 QUỐC GIA
#       ↓
# 🏛 THỦ ĐÔ
#       ↓
# 🏙 THÀNH PHỐ
#
# CHƯA KẾT NỐI DỮ LIỆU THẬT
# =====================================================


import streamlit as st
import plotly.graph_objects as go



# =====================================================
# CẤU HÌNH
# =====================================================


st.set_page_config(

    page_title="WEOS Global Economic Map",

    page_icon="🌍",

    layout="wide"

)



# =====================================================
# TIÊU ĐỀ
# =====================================================


st.markdown(

"""
<h1 style="text-align:center">
🌍 WEOS
</h1>

<h3 style="text-align:center">
BẢN ĐỒ KINH TẾ TOÀN CẦU
</h3>

<p style="text-align:center">
Hệ thống zoom theo tầng kinh tế
</p>

""",

unsafe_allow_html=True

)



# =====================================================
# CHỌN CẤP ĐỘ HIỂN THỊ
# =====================================================


level = st.sidebar.selectbox(

    "🔍 Chọn cấp độ bản đồ",

    [

        "🌍 Toàn cầu",

        "🇻🇳 Quốc gia",

        "🏛 Thủ đô",

        "🏙 Thành phố"

    ]

)



# =====================================================
# DỮ LIỆU KHUNG
#
# SAU NÀY THAY BẰNG DATABASE THẬT
#
# =====================================================


world = [

    {

        "name":"Toàn cầu",

        "lat":0,

        "lon":0

    }

]



countries = [

    {

        "name":"Việt Nam",

        "lat":14,

        "lon":108

    },

    {

        "name":"Hoa Kỳ",

        "lat":38,

        "lon":-97

    },

    {

        "name":"Trung Quốc",

        "lat":35,

        "lon":103

    }

]



capitals = [

    {

        "name":"Hà Nội",

        "lat":21.0285,

        "lon":105.8542

    },

    {

        "name":"Washington D.C",

        "lat":38.9072,

        "lon":-77.0369

    },

    {

        "name":"Bắc Kinh",

        "lat":39.9042,

        "lon":116.4074

    }

]



cities = [

    {

        "name":"TP Hồ Chí Minh",

        "lat":10.8231,

        "lon":106.6297

    },

    {

        "name":"New York",

        "lat":40.7128,

        "lon":-74.0060

    },

    {

        "name":"Thượng Hải",

        "lat":31.2304,

        "lon":121.4737

    }

]



# =====================================================
# XỬ LÝ CẤP ĐỘ ZOOM
# =====================================================


if level == "🌍 Toàn cầu":

    data = world

    zoom = 1



elif level == "🇻🇳 Quốc gia":

    data = countries

    zoom = 1.4



elif level == "🏛 Thủ đô":

    data = capitals

    zoom = 2



else:

    data = cities

    zoom = 3



# =====================================================
# TẠO BẢN ĐỒ
# =====================================================


map_view = go.Figure()



map_view.add_trace(

    go.Scattergeo(

        lat=[

            x["lat"]

            for x in data

        ],

        lon=[

            x["lon"]

            for x in data

        ],

        text=[

            x["name"]

            for x in data

        ],

        mode="markers+text",

        marker=dict(

            size=12,

            color="cyan"

        ),

        textposition="top center",

        name="WEOS Location"

    )

)



# =====================================================
# CẤU HÌNH HIỂN THỊ
# =====================================================


map_view.update_geos(

    projection_type="orthographic",

    showland=True,

    landcolor="#103b2a",

    showocean=True,

    oceancolor="#001529",

    showcountries=True,

    countrycolor="#667788"

)



map_view.update_layout(

    height=800,

    margin=dict(

        l=0,

        r=0,

        t=0,

        b=0

    ),

    paper_bgcolor="#000000",

    font=dict(

        color="white"

    )

)



st.plotly_chart(

    map_view,

    use_container_width=True

)



# =====================================================
# TRẠNG THÁI HỆ THỐNG
# =====================================================


st.divider()



st.subheader(

    "CẤU TRÚC ZOOM WEOS"

)



st.write(

"""

Hiện tại đã tạo khung:


🌍 Toàn cầu

↓

🇺🇳 Quốc gia

↓

🏛 Thủ đô

↓

🏙 Thành phố



Mục tiêu tiếp theo:


🏭 Ngành nghề

↓

🏢 Doanh nghiệp

↓

💰 Nhà đầu tư

↓

🩸 Dòng tiền



Sau này mỗi tầng sẽ liên kết bằng:

- Mạch máu dòng tiền
- Dữ liệu kinh tế
- Quan hệ USD
- Chỉ số vĩ mô



"""

)



# =====================================================
# KẾT THÚC ĐOẠN 005
# =====================================================
