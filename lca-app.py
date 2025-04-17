import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="LCA Tool for WCO Biofuel (1 MJ FU)", layout="wide")

# -----------------------------------------
# Sidebar Navigation
# -----------------------------------------
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", ["Introduction", "Inventory Inputs", "LCA Calculations", "Detailed Analysis", "Visualizations", "Reporting"])

# -----------------------------------------
# Default Emission Factors (dummy placeholders)
# -----------------------------------------
default_factors():
    return {
        'wco_collection_ef': 0.3,       # kg CO2 per km
        'methanol_ef': 1.5,            # kg CO2 per liter of methanol
        'koh_ef': 2.0,                 # kg CO2 per kg of KOH
        'energy_ef': 0.5,              # kg CO2 per kWh
        'wastewater_treat_ef': 0.2,    # kg CO2 per L of wastewater
        'glycerol_disposal_ef': 0.1    # kg CO2 per kg glycerol
    }

# -----------------------------------------
# Session State Initialization
# -----------------------------------------
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
        'reaction_energy_kwh': 0.06,
        'purification_water_l': 27.0,
        'drying_energy_kwh': 1.0,
        # Stage 3 inputs
        'distribution_distance_km': 223.0,
        'load_capacity_l': 200.0,
        # End-of-life inputs
        'glycerol_kg': 5.0,
        'wastewater_l': 54.0,
        # Emission factors
        **factors
    }

# -----------------------------------------
# Introduction
# -----------------------------------------
if section == "Introduction":
    st.title("LCA Tool: Biofuel from Waste Cooking Oil (WCO)")
    st.markdown("**Goal:** Evaluate environmental impacts of producing & using WCO biofuel in Malaysia vs diesel (Cradle-to-Grave, FU=1 MJ)")
    st.markdown("**System Boundary:** Raw acquisition → Production → Distribution → Use Phase → End-of-Life")

elif section == "Inventory Inputs":
    st.title("Inventory Data Inputs")
    inv = st.session_state.inv
    # Two columns for clarity
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Stage 1: Raw Material Acquisition")
        inv['wco_volume_l'] = st.number_input("WCO Volume (L)", value=inv['wco_volume_l'], step=1.0)
        inv['collection_distance_km'] = st.number_input("Collection Distance (km)", value=inv['collection_distance_km'], step=1.0)
        inv['methanol_l'] = st.number_input("Methanol Usage (L)", value=inv['methanol_l'], step=0.1)
        inv['koh_kg'] = st.number_input("KOH Catalyst (kg)", value=inv['koh_kg'], step=0.01)
        st.subheader("Stage 2: Production & Purification")
        inv['reaction_energy_kwh'] = st.number_input("Reaction Energy (kWh)", value=inv['reaction_energy_kwh'], step=0.01)
        inv['purification_water_l'] = st.number_input("Water for Washing (L)", value=inv['purification_water_l'], step=1.0)
        inv['drying_energy_kwh'] = st.number_input("Drying Energy (kWh)", value=inv['drying_energy_kwh'], step=0.1)
    with c2:
        st.subheader("Stage 3: Distribution")
        inv['distribution_distance_km'] = st.number_input("Distribution Distance (km)", value=inv['distribution_distance_km'], step=1.0)
        inv['load_capacity_l'] = st.number_input("Load Capacity (L)", value=inv['load_capacity_l'], step=1.0)
        st.subheader("End-of-Life")
        inv['glycerol_kg'] = st.number_input("Glycerol By-product (kg)", value=inv['glycerol_kg'], step=0.1)
        inv['wastewater_l'] = st.number_input("Wastewater (L)", value=inv['wastewater_l'], step=1.0)
    st.subheader("Emission Factors")
    inv['wco_collection_ef'] = st.number_input("Collection EF (kg CO2/km)", value=inv['wco_collection_ef'], step=0.01)
    inv['methanol_ef'] = st.number_input("Methanol EF (kg CO2/L)", value=inv['methanol_ef'], step=0.1)
    inv['koh_ef'] = st.number_input("KOH EF (kg CO2/kg)", value=inv['koh_ef'], step=0.1)
    inv['energy_ef'] = st.number_input("Energy EF (kg CO2/kWh)", value=inv['energy_ef'], step=0.01)
    inv['wastewater_treat_ef'] = st.number_input("Wastewater Treat EF (kg CO2/L)", value=inv['wastewater_treat_ef'], step=0.01)
    inv['glycerol_disposal_ef'] = st.number_input("Glycerol Disposal EF (kg CO2/kg)", value=inv['glycerol_disposal_ef'], step=0.01)

