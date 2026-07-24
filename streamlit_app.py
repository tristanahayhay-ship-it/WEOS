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
import streamlit as st
import plotly.graph_objects as go


# =====================================================
# WEOS
# GLOBAL ECONOMIC WORLD MAP
# ĐOẠN 006
#
# THÊM LỚP THÀNH PHỐ KINH TẾ
#
# QUỐC GIA
#      ↓
# THỦ ĐÔ
#      ↓
# THÀNH PHỐ
#
# CHƯA CÓ DỮ LIỆU THẬT
# =====================================================


st.set_page_config(
    page_title="WEOS Global Economic Map",
    page_icon="🌍",
    layout="wide"
)


st.markdown(
"""
<h1 style="text-align:center">
🌍 WEOS
</h1>

<h3 style="text-align:center">
BẢN ĐỒ KINH TẾ TOÀN CẦU
</h3>

<p style="text-align:center">
Xây dựng mạng lưới địa lý kinh tế
</p>
""",
unsafe_allow_html=True
)



# =====================================================
# DỮ LIỆU KHUNG
# SAU NÀY THAY BẰNG DATABASE THẬT
# =====================================================


locations = [

    {
        "name":"Hoa Kỳ",
        "type":"Quốc gia",
        "lat":38,
        "lon":-97
    },

    {
        "name":"Washington D.C",
        "type":"Thủ đô",
        "lat":38.9072,
        "lon":-77.0369
    },

    {
        "name":"New York",
        "type":"Trung tâm tài chính",
        "lat":40.7128,
        "lon":-74.0060
    },

    {
        "name":"California",
        "type":"Công nghệ",
        "lat":36.7783,
        "lon":-119.4179
    },


    {
        "name":"Việt Nam",
        "type":"Quốc gia",
        "lat":14,
        "lon":108
    },


    {
        "name":"Hà Nội",
        "type":"Thủ đô",
        "lat":21.0285,
        "lon":105.8542
    },


    {
        "name":"TP Hồ Chí Minh",
        "type":"Tài chính - Sản xuất",
        "lat":10.8231,
        "lon":106.6297
    }

]



# =====================================================
# TẠO BẢN ĐỒ
# =====================================================


fig = go.Figure()



# Điểm địa lý kinh tế


fig.add_trace(

    go.Scattergeo(

        lat=[
            x["lat"]
            for x in locations
        ],

        lon=[
            x["lon"]
            for x in locations
        ],

        text=[
            x["name"]
            for x in locations
        ],

        customdata=[
            x["type"]
            for x in locations
        ],


        mode="markers+text",


        marker=dict(

            size=12,

            color="cyan"

        ),


        textposition="top center",


        hovertemplate=

        """

        📍 %{text}


        Loại:

        %{customdata}


        Trạng thái:

        Chưa kết nối dữ liệu


        <extra></extra>

        """

    )

)



# =====================================================
# ĐỊA CẦU
# =====================================================


fig.update_geos(

    projection_type="orthographic",

    showland=True,

    landcolor="#123524",

    showocean=True,

    oceancolor="#001529",

    showcountries=True,

    countrycolor="#607080",

    showcoastlines=True

)



fig.update_layout(

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
    fig,
    use_container_width=True
)



# =====================================================
# HIỂN THỊ KIẾN TRÚC
# =====================================================


st.divider()


st.subheader(
"🧬 MÔ HÌNH CƠ THỂ KINH TẾ"
)



st.write(

"""

Hiện tại:


🌍 Quốc gia

↓

🏛 Thủ đô

↓

🏙 Thành phố kinh tế



Ví dụ:


Hoa Kỳ

↓

Washington D.C

(Bộ não - chính sách)


↓

New York

(Tài chính)


↓

California

(Công nghệ)



Việt Nam

↓

Hà Nội

(Điều hành)


↓

TP Hồ Chí Minh

(Tài chính - sản xuất)



Bước tiếp theo:


ĐOẠN 007:


🩸 Tạo các đường kết nối giữa:

Thủ đô → Thành phố → Ngành nghề


Sau đó mới đưa:

- Dòng tiền xanh/đỏ
- USD Flow
- dữ liệu thật


"""

)
import streamlit as st
import plotly.graph_objects as go


# =====================================================
# WEOS
# GLOBAL ECONOMIC WORLD MAP
# ĐOẠN 007
#
# XÂY DỰNG MẠCH MÁU KẾT NỐI ĐỊA LÝ
#
# CHƯA PHẢI DÒNG TIỀN THẬT
# CHỈ DỰNG KIẾN TRÚC
# =====================================================


st.set_page_config(
    page_title="WEOS Global Economic Map",
    page_icon="🌍",
    layout="wide"
)



st.markdown(
"""
<h1 style="text-align:center">
🌍 WEOS
</h1>

<h3 style="text-align:center">
MẠNG LƯỚI KINH TẾ TOÀN CẦU
</h3>

<p style="text-align:center">
Giai đoạn xây dựng hệ thống mạch máu
</p>

""",
unsafe_allow_html=True
)



# =====================================================
# CÁC NÚT KINH TẾ
# =====================================================


nodes = [

    {
        "name":"Washington D.C",
        "lat":38.9072,
        "lon":-77.0369,
        "role":"Bộ não chính sách"
    },


    {
        "name":"New York",
        "lat":40.7128,
        "lon":-74.0060,
        "role":"Trung tâm tài chính"
    },


    {
        "name":"California",
        "lat":36.7783,
        "lon":-119.4179,
        "role":"Công nghệ"
    },


    {
        "name":"Hà Nội",
        "lat":21.0285,
        "lon":105.8542,
        "role":"Trung tâm điều hành"
    },


    {
        "name":"TP Hồ Chí Minh",
        "lat":10.8231,
        "lon":106.6297,
        "role":"Sản xuất - tài chính"
    }

]



# =====================================================
# TẠO BẢN ĐỒ
# =====================================================


fig = go.Figure()



# =====================================================
# LỚP MẠCH MÁU
#
# Đường kết nối
# sau này thay bằng dòng tiền thật
# =====================================================


connections = [

    (
        nodes[0],
        nodes[1]
    ),

    (
        nodes[0],
        nodes[2]
    ),

    (
        nodes[3],
        nodes[4]
    )

]



for start,end in connections:


    fig.add_trace(

        go.Scattergeo(

            lat=[
                start["lat"],
                end["lat"]
            ],


            lon=[
                start["lon"],
                end["lon"]
            ],


            mode="lines",


            line=dict(

                width=3,

                color="cyan"

            ),


            opacity=0.8,


            hoverinfo="none"

        )

    )



