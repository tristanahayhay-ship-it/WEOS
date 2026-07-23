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
# ==========================================================
# WEOS
# ĐOẠN 5
# GLOBAL INTELLIGENCE SYSTEM
# REAL FLOW DATA ARCHITECTURE FOUNDATION V1
# ==========================================================


# ==========================================================
# REAL FLOW DATA MEMORY FOUNDATION
# ==========================================================

if "real_flow_database_v1" not in st.session_state:


    st.session_state.real_flow_database_v1 = []



# ==========================================================
# FLOW DATA STRUCTURE ENGINE
# ==========================================================


def create_flow_record_v1(

    source,

    destination,

    flow_type,

    asset,

    direction,

    strength,

    location_source,

    location_destination

):


    flow_record = {


        "Source":

        source,


        "Destination":

        destination,


        "Flow Type":

        flow_type,


        "Asset":

        asset,


        "Direction":

        direction,


        "Strength":

        strength,


        "Source Location":

        location_source,


        "Destination Location":

        location_destination,


        "Data Status":

        "REAL DATA REQUIRED"


    }



    return flow_record



# ==========================================================
# INITIAL FLOW STRUCTURE
# ==========================================================

if len(

    st.session_state.real_flow_database_v1

) == 0:



    st.session_state.real_flow_database_v1.append(


        create_flow_record_v1(


            "United States",


            "Global Market",


            "Capital Flow",


            "USD",


            "OUTFLOW",


            0,


            "New York",


            "Global"


        )

    )



    st.session_state.real_flow_database_v1.append(


        create_flow_record_v1(


            "Central Banks",


            "Gold Market",


            "Commodity Flow",


            "Gold",


            "INFLOW",


            0,


            "Global",


            "Gold Market"


        )

    )



    st.session_state.real_flow_database_v1.append(


        create_flow_record_v1(


            "Investment Funds",


            "Stock Market",


            "Financial Flow",


            "Equity",


            "INFLOW",


            0,


            "Global Funds",


            "Stock Exchanges"


        )

    )



# ==========================================================
# FLOW CATEGORY ENGINE
# ==========================================================


def flow_category_engine_v1():


    categories = {


        "Currency":

        "USD, EUR, JPY, CNY",


        "Commodity":

        "Gold, Oil, Metals",


        "Equity":

        "Stock Market",


        "Bond":

        "Government Debt",


        "Trade":

        "Goods & Services",


        "Investment":

        "FDI & Funds"

    }


    return categories



# ==========================================================
# FLOW STATUS ENGINE
# ==========================================================


def real_flow_status_engine_v1():


    status = {


        "Currency Flow":

        "WAITING REAL DATA",


        "Gold Flow":

        "WAITING REAL DATA",


        "Stock Flow":

        "WAITING REAL DATA",


        "Trade Flow":

        "WAITING REAL DATA",


        "Investment Flow":

        "WAITING REAL DATA"


    }


    return status



# ==========================================================
# FLOW DATABASE DISPLAY
# ==========================================================


st.divider()


st.subheader(

    "💰 WEOS FLOW DATA FOUNDATION"

)



flow_df = pd.DataFrame(

    st.session_state.real_flow_database_v1

)



st.dataframe(

    flow_df,

    use_container_width=True,

    hide_index=True

)



# ==========================================================
# FLOW LAYER STATUS
# ==========================================================


st.subheader(

    "🌐 Economic Flow Layers"

)



flow_status = real_flow_status_engine_v1()



flow_status_df = pd.DataFrame(

    {

        "Layer":

        flow_status.keys(),


        "Status":

        flow_status.values()

    }

)



st.dataframe(

    flow_status_df,

    use_container_width=True,

    hide_index=True

)



# ==========================================================
# KẾT THÚC ĐOẠN 5
# REAL FLOW DATA ARCHITECTURE FOUNDATION V1
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 6
# GLOBAL INTELLIGENCE SYSTEM
# ECONOMIC NODE INTELLIGENCE ENGINE V1
# ==========================================================


