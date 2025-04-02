import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Set up the Streamlit page configuration
st.set_page_config(page_title="LCA Tool for Biofuel Production", layout="wide")

# --------------------------------------------------
# Sidebar Navigation
# --------------------------------------------------
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", 
                           ["Introduction", "Input Data", "LCA Calculations", "Visualizations", "Reporting"])

# --------------------------------------------------
# Session State Initialization
# --------------------------------------------------
if "inputs" not in st.session_state:
    st.session_state.inputs = {
         "waste_volume": 1000.0,                   # in liters
         "collection_distance": 10.0,              # in km
         "collection_frequency": 2,                # times per day
         "conversion_efficiency": 80.0,            # in percentage
         "processing_energy_consumption": 0.5,     # kWh per liter
         "emission_factor_collection": 0.3,        # kg CO2 per km
         "emission_factor_processing": 0.4,        # kg CO2 per kWh
         "emission_factor_distribution": 0.2       # kg CO2 per km
    }

# --------------------------------------------------
# Placeholder for External API Integration
# --------------------------------------------------
@st.cache_data
def fetch_external_emission_factors(region="default"):
    """
    This function simulates fetching regional emission factors from an external API.
    In a production setting, replace the below dummy values with an API call.
    """
    # Dummy external data
    return {
        "emission_factor_collection": 0.3,
        "emission_factor_processing": 0.4,
        "emission_factor_distribution": 0.2
    }

# --------------------------------------------------
# LCA Calculation Function with Caching
# --------------------------------------------------
@st.cache_data
def calculate_lca(waste_volume, collection_distance, collection_frequency,
                  conversion_efficiency, processing_energy_consumption,
                  emission_factor_collection, emission_factor_processing, emission_factor_distribution):
    """
    Performs the Life Cycle Assessment calculations based on user inputs.
    
    Calculation logic (simplified):
      - Collection emissions: scales with waste volume, distance, and frequency.
      - Processing emissions: based on energy consumption and conversion efficiency.
      - Distribution emissions: similar to collection.
    """
    collection_emissions = (waste_volume / 10) * collection_distance * collection_frequency * emission_factor_collection
    processing_emissions = (waste_volume * processing_energy_consumption) * emission_factor_processing * (100 / conversion_efficiency)
    distribution_emissions = (waste_volume / 10) * collection_distance * emission_factor_distribution
    total_emissions = collection_emissions + processing_emissions + distribution_emissions
    net_emissions = total_emissions  # Offsets can be integrated here in the future.
    return {
         "Collection Emissions (kg CO2)": collection_emissions,
         "Processing Emissions (kg CO2)": processing_emissions,
         "Distribution Emissions (kg CO2)": distribution_emissions,
         "Total Emissions (kg CO2)": total_emissions,
         "Net Emissions (kg CO2)": net_emissions
    }

# --------------------------------------------------
# Section: Introduction
# --------------------------------------------------
if section == "Introduction":
    st.title("LCA Tool for Biofuel Production from Waste Cooking Oil")
    st.markdown("### Overview")
    st.write(
        """
        This innovative online tool is designed for environmental engineers, sustainability consultants,
        academic researchers, policymakers, and non-specialists. It enables users to evaluate the environmental
        impact of biofuel production from waste cooking oil through a comprehensive life cycle assessment (LCA).
        The tool features:
        
        - **User-Friendly Input:** Use intuitive widgets to enter data.
        - **Real-Time Calculations:** Dynamic simulation of emissions and energy flows.
        - **Interactive Visualizations:** Sankey diagrams, bar charts, and pie charts.
        - **Detailed Reporting:** Generate exportable CSV (and in future PDF) reports.
        """
    )
    st.markdown("### User Requirements & Personas")
    st.markdown(
        """
        **Target Audience:**
        - Environmental Engineers
        - Sustainability Consultants
        - Academic Researchers
        - Policymakers
        - Community Stakeholders
        
        **Key User Needs:**
        - **Ease-of-Use:** Step-by-step guidance with clear input instructions.
        - **Real-Time Feedback:** Immediate update of calculations and visualizations.
        - **Detailed Reporting:** Exportable reports summarizing key LCA metrics.
        - **Accessibility:** Mobile responsive and accessible interface.
        """
    )
    st.markdown("### Future Enhancements")
    st.markdown(
        """
        Future versions may include:
        - Integration with machine learning models for predictive insights.
        - Additional environmental impact metrics (e.g., water usage, land footprint).
        - Extended API support for real-time regulatory data.
        - Enhanced multi-user collaboration and secure data management.
        """
    )