# =====================================================
# CÁC NÚT KINH TẾ
# =====================================================


fig.add_trace(

    go.Scattergeo(

        lat=[

            n["lat"]

            for n in nodes

        ],


        lon=[

            n["lon"]

            for n in nodes

        ],


        text=[

            n["name"]

            for n in nodes

        ],


        customdata=[

            n["role"]

            for n in nodes

        ],


        mode="markers+text",


        marker=dict(

            size=14,

            color="gold"

        ),


        textposition="top center",


        hovertemplate=

        """

        📍 %{text}


        Vai trò:

        %{customdata}


        <extra></extra>

        """

    )

)



# =====================================================
# HIỂN THỊ TRÁI ĐẤT
# =====================================================


fig.update_geos(

    projection_type="orthographic",

    showland=True,

    landcolor="#103b2a",

    showocean=True,

    oceancolor="#001529",

    showcountries=True,

    countrycolor="#667788"

)



fig.update_layout(

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

    fig,

    use_container_width=True

)



# =====================================================
# GIẢI THÍCH
# =====================================================


st.divider()


st.subheader(
"🩸 HỆ THỐNG MẠCH MÁU WEOS"
)



st.write(

"""

Đã tạo:


🟡 Điểm nút kinh tế

↓

🩵 Đường kết nối


Sau này các đường này sẽ không còn là đường địa lý.


Nó sẽ trở thành:


🩸 DÒNG TIỀN THẬT


Ví dụ:


USD mạnh:


Mỹ

↓

Trái phiếu

↓

Dòng tiền rời vàng


USD yếu:


USD

↓

Vàng

↓

Hàng hóa

↓

Thị trường mới nổi



Mỗi đường sẽ có:


- Hướng chảy

- Giá trị USD

- Màu xanh / đỏ

- Tốc độ

- Nguyên nhân


"""

)
import streamlit as st
import plotly.graph_objects as go
import numpy as np


# =====================================================
# WEOS
# GLOBAL ECONOMIC WORLD MAP
# ĐOẠN 008
#
# TẠO MẠCH MÁU CÓ CHUYỂN ĐỘNG
#
# CHƯA KẾT NỐI DÒNG TIỀN THẬT
# =====================================================


st.set_page_config(
    page_title="WEOS Global Economic Map",
    page_icon="🌍",
    layout="wide"
)



st.markdown(
"""
<h1 style="text-align:center">
🌍 WEOS
</h1>

<h3 style="text-align:center">
HỆ TUẦN HOÀN KINH TẾ TOÀN CẦU
</h3>

<p style="text-align:center">
Mô phỏng mạch máu dòng tiền
</p>
""",
unsafe_allow_html=True
)



# =====================================================
# DỮ LIỆU NÚT KINH TẾ
# =====================================================


nodes = {

    "Washington":(
        38.9072,
        -77.0369
    ),

    "New York":(
        40.7128,
        -74.0060
    ),

    "California":(
        36.7783,
        -119.4179
    ),

    "Hà Nội":(
        21.0285,
        105.8542
    ),

    "TP.HCM":(
        10.8231,
        106.6297
    )

}



# =====================================================
# MẠCH KẾT NỐI
# =====================================================


flows = [

    (
        "Washington",
        "New York"
    ),

    (
        "Washington",
        "California"
    ),

    (
        "Hà Nội",
        "TP.HCM"
    )

]



fig = go.Figure()



# =====================================================
# VẼ MẠCH MÁU
# =====================================================


for start,end in flows:


    lat1,lon1 = nodes[start]

    lat2,lon2 = nodes[end]


    # đường chính

    fig.add_trace(

        go.Scattergeo(

            lat=[
                lat1,
                lat2
            ],

            lon=[
                lon1,
                lon2
            ],

            mode="lines",

            line=dict(

                width=3,

                color="cyan"

            ),

            opacity=0.8,

            hoverinfo="none"

        )

    )


    # điểm sáng chạy trên mạch

    for t in np.linspace(0,1,8):


        lat = lat1 + (lat2-lat1)*t

        lon = lon1 + (lon2-lon1)*t



        fig.add_trace(

            go.Scattergeo(

                lat=[lat],

                lon=[lon],

                mode="markers",

                marker=dict(

                    size=6,

                    color="yellow"

                ),

                hoverinfo="none"

            )

        )





# =====================================================
# ĐIỂM KINH TẾ
# =====================================================


fig.add_trace(

    go.Scattergeo(

        lat=[

            x[0]

            for x in nodes.values()

        ],

        lon=[

            x[1]

            for x in nodes.values()

        ],


        text=list(nodes.keys()),


        mode="markers+text",


        marker=dict(

            size=15,

            color="gold"

        ),


        textposition="top center"

    )

)



# =====================================================
# ĐỊA CẦU
# =====================================================


fig.update_geos(

    projection_type="orthographic",

    showland=True,

    landcolor="#103b2a",

    showocean=True,

    oceancolor="#001529",

    showcountries=True,

    countrycolor="#667788"

)



fig.update_layout(

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

    fig,

    use_container_width=True

)



# =====================================================
# GIẢI THÍCH
# =====================================================


st.divider()


st.subheader(
"🩸 MẠCH MÁU KINH TẾ"
)



st.write(
"""

Đã thêm:


✅ Đường kết nối kinh tế

✅ Điểm sáng trên dòng chảy

✅ Mô phỏng hướng vận động


Trong WEOS thật:


Điểm sáng này sau này sẽ trở thành:


💵 Dòng tiền USD

📈 Vốn đầu tư

🏦 Dòng vốn ngân hàng

🏭 Vốn doanh nghiệp


Mỗi dòng sẽ có:


🟢 Tiền vào

🔴 Tiền rút

💲 Giá trị USD

⏱ Thời gian thực

📍 Vị trí nguồn và đích


"""
)
import streamlit as st
import plotly.graph_objects as go


# =====================================================
# WEOS
# GLOBAL ECONOMIC WORLD MAP
# ĐOẠN 009
#
# MÀU SẮC DÒNG TIỀN
#
# XANH  = VỐN VÀO
# ĐỎ    = VỐN RÚT RA
#
# CHƯA KẾT NỐI DỮ LIỆU THẬT
# =====================================================


st.set_page_config(
    page_title="WEOS Global Economic Map",
    page_icon="🌍",
    layout="wide"
)