elif section == "LCA Calculations" or section == "Detailed Analysis":
    st.title("LCA Calculations & Stage Emissions")
    inv = st.session_state.inv
    # Compute per-stage emissions for 1 MJ FU
    # Stage 1: Collection + chemicals
    stage1 = (inv['wco_volume_l']/inv['load_capacity_l'] * inv['collection_distance_km'] * inv['wco_collection_ef']) + \
             (inv['methanol_l'] * inv['methanol_ef']) + \
             (inv['koh_kg'] * inv['koh_ef'])

    # Stage 2: Production & purification
    stage2 = (inv['reaction_energy_kwh'] * inv['energy_ef']) + \
             (inv['purification_water_l'] * inv['wastewater_treat_ef']) + \
             (inv['drying_energy_kwh'] * inv['energy_ef'])

    # Stage 3: Distribution transport
    stage3 = (inv['distribution_distance_km'] * inv['wco_collection_ef']) * (1.0/inv['load_capacity_l'])

    # End-of-Life: glycerol + wastewater
    stage5 = (inv['glycerol_kg'] * inv['glycerol_disposal_ef']) + \
             (inv['wastewater_l'] * inv['wastewater_treat_ef'])

    total = stage1 + stage2 + stage3 + stage5

    metrics = {
        'Stage 1 - Raw Material Acquisition (kg CO2)': stage1,
        'Stage 2 - Production & Purification (kg CO2)': stage2,
        'Stage 3 - Distribution (kg CO2)': stage3,
        'Stage 5 - End-of-Life (kg CO2)': stage5,
        'Total (kg CO2 per 1 MJ)': total
    }

    for k, v in metrics.items():
        st.write(f"**{k}:** {v:.4f}")

    if section == "Detailed Analysis":
        st.markdown("---")
        st.header("Interpretation & Analysis")
        st.markdown(f"- **Stage 1** contributes {stage1/total*100:.1f}% of total emissions, dominated by chemical production and WCO transport.")
        st.markdown(f"- **Stage 2** contributes {stage2/total*100:.1f}% of total emissions, driven by energy use in reaction and drying.")
        st.markdown(f"- **Stage 3** contributes {stage3/total*100:.1f}% of total emissions, reflecting distribution distances.")
        st.markdown(f"- **End-of-Life** contributes {stage5/total*100:.1f}% from glycerol disposal and wastewater treatment.")
        st.markdown("**Opportunities for Impact Reduction:**")
        st.markdown("- Improve conversion efficiency to reduce chemical usage.")
        st.markdown("- Switch to renewable energy for heating and drying.")
        st.markdown("- Optimize distribution logistics or increase vehicle load capacity.")

elif section == "Visualizations":
    st.title("Emissions Visualization by Stage")
    inv = st.session_state.inv
    # reuse metrics calculation
    values = list(metrics.values())[:-1]
    labels = [k.split(' - ')[1].split(' (')[0] for k in list(metrics.keys())[:-1]]
    df = pd.DataFrame({'Stage': labels, 'Emissions': values})
    fig = px.pie(df, names='Stage', values='Emissions', title='Emission Breakdown per Stage')
    st.plotly_chart(fig, use_container_width=True)

elif section == "Reporting":
    st.title("Downloadable LCA Report")
    df_report = pd.DataFrame(list(metrics.items()), columns=['Metric','Value (kg CO2)'])
    st.dataframe(df_report)
    csv = df_report.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV Report", data=csv, file_name='lca_report.csv')

# Footer
st.markdown("---")
st.markdown("*LCA Tool for WCO Biofuel | FU = 1 MJ | Cradle-to-Grave* ")