# ==========================================================
# ECONOMIC NODE MEMORY FOUNDATION
# ==========================================================

if "economic_nodes_v1" not in st.session_state:


    st.session_state.economic_nodes_v1 = []



# ==========================================================
# NODE CREATION ENGINE
# ==========================================================


def create_economic_node_v1(

    name,

    country,

    node_type,

    industry,

    latitude,

    longitude

):


    node = {


        "Location":

        name,


        "Country":

        country,


        "Node Type":

        node_type,


        "Industry":

        industry,


        "Latitude":

        latitude,


        "Longitude":

        longitude,


        "Capital Flow":

        "UNKNOWN",


        "Data Status":

        "REAL DATA REQUIRED"


    }


    return node



# ==========================================================
# INITIAL ECONOMIC NODE FOUNDATION
# ==========================================================

if len(

    st.session_state.economic_nodes_v1

) == 0:



    st.session_state.economic_nodes_v1.extend(



        [

            create_economic_node_v1(

                "New York Financial District",

                "United States",

                "Financial Hub",

                "Banking / Investment",

                40.7128,

                -74.0060

            ),



            create_economic_node_v1(

                "London Financial Center",

                "United Kingdom",

                "Financial Hub",

                "Global Finance",

                51.5074,

                -0.1278

            ),



            create_economic_node_v1(

                "Shanghai Trade Hub",

                "China",

                "Trade Hub",

                "Manufacturing / Export",

                31.2304,

                121.4737

            ),



            create_economic_node_v1(

                "Dubai Energy Center",

                "United Arab Emirates",

                "Energy Hub",

                "Oil / Gas",

                25.2048,

                55.2708

            ),



            create_economic_node_v1(

                "Zurich Wealth Center",

                "Switzerland",

                "Financial Hub",

                "Asset Management",

                47.3769,

                8.5417

            ),



            create_economic_node_v1(

                "Singapore Capital Hub",

                "Singapore",

                "Financial Hub",

                "Investment / Trade",

                1.3521,

                103.8198

            )

        ]

    )



# ==========================================================
# NODE CLASSIFICATION ENGINE
# ==========================================================


def economic_node_classification_v1():


    classification = {


        "Financial Hub":

        "Money concentration and investment",


        "Trade Hub":

        "Goods and supply movement",


        "Energy Hub":

        "Energy production and distribution",


        "Resource Hub":

        "Raw material source",


        "Industrial Hub":

        "Manufacturing center"

    }


    return classification



# ==========================================================
# NODE RELATION FOUNDATION
# ==========================================================


if "node_relation_v1" not in st.session_state:


    st.session_state.node_relation_v1 = []



def create_node_relation_v1(

    node_a,

    node_b,

    relation_type

):


    relation = {


        "From":

        node_a,


        "To":

        node_b,


        "Relation":

        relation_type,


        "Status":

        "WAITING REAL DATA"

    }


    return relation



# ==========================================================
# INITIAL CONNECTION STRUCTURE
# ==========================================================


if len(

    st.session_state.node_relation_v1

) == 0:



    st.session_state.node_relation_v1.append(


        create_node_relation_v1(

            "New York Financial District",

            "London Financial Center",

            "Capital Connection"

        )

    )


    st.session_state.node_relation_v1.append(


        create_node_relation_v1(

            "Dubai Energy Center",

            "Shanghai Trade Hub",

            "Energy Supply Connection"

        )

    )


    st.session_state.node_relation_v1.append(


        create_node_relation_v1(

            "Singapore Capital Hub",

            "Global Market",

            "Investment Connection"

        )

    )



# ==========================================================
# NODE DISPLAY
# ==========================================================


st.divider()


st.subheader(

    "📍 WEOS ECONOMIC NODE INTELLIGENCE"

)



node_df = pd.DataFrame(

    st.session_state.economic_nodes_v1

)



st.dataframe(

    node_df,

    use_container_width=True,

    hide_index=True

)



# ==========================================================
# NODE RELATION DISPLAY
# ==========================================================