st.markdown(
"""
<h1 style="text-align:center">
🌍 WEOS
</h1>

<h3 style="text-align:center">
MẠNG LƯỚI DÒNG TIỀN TOÀN CẦU
</h3>

<p style="text-align:center">
Mô phỏng dòng vốn xanh và đỏ
</p>
""",
unsafe_allow_html=True
)



# =====================================================
# CÁC ĐIỂM KINH TẾ
# =====================================================


nodes = {

    "Hoa Kỳ":(38,-97),

    "New York":(40.7128,-74.0060),

    "Washington":(38.9072,-77.0369),

    "Châu Âu":(50,10),

    "Châu Á":(30,110),

    "Vàng":(25,45)

}



# =====================================================
# DÒNG TIỀN
#
# SAU NÀY:
#
# value = USD thật
#
# direction = dữ liệu thật
#
# =====================================================


money_flows = [

    {

        "from":"Hoa Kỳ",

        "to":"New York",

        "value":80,

        "status":"green"

    },


    {

        "from":"Hoa Kỳ",

        "to":"Châu Âu",

        "value":40,

        "status":"red"

    },


    {

        "from":"Hoa Kỳ",

        "to":"Vàng",

        "value":60,

        "status":"green"

    },


    {

        "from":"Châu Á",

        "to":"Hoa Kỳ",

        "value":30,

        "status":"red"

    }

]



fig = go.Figure()



# =====================================================
# VẼ DÒNG TIỀN
# =====================================================


for flow in money_flows:


    start = nodes[flow["from"]]

    end = nodes[flow["to"]]


    color = (

        "lime"

        if flow["status"]=="green"

        else

        "red"

    )


    width = (

        flow["value"]

        /20

    )


    fig.add_trace(

        go.Scattergeo(

            lat=[

                start[0],

                end[0]

            ],

            lon=[

                start[1],

                end[1]

            ],

            mode="lines",

            line=dict(

                color=color,

                width=width

            ),

            opacity=0.8,

            hovertemplate=

            f"""

            DÒNG TIỀN


            Từ:

            {flow["from"]}


            Đến:

            {flow["to"]}


            Giá trị:

            {flow["value"]} tỷ USD


            Trạng thái:

            {"Vốn vào" if flow["status"]=="green" else "Rút vốn"}


            <extra></extra>

            """

        )

    )



# =====================================================
# HIỂN THỊ NÚT
# =====================================================


fig.add_trace(

    go.Scattergeo(

        lat=[

            x[0]

            for x in nodes.values()

        ],

        lon=[

            x[1]

            for x in nodes.values()

        ],

        text=list(nodes.keys()),

        mode="markers+text",

        marker=dict(

            size=14,

            color="gold"

        ),

        textposition="top center"

    )

)



# =====================================================
# QUẢ CẦU
# =====================================================


fig.update_geos(

    projection_type="orthographic",

    showland=True,

    landcolor="#103b2a",

    showocean=True,

    oceancolor="#001529",

    showcountries=True,

    countrycolor="#667788"

)



fig.update_layout(

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

    fig,

    use_container_width=True

)



# =====================================================
# THÔNG TIN
# =====================================================


st.divider()


st.subheader(
"🩸 TRẠNG THÁI DÒNG TIỀN"
)


st.write(
"""

Quy tắc WEOS:


🟢 Xanh:

- Dòng vốn đi vào
- Đầu tư tăng
- Tích lũy tài sản


🔴 Đỏ:

- Dòng vốn rút ra
- Phòng thủ
- Thoái vốn


Độ dày đường:

= sức mạnh dòng tiền


Sau này dữ liệu thật sẽ lấy từ:


- Forex
- ETF Flow
- Bond Flow
- Stock Flow
- Crypto Flow
- Commodity Flow


"""
)
import streamlit as st
import plotly.graph_objects as go


# =====================================================
# WEOS
# GLOBAL ECONOMIC WORLD MAP
# ĐOẠN 010
#
# THỦ ĐÔ = BỘ NÃO KINH TẾ
#
# TẠO HỆ THỐNG CHỈ SỐ
#
# CHƯA KẾT NỐI DỮ LIỆU THẬT
# =====================================================


st.set_page_config(

    page_title="WEOS Global Economic Map",

    page_icon="🌍",

    layout="wide"

)



st.markdown(

"""
<h1 style="text-align:center">
🌍 WEOS
</h1>

<h3 style="text-align:center">
BỘ NÃO KINH TẾ QUỐC GIA
</h3>

<p style="text-align:center">
Thủ đô là trung tâm điều khiển
</p>

""",

unsafe_allow_html=True

)



# =====================================================
# DỮ LIỆU KHUNG QUỐC GIA
# =====================================================


countries = {


    "Hoa Kỳ":

    {

        "capital":"Washington D.C",

        "lat":38.9072,

        "lon":-77.0369,


        "data":

        {

            "GDP":"2.5%",

            "CPI":"3.1%",

            "PCE":"2.8%",

            "NFP":"+175K",

            "Unemployment":"4.2%",

            "FED Rate":"4.50%",

            "Gold Reserve":"8,133 tons"

        }

    },


    "Việt Nam":

    {

        "capital":"Hà Nội",

        "lat":21.0285,

        "lon":105.8542,


        "data":

        {

            "GDP":"6.2%",

            "CPI":"3.5%",

            "PCE":"N/A",

            "NFP":"N/A",

            "Unemployment":"2.3%",

            "Interest Rate":"4.5%",

            "Gold Reserve":"N/A"

        }

    }

}



# =====================================================
# CHỌN QUỐC GIA
# =====================================================


selected = st.sidebar.selectbox(

    "🌍 Chọn quốc gia",

    list(countries.keys())

)



country = countries[selected]



# =====================================================
# BẢN ĐỒ
# =====================================================


fig = go.Figure()



fig.add_trace(

    go.Scattergeo(

        lat=[country["lat"]],

        lon=[country["lon"]],

        text=[country["capital"]],

        mode="markers+text",

        marker=dict(

            size=20,

            color="gold"

        ),

        textposition="top center"

    )

)



fig.update_geos(

    projection_type="orthographic",

    showland=True,

    landcolor="#103b2a",

    showocean=True,

    oceancolor="#001529",

    showcountries=True

)



fig.update_layout(

    height=700,

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

    fig,

    use_container_width=True

)



# =====================================================
# BẢNG NÃO KINH TẾ
# =====================================================


st.divider()



st.subheader(

f"🧠 {country['capital']} - TRUNG TÂM ĐIỀU KHIỂN KINH TẾ"

)



for key,value in country["data"].items():

    st.metric(

        key,

        value

    )