# --------------------------------------------------
# Section: Input Data
# --------------------------------------------------
elif section == "Input Data":
    st.title("Input Data & External Data Integration")
    st.markdown("Enter the parameters needed for the LCA analysis using the input widgets below.")

    # Two-column layout for better organization
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Waste & Collection Data")
        st.session_state.inputs["waste_volume"] = st.number_input(
            "Waste Oil Volume (liters)", 
            min_value=0.0, 
            value=st.session_state.inputs["waste_volume"], 
            step=100.0
        )
        st.session_state.inputs["collection_distance"] = st.number_input(
            "Average Collection Distance (km)", 
            min_value=0.0, 
            value=st.session_state.inputs["collection_distance"], 
            step=1.0
        )
        st.session_state.inputs["collection_frequency"] = st.number_input(
            "Collection Frequency (times per day)", 
            min_value=0, 
            value=st.session_state.inputs["collection_frequency"], 
            step=1
        )
    with col2:
        st.subheader("Processing & Emission Factors")
        st.session_state.inputs["conversion_efficiency"] = st.slider(
            "Conversion Efficiency (%)", 
            min_value=0.0, 
            max_value=100.0, 
            value=st.session_state.inputs["conversion_efficiency"]
        )
        st.session_state.inputs["processing_energy_consumption"] = st.number_input(
            "Processing Energy Consumption (kWh per liter)", 
            min_value=0.0, 
            value=st.session_state.inputs["processing_energy_consumption"], 
            step=0.1
        )
        # Option to fetch external emission factors
        if st.button("Fetch Regional Emission Factors"):
            external_factors = fetch_external_emission_factors()
            st.session_state.inputs["emission_factor_collection"] = external_factors["emission_factor_collection"]
            st.session_state.inputs["emission_factor_processing"] = external_factors["emission_factor_processing"]
            st.session_state.inputs["emission_factor_distribution"] = external_factors["emission_factor_distribution"]
            st.success("Emission factors updated from external data source.")
        st.session_state.inputs["emission_factor_collection"] = st.number_input(
            "Emission Factor for Collection (kg CO2 per km)", 
            min_value=0.0, 
            value=st.session_state.inputs["emission_factor_collection"], 
            step=0.05
        )
        st.session_state.inputs["emission_factor_processing"] = st.number_input(
            "Emission Factor for Processing (kg CO2 per kWh)", 
            min_value=0.0, 
            value=st.session_state.inputs["emission_factor_processing"], 
            step=0.05
        )
        st.session_state.inputs["emission_factor_distribution"] = st.number_input(
            "Emission Factor for Distribution (kg CO2 per km)", 
            min_value=0.0, 
            value=st.session_state.inputs["emission_factor_distribution"], 
            step=0.05
        )
    st.markdown("_(Note: Future releases will include file uploaders for historical data and advanced API integrations.)_")

# --------------------------------------------------
# Section: LCA Calculations
# --------------------------------------------------
elif section == "LCA Calculations":
    st.title("Life Cycle Assessment Calculations")
    inputs = st.session_state.inputs
    results = calculate_lca(
         waste_volume=inputs["waste_volume"],
         collection_distance=inputs["collection_distance"],
         collection_frequency=inputs["collection_frequency"],
         conversion_efficiency=inputs["conversion_efficiency"],
         processing_energy_consumption=inputs["processing_energy_consumption"],
         emission_factor_collection=inputs["emission_factor_collection"],
         emission_factor_processing=inputs["emission_factor_processing"],
         emission_factor_distribution=inputs["emission_factor_distribution"]
    )
    st.markdown("### Calculated LCA Metrics")
    for key, value in results.items():
         st.write(f"**{key}:** {value:.2f} kg CO2")
    st.markdown("These calculations update in real time as you adjust the input parameters.")

