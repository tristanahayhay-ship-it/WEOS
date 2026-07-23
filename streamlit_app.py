# ==========================================================
# WEOS
# ĐOẠN 1
# GLOBAL INTELLIGENCE SYSTEM
# CORE FOUNDATION ENGINE V1
# ==========================================================


# ==========================================================
# IMPORT CORE LIBRARY
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import time



# ==========================================================
# SYSTEM CONFIGURATION
# ==========================================================

st.set_page_config(

    page_title="WEOS Global Intelligence",

    page_icon="🌍",

    layout="wide",

    initial_sidebar_state="expanded"

)



# ==========================================================
# WEOS IDENTITY
# ==========================================================

WEOS_NAME = (

    "World Economic Observation System"

)


WEOS_VERSION = (

    "V1.0 CORE FOUNDATION"

)



# ==========================================================
# GLOBAL MEMORY FOUNDATION
# ==========================================================

if "weos_memory" not in st.session_state:

    st.session_state.weos_memory = {

        "System":

        [],


        "Countries":

        [],


        "Flows":

        [],


        "Markets":

        [],


        "Events":

        []

    }



# ==========================================================
# SYSTEM INITIALIZATION
# ==========================================================

if "weos_initialized" not in st.session_state:

    st.session_state.weos_initialized = True


    st.session_state.weos_memory["System"].append(

        {

            "Time":

            time.strftime("%Y-%m-%d %H:%M:%S"),


            "Status":

            "CORE INITIALIZED",


            "Version":

            WEOS_VERSION

        }

    )



# ==========================================================
# BASIC SYSTEM STATUS ENGINE
# ==========================================================

def weos_system_status_v1():

    status = {

        "Core":

        "ONLINE",


        "Database":

        "INITIALIZING",


        "Global Map":

        "WAITING",


        "Flow Engine":

        "WAITING",


        "AI Engine":

        "NOT STARTED"

    }


    return status



# ==========================================================
# SYSTEM STATUS DISPLAY
# ==========================================================

status = weos_system_status_v1()



status_df = pd.DataFrame(

    {

        "MODULE":

        status.keys(),


        "STATUS":

        status.values()

    }

)



# ==========================================================
# END OF WEOS CORE FOUNDATION V1
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 2
# GLOBAL INTELLIGENCE SYSTEM
# FUTURE DARK COMMAND CENTER UI ENGINE V1
# ==========================================================


# ==========================================================
# GLOBAL UI STYLE ENGINE
# ==========================================================

st.markdown(

"""

<style>


/* MAIN BACKGROUND */

[data-testid="stAppViewContainer"] {

    background:

    radial-gradient(

        circle at top,

        #172554,

        #020617 60%

    );

    color:white;

}



/* SIDEBAR */

[data-testid="stSidebar"] {

    background:

    linear-gradient(

        180deg,

        #020617,

        #0f172a

    );

}



/* TEXT */

h1,h2,h3,h4 {

    color:#e2e8f0;

}



/* CARDS */

.weos-card {

    background:

    rgba(15,23,42,0.85);


    border:

    1px solid rgba(56,189,248,0.2);


    border-radius:

    18px;


    padding:

    20px;


    box-shadow:

    0 0 25px rgba(14,165,233,0.08);

}



/* GLOW TEXT */

.weos-glow {

    color:#38bdf8;

    text-shadow:

    0 0 15px #38bdf8;

}



</style>

""",

unsafe_allow_html=True

)



# ==========================================================
# HEADER COMPONENT
# ==========================================================


st.markdown(

"""

<div class="weos-card">


<h1 class="weos-glow">

🌍 WEOS GLOBAL INTELLIGENCE CENTER

</h1>


<p>

World Economic Observation System

<br>

Global Economic Nervous System

</p>


</div>

""",

unsafe_allow_html=True

)



# ==========================================================
# COMMAND SIDEBAR
# ==========================================================


st.sidebar.markdown(

"""

<h2 style="color:#38bdf8">

🌐 WEOS CONTROL

</h2>

""",

unsafe_allow_html=True

)



selected_layer = st.sidebar.selectbox(

    "ACTIVE SYSTEM LAYER",

    [

        "Global Overview",

        "Capital Flow",

        "Commodity Flow",

        "Financial Market",

        "Geopolitical Layer",

        "Economic Network"

    ]

)



zoom_level = st.sidebar.slider(

    "MAP ZOOM LEVEL",

    1,

    10,

    1

)



system_mode = st.sidebar.radio(

    "SYSTEM MODE",

    [

        "Observation",

        "Analysis",

        "Simulation"

    ]

)



# ==========================================================
# UI MEMORY
# ==========================================================