# =====================================================
# GIẢI THÍCH
# =====================================================


st.subheader(

"🔗 LIÊN KẾT VỚI MẠCH MÁU"

)



st.write(

"""

Trong WEOS:


🏛 Thủ đô

=

🧠 Bộ não


Các chỉ số kinh tế sẽ điều khiển:


GDP

↓

Sản xuất

↓

Việc làm

↓

Doanh nghiệp

↓

Dòng tiền


Ví dụ:


NFP giảm

↓

Nguy cơ việc làm yếu

↓

Ngành sản xuất bị ảnh hưởng

↓

Dòng tiền rút khỏi khu vực yếu


Bản đồ sẽ đổi màu theo dữ liệu thật.


"""

)
import streamlit as st
import plotly.graph_objects as go


# =====================================================
# WEOS
# GLOBAL ECONOMIC WORLD MAP
# ĐOẠN 011
#
# THỦ ĐÔ → THÀNH PHỐ → NGÀNH NGHỀ
#
# XÂY DỰNG HỆ THẦN KINH KINH TẾ
#
# CHƯA KẾT NỐI DỮ LIỆU THẬT
# =====================================================


st.set_page_config(

    page_title="WEOS Economic Network",

    page_icon="🌍",

    layout="wide"

)



st.markdown(

"""
<h1 style="text-align:center">
🌍 WEOS
</h1>

<h3 style="text-align:center">
HỆ THẦN KINH KINH TẾ TOÀN CẦU
</h3>

<p style="text-align:center">
Thủ đô điều khiển - Ngành nghề phản ứng
</p>

""",

unsafe_allow_html=True

)



# =====================================================
# MÔ HÌNH QUỐC GIA
# =====================================================


economic_network = {


    "Hoa Kỳ":

    {

        "capital":

        {

            "name":"Washington D.C",

            "lat":38.9072,

            "lon":-77.0369,


            "indicator":

            {

                "NFP":"Giảm",

                "Unemployment":"Tăng",

                "GDP":"Chậm lại"

            }

        },


        "regions":

        [

            {

                "name":"Michigan",

                "lat":44.3148,

                "lon":-85.6024,

                "sector":"Ô tô",

                "status":"RED"

            },


            {

                "name":"California",

                "lat":36.7783,

                "lon":-119.4179,

                "sector":"Công nghệ",

                "status":"GREEN"

            },


            {

                "name":"Texas",

                "lat":31,

                "lon":-99,

                "sector":"Năng lượng",

                "status":"GREEN"

            }

        ]

    }

}



country = economic_network["Hoa Kỳ"]



# =====================================================
# TẠO BẢN ĐỒ
# =====================================================


fig = go.Figure()



# -----------------------------
# ĐƯỜNG THẦN KINH
# -----------------------------


for region in country["regions"]:


    color = (

        "red"

        if region["status"]=="RED"

        else

        "lime"

    )


    fig.add_trace(

        go.Scattergeo(

            lat=[

                country["capital"]["lat"],

                region["lat"]

            ],


            lon=[

                country["capital"]["lon"],

                region["lon"]

            ],


            mode="lines",


            line=dict(

                color=color,

                width=3

            ),


            opacity=0.7

        )

    )



# -----------------------------
# THỦ ĐÔ
# -----------------------------


fig.add_trace(

    go.Scattergeo(

        lat=[

            country["capital"]["lat"]

        ],


        lon=[

            country["capital"]["lon"]

        ],


        text=["🧠 Washington D.C"],


        mode="markers+text",


        marker=dict(

            size=18,

            color="gold"

        )

    )

)



# -----------------------------
# VÙNG KINH TẾ
# -----------------------------


fig.add_trace(

    go.Scattergeo(

        lat=[

            r["lat"]

            for r in country["regions"]

        ],


        lon=[

            r["lon"]

            for r in country["regions"]

        ],


        text=[

            r["name"]

            for r in country["regions"]

        ],


        mode="markers+text",


        marker=dict(

            size=14,

            color=[

                "red"

                if r["status"]=="RED"

                else

                "lime"

                for r in country["regions"]

            ]

        )


    )

)



# =====================================================
# HIỂN THỊ
# =====================================================


fig.update_geos(

    projection_type="orthographic",

    showland=True,

    landcolor="#103b2a",

    showocean=True,

    oceancolor="#001529",

    showcountries=True

)



fig.update_layout(

    height=800,

    paper_bgcolor="#000000",

    font=dict(

        color="white"

    )

)



st.plotly_chart(

    fig,

    use_container_width=True

)



# =====================================================
# BỘ NÃO
# =====================================================


st.divider()


st.subheader(

"🧠 Washington D.C - Chỉ số điều khiển"

)



for k,v in country["capital"]["indicator"].items():

    st.metric(

        k,

        v

    )



# =====================================================
# GIẢI THÍCH
# =====================================================


st.subheader(

"🩸 Ảnh hưởng xuống nền kinh tế"

)



st.write(

"""

Ví dụ:


NFP giảm

↓

Washington D.C nhận tín hiệu


↓

Truyền xuống các vùng:


🔴 Michigan

Ngành:
Ô tô

Trạng thái:
Dòng tiền suy yếu


🟢 California

Ngành:
Công nghệ

Trạng thái:
Dòng vốn tiếp tục vào



Sau này:


Các đường này sẽ không còn là mô phỏng.


Chúng sẽ nhận:


- Việc làm thật

- Sản xuất thật

- Vốn đầu tư thật

- Dòng tiền USD thật


"""

)
import streamlit as st
import plotly.graph_objects as go


# =====================================================
# WEOS
# GLOBAL ECONOMIC WORLD MAP
# ĐOẠN 012
#
# THÊM TẦNG DOANH NGHIỆP
#
# THỦ ĐÔ
#    ↓
# VÙNG
#    ↓
# NGÀNH
#    ↓
# DOANH NGHIỆP
#
# CHƯA CÓ DỮ LIỆU THẬT
# =====================================================


st.set_page_config(
    page_title="WEOS Economic Network",
    page_icon="🌍",
    layout="wide"
)



st.markdown(
"""
<h1 style="text-align:center">
🌍 WEOS
</h1>

<h3 style="text-align:center">
MẠNG LƯỚI KINH TẾ VI MÔ → VĨ MÔ
</h3>

<p style="text-align:center">
Doanh nghiệp là tế bào của nền kinh tế
</p>
""",
unsafe_allow_html=True
)



# =====================================================
# MÔ HÌNH DOANH NGHIỆP
# =====================================================


