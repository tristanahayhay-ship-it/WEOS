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