if "ui_state" not in st.session_state:

    st.session_state.ui_state = {

        "Layer":

        "Global Overview",


        "Zoom":

        1,


        "Mode":

        "Observation"

    }



st.session_state.ui_state["Layer"] = selected_layer

st.session_state.ui_state["Zoom"] = zoom_level

st.session_state.ui_state["Mode"] = system_mode



# ==========================================================
# SYSTEM PANEL
# ==========================================================


col1, col2, col3 = st.columns(3)



with col1:

    st.markdown(

    """

    <div class="weos-card">

    <h3>🌍 GLOBAL MAP</h3>

    <p>

    STATUS:

    INITIALIZING

    </p>

    </div>

    """,

    unsafe_allow_html=True

    )



with col2:

    st.markdown(

    """

    <div class="weos-card">

    <h3>💰 FLOW ENGINE</h3>

    <p>

    STATUS:

    WAITING DATA

    </p>

    </div>

    """,

    unsafe_allow_html=True

    )



with col3:

    st.markdown(

    """

    <div class="weos-card">

    <h3>🧠 INTELLIGENCE</h3>

    <p>

    STATUS:

    FOUNDATION

    </p>

    </div>

    """,

    unsafe_allow_html=True

    )



# ==========================================================
# CURRENT CONTROL STATE
# ==========================================================


st.divider()


st.subheader(

    "⚙ Current System Configuration"

)



ui_df = pd.DataFrame(

    {

        "Parameter":

        st.session_state.ui_state.keys(),


        "Value":

        st.session_state.ui_state.values()

    }

)



st.dataframe(

    ui_df,

    use_container_width=True,

    hide_index=True

)



# ==========================================================
# END OF WEOS DARK COMMAND CENTER UI ENGINE V1
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 3
# GLOBAL INTELLIGENCE SYSTEM
# 3D GLOBAL EARTH ENGINE V1
# ==========================================================


# ==========================================================
# IMPORT 3D ENGINE
# ==========================================================

import plotly.graph_objects as go



# ==========================================================
# GLOBAL EARTH DATA FOUNDATION
# ==========================================================


if "earth_nodes_v1" not in st.session_state:


    st.session_state.earth_nodes_v1 = [


        {

            "Name":

            "New York",

            "Country":

            "USA",

            "Latitude":

            40.7128,

            "Longitude":

            -74.0060,

            "Type":

            "Financial Hub"

        },


        {

            "Name":

            "London",

            "Country":

            "UK",

            "Latitude":

            51.5074,

            "Longitude":

            -0.1278,

            "Type":

            "Financial Hub"

        },


        {

            "Name":

            "Shanghai",

            "Country":

            "China",

            "Latitude":

            31.2304,

            "Longitude":

            121.4737,

            "Type":

            "Trade Hub"

        },


        {

            "Name":

            "Dubai",

            "Country":

            "UAE",

            "Latitude":

            25.2048,

            "Longitude":

            55.2708,

            "Type":

            "Energy Hub"

        },


        {

            "Name":

            "Singapore",

            "Country":

            "Singapore",

            "Latitude":

            1.3521,

            "Longitude":

            103.8198,

            "Type":

            "Capital Hub"

        }

    ]



# ==========================================================
# CREATE EARTH DATAFRAME
# ==========================================================


earth_df = pd.DataFrame(

    st.session_state.earth_nodes_v1

)



# ==========================================================
# EARTH VISUALIZATION ENGINE
# ==========================================================


def create_global_earth_v1():


    fig = go.Figure()



    # ------------------------------------------------------
    # ECONOMIC NODE LAYER
    # ------------------------------------------------------


    fig.add_trace(

        go.Scattergeo(

            lat=

            earth_df["Latitude"],


            lon=

            earth_df["Longitude"],


            mode=

            "markers+text",



            text=

            earth_df["Name"],



            textfont=dict(

                color="#e2e8f0"

            ),



            marker=dict(

                size=12,

                color="#38bdf8",

                line=dict(

                    color="white",

                    width=1

                )

            )

        )

    )



    # ------------------------------------------------------
    # EARTH STYLE
    # ------------------------------------------------------


    fig.update_geos(


        projection_type=

        "orthographic",



        showland=True,


        landcolor=

        "#0f172a",



        showocean=True,


        oceancolor=

        "#020617",



        showcountries=True,


        countrycolor=

        "#334155",



        showcoastlines=True,


        coastlinecolor=

        "#475569",



        bgcolor=

        "#020617"

    )



    fig.update_layout(


        height=

        750,



        paper_bgcolor=

        "#020617",



        margin=dict(

            l=0,

            r=0,

            t=0,

            b=0

        )

    )


    return fig