st.subheader(

    "🔗 Economic Network Connections"

)



relation_df = pd.DataFrame(

    st.session_state.node_relation_v1

)



st.dataframe(

    relation_df,

    use_container_width=True,

    hide_index=True

)



# ==========================================================
# KẾT THÚC ĐOẠN 6
# ECONOMIC NODE INTELLIGENCE ENGINE V1
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 7
# GLOBAL INTELLIGENCE SYSTEM
# COMMODITY & RESOURCE FLOW ENGINE V1
# ==========================================================


# ==========================================================
# COMMODITY MEMORY FOUNDATION
# ==========================================================

if "commodity_database_v1" not in st.session_state:


    st.session_state.commodity_database_v1 = []



# ==========================================================
# COMMODITY CREATION ENGINE
# ==========================================================


def create_commodity_node_v1(

    name,

    category,

    source_location,

    main_industry

):


    commodity = {


        "Commodity":

        name,


        "Category":

        category,


        "Source Location":

        source_location,


        "Industry":

        main_industry,


        "Supply Status":

        "UNKNOWN",


        "Flow Status":

        "REAL DATA REQUIRED"

    }


    return commodity



# ==========================================================
# INITIAL COMMODITY FOUNDATION
# ==========================================================

if len(

    st.session_state.commodity_database_v1

) == 0:



    st.session_state.commodity_database_v1.extend(



        [

            create_commodity_node_v1(

                "Gold",

                "Precious Metal",

                "Global Mining Regions",

                "Finance / Reserve Asset"

            ),



            create_commodity_node_v1(

                "Crude Oil",

                "Energy",

                "Middle East",

                "Energy Industry"

            ),



            create_commodity_node_v1(

                "Natural Gas",

                "Energy",

                "Russia / Middle East / USA",

                "Energy Supply"

            ),



            create_commodity_node_v1(

                "Copper",

                "Industrial Metal",

                "Chile / Peru",

                "Manufacturing"

            ),



            create_commodity_node_v1(

                "Agriculture",

                "Food Commodity",

                "Global Farming Regions",

                "Food Supply Chain"

            )

        ]

    )



# ==========================================================
# RESOURCE LOCATION ENGINE
# ==========================================================


if "resource_locations_v1" not in st.session_state:


    st.session_state.resource_locations_v1 = []



def create_resource_location_v1(

    location,

    country,

    resource,

    latitude,

    longitude

):


    resource_node = {


        "Location":

        location,


        "Country":

        country,


        "Resource":

        resource,


        "Latitude":

        latitude,


        "Longitude":

        longitude,


        "Status":

        "REAL DATA REQUIRED"

    }


    return resource_node



# ==========================================================
# INITIAL RESOURCE LOCATIONS
# ==========================================================

if len(

    st.session_state.resource_locations_v1

) == 0:



    st.session_state.resource_locations_v1.extend(



        [

            create_resource_location_v1(

                "Gold Mining Region",

                "China",

                "Gold",

                36.6,

                117.0

            ),



            create_resource_location_v1(

                "Middle East Oil Region",

                "Saudi Arabia",

                "Crude Oil",

                24.0,

                45.0

            ),



            create_resource_location_v1(

                "Copper Mining Region",

                "Chile",

                "Copper",

                -23.6,

                -70.4

            )

        ]

    )



# ==========================================================
# COMMODITY FLOW STRUCTURE
# ==========================================================


if "commodity_flow_network_v1" not in st.session_state:


    st.session_state.commodity_flow_network_v1 = []



def create_commodity_flow_v1(

    source,

    destination,

    commodity,

    flow_type

):


    flow = {


        "Source":

        source,


        "Destination":

        destination,


        "Commodity":

        commodity,


        "Flow Type":

        flow_type,


        "Status":

        "WAITING REAL DATA"

    }


    return flow



# ==========================================================
# INITIAL COMMODITY CONNECTIONS
# ==========================================================


