import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from streamlit.runtime.scriptrunner import get_script_run_ctx

# Page configuration
st.set_page_config(page_title="LCA Tool for WCO Biofuel (1 MJ FU)", layout="wide")

# Sidebar navigation with hierarchical structure
st.sidebar.title("Navigation")
main_menu = st.sidebar.radio(
    "Main Menu", 
    [
        "Introduction", 
        "Inventory Inputs", 
        "LCA Calculations", 
        "Detailed Analysis", 
        "Results & Comparison"
    ]
)

# Default emission factors and inventory initialization
def default_factors():
    return {
        'wco_collection_ef': 0.3,       # kg CO2 per km
        'methanol_ef': 1.5,            # kg CO2 per liter
        'koh_ef': 2.0,                 # kg CO2 per kg
        'energy_ef': 0.5,              # kg CO2 per kWh
        'electricity_ef': 0.6,         # g CO2-eq per MJ of electricity
        'wastewater_treat_ef': 0.2,    # kg CO2 per L
        'glycerol_disposal_ef': 0.1    # kg CO2 per kg
    }

if 'inv' not in st.session_state:
    factors = default_factors()
    st.session_state.inv = {
        # Functional unit: 1 MJ
        'fu_mj': 1.0,
        # Stage 1 inputs
        'wco_volume_l': 30.0,
        'collection_distance_km': 24.6,
        'methanol_l': 8.54,
        'koh_kg': 0.45,
        # Stage 2 inputs
        'reaction_energy_mj': 0.06 * 3.6,  # converting kWh to MJ if needed
        'purification_water_l': 27.0,
        'drying_energy_mj': 1.0 * 3.6,
        # Stage 3 inputs
        'distribution_distance_km': 223.0,
        'load_capacity_l': 200.0,
        # End-of-life inputs
        'glycerol_kg': 5.0,
        'wastewater_l': 54.0,
        # Emission factors
        **factors
    }
inv = st.session_state.inv

# Define df_radar globally to avoid NameError
df_radar = pd.DataFrame({
    "Category": ["CC", "HT", "FD", "PMF", "POF"],
    "Biofuel Diesel": [934.95, 783.93, 671.66, 5.06, 8.97],
    "Fossil Diesel": [1000, 900, 800, 6, 10]
})

# Ensure metrics is calculated before any section that uses it
# Compute stage emissions per 1 MJ FU
stage1 = (inv['collection_distance_km'] * inv['wco_collection_ef']) + (inv['methanol_l'] * inv['methanol_ef']) + (inv['koh_kg'] * inv['koh_ef'])
stage2 = (inv['reaction_energy_mj'] * inv['energy_ef']) + (inv['purification_water_l'] * inv['wastewater_treat_ef']) + (inv['drying_energy_mj'] * inv['energy_ef'])
stage3 = (inv['distribution_distance_km'] * inv['wco_collection_ef']) / inv['load_capacity_l']
stage5 = (inv['glycerol_kg'] * inv['glycerol_disposal_ef']) + (inv['wastewater_l'] * inv['wastewater_treat_ef'])
total = stage1 + stage2 + stage3 + stage5
metrics = {
    'Stage 1 Acquisition': stage1,
    'Stage 2 Production': stage2,
    'Stage 3 Distribution': stage3,
    'Stage 5 End-of-Life': stage5,
    'Total': total
}

# Sections implementation
if main_menu == "Introduction":
    st.title("LCA Tool: Biofuel from Waste Cooking Oil (WCO)")
    st.markdown("**Goal:** Evaluate environmental impacts of producing & using WCO biofuel in Malaysia vs diesel (Cradle-to-Grave, FU=1 MJ)")
    st.markdown("**System Boundary:** Raw acquisition → Production → Distribution → Use Phase → End-of-Life")
    st.markdown("**Functional Unit:** 1 MJ of biofuel")
    # System boundary diagram
    st.image("https://freeimage.host/i/30mwsp4", caption="System Boundary Diagram", use_container_width=True)