# ==========================================================
# DISPLAY GLOBAL EARTH
# ==========================================================


st.divider()


st.subheader(

    "🌍 WEOS GLOBAL EARTH VIEW"

)



earth = create_global_earth_v1()



st.plotly_chart(

    earth,

    use_container_width=True

)



# ==========================================================
# EARTH NODE INFORMATION PANEL
# ==========================================================


st.divider()


st.subheader(

    "📍 Economic Location Nodes"

)



node_display = earth_df[

    [

        "Name",

        "Country",

        "Type"

    ]

]



st.dataframe(

    node_display,

    use_container_width=True,

    hide_index=True

)



# ==========================================================
# END OF WEOS 3D GLOBAL EARTH ENGINE V1
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 4
# GLOBAL INTELLIGENCE SYSTEM
# GLOBAL FLOW NETWORK ENGINE V1
# ==========================================================


# ==========================================================
# FLOW NETWORK MEMORY FOUNDATION
# ==========================================================

if "global_flow_network_v1" not in st.session_state:


    st.session_state.global_flow_network_v1 = [


        {

            "From":

            "New York",


            "To":

            "London",


            "Flow Type":

            "Capital",


            "Direction":

            "INFLOW",


            "Strength":

            80


        },


        {

            "From":

            "London",


            "To":

            "Shanghai",


            "Flow Type":

            "Trade",


            "Direction":

            "OUTFLOW",


            "Strength":

            65


        },


        {

            "From":

            "Dubai",


            "To":

            "Singapore",


            "Flow Type":

            "Energy",


            "Direction":

            "INFLOW",


            "Strength":

            70


        },


        {

            "From":

            "Zurich",


            "To":

            "New York",


            "Flow Type":

            "Investment",


            "Direction":

            "OUTFLOW",


            "Strength":

            55


        }


    ]



# ==========================================================
# FLOW COLOR ENGINE
# ==========================================================


def flow_color_engine_v1(direction):


    if direction == "INFLOW":

        return "#22c55e"


    elif direction == "OUTFLOW":

        return "#ef4444"


    else:

        return "#38bdf8"



# ==========================================================
# FLOW WIDTH ENGINE
# ==========================================================


def flow_width_engine_v1(strength):


    return max(

        1,

        strength / 20

    )



# ==========================================================
# GLOBAL FLOW VISUALIZATION ENGINE
# ==========================================================


def create_global_flow_network_v1():


    fig = create_global_earth_v1()



    flow_df = pd.DataFrame(

        st.session_state.global_flow_network_v1

    )



    node_df = pd.DataFrame(

        st.session_state.earth_nodes_v1

    )



    for index,row in flow_df.iterrows():


        start = node_df[

            node_df["Name"]

            ==

            row["From"]

        ].iloc[0]



        end = node_df[

            node_df["Name"]

            ==

            row["To"]

        ].iloc[0]



        fig.add_trace(


            go.Scattergeo(


                lat=[

                    start["Latitude"],

                    end["Latitude"]

                ],


                lon=[

                    start["Longitude"],

                    end["Longitude"]

                ],



                mode="lines",



                line=dict(

                    width=

                    flow_width_engine_v1(

                        row["Strength"]

                    ),


                    color=

                    flow_color_engine_v1(

                        row["Direction"]

                    )

                ),



                opacity=0.8,



                hovertext=(

                    row["Flow Type"]

                    +

                    " | "

                    +

                    row["Direction"]

                )

            )

        )



    return fig



# ==========================================================
# DISPLAY FLOW NETWORK
# ==========================================================


st.divider()


st.subheader(

    "🧬 WEOS GLOBAL ECONOMIC FLOW NETWORK"

)



flow_map = create_global_flow_network_v1()



st.plotly_chart(

    flow_map,

    use_container_width=True

)



# ==========================================================
# FLOW DATA PANEL
# ==========================================================


st.divider()


st.subheader(

    "💰 Current Flow Network"

)



flow_display = pd.DataFrame(

    st.session_state.global_flow_network_v1

)



st.dataframe(

    flow_display,

    use_container_width=True,

    hide_index=True

)



# ==========================================================
# FLOW LEGEND
# ==========================================================


st.markdown(

"""

### Flow Color Meaning

🟢 **Green**

Capital / Resource Inflow


🔴 **Red**

Capital / Resource Outflow


🔵 **Blue**

Neutral Connection


Strength càng lớn:

→ Sợi dây càng dày

→ Dòng chảy càng mạnh


""",

unsafe_allow_html=True

)



# ==========================================================
# END OF WEOS GLOBAL FLOW NETWORK ENGINE V1
# ==========================================================