if len(

    st.session_state.commodity_flow_network_v1

) == 0:



    st.session_state.commodity_flow_network_v1.append(


        create_commodity_flow_v1(

            "Mining Region",

            "Global Gold Market",

            "Gold",

            "Resource Flow"

        )

    )



    st.session_state.commodity_flow_network_v1.append(


        create_commodity_flow_v1(

            "Middle East",

            "Global Energy Market",

            "Crude Oil",

            "Energy Flow"

        )

    )



    st.session_state.commodity_flow_network_v1.append(


        create_commodity_flow_v1(

            "Chile",

            "Manufacturing Industry",

            "Copper",

            "Industrial Flow"

        )

    )



# ==========================================================
# COMMODITY DISPLAY
# ==========================================================


st.divider()


st.subheader(

    "⛏ WEOS COMMODITY INTELLIGENCE"

)



commodity_df = pd.DataFrame(

    st.session_state.commodity_database_v1

)



st.dataframe(

    commodity_df,

    use_container_width=True,

    hide_index=True

)



# ==========================================================
# RESOURCE LOCATION DISPLAY
# ==========================================================


st.subheader(

    "📍 Resource Geographic Nodes"

)



resource_df = pd.DataFrame(

    st.session_state.resource_locations_v1

)



st.dataframe(

    resource_df,

    use_container_width=True,

    hide_index=True

)



# ==========================================================
# COMMODITY FLOW DISPLAY
# ==========================================================


st.subheader(

    "🔄 Commodity Flow Network"

)



commodity_flow_df = pd.DataFrame(

    st.session_state.commodity_flow_network_v1

)



st.dataframe(

    commodity_flow_df,

    use_container_width=True,

    hide_index=True

)



# ==========================================================
# KẾT THÚC ĐOẠN 7
# COMMODITY & RESOURCE FLOW ENGINE V1
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 8
# GLOBAL INTELLIGENCE SYSTEM
# GLOBAL TRADE ROUTE & SUPPLY CHAIN ENGINE V1
# ==========================================================


# ==========================================================
# TRADE ROUTE MEMORY FOUNDATION
# ==========================================================

if "trade_route_database_v1" not in st.session_state:

    st.session_state.trade_route_database_v1 = []



# ==========================================================
# TRADE ROUTE CREATION ENGINE
# ==========================================================


def create_trade_route_v1(

    source,

    destination,

    commodity,

    transport_type,

    importance

):


    route = {


        "Source":

        source,


        "Destination":

        destination,


        "Commodity":

        commodity,


        "Transport":

        transport_type,


        "Strategic Importance":

        importance,


        "Flow Status":

        "REAL DATA REQUIRED"

    }


    return route



# ==========================================================
# INITIAL GLOBAL TRADE ROUTES
# ==========================================================


if len(

    st.session_state.trade_route_database_v1

) == 0:



    st.session_state.trade_route_database_v1.extend(



        [

            create_trade_route_v1(

                "Middle East",

                "Asia",

                "Crude Oil",

                "Sea Transport",

                "HIGH"

            ),



            create_trade_route_v1(

                "China",

                "Global Market",

                "Manufactured Goods",

                "Sea + Air",

                "HIGH"

            ),



            create_trade_route_v1(

                "Australia",

                "China",

                "Iron Ore",

                "Sea Transport",

                "HIGH"

            ),



            create_trade_route_v1(

                "South America",

                "Asia",

                "Agriculture",

                "Sea Transport",

                "MEDIUM"

            )

        ]

    )



# ==========================================================
# LOGISTICS HUB ENGINE
# ==========================================================


if "logistics_hubs_v1" not in st.session_state:


    st.session_state.logistics_hubs_v1 = []



def create_logistics_hub_v1(

    name,

    country,

    hub_type,

    latitude,

    longitude

):


    hub = {


        "Location":

        name,


        "Country":

        country,


        "Hub Type":

        hub_type,


        "Latitude":

        latitude,


        "Longitude":

        longitude,


        "Status":

        "REAL DATA REQUIRED"

    }


    return hub



# ==========================================================
# INITIAL LOGISTICS NODES
# ==========================================================