elif main_menu == "Inventory Inputs":
    st.title("Inventory Data Inputs")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Stage 1: Raw Material Acquisition")
        inv['wco_volume_l'] = st.number_input("WCO Volume (L)", value=inv['wco_volume_l'], step=1.0)
        inv['collection_distance_km'] = st.number_input("Collection Distance (km)", value=inv['collection_distance_km'], step=1.0)
        inv['methanol_l'] = st.number_input("Methanol Usage (L)", value=inv['methanol_l'], step=0.1)
        inv['koh_kg'] = st.number_input("KOH Catalyst (kg)", value=inv['koh_kg'], step=0.01)
    with c2:
        st.subheader("Stage 2: Production & Purification")
        inv['reaction_energy_mj'] = st.number_input("Reaction Energy (MJ)", value=inv['reaction_energy_mj'], step=0.1)
        inv['purification_water_l'] = st.number_input("Water for Washing (L)", value=inv['purification_water_l'], step=1.0)
        inv['drying_energy_mj'] = st.number_input("Drying Energy (MJ)", value=inv['drying_energy_mj'], step=0.1)
    st.subheader("Stage 3: Distribution")
    inv['distribution_distance_km'] = st.number_input("Distribution Distance (km)", value=inv['distribution_distance_km'], step=1.0)
    inv['load_capacity_l'] = st.number_input("Load Capacity (L)", value=inv['load_capacity_l'], step=1.0)
    st.subheader("End-of-Life")
    inv['glycerol_kg'] = st.number_input("Glycerol By-product (kg)", value=inv['glycerol_kg'], step=0.1)
    inv['wastewater_l'] = st.number_input("Wastewater (L)", value=inv['wastewater_l'], step=1.0)
    st.subheader("Emission Factors")
    for ef in ['wco_collection_ef', 'methanol_ef', 'koh_ef', 'energy_ef', 'electricity_ef', 'wastewater_treat_ef', 'glycerol_disposal_ef']:
        inv[ef] = st.number_input(f"{ef.replace('_', ' ').title()}", value=inv[ef], step=0.01)

elif main_menu in ("LCA Calculations", "Detailed Analysis"):
    st.title("LCA Calculations & Stage Emissions")
    for k, v in metrics.items():
        st.write(f"**{k}:** {v:.4f} kg CO2")
    if main_menu == "Detailed Analysis":
        st.markdown("---")
        st.header("Interpretation & Analysis")
        for i, (k, v) in enumerate(metrics.items()):
            if k != 'Total':
                st.markdown(f"- **{k}** contributes {v/total*100:.1f}% of total emissions.")
        st.markdown("**Opportunities for Impact Reduction:**")
        st.markdown("- Improve conversion efficiency.")
        st.markdown("- Switch to renewable electricity.")
        st.markdown("- Optimize distribution logistics.")

