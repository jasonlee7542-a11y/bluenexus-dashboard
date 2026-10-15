import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="BlueNexus Dashboard", layout="wide")
st.title("🌊 BlueNexus Industrial Telemetry Dashboard")

# Simple Password Protection
password = st.text_input("Enter password to access dashboard:", type="password")
if password != "blueNEXUS!":
    st.warning("Please enter the correct password to view the BlueNexus pipeline.")
    st.stop()

plant = st.sidebar.selectbox("Select Plant", ["Plant A", "Plant B"])
st.write(f"Currently viewing data for **{plant}**")

file_name = "plant_A_equipment_daily.csv" if plant == "Plant A" else "plant_B_equipment_daily.csv"

try:
    df = pd.read_csv(file_name)
    
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        x_axis_col = 'date'
    else:
        x_axis_col = df.columns[0] 
        
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    # --- OVERLAY CHART SECTION ---
    st.subheader("Diagnostic Overlay (Shape & Trend Correlation)")
    st.write("Select variables to overlay using the checkboxes below.")
    
    selected_cols = []
    
    col1, col2, col3 = st.columns(3)
    
    for i, col_name in enumerate(numeric_cols):
        target_col = [col1, col2, col3][i % 3] 
        with target_col:
            is_checked = st.checkbox(col_name, value=(i < 2))
            if is_checked:
                selected_cols.append(col_name)
                
    st.divider()
    
    normalize = st.checkbox("Normalize variables (Scale everything from 0 to 100%)", value=True)
    
    if len(selected_cols) > 0:
        plot_df = df.copy()
        
        if normalize:
            for col in selected_cols:
                min_val = plot_df[col].min()
                max_val = plot_df[col].max()
                if max_val != min_val:
                    plot_df[col] = ((plot_df[col] - min_val) / (max_val - min_val)) * 100
                else:
                    plot_df[col] = 0 
            y_label = "Normalized Scale (0 = Min, 100 = Max)"
        else:
            y_label = "Raw Sensor Values"

        fig_line = px.line(
            plot_df, 
            x=x_axis_col, 
            y=selected_cols, 
            title=f"{plant}: Telemetry Overlay"
        )
        
        fig_line.update_layout(
            template="plotly_white",
            xaxis_title="Date",
            yaxis_title=y_label,
            legend_title="Variables",
            hovermode="x unified" 
        )
        
        st.plotly_chart(fig_line, use_container_width=True, theme=None)
    else:
        st.warning("Please check at least one box above to render the chart.")
    
    # --- NEW DISTRIBUTION ANALYSIS SECTION ---
    st.divider()
    st.subheader("Statistical Distribution Analysis")
    st.write("Select a single variable below to inspect its data distribution, quartiles, and outliers.")
    
    dist_var = st.selectbox("Select variable for distribution:", numeric_cols)
    
    if dist_var:
        fig_box = px.box(
            df, 
            y=dist_var, 
            title=f"Distribution of {dist_var}"
        )
        
        fig_box.update_traces(boxmean=True)
        fig_box.update_layout(template="plotly_white", yaxis_title="Raw Value")
        
        st.plotly_chart(fig_box, use_container_width=True, theme=None)

except FileNotFoundError:
    st.error(f"⚠️ Could not find '{file_name}' in your project folder.")