if len(

    st.session_state.logistics_hubs_v1

) == 0:



    st.session_state.logistics_hubs_v1.extend(



        [

            create_logistics_hub_v1(

                "Singapore Port",

                "Singapore",

                "Global Shipping Hub",

                1.2644,

                103.8222

            ),



            create_logistics_hub_v1(

                "Shanghai Port",

                "China",

                "Manufacturing Export Hub",

                31.2304,

                121.4737

            ),



            create_logistics_hub_v1(

                "Rotterdam Port",

                "Netherlands",

                "European Trade Hub",

                51.9244,

                4.4777

            ),



            create_logistics_hub_v1(

                "Dubai Port",

                "UAE",

                "Energy Logistics Hub",

                25.2769,

                55.2962

            )

        ]

    )



# ==========================================================
# SUPPLY CHAIN LAYER
# ==========================================================


if "supply_chain_network_v1" not in st.session_state:


    st.session_state.supply_chain_network_v1 = []



def create_supply_chain_link_v1(

    industry,

    stage,

    location

):


    link = {


        "Industry":

        industry,


        "Stage":

        stage,


        "Location":

        location,


        "Data Status":

        "REAL DATA REQUIRED"

    }


    return link



# ==========================================================
# INITIAL SUPPLY CHAIN STRUCTURE
# ==========================================================


if len(

    st.session_state.supply_chain_network_v1

) == 0:



    st.session_state.supply_chain_network_v1.extend(



        [

            create_supply_chain_link_v1(

                "Gold",

                "Mining",

                "Mining Regions"

            ),



            create_supply_chain_link_v1(

                "Gold",

                "Refining",

                "Global Refinery Centers"

            ),



            create_supply_chain_link_v1(

                "Technology",

                "Manufacturing",

                "Asia Industrial Zones"

            ),



            create_supply_chain_link_v1(

                "Energy",

                "Production",

                "Middle East"

            )

        ]

    )



# ==========================================================
# TRADE ROUTE DISPLAY
# ==========================================================


st.divider()


st.subheader(

    "🚢 WEOS GLOBAL TRADE ROUTE NETWORK"

)



trade_df = pd.DataFrame(

    st.session_state.trade_route_database_v1

)



st.dataframe(

    trade_df,

    use_container_width=True,

    hide_index=True

)



# ==========================================================
# LOGISTICS DISPLAY
# ==========================================================


st.subheader(

    "⚓ Global Logistics Hubs"

)



hub_df = pd.DataFrame(

    st.session_state.logistics_hubs_v1

)



st.dataframe(

    hub_df,

    use_container_width=True,

    hide_index=True

)



# ==========================================================
# SUPPLY CHAIN DISPLAY
# ==========================================================


st.subheader(

    "🏭 Supply Chain Network"

)



supply_df = pd.DataFrame(

    st.session_state.supply_chain_network_v1

)



st.dataframe(

    supply_df,

    use_container_width=True,

    hide_index=True

)



# ==========================================================
# KẾT THÚC ĐOẠN 8
# GLOBAL TRADE ROUTE & SUPPLY CHAIN ENGINE V1
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 9
# GLOBAL INTELLIGENCE SYSTEM
# CAPITAL FLOW INTELLIGENCE ENGINE V1
# ==========================================================


# ==========================================================
# CAPITAL FLOW MEMORY FOUNDATION
# ==========================================================

if "capital_flow_database_v1" not in st.session_state:

    st.session_state.capital_flow_database_v1 = []



# ==========================================================
# CAPITAL FLOW CREATION ENGINE
# ==========================================================


def create_capital_flow_record_v1(

    source,

    destination,

    asset,

    flow_direction,

    sector,

    location

):


    capital_flow = {


        "Source":

        source,


        "Destination":

        destination,


        "Asset":

        asset,


        "Direction":

        flow_direction,


        "Sector":

        sector,


        "Location":

        location,


        "Flow Strength":

        "REAL DATA REQUIRED",


        "Data Status":

        "WAITING REAL SOURCE"

    }


    return capital_flow



