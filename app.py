import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit as st

# Simple Password Protection
password = st.text_input("Enter password to access dashboard:", type="password")
if password != "blueNEXUS!":
    st.warning("Please enter the correct password to view the BlueNexus pipeline.")
    st.stop()  # Stops the rest of the app from loading

st.set_page_config(page_title="BlueNexus Dashboard", layout="wide")
st.title("🌊 BlueNexus Industrial Telemetry Dashboard")

plant = st.sidebar.selectbox("Select Plant", ["Plant A", "Plant B"])
st.write(f"Currently viewing data for **{plant}**")

file_name = (
    "plant_A_equipment_daily.csv"
    if plant == "Plant A"
    else "plant_B_equipment_daily.csv"
)

try:
    df = pd.read_csv(file_name)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        x_axis_col = "date"
    else:
        x_axis_col = df.columns[0]

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    st.subheader("Diagnostic Overlay (Shape & Trend Correlation)")
    st.write("Select variables to overlay using the checkboxes below.")

    # Four-column checkbox grid
    selected_cols = []
    checkbox_columns = st.columns(4)

    for i, col_name in enumerate(numeric_cols):
        with checkbox_columns[i % 4]:
            is_checked = st.checkbox(
                col_name,
                value=(i < 2),
                key=f"{plant}_{col_name}",
            )

            if is_checked:
                selected_cols.append(col_name)

    st.divider()

    normalize = st.checkbox(
        "Normalize variables (Scale everything from 0 to 100%)",
        value=True,
    )

    if selected_cols:
        plot_df = df.copy()

        if normalize:
            for col in selected_cols:
                min_val = plot_df[col].min()
                max_val = plot_df[col].max()

                if pd.isna(min_val) or pd.isna(max_val):
                    continue

                if max_val != min_val:
                    plot_df[col] = (
                        (plot_df[col] - min_val) / (max_val - min_val)
                    ) * 100
                else:
                    # Keep missing readings missing.
                    plot_df[col] = plot_df[col].where(
                        plot_df[col].isna(), 0
                    )

            y_label = "Normalized Scale (0 = Min, 100 = Max)"
        else:
            y_label = "Raw Sensor Values"

        fig = px.line(
            plot_df,
            x=x_axis_col,
            y=selected_cols,
            title=f"{plant}: Telemetry Overlay",
        )

        fig.update_layout(
            template="plotly_white",
            xaxis_title="Date" if x_axis_col == "date" else x_axis_col,
            yaxis_title=y_label,
            legend_title="Variables",
            hovermode="x unified",
        )

        st.plotly_chart(fig, use_container_width=True, theme=None)

    else:
        st.warning("Please check at least one box above to render the chart.")

except FileNotFoundError:
    st.error(f"⚠️ Could not find '{file_name}' in your project folder.")