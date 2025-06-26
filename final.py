import pandas as pd
from pyvis.network import Network
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Irish Food Network Map", layout="wide")

# Theme selection
mode = st.sidebar.selectbox("Select Theme Mode", ["Light", "Dark"])

if mode == "Light":
    bgcolor = "#ffffff"
    font_color = "#000000"
    node_color = "#2E8B57"
    pos_edge_color = "green"
    neg_edge_color = "red"
    instruction_bg = "#e8f5e9"
    instruction_text_color = "#000"
    instruction_header_color = "#2E8B57"
else:
    bgcolor = "#121212"
    font_color = "#ddd"
    node_color = "#32cd32"
    pos_edge_color = "lime"
    neg_edge_color = "tomato"
    instruction_bg = "#222"
    instruction_text_color = "#ccc"
    instruction_header_color = "#90ee90"

# Header
st.markdown(f"""
    <h1 style='text-align: center; color: {instruction_header_color};'>Stakeholder Network Mapping Tool</h1>
    <p style='text-align: center; font-size:18px; color: {instruction_text_color};'>
        Exploring stakeholder influence networks
    </p>
    <hr style="border-top: 1px solid #bbb;">
""", unsafe_allow_html=True)

# Load Excel data directly (no file upload)
file_path = "irish_food_system_network.xlsx"
nodes_df = pd.read_excel(file_path, sheet_name="Nodes")
links_df = pd.read_excel(file_path, sheet_name="Links")

# Optional Tier Filter
if "Tier" in nodes_df.columns:
    st.sidebar.markdown("### 🔍 Filter by Tier")
    available_tiers = ["All"] + sorted(nodes_df["Tier"].dropna().unique().tolist())
    selected_tier = st.sidebar.selectbox("Select a Tier", available_tiers)

    if selected_tier != "All":
        nodes_df = nodes_df[nodes_df["Tier"] == selected_tier]
        valid_node_ids = set(nodes_df["NodeID"])
        links_df = links_df[
            links_df["SourceID"].isin(valid_node_ids) &
            links_df["TargetID"].isin(valid_node_ids)
        ]

# Instructions and Legend
st.markdown(f"""
<div style="background-color:{instruction_bg}; padding:15px; border-radius:8px; margin-bottom:15px; color:{instruction_text_color};">
    <h3 style="color:{instruction_header_color};">🛠️ How to interact with the network graph:</h3>
    <ul>
        <li>Drag nodes to reposition.</li>
        <li>Zoom in/out with mouse wheel or touchpad.</li>
        <li>Hover over nodes or edges to see details.</li>
        <li>Click nodes to highlight connected edges.</li>
    </ul>
    <h3 style="color:{instruction_header_color};">📖 Legend:</h3>
    <ul>
        <li><span style="color:{node_color};">●</span> Nodes represent stakeholders/entities.</li>
        <li><span style="color:{pos_edge_color};">───</span> Positive influence/support edges.</li>
        <li><span style="color:{neg_edge_color};">───</span> Negative influence/obstacle edges.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Build Pyvis network
net = Network(height="900px", width="100%", directed=True, bgcolor=bgcolor, font_color=font_color)
net.barnes_hut(
    gravity=-20000,
    central_gravity=0.3,
    spring_length=150,
    spring_strength=0.05,
    damping=0.25
)
net.toggle_physics(True)

for _, row in nodes_df.iterrows():
    net.add_node(
        row["NodeID"],
        label=row["Name"],
        title=f'{row["Type"]}: {row.get("Description", "")}',
        shape="dot",
        size=15,
        color=node_color
    )

for _, row in links_df.iterrows():
    color = pos_edge_color if row["Polarity"] == "+" else neg_edge_color
    net.add_edge(
        row["SourceID"],
        row["TargetID"],
        title=f'{row["InfluenceType"]} ({row["Strength"]})',
        color=color
    )

net.save_graph("food_network.html")

st.markdown("### 🌐 Interactive Network Map")
with open("food_network.html", "r", encoding="utf-8") as f:
    html = f.read()
    components.html(html, height=900, scrolling=True)
