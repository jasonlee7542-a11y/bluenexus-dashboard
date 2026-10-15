import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde
import plotly.express as px
import plotly.graph_objects as go

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
    
    # --- STATISTICAL DENSITY DISTRIBUTION SECTION ---
    st.divider()
    st.subheader("Statistical Distribution & Quartile Analysis")
    st.write("Select a single variable to inspect its density curve, percentiles, mean, median, and IQR.")
    
    dist_var = st.selectbox("Select variable for distribution analysis:", numeric_cols)
    
    if dist_var:
        clean_series = df[dist_var].dropna()
        
        if not clean_series.empty:
            # Calculate Statistical Metrics
            min_val = clean_series.min()
            q1 = clean_series.quantile(0.25)
            median_val = clean_series.median()
            mean_val = clean_series.mean()
            q3 = clean_series.quantile(0.75)
            max_val = clean_series.max()
            iqr = q3 - q1
            
            # Display Quick Summary Cards
            m1, m2, m3, m4, m5, m6 = st.columns(6)
            m1.metric("Min", f"{min_val:.2f}")
            m2.metric("Q1 (25%)", f"{q1:.2f}")
            m3.metric("Median (50%)", f"{median_val:.2f}")
            m4.metric("Mean", f"{mean_val:.2f}")
            m5.metric("Q3 (75%)", f"{q3:.2f}")
            m6.metric("IQR (Q3-Q1)", f"{iqr:.2f}")
            
            # Calculate Density Curve
            kde = gaussian_kde(clean_series)
            x_range = np.linspace(min_val, max_val, 200)
            y_density = kde(x_range)
            
            fig_density = go.Figure()
            
            # Add Filled Density Curve
            fig_density.add_trace(go.Scatter(
                x=x_range, 
                y=y_density,
                mode='lines',
                name='Density Curve',
                line=dict(color='#2B5B84', width=2.5),
                fill='tozeroy',
                fillcolor='rgba(43, 91, 132, 0.15)'
            ))
            
            # Add Vertical Marker Lines with Labels
            markers = [
                (min_val, "Min", "#888888", "dash"),
                (q1, "Q1 (25th)", "#1F77B4", "dash"),
                (median_val, "Median (50th)", "#2CA02C", "solid"),
                (mean_val, "Mean", "#FF7F0E", "dot"),
                (q3, "Q3 (75th)", "#1F77B4", "dash"),
                (max_val, "Max", "#888888", "dash")
            ]
            
            for val, label, color, dash_style in markers:
                fig_density.add_vline(
                    x=val,
                    line_width=2,
                    line_dash=dash_style,
                    line_color=color,
                    annotation_text=f"{label}<br>{val:.2f}",
                    annotation_position="top"
                )
                
            fig_density.update_layout(
                title=f"Density Distribution & Quartiles for {dist_var}",
                xaxis_title=dist_var,
                yaxis_title="Density",
                template="plotly_white",
                showlegend=False,
                margin=dict(t=80)
            )
            
            st.plotly_chart(fig_density, use_container_width=True, theme=None)

except FileNotFoundError:
    st.error(f"⚠️ Could not find '{file_name}' in your project folder.")