network = {


"Washington D.C":
{

"lat":38.9072,
"lon":-77.0369,


"regions":

[

{

"name":"Michigan",

"lat":44.3148,

"lon":-85.6024,


"industry":"Ô tô",


"companies":

[

{

"name":"Nhà máy ô tô A",

"capital":"5 tỷ USD",

"status":"GREEN"

},


{

"name":"Nhà cung cấp B",

"capital":"1 tỷ USD",

"status":"RED"

}

]

},



{

"name":"California",

"lat":36.7783,

"lon":-119.4179,


"industry":"Công nghệ",


"companies":

[

{

"name":"Tập đoàn công nghệ C",

"capital":"20 tỷ USD",

"status":"GREEN"

}

]

}

]

}

}



brain = network["Washington D.C"]



fig = go.Figure()



# =====================================================
# DÂY THẦN KINH:
# THỦ ĐÔ → VÙNG
# =====================================================


for region in brain["regions"]:


    fig.add_trace(

        go.Scattergeo(

            lat=[

                brain["lat"],

                region["lat"]

            ],


            lon=[

                brain["lon"],

                region["lon"]

            ],


            mode="lines",


            line=dict(

                color="cyan",

                width=3

            )

        )

    )


# =====================================================
# VÙNG → DOANH NGHIỆP
# =====================================================


for region in brain["regions"]:


    for company in region["companies"]:


        color = (

            "lime"

            if company["status"]=="GREEN"

            else

            "red"

        )


        fig.add_trace(

            go.Scattergeo(

                lat=[

                    region["lat"]

                ],


                lon=[

                    region["lon"]

                ],


                mode="markers",


                marker=dict(

                    size=16,

                    color=color

                ),


                text=[

                    company["name"]

                ],


                hovertemplate=

                f"""

                🏢 {company["name"]}


                Ngành:

                {region["industry"]}


                Vốn:

                {company["capital"]}


                Trạng thái:

                {company["status"]}


                <extra></extra>

                """

            )

        )



# =====================================================
# THỦ ĐÔ
# =====================================================


fig.add_trace(

go.Scattergeo(

lat=[brain["lat"]],

lon=[brain["lon"]],

text=["🧠 Washington D.C"],

mode="markers+text",

marker=dict(

size=20,

color="gold"

)

)

)



# =====================================================
# HIỂN THỊ
# =====================================================


fig.update_geos(

projection_type="orthographic",

showland=True,

landcolor="#103b2a",

showocean=True,

oceancolor="#001529",

showcountries=True

)



fig.update_layout(

height=800,

paper_bgcolor="#000000",

font=dict(color="white")

)



st.plotly_chart(

fig,

use_container_width=True

)



# =====================================================
# THÔNG TIN
# =====================================================


st.divider()


st.subheader(
"🏢 DOANH NGHIỆP TRONG CƠ THỂ KINH TẾ"
)



st.write(

"""

Trong WEOS:


Doanh nghiệp = tế bào kinh tế


Ví dụ:


🏛 Chính sách

↓

🏙 Khu vực

↓

🏭 Ngành ô tô

↓

🏢 Doanh nghiệp

↓

💰 Dòng vốn


Sau này mỗi doanh nghiệp sẽ có:


- Vị trí địa lý

- Ngành

- Quy mô vốn

- Lao động

- Doanh thu

- Đầu tư

- Dòng tiền vào / ra


Và khi USD thay đổi:


Dòng vốn sẽ tự thay đổi màu:


🟢 Vốn vào

🔴 Vốn rút


"""

)
import streamlit as st
import plotly.graph_objects as go


# =====================================================
# WEOS
# GLOBAL ECONOMIC WORLD MAP
#
# ĐOẠN 013
#
# HỆ THỐNG ZOOM KINH TẾ
#
# WORLD
#   ↓
# COUNTRY
#   ↓
# CAPITAL
#   ↓
# CITY
#   ↓
# INDUSTRY
#   ↓
# COMPANY
#
# =====================================================


st.set_page_config(
    page_title="WEOS Economic World",
    page_icon="🌍",
    layout="wide"
)



st.markdown(
"""
<h1 style="text-align:center">
🌍 WEOS
</h1>

<h3 style="text-align:center">
ZOOM VÀO CƠ THỂ KINH TẾ
</h3>
""",
unsafe_allow_html=True
)



# =====================================================
# CẤP ĐỘ ZOOM
# =====================================================


level = st.sidebar.radio(

    "🔍 Cấp độ quan sát",

    [

        "🌍 Toàn cầu",

        "🇺🇸 Quốc gia",

        "🏛 Thủ đô",

        "🏙 Thành phố",

        "🏭 Ngành",

        "🏢 Doanh nghiệp"

    ]

)



# =====================================================
# DỮ LIỆU KHUNG
# SAU NÀY THAY BẰNG DATABASE THẬT
# =====================================================


data = {


"world":

[

("Hoa Kỳ",38,-97),

("Việt Nam",14,108),

("Trung Quốc",35,103)

],



"country":

[

("Washington D.C",38.9,-77),

("New York",40.7,-74),

("California",36.7,-119)

],



"capital":

[

("FED",38.9,-77),

("Treasury",38.8,-77),

("Government",38.9,-77)

],



"city":

[

("New York Finance",40.7,-74),

("Silicon Valley",37,-122)

],



"industry":

[

("Technology",37,-122),

("Finance",40.7,-74),

("Energy",31,-99)

],



"company":

[

("Company A",37,-122),

("Company B",40.7,-74)

]

}



# =====================================================
# CHỌN DỮ LIỆU THEO ZOOM
# =====================================================


if level=="🌍 Toàn cầu":

    selected=data["world"]


elif level=="🇺🇸 Quốc gia":

    selected=data["country"]


elif level=="🏛 Thủ đô":

    selected=data["capital"]


elif level=="🏙 Thành phố":

    selected=data["city"]


elif level=="🏭 Ngành":

    selected=data["industry"]


else:

    selected=data["company"]




# =====================================================
# VẼ BẢN ĐỒ
# =====================================================


fig = go.Figure()



fig.add_trace(

go.Scattergeo(

lat=[x[1] for x in selected],

lon=[x[2] for x in selected],

text=[x[0] for x in selected],

mode="markers+text",

marker=dict(

size=15,

color="cyan"

),

textposition="top center"

)

)



fig.update_geos(

projection_type="orthographic",

showland=True,

landcolor="#103b2a",

showocean=True,

oceancolor="#001529",

showcountries=True

)