elif main_menu == "Results & Comparison":
    st.title("Results & Comparison")


        
    # Overview Section
    st.header("Overview: Biofuel Diesel vs. Fossil Diesel")

    # High-level summary
    st.subheader("Total Impact Summary")
    total_biofuel = metrics['Total']
    total_fossil = 2897.2125  # Example total for fossil diesel
    summary_data = {
        "Metric": ["Total Impact (kg CO2)", "Water Depletion (m³)", "CO2 Emissions (kg)"],
        "Biofuel Diesel": [f"{total_biofuel:.2f}", "8.8", "2317.77"],
        "Fossil Diesel": [f"{total_fossil:.2f}", "11", "2897.21"]
    }
    df_summary = pd.DataFrame(summary_data)
    st.table(df_summary)

    # Pie chart for lifecycle stages
    st.subheader("Lifecycle Stage Contributions")
    labels = [k for k in metrics if k != 'Total']
    values = [metrics[k] for k in labels]
    fig_pie = px.pie(
        names=labels, values=values, title="Biofuel Diesel Lifecycle Stage Contributions"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # Adding detailed data table for better clarity
    st.subheader("Detailed Impact Data")

    # Midpoint and Endpoint categories
    midpoint_endpoint_data = {
        "Midpoint Impact Categories": [
            "Climate change", "Ozone depletion", "Fossil fuel depletion", "Human toxicity", "Ionizing radiation", "Mineral resource depletion", "Particulate matter formation", "Photochemical oxidant formation", "Water depletion"
        ],
        "Abbreviation": ["CC", "OD", "FD", "HT", "IR", "MRD", "PMF", "POF", "WD"],
        "Units": ["kg CO2 eq", "kg CFC-11 eq", "kg oil eq", "kg 1,4-DB eq", "kg U235 eq", "kg Fe eq", "kg PM-2.5 eq", "kg NOx eq", "m³"],
        "Endpoint Impact Categories": [
            "Human health", "Ecosystem diversity", "Resource availability", "", "", "", "", "", ""
        ],
        "Abbreviation (Endpoint)": ["HH", "ED", "RA", "", "", "", "", "", ""],
        "Units (Endpoint)": ["DALY", "Species year", "$", "", "", "", "", "", ""]
    }
    df_midpoint_endpoint = pd.DataFrame(midpoint_endpoint_data)
    st.table(df_midpoint_endpoint)

    # Detailed impact data
    impact_data = {
        "Impact Category": ["CC (kg CO2 eq)", "OD (kg CFC-11 eq)", "IR (kg U235 eq)", "PMF (kg PM-2.5 eq)", "POF (kg NOx eq)", "HT (kg 1,4-DB eq)", "WD (m³)", "MD (kg Fe eq)", "FD (kg oil eq)"],
        "Collection": [175, 0, 0.84, 0.28, 0.74, 45.39, 1.58, 0.45, 40.95],
        "Pretreatment": [158.87, 0, 3.28, 0.35, 0.48, 70.08, 0.66, 1.62, 32.84],
        "Transesterification": [934.95, 0, 8.19, 2.19, 3.15, 332.36, 1.77, 8.74, 280.26],
        "Transportation": [114, 0, 0.03, 0.05, 1.45, 3.74, 3.02, 0.07, 37.35],
        "Use Phase": [934.95, 0, 8.19, 2.19, 3.15, 332.36, 1.77, 8.74, 280.26],
        "Biofuel Diesel": [2317.77, 0, 20.53, 5.06, 8.97, 783.93, 8.8, 19.62, 671.66],
        "Fossil Diesel": [2897.2125, 0, 25.6625, 6.325, 11.2125, 979.9125, 11, 24.525, 839.575]
    }
    df_impact = pd.DataFrame(impact_data)
    st.table(df_impact)

    # Life cycle stage data
    lifecycle_data = {
        "Life Cycle Stage": ["Raw Material Acquisition", "Production", "Distribution", "Use Phase", "End-of-Life", "Total"],
        "Energy Use (MJ/MJ)": [0.01, 0.07, 0.0205, 0.9, 0.012, 1.0025],
        "GWP (g CO2-eq/MJ)": [5.6, 22, 8.3, 70, 4.2, 110],
        "NOx (mg/MJ)": [10, 20, 15, 50, 5, 100],
        "PM (mg/MJ)": [2, 5, 3, 10, 1, 21],
        "HC (mg/MJ)": [3, 8, 5, 15, 2, 33],
        "Water Pollution (liters)": [0, 1.46, 0, 0, 0.5, 1.96],
        "Solid Waste (g)": [0, 5, 0, 0, 2, 7]
    }
    df_lifecycle = pd.DataFrame(lifecycle_data)
    st.table(df_lifecycle)

    # Heatmap for impact categories
    st.subheader("Impact Categories Heatmap")
    data_heatmap = {
        "Impact Category": [
            "CC", "OD", "IR", "PMF", "POF", "HT", "WD", "MRD", "FD"
        ],
        "Collection": [175, 0, 0.84, 0.28, 0.74, 45.39, 1.58, 0.45, 40.95],
        "Pretreatment": [158.87, 0, 3.28, 0.35, 0.48, 70.08, 0.66, 1.62, 32.84],
        "Transesterification": [934.95, 0, 8.19, 2.19, 3.15, 332.36, 1.77, 8.74, 280.26],
        "Transportation": [114, 0, 0.03, 0.05, 1.45, 3.74, 3.02, 0.07, 37.35],
        "Use Phase": [934.95, 0, 8.19, 2.19, 3.15, 332.36, 1.77, 8.74, 280.26],
        "Biofuel Diesel": [2317.77, 0, 20.53, 5.06, 8.97, 783.93, 8.8, 19.62, 671.66],
        "Fossil Diesel": [2897.2125, 0, 25.6625, 6.325, 11.2125, 979.9125, 11, 24.525, 839.575]
    }
    df_heatmap = pd.DataFrame(data_heatmap).set_index("Impact Category")
    fig_heatmap = sns.heatmap(df_heatmap, annot=True, cmap="coolwarm")
    st.pyplot(fig_heatmap.figure)

    # Lifecycle Stages Section
    st.header("Lifecycle Stages: Biofuel Diesel vs. Fossil Diesel")

    # Bar charts for lifecycle stages
    st.subheader("Impact Comparison by Lifecycle Stage")
    df_stage = pd.DataFrame({
        "Stage": ["Collection", "Pretreatment", "Transesterification", "Transportation", "Use Phase"],
        "Biofuel Diesel": [175, 158.87, 934.95, 114, 934.95],
        "Fossil Diesel": [200, 180, 1000, 120, 1000]
    })
    fig_bar = px.bar(
        df_stage, x="Stage", y=["Biofuel Diesel", "Fossil Diesel"],
        barmode="group", title="Lifecycle Stage Comparison"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Line graph for cumulative impact
    st.subheader("Cumulative Impact Across Stages")
    df_cumulative = df_stage.copy()
    df_cumulative["Biofuel Diesel"] = df_cumulative["Biofuel Diesel"].cumsum()
    df_cumulative["Fossil Diesel"] = df_cumulative["Fossil Diesel"].cumsum()
    fig_line = px.line(
        df_cumulative, x="Stage", y=["Biofuel Diesel", "Fossil Diesel"],
        title="Cumulative Impact Across Stages"
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # Treemaps for most impactful stages
    st.subheader("Most Impactful Stages by Category")
    df_treemap = pd.DataFrame({
        "Category": ["CC", "HT", "FD"],
        "Stage": ["Transesterification", "Use Phase", "Collection"],
        "Impact": [934.95, 934.95, 175]
    })
    fig_treemap = px.treemap(
        df_treemap, path=["Category", "Stage"], values="Impact",
        title="Most Impactful Stages by Category"
    )
    st.plotly_chart(fig_treemap, use_container_width=True)

    # Impact Categories Section
    st.header("Impact Categories: Biofuel Diesel vs. Fossil Diesel")

    # Ensure the 'Reduction' column is added to the DataFrame before using it in the chart
    if 'Reduction' not in df_radar.columns:
        df_radar["Reduction"] = (
            (df_radar["Fossil Diesel"] - df_radar["Biofuel Diesel"]) / df_radar["Fossil Diesel"] * 100
        )

    # Radar chart for all categories
    st.subheader("Radar Chart: Impact Categories")
    fig_radar = px.line_polar(
        df_radar, r="Biofuel Diesel", theta="Category", line_close=True,
        title="Radar Chart: Biofuel Diesel"
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # Grouped bar charts for each category
    st.subheader("Grouped Bar Charts: Impact Categories")
    fig_grouped_bar = px.bar(
        df_radar, x="Category", y=["Biofuel Diesel", "Fossil Diesel"],
        barmode="group", title="Grouped Bar Charts"
    )
    st.plotly_chart(fig_grouped_bar, use_container_width=True)

    # Percentage reduction charts
    st.subheader("Percentage Reduction: Biofuel vs. Fossil Diesel")
    fig_reduction = px.bar(
        df_radar, x="Category", y="Reduction", title="Percentage Reduction"
    )
    st.plotly_chart(fig_reduction, use_container_width=True)

    # Biofuel vs. Fossil Diesel Section
    st.header("Biofuel Diesel vs. Fossil Diesel")

    # Side-by-side bar charts
    st.subheader("Side-by-Side Bar Charts")
    fig_side_by_side = px.bar(
        df_radar, x="Category", y=["Biofuel Diesel", "Fossil Diesel"],
        barmode="group", title="Side-by-Side Bar Charts"
    )
    st.plotly_chart(fig_side_by_side, use_container_width=True)

    # Line graphs for percentage reduction
    st.subheader("Percentage Reduction Line Graph")
    if 'Reduction' not in df_radar.columns:
        df_radar["Reduction"] = (
            (df_radar["Fossil Diesel"] - df_radar["Biofuel Diesel"]) / df_radar["Fossil Diesel"] * 100
        )
    fig_line_reduction = px.line(
        df_radar, x="Category", y="Reduction",
        title="Percentage Reduction Line Graph"
    )
    st.plotly_chart(fig_line_reduction, use_container_width=True)
        

    # Icon-based visuals for key metrics
    st.subheader("Key Metrics")
    st.markdown(
        "- **Water Depletion:** Biofuel Diesel uses 8.8 m³ vs. Fossil Diesel 11 m³\n"
        "- **CO2 Emissions:** Biofuel Diesel emits 2317.77 kg vs. Fossil Diesel 2897.21 kg"
    )

# Footer
st.markdown("---")
st.markdown("*LCA Tool for WCO Biofuel | FU = 1 MJ | Cradle-to-Grave*")