# ==========================================================
# INITIAL CAPITAL FLOW STRUCTURE
# ==========================================================


if len(

    st.session_state.capital_flow_database_v1

) == 0:



    st.session_state.capital_flow_database_v1.extend(



        [

            create_capital_flow_record_v1(

                "Global Investors",

                "US Treasury Market",

                "USD / Bonds",

                "INFLOW",

                "Fixed Income",

                "United States"

            ),



            create_capital_flow_record_v1(

                "Investment Funds",

                "Technology Sector",

                "Equity Capital",

                "INFLOW",

                "Technology",

                "United States / Asia"

            ),



            create_capital_flow_record_v1(

                "Risk Assets",

                "Gold Market",

                "Gold Capital",

                "INFLOW",

                "Precious Metal",

                "Global"

            ),



            create_capital_flow_record_v1(

                "Emerging Markets",

                "US Dollar Assets",

                "Currency Flow",

                "OUTFLOW",

                "Currency",

                "Global"

            )

        ]

    )



# ==========================================================
# ASSET CLASS ENGINE
# ==========================================================


def capital_asset_class_engine_v1():


    assets = {


        "Currency":

        [

            "USD",

            "EUR",

            "JPY",

            "CNY"

        ],



        "Precious Metal":

        [

            "Gold",

            "Silver"

        ],



        "Equity":

        [

            "Stock Market",

            "Technology",

            "Energy"

        ],



        "Fixed Income":

        [

            "Government Bonds",

            "Corporate Bonds"

        ],



        "Commodity":

        [

            "Oil",

            "Gas",

            "Metals"

        ]

    }


    return assets



# ==========================================================
# CAPITAL FLOW COLOR ENGINE
# ==========================================================


def capital_flow_color_engine_v1(direction):


    if direction == "INFLOW":

        return "GREEN"



    elif direction == "OUTFLOW":

        return "RED"



    else:

        return "BLUE"



# ==========================================================
# USD IMPACT FOUNDATION
# ==========================================================


def usd_strength_impact_engine_v1():


    impact = {


        "USD Strong":


        {


            "Positive":

            [

                "Dollar Assets",

                "US Bonds"

            ],


            "Pressure":

            [

                "Gold",

                "Emerging Markets",

                "Commodities"

            ]

        },



        "USD Weak":


        {


            "Positive":

            [

                "Gold",

                "Commodities",

                "Risk Assets"

            ],


            "Pressure":

            [

                "Dollar Assets"

            ]

        }


    }


    return impact



# ==========================================================
# CAPITAL FLOW DISPLAY
# ==========================================================


st.divider()


st.subheader(

    "💰 WEOS CAPITAL FLOW INTELLIGENCE"

)



capital_df = pd.DataFrame(

    st.session_state.capital_flow_database_v1

)



st.dataframe(

    capital_df,

    use_container_width=True,

    hide_index=True

)



# ==========================================================
# ASSET NETWORK DISPLAY
# ==========================================================


st.subheader(

    "📊 Global Asset Class Network"

)



asset_network = capital_asset_class_engine_v1()



asset_df = pd.DataFrame(

    {

        "Asset Class":

        asset_network.keys(),


        "Assets":

        asset_network.values()

    }

)



st.dataframe(

    asset_df,

    use_container_width=True,

    hide_index=True

)



# ==========================================================
# USD RELATION DISPLAY
# ==========================================================


st.subheader(

    "💵 USD Global Impact Map"

)



usd_map = usd_strength_impact_engine_v1()



for state,data in usd_map.items():


    st.markdown(

        f"""

        ### {state}


        Positive Flow:

        {", ".join(data["Positive"])}


        Pressure:

        {", ".join(data["Pressure"])}

        """

    )



# ==========================================================
# KẾT THÚC ĐOẠN 9
# CAPITAL FLOW INTELLIGENCE ENGINE V1
# ==========================================================
# ==========================================================
# WEOS
# ĐOẠN 10
# GLOBAL INTELLIGENCE SYSTEM
# FINANCIAL MARKET CONNECTION ENGINE V1
# ==========================================================