fig.update_layout(

height=800,

paper_bgcolor="#000000",

font=dict(color="white"),

margin=dict(

l=0,

r=0,

t=0,

b=0

)

)



st.plotly_chart(

fig,

use_container_width=True

)



# =====================================================
# GIẢI THÍCH
# =====================================================


st.divider()


st.subheader(
"🌐 CẤU TRÚC ZOOM WEOS"
)



st.write(

"""

WEOS hoạt động như kính hiển vi kinh tế:


🌍 Toàn cầu

Nhìn:

- 195 quốc gia
- USD Flow
- Dòng tiền quốc tế


⬇️


🇺🇸 Quốc gia

Nhìn:

- Sức khỏe kinh tế
- Dòng vốn vào/ra


⬇️


🏛 Thủ đô

Nhìn:

- GDP
- CPI
- PCE
- NFP
- Lãi suất
- Chính sách


⬇️


🏭 Ngành

Nhìn:

- Sản xuất
- Công nghệ
- Năng lượng
- Tài chính


⬇️


🏢 Doanh nghiệp

Nhìn:

- Vốn
- Việc làm
- Đầu tư
- Dòng tiền


Mục tiêu cuối:


Càng zoom sâu:

Càng thấy rõ:

💰 Tiền đi đâu

🩸 Chảy mạnh hay yếu

🟢 Vào

🔴 Ra


"""

)
import streamlit as st
import plotly.graph_objects as go


# =====================================================
# WEOS
# GLOBAL ECONOMIC WORLD MAP
#
# ĐOẠN 014
#
# MONEY FLOW ENGINE
#
# DÒNG TIỀN CÓ GIÁ TRỊ USD
#
# CHƯA KẾT NỐI DỮ LIỆU THẬT
# =====================================================


st.set_page_config(
    page_title="WEOS Money Flow",
    page_icon="🌍",
    layout="wide"
)



st.markdown(
"""
<h1 style="text-align:center">
🌍 WEOS
</h1>

<h3 style="text-align:center">
MẠCH MÁU DÒNG TIỀN TOÀN CẦU
</h3>

<p style="text-align:center">
Capital Flow Visualization
</p>
""",
unsafe_allow_html=True
)



# =====================================================
# CÁC NÚT DÒNG TIỀN
# =====================================================


places = {


    "Hoa Kỳ":
    (
        38,
        -97
    ),


    "Trái phiếu Mỹ":
    (
        38.8,
        -77
    ),


    "Vàng":
    (
        25,
        45
    ),


    "Châu Á":
    (
        30,
        110
    ),


    "Crypto":
    (
        20,
        0
    )

}



# =====================================================
# DÒNG TIỀN
#
# SAU NÀY THAY BẰNG:
#
# ETF FLOW
# BOND FLOW
# STOCK FLOW
# FX FLOW
#
# =====================================================


flows = [


{

"from":"Hoa Kỳ",

"to":"Trái phiếu Mỹ",

"value":500,

"direction":"IN"

},



{

"from":"Hoa Kỳ",

"to":"Vàng",

"value":120,

"direction":"OUT"

},



{

"from":"Hoa Kỳ",

"to":"Châu Á",

"value":80,

"direction":"IN"

},



{

"from":"Crypto",

"to":"Hoa Kỳ",

"value":60,

"direction":"OUT"

}


]



fig = go.Figure()



# =====================================================
# VẼ MẠCH MÁU DÒNG TIỀN
# =====================================================


for flow in flows:


    start = places[flow["from"]]

    end = places[flow["to"]]


    if flow["direction"]=="IN":

        color="lime"

    else:

        color="red"



    width = flow["value"]/50



    fig.add_trace(

        go.Scattergeo(

            lat=[

                start[0],

                end[0]

            ],


            lon=[

                start[1],

                end[1]

            ],


            mode="lines",


            line=dict(

                color=color,

                width=width

            ),


            hovertemplate=f"""

            🩸 DÒNG TIỀN


            Từ:

            {flow["from"]}


            Đến:

            {flow["to"]}


            Giá trị:

            {flow["value"]} tỷ USD


            Trạng thái:

            {"Vào" if flow["direction"]=="IN" else "Rút ra"}


            <extra></extra>

            """

        )

    )



# =====================================================
# ĐIỂM KINH TẾ
# =====================================================


fig.add_trace(

    go.Scattergeo(

        lat=[

            x[0]

            for x in places.values()

        ],

        lon=[

            x[1]

            for x in places.values()

        ],

        text=list(places.keys()),


        mode="markers+text",


        marker=dict(

            size=15,

            color="gold"

        ),

        textposition="top center"

    )

)



# =====================================================
# QUẢ CẦU
# =====================================================


fig.update_geos(

    projection_type="orthographic",

    showland=True,

    landcolor="#103b2a",

    showocean=True,

    oceancolor="#001529",

    showcountries=True

)



fig.update_layout(

    height=800,

    paper_bgcolor="#000000",

    font=dict(color="white"),

    margin=dict(

        l=0,

        r=0,

        t=0,

        b=0

    )

)



st.plotly_chart(

    fig,

    use_container_width=True

)



# =====================================================
# THÔNG TIN DÒNG TIỀN
# =====================================================


st.divider()


st.subheader(
"🩸 CHI TIẾT DÒNG TIỀN"
)



for flow in flows:


    st.write(

        f"""
        **{flow['from']} → {flow['to']}**

        Giá trị:

        {flow['value']} tỷ USD


        Trạng thái:

        {"🟢 Dòng tiền vào" if flow['direction']=="IN" else "🔴 Dòng tiền rút"}

        """

    )



st.info(

"""
Sau này mỗi đường dây sẽ được thay bằng dữ liệu thật:

- Dòng vốn ETF
- Dòng vốn trái phiếu
- Dòng vốn cổ phiếu
- Dòng vốn ngoại hối
- Crypto Flow
- Commodity Flow

Và chạy theo thời gian thực.
"""

)
import streamlit as st
import plotly.graph_objects as go


# =====================================================
# WEOS
# GLOBAL ECONOMIC WORLD MAP
#
# ĐOẠN 014
#
# MONEY FLOW ENGINE
#
# DÒNG TIỀN CÓ GIÁ TRỊ USD
#
# CHƯA KẾT NỐI DỮ LIỆU THẬT
# =====================================================


st.set_page_config(
    page_title="WEOS Money Flow",
    page_icon="🌍",
    layout="wide"
)