# --------------------------------------------------
# Section: Interactive Visualizations
# --------------------------------------------------
elif section == "Visualizations":
    st.title("Interactive Visualizations")
    inputs = st.session_state.inputs
    results = calculate_lca(
         waste_volume=inputs["waste_volume"],
         collection_distance=inputs["collection_distance"],
         collection_frequency=inputs["collection_frequency"],
         conversion_efficiency=inputs["conversion_efficiency"],
         processing_energy_consumption=inputs["processing_energy_consumption"],
         emission_factor_collection=inputs["emission_factor_collection"],
         emission_factor_processing=inputs["emission_factor_processing"],
         emission_factor_distribution=inputs["emission_factor_distribution"]
    )
    
    # Bar Chart: Emissions by Stage
    df_bar = pd.DataFrame({
         "Stage": ["Collection", "Processing", "Distribution"],
         "Emissions (kg CO2)": [
             results["Collection Emissions (kg CO2)"],
             results["Processing Emissions (kg CO2)"],
             results["Distribution Emissions (kg CO2)"]
         ]
    })
    fig_bar = px.bar(df_bar, x="Stage", y="Emissions (kg CO2)", 
                     title="Emissions by Life Cycle Stage", text_auto=True)
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Sankey Diagram: Emissions Flow
    labels = ["Collection", "Processing", "Distribution", "Total Emissions"]
    node = dict(label=labels, pad=15, thickness=20)
    link = dict(
         source=[0, 1, 2],
         target=[1, 2, 3],
         value=[
             results["Collection Emissions (kg CO2)"],
             results["Processing Emissions (kg CO2)"],
             results["Distribution Emissions (kg CO2)"]
         ]
    )
    fig_sankey = go.Figure(go.Sankey(node=node, link=link))
    fig_sankey.update_layout(title_text="Sankey Diagram of Emissions Flow", font_size=10)
    st.plotly_chart(fig_sankey, use_container_width=True)
    
    # Pie Chart: Emission Breakdown
    fig_pie = px.pie(df_bar, names="Stage", values="Emissions (kg CO2)", title="Emission Breakdown")
    st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("All visualizations update dynamically as you modify the inputs.")

# --------------------------------------------------
# Section: Reporting & Exporting
# --------------------------------------------------
elif section == "Reporting":
    st.title("Reporting & Exporting Results")
    inputs = st.session_state.inputs
    results = calculate_lca(
         waste_volume=inputs["waste_volume"],
         collection_distance=inputs["collection_distance"],
         collection_frequency=inputs["collection_frequency"],
         conversion_efficiency=inputs["conversion_efficiency"],
         processing_energy_consumption=inputs["processing_energy_consumption"],
         emission_factor_collection=inputs["emission_factor_collection"],
         emission_factor_processing=inputs["emission_factor_processing"],
         emission_factor_distribution=inputs["emission_factor_distribution"]
    )
    # Create a DataFrame for reporting
    df_results = pd.DataFrame(list(results.items()), columns=["LCA Metric", "Value (kg CO2)"])
    st.dataframe(df_results)
    
    # CSV Download Button for the report
    csv = df_results.to_csv(index=False).encode('utf-8')
    st.download_button(
         label="Download Report as CSV",
         data=csv,
         file_name="lca_report.csv",
         mime="text/csv"
    )
    
    st.markdown("### Future Reporting Enhancements")
    st.markdown(
        """
        Future updates may include:
        - PDF report generation with detailed insights.
        - Additional visual export options.
        - Integration with regulatory data sources.
        """
    )

# --------------------------------------------------
# Footer: Security & Scalability Note
# --------------------------------------------------
st.markdown("---")
st.markdown(
    """
    **Security & Scalability Note:**  
    This tool leverages HTTPS and Streamlit’s session state for secure data handling. Future versions will include 
    robust user authentication, data encryption, and cloud-based scaling strategies.
    """
)