# ==========================================================
# FINANCIAL MARKET MEMORY FOUNDATION
# ==========================================================

if "financial_market_network_v1" not in st.session_state:

    st.session_state.financial_market_network_v1 = []



# ==========================================================
# MARKET CONNECTION CREATION ENGINE
# ==========================================================


def create_market_connection_v1(

    source,

    destination,

    asset,

    relationship,

    impact

):


    connection = {


        "Source":

        source,


        "Destination":

        destination,


        "Asset":

        asset,


        "Relationship":

        relationship,


        "Impact":

        impact,


        "Data Status":

        "REAL DATA REQUIRED"

    }


    return connection



# ==========================================================
# INITIAL FINANCIAL CONNECTION STRUCTURE
# ==========================================================


if len(

    st.session_state.financial_market_network_v1

) == 0:



    st.session_state.financial_market_network_v1.extend(



        [

            create_market_connection_v1(

                "Federal Reserve",

                "US Dollar",

                "USD",

                "Interest Rate Policy",

                "Currency Impact"

            ),



            create_market_connection_v1(

                "US Dollar",

                "Gold Market",

                "Gold",

                "Inverse Relationship",

                "Precious Metal Impact"

            ),



            create_market_connection_v1(

                "Bond Yield",

                "Stock Market",

                "Equity",

                "Capital Allocation",

                "Risk Appetite"

            ),



            create_market_connection_v1(

                "Oil Market",

                "Inflation",

                "Energy",

                "Supply Cost",

                "Economic Pressure"

            )

        ]

    )



# ==========================================================
# FINANCIAL ASSET ENGINE
# ==========================================================


def financial_asset_engine_v1():


    assets = {


        "Currency Market":

        [

            "USD",

            "EUR",

            "JPY",

            "CNY"

        ],



        "Bond Market":

        [

            "US Treasury",

            "Government Bonds"

        ],



        "Equity Market":

        [

            "Technology",

            "Energy",

            "Financial"

        ],



        "Commodity Market":

        [

            "Gold",

            "Oil",

            "Copper"

        ]

    }


    return assets



# ==========================================================
# MARKET RELATIONSHIP ENGINE
# ==========================================================


def market_relationship_engine_v1():


    relationships = {


        "USD ↑":

        {

            "Gold":

            "Pressure",


            "Commodities":

            "Pressure",


            "Dollar Assets":

            "Support"

        },



        "USD ↓":

        {

            "Gold":

            "Support",


            "Commodities":

            "Support",


            "Dollar Assets":

            "Pressure"

        },



        "Yield ↑":

        {

            "Bond":

            "Attraction",


            "Risk Assets":

            "Pressure"

        }

    }


    return relationships



# ==========================================================
# FINANCIAL NETWORK DISPLAY
# ==========================================================


st.divider()


st.subheader(

    "📈 WEOS FINANCIAL MARKET CONNECTION NETWORK"

)



financial_df = pd.DataFrame(

    st.session_state.financial_market_network_v1

)



st.dataframe(

    financial_df,

    use_container_width=True,

    hide_index=True

)



# ==========================================================
# ASSET MAP DISPLAY
# ==========================================================


st.subheader(

    "🌐 Global Financial Asset Layers"

)



asset_layer = financial_asset_engine_v1()



asset_layer_df = pd.DataFrame(

    {

        "Market":

        asset_layer.keys(),


        "Assets":

        asset_layer.values()

    }

)



st.dataframe(

    asset_layer_df,

    use_container_width=True,

    hide_index=True

)



# ==========================================================
# RELATIONSHIP DISPLAY
# ==========================================================


st.subheader(

    "🔗 Economic Relationship Logic"

)



relationship = market_relationship_engine_v1()



for condition,data in relationship.items():


    st.markdown(

        f"""

### {condition}


{data}

        """

    )



# ==========================================================
# KẾT THÚC ĐOẠN 10
# FINANCIAL MARKET CONNECTION ENGINE V1
# ==========================================================