st.markdown(
"""
<h1 style="text-align:center">
🌍 WEOS
</h1>

<h3 style="text-align:center">
MẠCH MÁU DÒNG TIỀN TOÀN CẦU
</h3>

<p style="text-align:center">
Capital Flow Visualization
</p>
""",
unsafe_allow_html=True
)



# =====================================================
# CÁC NÚT DÒNG TIỀN
# =====================================================


places = {


    "Hoa Kỳ":
    (
        38,
        -97
    ),


    "Trái phiếu Mỹ":
    (
        38.8,
        -77
    ),


    "Vàng":
    (
        25,
        45
    ),


    "Châu Á":
    (
        30,
        110
    ),


    "Crypto":
    (
        20,
        0
    )

}



# =====================================================
# DÒNG TIỀN
#
# SAU NÀY THAY BẰNG:
#
# ETF FLOW
# BOND FLOW
# STOCK FLOW
# FX FLOW
#
# =====================================================


flows = [


{

"from":"Hoa Kỳ",

"to":"Trái phiếu Mỹ",

"value":500,

"direction":"IN"

},



{

"from":"Hoa Kỳ",

"to":"Vàng",

"value":120,

"direction":"OUT"

},



{

"from":"Hoa Kỳ",

"to":"Châu Á",

"value":80,

"direction":"IN"

},



{

"from":"Crypto",

"to":"Hoa Kỳ",

"value":60,

"direction":"OUT"

}


]



fig = go.Figure()



# =====================================================
# VẼ MẠCH MÁU DÒNG TIỀN
# =====================================================


for flow in flows:


    start = places[flow["from"]]

    end = places[flow["to"]]


    if flow["direction"]=="IN":

        color="lime"

    else:

        color="red"



    width = flow["value"]/50



    fig.add_trace(

        go.Scattergeo(

            lat=[

                start[0],

                end[0]

            ],


            lon=[

                start[1],

                end[1]

            ],


            mode="lines",


            line=dict(

                color=color,

                width=width

            ),


            hovertemplate=f"""

            🩸 DÒNG TIỀN


            Từ:

            {flow["from"]}


            Đến:

            {flow["to"]}


            Giá trị:

            {flow["value"]} tỷ USD


            Trạng thái:

            {"Vào" if flow["direction"]=="IN" else "Rút ra"}


            <extra></extra>

            """

        )

    )



# =====================================================
# ĐIỂM KINH TẾ
# =====================================================


fig.add_trace(

    go.Scattergeo(

        lat=[

            x[0]

            for x in places.values()

        ],

        lon=[

            x[1]

            for x in places.values()

        ],

        text=list(places.keys()),


        mode="markers+text",


        marker=dict(

            size=15,

            color="gold"

        ),

        textposition="top center"

    )

)



# =====================================================
# QUẢ CẦU
# =====================================================


fig.update_geos(

    projection_type="orthographic",

    showland=True,

    landcolor="#103b2a",

    showocean=True,

    oceancolor="#001529",

    showcountries=True

)



fig.update_layout(

    height=800,

    paper_bgcolor="#000000",

    font=dict(color="white"),

    margin=dict(

        l=0,

        r=0,

        t=0,

        b=0

    )

)



st.plotly_chart(

    fig,

    use_container_width=True

)



# =====================================================
# THÔNG TIN DÒNG TIỀN
# =====================================================


st.divider()


st.subheader(
"🩸 CHI TIẾT DÒNG TIỀN"
)



for flow in flows:


    st.write(

        f"""
        **{flow['from']} → {flow['to']}**

        Giá trị:

        {flow['value']} tỷ USD


        Trạng thái:

        {"🟢 Dòng tiền vào" if flow['direction']=="IN" else "🔴 Dòng tiền rút"}

        """

    )



st.info(

"""
Sau này mỗi đường dây sẽ được thay bằng dữ liệu thật:

- Dòng vốn ETF
- Dòng vốn trái phiếu
- Dòng vốn cổ phiếu
- Dòng vốn ngoại hối
- Crypto Flow
- Commodity Flow

Và chạy theo thời gian thực.
"""

)
import streamlit as st
import plotly.graph_objects as go


# =====================================================
# WEOS
# GLOBAL ECONOMIC WORLD MAP
#
# ĐOẠN 016
#
# GOLD FLOW ENGINE
#
# VÀNG = TÀI SẢN TRÚ ẨN TOÀN CẦU
#
# CHƯA KẾT NỐI DỮ LIỆU THẬT
# =====================================================


st.set_page_config(

    page_title="WEOS Gold Flow",

    page_icon="🌍",

    layout="wide"

)



st.markdown(

"""
<h1 style="text-align:center">
🌍 WEOS
</h1>

<h3 style="text-align:center">
GOLD FLOW ENGINE
</h3>

<p style="text-align:center">
Dòng tiền trú ẩn của thế giới
</p>

""",

unsafe_allow_html=True

)



# =====================================================
# CÁC TRUNG TÂM VÀNG
# =====================================================


gold_nodes = {


    "Mỹ":
    (
        38,
        -97
    ),


    "Trung Quốc":
    (
        35,
        103
    ),


    "Ấn Độ":
    (
        20,
        78
    ),


    "Trung Đông":
    (
        25,
        45
    ),


    "Thị trường vàng":
    (
        25,
        0
    )

}



# =====================================================
# DÒNG VÀNG
#
# SAU NÀY THAY BẰNG:
#
# - Central Bank Gold Purchase
# - ETF Gold Flow
# - Futures Flow
# - Physical Gold Demand
#
# =====================================================


gold_flows = [

    {

        "from":"Trung Quốc",

        "to":"Thị trường vàng",

        "value":80,

        "status":"buy"

    },


    {

        "from":"Ấn Độ",

        "to":"Thị trường vàng",

        "value":50,

        "status":"buy"

    },


    {

        "from":"Thị trường vàng",

        "to":"Mỹ",

        "value":30,

        "status":"sell"

    }


]



fig = go.Figure()



# =====================================================
# VẼ DÒNG VÀNG
# =====================================================


for flow in gold_flows:


    start = gold_nodes[flow["from"]]

    end = gold_nodes[flow["to"]]


    if flow["status"]=="buy":

        color="gold"

    else:

        color="red"



    fig.add_trace(

        go.Scattergeo(

            lat=[

                start[0],

                end[0]

            ],

            lon=[

                start[1],

                end[1]

            ],

            mode="lines",


            line=dict(

                color=color,

                width=5

            ),


            hovertemplate=f"""

            🟡 GOLD FLOW


            {flow["from"]}

            ↓

            {flow["to"]}


            Giá trị:

            {flow["value"]} tỷ USD


            Trạng thái:

            {"Mua vàng" if flow["status"]=="buy" else "Bán vàng"}


            <extra></extra>

            """

        )

    )



# =====================================================
# ĐIỂM VÀNG
# =====================================================


fig.add_trace(

    go.Scattergeo(

        lat=[

            x[0]

            for x in gold_nodes.values()

        ],

        lon=[

            x[1]

            for x in gold_nodes.values()

        ],

        text=list(gold_nodes.keys()),


        mode="markers+text",


        marker=dict(

            size=16,

            color="yellow"

        )

    )

)



# =====================================================
# ĐỊA CẦU
# =====================================================


fig.update_geos(

    projection_type="orthographic",

    showland=True,

    landcolor="#103b2a",

    showocean=True,

    oceancolor="#001529",

    showcountries=True

)



fig.update_layout(

    height=800,

    paper_bgcolor="#000000",

    font=dict(

        color="white"

    )

)



st.plotly_chart(

    fig,

    use_container_width=True

)



# =====================================================
# THÔNG TIN
# =====================================================


st.divider()



st.subheader(
"🟡 VÀNG TRONG HỆ THỐNG WEOS"
)



st.write(

"""

Vàng là một cơ quan dự trữ của cơ thể kinh tế.


WEOS sẽ theo dõi:


🏦 Ngân hàng trung ương

- Mua vàng
- Bán vàng
- Dự trữ vàng


📈 ETF vàng

- Dòng vốn vào
- Dòng vốn ra


🌍 Quốc gia

- Ai tích lũy vàng
- Ai giảm vàng



Khi dữ liệu thật kết nối:


USD mạnh:

→ Dòng vàng có thể bị rút


USD yếu:

→ Dòng tiền tìm đến vàng


Mỗi dòng sẽ hiển thị:


🟡 Giá trị USD

📍 Nguồn

📍 Đích

⏱ Thời gian

📈 Xu hướng


"""

)
import streamlit as st
import plotly.graph_objects as go


# =====================================================
# WEOS
# GLOBAL ECONOMIC WORLD MAP
#
# ĐOẠN 017
#
# GLOBAL ASSET FLOW ENGINE
#
# CÁC LOẠI TÀI SẢN TOÀN CẦU
#
# CHƯA KẾT NỐI DỮ LIỆU THẬT
# =====================================================


st.set_page_config(

    page_title="WEOS Asset Flow",

    page_icon="🌍",

    layout="wide"

)



st.markdown(

"""
<h1 style="text-align:center">
🌍 WEOS
</h1>

<h3 style="text-align:center">
GLOBAL ASSET FLOW NETWORK
</h3>

<p style="text-align:center">
Dòng tiền giữa các loại tài sản
</p>
""",

unsafe_allow_html=True

)



# =====================================================
# CÁC TRUNG TÂM TÀI SẢN
# =====================================================


assets = {


    "USD":

    (
        38,
        -97
    ),


    "Vàng":

    (
        25,
        45
    ),


    "Chứng khoán Mỹ":

    (
        40,
        -74
    ),


    "Crypto":

    (
        20,
        0
    ),


    "Dầu":

    (
        25,
        55
    ),


    "Bất động sản":

    (
        30,
        100
    )

}



# =====================================================
# DÒNG TIỀN GIỮA TÀI SẢN
#
# SAU NÀY:
#
# ETF FLOW
# MARKET DATA
# FUND FLOW
#
# =====================================================


flows = [


{

"from":"USD",

"to":"Trái phiếu Mỹ",

"value":300,

"state":"green"

},



{

"from":"USD",

"to":"Vàng",

"value":150,

"state":"green"

},



{

"from":"USD",

"to":"Crypto",

"value":80,

"state":"green"

},



{

"from":"Chứng khoán Mỹ",

"to":"USD",

"value":100,

"state":"red"

},



{

"from":"USD",

"to":"Dầu",

"value":70,

"state":"green"

}

]



# thêm nút còn thiếu

assets["Trái phiếu Mỹ"]=(38.8,-77)



fig = go.Figure()



# =====================================================
# VẼ DÒNG TÀI SẢN
# =====================================================


for flow in flows:


    start = assets[flow["from"]]

    end = assets[flow["to"]]


    color = (

        "lime"

        if flow["state"]=="green"

        else

        "red"

    )



    fig.add_trace(

        go.Scattergeo(

            lat=[

                start[0],

                end[0]

            ],


            lon=[

                start[1],

                end[1]

            ],


            mode="lines",


            line=dict(

                color=color,

                width=5

            ),


            hovertemplate=f"""

            💰 ASSET FLOW


            {flow["from"]}

            ↓

            {flow["to"]}


            Giá trị:

            {flow["value"]} tỷ USD


            Trạng thái:

            {"Dòng tiền vào" if flow["state"]=="green" else "Dòng tiền rút"}


            <extra></extra>

            """

        )

    )



# =====================================================
# ĐIỂM TÀI SẢN
# =====================================================


fig.add_trace(

    go.Scattergeo(

        lat=[

            x[0]

            for x in assets.values()

        ],

        lon=[

            x[1]

            for x in assets.values()

        ],


        text=list(assets.keys()),


        mode="markers+text",


        marker=dict(

            size=16,

            color="gold"

        )

    )

)



# =====================================================
# QUẢ CẦU
# =====================================================


fig.update_geos(

    projection_type="orthographic",

    showland=True,

    landcolor="#103b2a",

    showocean=True,

    oceancolor="#001529",

    showcountries=True

)



fig.update_layout(

    height=800,

    paper_bgcolor="#000000",

    font=dict(color="white")

)



st.plotly_chart(

    fig,

    use_container_width=True

)



# =====================================================
# GIẢI THÍCH
# =====================================================


st.divider()


st.subheader(
"🌐 CÁC CƠ QUAN TÀI SẢN"
)



st.write(

"""

Trong WEOS:


💵 USD

=

Trung tâm thanh khoản


🟡 Vàng

=

Nơi trú ẩn


📈 Chứng khoán

=

Tăng trưởng


₿ Crypto

=

Tài sản rủi ro cao


🛢 Dầu

=

Năng lượng kinh tế


🏠 Bất động sản

=

Tài sản thực



Khi môi trường thay đổi:


FED tăng lãi suất

↓

USD mạnh

↓

Dòng tiền co lại



FED giảm lãi suất

↓

USD yếu

↓

Dòng tiền tìm kiếm lợi nhuận



Sau này mỗi dòng sẽ chạy bằng dữ liệu thật.

"""

)
