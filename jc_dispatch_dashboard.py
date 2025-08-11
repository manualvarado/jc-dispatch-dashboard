# JC Dispatch Operational & Performance Dashboard
# Cursor Streamlit Prompt - Paste directly into Cursor

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import os

# Try to import openpyxl for Excel support
try:
    import openpyxl
except ImportError:
    st.warning("openpyxl not installed. Excel files won't be supported. Install with: pip install openpyxl")

# State abbreviation to full name mapping
STATE_ABBR_TO_FULL = {
    'AL': 'ALABAMA', 'AK': 'ALASKA', 'AZ': 'ARIZONA', 'AR': 'ARKANSAS', 'CA': 'CALIFORNIA',
    'CO': 'COLORADO', 'CT': 'CONNECTICUT', 'DE': 'DELAWARE', 'FL': 'FLORIDA', 'GA': 'GEORGIA',
    'HI': 'HAWAII', 'ID': 'IDAHO', 'IL': 'ILLINOIS', 'IN': 'INDIANA', 'IA': 'IOWA',
    'KS': 'KANSAS', 'KY': 'KENTUCKY', 'LA': 'LOUISIANA', 'ME': 'MAINE', 'MD': 'MARYLAND',
    'MA': 'MASSACHUSETTS', 'MI': 'MICHIGAN', 'MN': 'MINNESOTA', 'MS': 'MISSISSIPPI',
    'MO': 'MISSOURI', 'MT': 'MONTANA', 'NE': 'NEBRASKA', 'NV': 'NEVADA', 'NH': 'NEW HAMPSHIRE',
    'NJ': 'NEW JERSEY', 'NM': 'NEW MEXICO', 'NY': 'NEW YORK', 'NC': 'NORTH CAROLINA',
    'ND': 'NORTH DAKOTA', 'OH': 'OHIO', 'OK': 'OKLAHOMA', 'OR': 'OREGON', 'PA': 'PENNSYLVANIA',
    'RI': 'RHODE ISLAND', 'SC': 'SOUTH CAROLINA', 'SD': 'SOUTH DAKOTA', 'TN': 'TENNESSEE',
    'TX': 'TEXAS', 'UT': 'UTAH', 'VT': 'VERMONT', 'VA': 'VIRGINIA', 'WA': 'WASHINGTON',
    'WV': 'WEST VIRGINIA', 'WI': 'WISCONSIN', 'WY': 'WYOMING'
}

st.set_page_config(page_title="JC Dispatch Operational & Performance Dashboard", layout="wide")

# Custom CSS for dark blue theme and dropdown styling
st.markdown("""
<style>
    /* Dark blue background */
    .main {
        background-color: #0e1a2b;
    }
    
    /* Dropdown menu styling - dark blue font */
    .stSelectbox > div > div > div > div {
        color: #1f77b4 !important;
        font-weight: 600 !important;
    }
    
    /* Multi-select dropdown styling */
    .stMultiSelect > div > div > div > div {
        color: #1f77b4 !important;
        font-weight: 600 !important;
    }
    
    /* Selectbox options */
    .stSelectbox .css-1d391kg {
        color: #1f77b4 !important;
    }
    
    /* Multi-select options */
    .stMultiSelect .css-1d391kg {
        color: #1f77b4 !important;
    }
    
    /* Dropdown placeholder text */
    .stSelectbox .css-1d391kg::placeholder {
        color: #1f77b4 !important;
    }
    
    /* Multi-select placeholder text */
    .stMultiSelect .css-1d391kg::placeholder {
        color: #1f77b4 !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1a2332 !important;
    }
    
    /* Main content area */
    .block-container {
        background-color: #0e1a2b !important;
    }
    
    /* Text color for better contrast */
    .stMarkdown, .stText {
        color: #ffffff !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    /* Metric cards */
    .css-1wivap2 {
        background-color: #1a2332 !important;
        border: 1px solid #2d3748 !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        background-color: #1a2332 !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("JC Dispatch Operational & Performance Dashboard")

# --- Sidebar for Data Management ---
st.sidebar.title("📁 Data Management")

# Check if converted files exist
converted_files_exist = all([
    os.path.exists("Trucking_Made_Successful_Data/market_data.csv"),
    os.path.exists("Trucking_Made_Successful_Data/market_rates_by_state.csv"),
    os.path.exists("Trucking_Made_Successful_Data/dead_zones_data.csv")
])

if converted_files_exist:
    st.sidebar.success("✅ Converted Trucking Made Successful files found!")
    use_converted_files = st.sidebar.checkbox(
        "Use converted Trucking Made Successful data",
        value=True,
        help="Use the automatically converted data files"
    )
else:
    st.sidebar.warning("⚠️ Converted files not found. Run convert_trucking_data.py first.")
    use_converted_files = False

# Main data file upload (required for operational data)
uploaded_file = st.sidebar.file_uploader(
    "Upload your main operational data file (CSV/Excel)",
    type=['csv', 'xlsx', 'xls'],
    help="Upload your main operational data file"
)

if uploaded_file is not None:
    file_to_use = uploaded_file
    st.sidebar.success(f"✅ File uploaded: {uploaded_file.name}")
else:
    st.sidebar.error("Please upload your main operational data file.")
    st.stop()

# Sidebar filters
st.sidebar.title("🔍 Filters")
st.sidebar.markdown("---")

# Date range filter (will be populated after data loads)
date_filter_enabled = st.sidebar.checkbox("Enable Date Range Filter", value=False)

# Trucking Made Successful Reference Data
st.sidebar.title("📊 Reference Data")
st.sidebar.markdown("---")

# Use converted files or manual upload
if use_converted_files:
    st.sidebar.info("📊 Using converted Trucking Made Successful data files")
    market_data_file = None
    dead_zones_file = None
    market_rates_file = None
else:
    st.sidebar.info("📊 Manual upload mode")
    
    # Market data upload
    market_data_file = st.sidebar.file_uploader(
        "Trucking Made Successful - Market Data",
        type=['csv', 'xlsx', 'xls'],
        help="Upload market data file with load-to-truck ratios, market rates, etc."
    )
    
    # Dead zones data upload
    dead_zones_file = st.sidebar.file_uploader(
        "Trucking Made Successful - Dead Zones Data",
        type=['csv', 'xlsx', 'xls'],
        help="Upload dead zones data with market rates, load availability, etc."
    )
    
    # Market rates by state/region
    market_rates_file = st.sidebar.file_uploader(
        "Trucking Made Successful - Market Rates by State",
        type=['csv', 'xlsx', 'xls'],
        help="Upload market rates data by state/region"
    )

# Driver-FC mapping upload
driver_fc_file = st.sidebar.file_uploader(
    "Driver-FC Mapping File",
    type=['csv', 'xlsx', 'xls'],
    help="Upload file mapping drivers to dispatchers (FC)"
)

# Load history file upload
load_history_file = st.sidebar.file_uploader(
    "Full Load History",
    type=['csv', 'xlsx', 'xls'],
    help="Upload complete load history file for comprehensive analysis"
)

# --- Load Data ---
@st.cache_data
def load_data(file_source):
    try:
        # Load the data from uploaded file or default file
        if isinstance(file_source, str):
            load_data = pd.read_csv(file_source)
        else:
            load_data = pd.read_csv(file_source)
        
        # Clean and preprocess the data
        load_data['DELIVERY DATE'] = pd.to_datetime(load_data['DELIVERY DATE'], errors='coerce')
        load_data['PICK-UP DATE'] = pd.to_datetime(load_data['PICK-UP DATE'], errors='coerce')
        load_data['DATE UPLOADED TO THE SYSTEM'] = pd.to_datetime(load_data['DATE UPLOADED TO THE SYSTEM'], errors='coerce')
        
        # Convert timezone-aware datetimes to timezone-naive to avoid comparison issues
        for col in ['DATE UPLOADED TO THE SYSTEM', 'PICK-UP DATE', 'DELIVERY DATE']:
            if col in load_data.columns and load_data[col].dt.tz is not None:
                load_data[col] = load_data[col].dt.tz_localize(None)
        
        # Filter out AMAZON RELAY loads as requested
        if 'BROKER NAME' in load_data.columns:
            load_data = load_data[~load_data['BROKER NAME'].str.contains('AMAZON RELAY', case=False, na=False)]
            st.sidebar.info(f"Filtered out AMAZON RELAY loads. Remaining loads: {len(load_data)}")
        
        # Filter out canceled loads as they are not invoiced
        if 'LOAD STATUS' in load_data.columns:
            initial_count = len(load_data)
            load_data = load_data[~load_data['LOAD STATUS'].str.contains('cancel', case=False, na=False)]
            canceled_count = initial_count - len(load_data)
            st.sidebar.info(f"Filtered out {canceled_count} canceled loads. Remaining loads: {len(load_data)}")
        
        # Convert currency columns to numeric, removing commas and dollar signs
        load_data['BROKER RATE (FC) [$]'] = pd.to_numeric(load_data['BROKER RATE (FC) [$]'].astype(str).str.replace(',', '').str.replace('$', ''), errors='coerce')
        load_data['DRIVER RATE [$]'] = pd.to_numeric(load_data['DRIVER RATE [$]'].astype(str).str.replace(',', '').str.replace('$', ''), errors='coerce')
        load_data['FULL MILES TOTAL'] = pd.to_numeric(load_data['FULL MILES TOTAL'], errors='coerce')
        
        # Create week column based on DELIVERY DATE - Week starts on Tuesday, ends on Monday
        # This ensures weeks are counted using DELIVERY DATE as the indicator
        def get_week_start_tuesday(delivery_date):
            if pd.isna(delivery_date):
                return None
            # Convert to datetime if it's not already
            if isinstance(delivery_date, str):
                delivery_date = pd.to_datetime(delivery_date, errors='coerce')
            if pd.isna(delivery_date):
                return None
            
            # Get the day of week (0=Monday, 1=Tuesday, ..., 6=Sunday)
            day_of_week = delivery_date.weekday()
            
            # Calculate days to subtract to get to the previous Tuesday
            # If delivery_date is Tuesday (1), subtract 0 days
            # If delivery_date is Wednesday (2), subtract 1 day
            # If delivery_date is Thursday (3), subtract 2 days
            # If delivery_date is Friday (4), subtract 3 days
            # If delivery_date is Saturday (5), subtract 4 days
            # If delivery_date is Sunday (6), subtract 5 days
            # If delivery_date is Monday (0), subtract 6 days
            days_to_subtract = (day_of_week - 1) % 7
            
            # Get the Tuesday that starts this week
            week_start_tuesday = delivery_date - pd.Timedelta(days=days_to_subtract)
            return week_start_tuesday
        
        load_data['WEEK'] = load_data['DELIVERY DATE'].apply(get_week_start_tuesday)
        
        # Create BOOKING TIME column for use throughout the dashboard
        load_data['BOOKING TIME'] = pd.to_datetime(load_data['DATE UPLOADED TO THE SYSTEM'], errors='coerce')
        if load_data['BOOKING TIME'].dt.tz is not None:
            load_data['BOOKING TIME'] = load_data['BOOKING TIME'].dt.tz_localize(None)
        
        return load_data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load the main data
df = load_data(file_to_use)

# --- Global Dispatcher Filter ---
if not df.empty and 'FC NAME' in df.columns:
    # Get unique dispatchers for global filter
    all_dispatchers = sorted(df['FC NAME'].dropna().astype(str).unique())
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Global Dispatcher Filter")
    
    # Global dispatcher multi-select
    selected_global_dispatchers = st.sidebar.multiselect(
        "Select Dispatchers to Include:",
        options=all_dispatchers,
        default=all_dispatchers,
        help="Select which dispatchers to include in ALL dashboard views. Leave empty to show all dispatchers."
    )
    
    # Apply global dispatcher filter
    if selected_global_dispatchers:
        df = df[df['FC NAME'].isin(selected_global_dispatchers)]
        st.sidebar.success(f"✅ Filtered to {len(selected_global_dispatchers)} dispatcher(s): {", ".join(selected_global_dispatchers)}")
    else:
        st.sidebar.info("ℹ️ Showing data for all dispatchers")
    
    st.sidebar.markdown("---")

# Display global filter status in main area
if not df.empty:
    if selected_global_dispatchers:
        st.info(f"🎯 **Global Filter Active**: Showing data for {len(selected_global_dispatchers)} dispatcher(s): {", ".join(selected_global_dispatchers)} | 📊 **Total Records**: {len(df):,}")
    else:
        st.info(f"ℹ️ **Global Filter**: Showing data for all dispatchers | 📊 **Total Records**: {len(df):,}")

# Load reference data if provided
@st.cache_data
def process_trucking_made_successful_data(df):
    """Process Trucking Made Successful data format to extract state and value information"""
    if df is None or df.empty:
        return None
    
    try:
        # Check if this is the expected format (id, metadata, name, value)
        if 'name' in df.columns and 'value' in df.columns:
            # Extract state names and values
            processed_data = df[['name', 'value']].copy()
            
            # Clean the value column (remove brackets and convert to float)
            processed_data['value'] = processed_data['value'].astype(str).str.replace('[', '').str.replace(']', '').astype(float)
            
            # Create state code mapping (first 2 letters of state name)
            processed_data['STATE'] = processed_data['name'].str[:2].str.upper()
            
            return processed_data
        else:
            return None
    except Exception as e:
        st.sidebar.error(f"❌ Error processing Trucking Made Successful data: {e}")
        return None

@st.cache_data
def load_reference_data(market_file, dead_zones_file, market_rates_file, driver_fc_file, load_history_file, use_converted_files=False):
    reference_data = {}
    
    # Load converted files directly if enabled
    if use_converted_files:
        try:
            # Load market data
            market_data = pd.read_csv("Trucking_Made_Successful_Data/market_data.csv")
            reference_data['market'] = market_data
            st.sidebar.success("✅ Converted market data loaded")
            
            # Load dead zones data
            dead_zones_data = pd.read_csv("Trucking_Made_Successful_Data/dead_zones_data.csv")
            reference_data['dead_zones'] = dead_zones_data
            st.sidebar.success("✅ Converted dead zones data loaded")
            
            # Load market rates data
            rates_data = pd.read_csv("Trucking_Made_Successful_Data/market_rates_by_state.csv")
            reference_data['market_rates'] = rates_data
            st.sidebar.success("✅ Converted market rates data loaded")
            
        except Exception as e:
            st.sidebar.error(f"❌ Error loading converted files: {e}")
            return {}
    
    else:
        # Load market data from uploaded file
        if market_file is not None:
            try:
                if market_file.name.endswith('.csv'):
                    market_data = pd.read_csv(market_file)
                else:
                    market_data = pd.read_excel(market_file)
                
                # Process Trucking Made Successful format
                processed_market = process_trucking_made_successful_data(market_data)
                if processed_market is not None:
                    reference_data['market'] = processed_market
                    st.sidebar.success(f"✅ Market data loaded: {market_file.name}")
                else:
                    reference_data['market'] = market_data
                    st.sidebar.success(f"✅ Market data loaded (standard format): {market_file.name}")
            except Exception as e:
                st.sidebar.error(f"❌ Error loading market data: {e}")
        
        # Load dead zones data from uploaded file
        if dead_zones_file is not None:
            try:
                if dead_zones_file.name.endswith('.csv'):
                    dead_zones_data = pd.read_csv(dead_zones_file)
                else:
                    dead_zones_data = pd.read_excel(dead_zones_file)
                
                # Process Trucking Made Successful format
                processed_dead_zones = process_trucking_made_successful_data(dead_zones_data)
                if processed_dead_zones is not None:
                    reference_data['dead_zones'] = processed_dead_zones
                    st.sidebar.success(f"✅ Dead zones data loaded: {dead_zones_file.name}")
                else:
                    reference_data['dead_zones'] = dead_zones_data
                    st.sidebar.success(f"✅ Dead zones data loaded (standard format): {dead_zones_file.name}")
            except Exception as e:
                st.sidebar.error(f"❌ Error loading dead zones data: {e}")
        
        # Load market rates data from uploaded file
        if market_rates_file is not None:
            try:
                if market_rates_file.name.endswith('.csv'):
                    rates_data = pd.read_csv(market_rates_file)
                else:
                    rates_data = pd.read_excel(market_rates_file)
                
                # Process Trucking Made Successful format
                processed_rates = process_trucking_made_successful_data(rates_data)
                if processed_rates is not None:
                    reference_data['market_rates'] = processed_rates
                    st.sidebar.success(f"✅ Market rates loaded: {market_rates_file.name}")
                else:
                    reference_data['market_rates'] = rates_data
                    st.sidebar.success(f"✅ Market rates loaded (standard format): {market_rates_file.name}")
            except Exception as e:
                st.sidebar.error(f"❌ Error loading market rates: {e}")
    
    # Load driver-FC mapping (always from upload)
    if driver_fc_file is not None:
        try:
            if driver_fc_file.name.endswith('.csv'):
                reference_data['driver_fc'] = pd.read_csv(driver_fc_file)
            else:
                reference_data['driver_fc'] = pd.read_excel(driver_fc_file)
            st.sidebar.success(f"✅ Driver-FC mapping loaded: {driver_fc_file.name}")
        except Exception as e:
            st.sidebar.error(f"❌ Error loading driver-FC mapping: {e}")
    
    # Load load history (always from upload)
    if load_history_file is not None:
        try:
            if load_history_file.name.endswith('.csv'):
                reference_data['load_history'] = pd.read_csv(load_history_file)
            else:
                reference_data['load_history'] = pd.read_excel(load_history_file)
            st.sidebar.success(f"✅ Load history loaded: {load_history_file.name}")
        except Exception as e:
            st.sidebar.error(f"❌ Error loading load history: {e}")
    
    return reference_data

# Load reference data
reference_data = load_reference_data(market_data_file, dead_zones_file, market_rates_file, driver_fc_file, load_history_file, use_converted_files)

if df.empty:
    st.error("No data loaded. Please check if the CSV file exists.")
    st.stop()

# --- KPI: Full-Week Active Drivers Overview ---
st.subheader("🟢 Full-Week Active Drivers (Tuesday to Monday)")

try:
    # Create a copy of the dataframe to avoid modifying the original
    df_full_week = df.copy()
    
    # Ensure dates are datetime
    df_full_week['PICK-UP DATE'] = pd.to_datetime(df_full_week['PICK-UP DATE'], errors='coerce')
    df_full_week['DELIVERY DATE'] = pd.to_datetime(df_full_week['DELIVERY DATE'], errors='coerce')
    
    # Remove rows with invalid dates
    df_full_week = df_full_week.dropna(subset=['PICK-UP DATE', 'DELIVERY DATE'])
    
    if df_full_week.empty:
        st.warning("⚠️ No valid date data available for Full-Week Active Drivers analysis.")
    else:
        # Calculate week start (Tuesday) for each delivery date
        def get_week_start_tuesday(delivery_date):
            # Get the Monday of the week containing delivery_date
            monday = delivery_date - pd.to_timedelta(delivery_date.weekday(), unit='d')
            # Add 1 day to get Tuesday
            tuesday = monday + pd.to_timedelta(1, unit='d')
            return tuesday
        
        df_full_week['WEEK_START'] = df_full_week['DELIVERY DATE'].apply(get_week_start_tuesday)
        
        # Group by driver and week
        weekly_driver = df_full_week.groupby(['DRIVER NAME', 'WEEK_START']).agg({
            'PICK-UP DATE': 'min',
            'DELIVERY DATE': 'max',
            'FULL MILES TOTAL': 'sum',
            'BROKER RATE (FC) [$]': 'sum',
            'LOAD ID': 'count',
            'FC NAME': 'first'  # Get dispatcher name
        }).reset_index()
        
        # Calculate RPM
        weekly_driver['RPM'] = weekly_driver['BROKER RATE (FC) [$]'] / weekly_driver['FULL MILES TOTAL']
        weekly_driver['RPM'] = weekly_driver['RPM'].fillna(0)
        
        # Define full-week criteria: drivers with activity spanning most of the week
        weekly_driver['WEEK_END'] = weekly_driver['WEEK_START'] + pd.to_timedelta(6, unit='d')  # Monday
        
        # Calculate the span of activity for each driver-week
        weekly_driver['ACTIVITY_SPAN'] = (weekly_driver['DELIVERY DATE'] - weekly_driver['PICK-UP DATE']).dt.days
        
        # A driver is considered "full-week active" if they have activity spanning at least 5 days
        # OR if they start early in the week (Tuesday/Wednesday) and end late in the week (Sunday/Monday)
        weekly_driver['IS_FULL_WEEK'] = (
            (weekly_driver['ACTIVITY_SPAN'] >= 5) |  # Activity spans at least 5 days
            (
                (weekly_driver['PICK-UP DATE'] <= weekly_driver['WEEK_START'] + pd.to_timedelta(1, unit='d')) &  # Start by Wednesday
                (weekly_driver['DELIVERY DATE'] >= weekly_driver['WEEK_END'] - pd.to_timedelta(1, unit='d'))     # End by Sunday
            )
        )
        
        # Filter only full-week active drivers
        full_week_drivers = weekly_driver[weekly_driver['IS_FULL_WEEK'] == True].copy()
        
        # Debug information
        st.write(f"📊 **Data Analysis:**")
        st.write(f"- Total driver-week combinations: {len(weekly_driver)}")
        st.write(f"- Drivers with activity span ≥ 5 days: {len(weekly_driver[weekly_driver['ACTIVITY_SPAN'] >= 5])}")
        st.write(f"- Drivers starting early and ending late: {len(weekly_driver[(weekly_driver['PICK-UP DATE'] <= weekly_driver['WEEK_START'] + pd.to_timedelta(1, unit='d')) & (weekly_driver['DELIVERY DATE'] >= weekly_driver['WEEK_END'] - pd.to_timedelta(1, unit='d'))])}")
        st.write(f"- Full-week active drivers found: {len(full_week_drivers)}")
        
        if not full_week_drivers.empty:
            # Display summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Full-Week Active Drivers", len(full_week_drivers))
            with col2:
                total_miles = full_week_drivers['FULL MILES TOTAL'].sum()
                st.metric("Total Miles", f"{total_miles:,.0f}")
            with col3:
                total_revenue = full_week_drivers['BROKER RATE (FC) [$]'].sum()
                st.metric("Total Revenue", f"${total_revenue:,.0f}")
            with col4:
                avg_rpm = full_week_drivers['RPM'].mean()
                st.metric("Average RPM", f"${avg_rpm:.2f}")
            
            # Timeline-style Gantt Chart
            st.markdown("### 🚛 Activity Span of Full-Week Drivers")
            gantt_data = full_week_drivers.rename(columns={
                'PICK-UP DATE': 'Start',
                'DELIVERY DATE': 'Finish',
                'FC NAME': 'Dispatcher'
            })
            
            fig_gantt = px.timeline(
                gantt_data,
                x_start="Start",
                x_end="Finish",
                y="DRIVER NAME",
                color="Dispatcher",
                hover_data=["RPM", "LOAD ID", "FULL MILES TOTAL"],
                title="Driver Activity Timeline (Full-Week Active Drivers)"
            )
            fig_gantt.update_yaxes(autorange="reversed")
            fig_gantt.update_layout(
                xaxis_title="Date",
                yaxis_title="Driver Name",
                height=400
            )
            st.plotly_chart(fig_gantt, use_container_width=True)
            
            # Bar Chart for Weekly RPM
            st.markdown("### 📊 Weekly RPM for Full-Week Drivers")
            fig_rpm = px.bar(
                full_week_drivers,
                x="DRIVER NAME",
                y="RPM",
                color="RPM",
                hover_data=["FULL MILES TOTAL", "BROKER RATE (FC) [$]", "LOAD ID"],
                title="Rate per Mile by Full-Week Active Driver"
            )
            fig_rpm.update_layout(
                xaxis_title="Driver Name",
                yaxis_title="Rate per Mile ($)",
                height=400
            )
            st.plotly_chart(fig_rpm, use_container_width=True)
            
            # Interactive summary table
            st.markdown("### 📋 Full-Week Driver Summary Table")
            summary_table = full_week_drivers[[
                'DRIVER NAME', 'WEEK_START', 'PICK-UP DATE', 'DELIVERY DATE',
                'FULL MILES TOTAL', 'BROKER RATE (FC) [$]', 'RPM', 'LOAD ID', 'FC NAME'
            ]].rename(columns={
                'LOAD ID': 'Total Loads',
                'FULL MILES TOTAL': 'Total Miles',
                'BROKER RATE (FC) [$]': 'Total Revenue',
                'WEEK_START': 'Week Start (Tuesday)',
                'FC NAME': 'Dispatcher'
            })
            
            # Format dates for display
            summary_table['Week Start (Tuesday)'] = summary_table['Week Start (Tuesday)'].dt.strftime('%b %d, %Y')
            summary_table['PICK-UP DATE'] = summary_table['PICK-UP DATE'].dt.strftime('%b %d, %Y')
            summary_table['DELIVERY DATE'] = summary_table['DELIVERY DATE'].dt.strftime('%b %d, %Y')
            summary_table['RPM'] = summary_table['RPM'].apply(lambda x: f"${x:.2f}")
            summary_table['Total Revenue'] = summary_table['Total Revenue'].apply(lambda x: f"${x:,.0f}")
            summary_table['Total Miles'] = summary_table['Total Miles'].apply(lambda x: f"{x:,.0f}")
            
            st.dataframe(summary_table, use_container_width=True, hide_index=True)
            
        else:
            st.info("ℹ️ No drivers found that meet the full-week active criteria (activity spanning at least 5 days OR early start/late finish).")
            
except Exception as e:
    st.error(f"❌ Error in Full-Week Active Drivers analysis: {str(e)}")
    st.info("Please check that your data contains valid PICK-UP DATE and DELIVERY DATE columns.")

# --- KPI 1: Weekly Earnings Evolution per Dispatcher ---
st.subheader("1. Weekly Earnings Evolution per Dispatcher")
    # Get drivers for this dispatcher
# Use the globally filtered data (no need for individual dispatcher selection)
if not df.empty:
    # Get drivers from the globally filtered data
    drivers = sorted(df['DRIVER NAME'].dropna().astype(str).unique())
    
    # Driver selection with multi-select
    selected_drivers = st.multiselect(
        "Select Drivers (remove to exclude):",
        drivers,
        default=drivers,
        help="Select which drivers to include in the chart. Remove drivers to exclude them."
    )
    
    if selected_drivers:
        # Filter data for selected drivers
        filtered_data = df[df['DRIVER NAME'].isin(selected_drivers)]

    drivers = sorted(dispatcher_data['DRIVER NAME'].dropna().astype(str).unique())
    
    # Driver selection with multi-select
    selected_drivers = st.multiselect(
        "Select Drivers (remove to exclude):",
        drivers,
        default=drivers,
        help="Select which drivers to include in the chart. Remove drivers to exclude them."
    )
    
    if selected_drivers:
        # Filter data for selected drivers
        filtered_data = dispatcher_data[dispatcher_data['DRIVER NAME'].isin(selected_drivers)]
        
        # Group by driver and week for earnings
        weekly_earnings = filtered_data.groupby(['DRIVER NAME', 'WEEK']).agg({
            'BROKER RATE (FC) [$]': 'sum',
            'DRIVER RATE [$]': 'sum'
        }).reset_index()
        
        # Group by driver and week for load count
        weekly_loads = filtered_data.groupby(['DRIVER NAME', 'WEEK']).size().reset_index(name='Load Count')
        
        # Merge earnings and load data
        weekly_data = weekly_earnings.merge(weekly_loads, on=['DRIVER NAME', 'WEEK'], how='left')
        weekly_data = weekly_data.dropna(subset=['WEEK'])
        
        if not weekly_data.empty:
            # Create bar chart for earnings (showing only broker rates as total revenue)
            fig1_earnings = px.bar(weekly_data, x='WEEK', y='BROKER RATE (FC) [$]', 
                                  color='DRIVER NAME',
                                  title=f"Weekly Earnings - {selected_dispatcher}",
                                  labels={'value': 'Amount ($)', 'y': 'Total Revenue ($)'})
            
            # Calculate total earnings per week for annotations (use only broker rates as total revenue)
            weekly_totals = weekly_data.groupby('WEEK').agg({
                'BROKER RATE (FC) [$]': 'sum'
            }).reset_index()
            weekly_totals['TOTAL_EARNINGS'] = weekly_totals['BROKER RATE (FC) [$]']
            
            # Add total amount annotations on top of each stacked bar
            for _, row in weekly_totals.iterrows():
                fig1_earnings.add_annotation(
                    x=row['WEEK'],
                    y=row['TOTAL_EARNINGS'],
                    text=f"${row['TOTAL_EARNINGS']:,.0f}",
                    showarrow=False,
                    yshift=15,
                    font=dict(size=12, color='black', weight='bold'),
                    bgcolor='white',
                    bordercolor='black',
                    borderwidth=1
                )
            
            fig1_earnings.update_layout(
                xaxis_title="Week (Tuesday-Monday)",
                yaxis_title="Earnings ($)",
                showlegend=True,
                legend_title="Driver Name"
            )
            
            st.plotly_chart(fig1_earnings, use_container_width=True)
            
            # Create line chart for load quantities
            fig1_loads = px.line(weekly_data, x='WEEK', y='Load Count', color='DRIVER NAME', markers=True,
                                title=f"Weekly Load Quantities - {selected_dispatcher}")
            
            fig1_loads.update_layout(
                xaxis_title="Week (Tuesday-Monday)",
                yaxis_title="Number of Loads",
                showlegend=True,
                legend_title="Driver Name"
            )
            
            st.plotly_chart(fig1_loads, use_container_width=True)
            
            # Show summary statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_broker_earnings = weekly_data['BROKER RATE (FC) [$]'].sum()
                st.metric("Total Broker Earnings", f"${total_broker_earnings:,.0f}")
            with col2:
                total_driver_earnings = weekly_data['DRIVER RATE [$]'].sum()
                st.metric("Total Driver Earnings", f"${total_driver_earnings:,.0f}")
            with col3:
                total_loads = weekly_data['Load Count'].sum()
                st.metric("Total Loads", f"{total_loads}")
            with col4:
                num_drivers = len(selected_drivers)
                st.metric("Active Drivers", f"{num_drivers}")
            
            # Show weekly breakdown
            with st.expander("📊 Weekly Breakdown Table", expanded=False):
                weekly_summary = weekly_data.groupby('WEEK').agg({
                    'BROKER RATE (FC) [$]': 'sum',
                    'DRIVER RATE [$]': 'sum',
                    'Load Count': 'sum'
                }).reset_index()
                
                # Format the week display
                weekly_summary['Week Display'] = weekly_summary['WEEK'].dt.strftime('%b %d, %Y')
                weekly_summary['BROKER RATE (FC) [$]'] = weekly_summary['BROKER RATE (FC) [$]'].apply(lambda x: f"${x:,.0f}")
                weekly_summary['DRIVER RATE [$]'] = weekly_summary['DRIVER RATE [$]'].apply(lambda x: f"${x:,.0f}")
                
                st.dataframe(weekly_summary[['Week Display', 'BROKER RATE (FC) [$]', 'DRIVER RATE [$]', 'Load Count']], 
                            use_container_width=True, hide_index=True)
            
            # Show detailed table
            with st.expander("📋 Detailed Weekly Earnings Data", expanded=False):
                display_data = weekly_data.copy()
                display_data['BROKER RATE (FC) [$]'] = display_data['BROKER RATE (FC) [$]'].apply(lambda x: f"${x:,.2f}")
                display_data['DRIVER RATE [$]'] = display_data['DRIVER RATE [$]'].apply(lambda x: f"${x:,.2f}")
                st.dataframe(display_data.sort_values(['DRIVER NAME', 'WEEK']), use_container_width=True)
        else:
            st.info(f"No weekly earnings data available for {selected_dispatcher}")
    else:
        st.info("Please select at least one driver to view the chart.")
else:
    # Show all dispatchers overview
    weekly_earnings_all = df.groupby(['FC NAME', 'WEEK']).agg({
        'BROKER RATE (FC) [$]': 'sum',
        'DRIVER RATE [$]': 'sum'
    }).reset_index()
    
    weekly_loads_all = df.groupby(['FC NAME', 'WEEK']).size().reset_index(name='Load Count')
    weekly_data_all = weekly_earnings_all.merge(weekly_loads_all, on=['FC NAME', 'WEEK'], how='left')
    weekly_data_all = weekly_data_all.dropna(subset=['WEEK'])
    
    if not weekly_data_all.empty:
        # Create bar chart for all dispatchers (showing only broker rates as total revenue)
        fig1_all_earnings = px.bar(weekly_data_all, x='WEEK', y='BROKER RATE (FC) [$]', 
                                   color='FC NAME',
                                   title="Weekly Earnings - All Dispatchers",
                                   labels={'value': 'Amount ($)', 'y': 'Total Revenue ($)'})
        
        # Calculate total earnings per week for annotations (All Dispatchers view - use only broker rates as total revenue)
        weekly_totals_all = weekly_data_all.groupby('WEEK').agg({
            'BROKER RATE (FC) [$]': 'sum'
        }).reset_index()
        weekly_totals_all['TOTAL_EARNINGS'] = weekly_totals_all['BROKER RATE (FC) [$]']
        
        # Add total amount annotations on top of each stacked bar
        for _, row in weekly_totals_all.iterrows():
            fig1_all_earnings.add_annotation(
                x=row['WEEK'],
                y=row['TOTAL_EARNINGS'],
                text=f"${row['TOTAL_EARNINGS']:,.0f}",
                showarrow=False,
                yshift=15,
                font=dict(size=12, color='black', weight='bold'),
                bgcolor='white',
                bordercolor='black',
                borderwidth=1
            )
        
        fig1_all_earnings.update_layout(
            xaxis_title="Week (Tuesday-Monday)",
            yaxis_title="Earnings ($)",
            showlegend=True,
            legend_title="Dispatcher (FC)"
        )
        
        st.plotly_chart(fig1_all_earnings, use_container_width=True)
        
        # Create line chart for load quantities
        fig1_all_loads = px.line(weekly_data_all, x='WEEK', y='Load Count', color='FC NAME', markers=True,
                                 title="Weekly Load Quantities - All Dispatchers")
        
        fig1_all_loads.update_layout(
            xaxis_title="Week (Tuesday-Monday)",
            yaxis_title="Number of Loads",
            showlegend=True,
            legend_title="Dispatcher (FC)"
        )
        
        st.plotly_chart(fig1_all_loads, use_container_width=True)
        
        # Show summary statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_broker_earnings = weekly_data_all['BROKER RATE (FC) [$]'].sum()
            st.metric("Total Broker Earnings", f"${total_broker_earnings:,.0f}")
        with col2:
            total_driver_earnings = weekly_data_all['DRIVER RATE [$]'].sum()
            st.metric("Total Driver Earnings", f"${total_driver_earnings:,.0f}")
        with col3:
            total_loads = weekly_data_all['Load Count'].sum()
            st.metric("Total Loads", f"{total_loads}")
        with col4:
            # Count unique dispatchers across all weeks
            unique_dispatchers = weekly_data_all['FC NAME'].nunique()
            st.metric("Active Dispatchers", f"{unique_dispatchers}")
        
        # Show weekly breakdown
        st.subheader("Weekly Breakdown")
        weekly_summary_all = weekly_data_all.groupby('WEEK').agg({
            'BROKER RATE (FC) [$]': 'sum',
            'DRIVER RATE [$]': 'sum',
            'Load Count': 'sum',
            'FC NAME': 'nunique'  # Count unique dispatchers per week
        }).reset_index()
        
        # Format the week display
        weekly_summary_all['Week Display'] = weekly_summary_all['WEEK'].dt.strftime('%b %d, %Y')
        weekly_summary_all['BROKER RATE (FC) [$]'] = weekly_summary_all['BROKER RATE (FC) [$]'].apply(lambda x: f"${x:,.0f}")
        weekly_summary_all['DRIVER RATE [$]'] = weekly_summary_all['DRIVER RATE [$]'].apply(lambda x: f"${x:,.0f}")
        weekly_summary_all.rename(columns={'FC NAME': 'Active Dispatchers'}, inplace=True)
        
        st.dataframe(weekly_summary_all[['Week Display', 'BROKER RATE (FC) [$]', 'DRIVER RATE [$]', 'Load Count', 'Active Dispatchers']], 
                    use_container_width=True, hide_index=True)
    else:
        st.info("No weekly earnings data available")

# --- KPI 2: Weekly Billing per Driver by Dispatcher ---
st.subheader("2. Weekly Billing per Driver by Dispatcher")

    drivers_billing = sorted(dispatcher_billing_data['DRIVER NAME'].dropna().astype(str).unique())
# Use the globally filtered data (no need for individual dispatcher selection)
if not df.empty:
    # Get drivers from the globally filtered data
    drivers_billing = sorted(df['DRIVER NAME'].dropna().astype(str).unique())
    
    # Driver selection with multi-select
    selected_drivers_billing = st.multiselect(
        "Select Drivers for Billing (remove to exclude):",
        drivers_billing,
        default=drivers_billing,
        key="billing_drivers",
        help="Select which drivers to include in the billing chart. Remove drivers to exclude them."
    )
    
    if selected_drivers_billing:
        # Filter data for selected drivers
        filtered_billing_data = df[df['DRIVER NAME'].isin(selected_drivers_billing)]
        billing = filtered_billing_data.groupby(['FC NAME', 'DRIVER NAME', 'WEEK'])['BROKER RATE (FC) [$]'].sum().reset_index()
    else:
        billing = pd.DataFrame()
else:
    billing = pd.DataFrame()

    
    # Driver selection with multi-select
    selected_drivers_billing = st.multiselect(
        "Select Drivers for Billing (remove to exclude):",
        drivers_billing,
        default=drivers_billing,
        key="billing_drivers",
        help="Select which drivers to include in the billing chart. Remove drivers to exclude them."
    )
    
    if selected_drivers_billing:
        # Filter data for selected drivers
        filtered_billing_data = dispatcher_billing_data[dispatcher_billing_data['DRIVER NAME'].isin(selected_drivers_billing)]
        billing = filtered_billing_data.groupby(['FC NAME', 'DRIVER NAME', 'WEEK'])['BROKER RATE (FC) [$]'].sum().reset_index()
    else:
        billing = pd.DataFrame()
else:
    # Use all data for all dispatchers
    billing = df.groupby(['FC NAME', 'DRIVER NAME', 'WEEK'])['BROKER RATE (FC) [$]'].sum().reset_index()

billing = billing.dropna(subset=['WEEK', 'BROKER RATE (FC) [$]'])

if not billing.empty:
    # Format week for display
    billing['Week Display'] = billing['WEEK'].dt.strftime('%b %d, %Y')
    
    # Create stacked bar chart with one bar per dispatcher per week
    fig2 = px.bar(billing, x='FC NAME', y='BROKER RATE (FC) [$]', color='DRIVER NAME', 
                  facet_col='Week Display',  # Separate chart for each week
                  barmode='stack',  # Stacked bars
                  hover_data=['WEEK', 'DRIVER NAME', 'BROKER RATE (FC) [$]'])
    
    # Update layout for better presentation
    fig2.update_layout(
        title="Weekly Billing by Dispatcher (Stacked by Driver) - Week by Week",
        xaxis_title="Dispatcher (FC)",
        yaxis_title="Billing Amount ($)",
        showlegend=True,
        legend_title="Driver Name"
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Show weekly summary table
    with st.expander("📊 Weekly Billing Summary", expanded=False):
        weekly_summary = billing.groupby(['WEEK', 'FC NAME'])['BROKER RATE (FC) [$]'].sum().reset_index()
        weekly_summary['Week Display'] = weekly_summary['WEEK'].dt.strftime('%b %d, %Y')
        weekly_summary['BROKER RATE (FC) [$]'] = weekly_summary['BROKER RATE (FC) [$]'].apply(lambda x: f"${x:,.2f}")
        weekly_summary = weekly_summary.sort_values(['WEEK', 'BROKER RATE (FC) [$]'], ascending=[True, False])
        
        st.dataframe(weekly_summary[['Week Display', 'FC NAME', 'BROKER RATE (FC) [$]']], 
                    use_container_width=True, hide_index=True)
    
    # Show overall summary table
    with st.expander("📊 Overall Billing Summary by Dispatcher", expanded=False):
        total_billing = billing.groupby('FC NAME')['BROKER RATE (FC) [$]'].sum().reset_index()
        summary_table = total_billing.sort_values('BROKER RATE (FC) [$]', ascending=False)
        summary_table['BROKER RATE (FC) [$]'] = summary_table['BROKER RATE (FC) [$]'].apply(lambda x: f"${x:,.2f}")
        st.dataframe(summary_table, use_container_width=True)
    
else:
    st.info("No billing data available")

# --- KPI 3: Rate per Mile (RPM) per Dispatcher ---
st.subheader("3. Rate per Mile Distribution per Dispatcher")
df['RPM'] = df['BROKER RATE (FC) [$]'] / df['FULL MILES TOTAL']
rpm_data = df[df['RPM'].notna() & (df['RPM'] > 0) & (df['RPM'] < 10)]  # Filter reasonable RPM values
if not rpm_data.empty:
    fig3 = px.violin(rpm_data, x="FC NAME", y="RPM", box=True, points="all", hover_data=["LOAD ID", "DRIVER NAME"])
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No RPM data available")

# --- KPI 4: Destination Market Quality Analysis ---
st.subheader("4. Destination Market Quality Analysis")

# Explanation of destination market quality concept
st.info("""
**What is Destination Market Quality?** 
- **Destination Markets** = States where loads terminate
- **Market Quality** = Assessment of outbound load opportunities and rates in each destination
- **High Quality Destinations** = Good markets for return loads with high rates
- **Low Quality Destinations** = Poor markets (Dead Zones) with limited outbound opportunities
- **Business Impact**: Understanding destination quality helps with:
  - Route planning and optimization
  - Repositioning strategies
  - Profitability forecasting
  - Risk assessment for empty miles
""")

    
# Use the globally filtered data (no need for individual dispatcher selection)
if not df.empty:
    # Get drivers from the globally filtered data
    drivers_dest = sorted(df['DRIVER NAME'].dropna().astype(str).unique())
    
    # Driver selection with multi-select
    selected_drivers_dest = st.multiselect(
        "Select Drivers for Destination Analysis (remove to exclude):",
        drivers_dest,
        default=drivers_dest,
        key="dest_drivers",
        help="Select which drivers to include in the destination analysis"
    )
    
    if selected_drivers_dest:
        # Filter data for selected drivers
        filtered_dest_data = df[df['DRIVER NAME'].isin(selected_drivers_dest)]
    else:
        filtered_dest_data = df.copy()
else:
    filtered_dest_data = pd.DataFrame()

    # Driver selection with multi-select
    selected_drivers_dest = st.multiselect(
        "Select Drivers for Destination Analysis (remove to exclude):",
        drivers_dest,
        default=drivers_dest,
        key="dest_drivers",
        help="Select which drivers to include in the destination analysis"
    )
    
    if selected_drivers_dest:
        # Filter data for selected drivers
        filtered_dest_data = dispatcher_dest_data[dispatcher_dest_data['DRIVER NAME'].isin(selected_drivers_dest)]
    else:
        filtered_dest_data = pd.DataFrame()
else:
    # Use all data for all dispatchers
    filtered_dest_data = df.copy()

# Check if CITY TO column exists (preferred method)
if 'CITY TO' in filtered_dest_data.columns and not filtered_dest_data.empty:
    st.success("✅ Using 'CITY TO' column for state extraction")
    
    # Extract state from CITY TO column (format: "CITY, ST")
    filtered_dest_data['CITY_STATE'] = filtered_dest_data['CITY TO'].astype(str)
    
    # Extract state code (last 2 characters after comma and space)
    filtered_dest_data['STATE_TO'] = filtered_dest_data['CITY_STATE'].str.extract(r',\s*([A-Z]{2})$')
    
    # Filter out rows where we couldn't extract state
    df_with_states = filtered_dest_data[filtered_dest_data['STATE_TO'].notna()]
    
    # Count deliveries by state
    destination_counts = df_with_states.groupby('STATE_TO').size().reset_index(name='Destination Deliveries')
    
    # Debug: Show what we found
    st.write(f"📊 Found {len(destination_counts)} states with delivery data")
    if not destination_counts.empty:
        with st.expander("📋 Destination Data Table", expanded=False):
            st.write("Top 10 states by delivery count:")
            st.dataframe(destination_counts.head(10), use_container_width=True)
            
            # Show city/state mapping for debugging
            st.write("📋 City to State Mapping (sample):")
            city_mapping_sample = df_with_states[['CITY TO', 'STATE_TO']].head(10)
            st.dataframe(city_mapping_sample, use_container_width=True)
    else:
        st.warning("⚠️ No valid state data found. Check CITY TO column format.")

else:
    st.error("❌ 'CITY TO' column not found!")
    st.write("Available columns:", list(df.columns))
    st.stop()

# Enhanced destination market quality analysis with Trucking Made Successful data
# Initialize analysis_df with basic destination counts
analysis_df = destination_counts[['STATE_TO', 'Destination Deliveries']].copy()

if 'market_rates' in reference_data and not destination_counts.empty:
    try:
        # Get market rates data for destination quality analysis
        rates_data = reference_data['market_rates']
        
        # Add dispatcher and driver filtering for destination analysis
        st.subheader("Filter Destination Analysis:")
        
        # Check for available driver/dispatcher columns
        driver_column = None
        dispatcher_column = None
        
        # Look for driver column (try different possible names)
        for col in ['DRIVER', 'DRIVER NAME', 'DRIVER_NAME']:
            if col in df.columns:
                driver_column = col
                break
        
        # Look for dispatcher/FC column (try different possible names)
        for col in ['FC NAME', 'FC_NAME', 'DISPATCHER', 'DISPATCHER NAME', 'DISPATCHER_NAME']:
            if col in df.columns:
                dispatcher_column = col
                break
        
        # FC/Dispatcher filter (primary filter)
        if dispatcher_column:
            all_dispatchers = ['All Dispatchers'] + sorted(df[dispatcher_column].unique().tolist())
            selected_dispatcher_dest = st.selectbox(f"Select {dispatcher_column} for Destination Analysis:", all_dispatchers)
        else:
            st.warning("⚠️ No dispatcher/FC column found. Available columns: " + ", ".join(df.columns.tolist()[:10]) + "...")
            selected_dispatcher_dest = 'All Dispatchers'
        
        # Driver filter (depends on dispatcher selection)
        if driver_column:
            if selected_dispatcher_dest == 'All Dispatchers':
                all_drivers = ['All Drivers'] + sorted(df[driver_column].unique().tolist())
            else:
                # Get drivers for selected dispatcher/FC
                dispatcher_drivers = df[df[dispatcher_column] == selected_dispatcher_dest][driver_column].unique().tolist()
                all_drivers = ['All Drivers'] + sorted(dispatcher_drivers)
            
            selected_driver_dest = st.selectbox("Select Driver for Destination Analysis:", all_drivers)
        else:
            st.warning("⚠️ No driver column found. Available columns: " + ", ".join(df.columns.tolist()[:10]) + "...")
            selected_driver_dest = 'All Drivers'
        
        # Filter data based on selections
        if dispatcher_column and driver_column:
            if selected_dispatcher_dest == 'All Dispatchers' and selected_driver_dest == 'All Drivers':
                filtered_dest_data = df.copy()
            elif selected_dispatcher_dest == 'All Dispatchers':
                filtered_dest_data = df[df[driver_column] == selected_driver_dest].copy()
            elif selected_driver_dest == 'All Drivers':
                filtered_dest_data = df[df[dispatcher_column] == selected_dispatcher_dest].copy()
            else:
                filtered_dest_data = df[(df[dispatcher_column] == selected_dispatcher_dest) & (df[driver_column] == selected_driver_dest)].copy()
        elif driver_column:
            # If only driver column exists, only filter by driver if selected
            if selected_driver_dest == 'All Drivers':
                filtered_dest_data = df.copy()
            else:
                filtered_dest_data = df[df[driver_column] == selected_driver_dest].copy()
        else:
            # No filtering columns found, use all data
            filtered_dest_data = df.copy()
        
        # Re-extract state data from filtered data
        if 'CITY TO' in filtered_dest_data.columns and not filtered_dest_data.empty:
            filtered_dest_data['CITY_STATE'] = filtered_dest_data['CITY TO'].astype(str)
            filtered_dest_data['STATE_TO'] = filtered_dest_data['CITY_STATE'].str.extract(r',\s*([A-Z]{2})$')
            filtered_dest_data = filtered_dest_data[filtered_dest_data['STATE_TO'].notna()]
            
            # Recalculate destination counts
            filtered_destination_counts = filtered_dest_data.groupby('STATE_TO').size().reset_index(name='Destination Deliveries')
            
            # Update analysis_df with filtered data
            analysis_df = filtered_destination_counts[['STATE_TO', 'Destination Deliveries']].copy()
            
            st.success(f"✅ Filtered data: {len(filtered_dest_data)} deliveries to {len(filtered_destination_counts)} states")
        else:
            st.warning("⚠️ No data available for selected filters")
            filtered_destination_counts = destination_counts
        
        # Perform market quality analysis BEFORE creating the three-column layout
        # This ensures the analysis_df has the 'High', 'Medium', 'Low' columns when we need them
        
        # Merge destination data with market rates for quality analysis
        try:
            # Enhanced market rates analysis with trailer type correlation
            try:
                # Load trailer-specific rates by state if available
                trailer_state_rates_file = os.path.join("Trucking_Made_Successful_Data", "market_rates_by_trailer_state.csv")
                trailer_mapping_file = os.path.join("Trucking_Made_Successful_Data", "trailer_type_mapping.csv")
                
                if os.path.exists(trailer_state_rates_file) and os.path.exists(trailer_mapping_file):
                    trailer_state_rates = pd.read_csv(trailer_state_rates_file)
                    trailer_mapping = pd.read_csv(trailer_mapping_file)
                    
                    # Create mapping dictionary
                    mapping_dict = dict(zip(trailer_mapping['ORIGINAL_TYPE'], trailer_mapping['STANDARD_TYPE']))
                    
                    # Add custom mappings for the specific trailer types in the data
                    custom_mapping = {
                        'DryVan': 'Dry Van',
                        'Flatbed': 'Flatbed', 
                        'Power Only': 'Dry Van',  # Power Only should be considered DryVan
                        'Reefer': 'Reefer',
                        'Stepdeck': 'Flatbed'  # Stepdeck should be considered Flatbed
                    }
                    
                    # Add trailer type analysis to destination data (use filtered data)
                    destination_with_trailer = filtered_dest_data[['STATE_TO', 'TRAILER']].copy()
                    destination_with_trailer['TRAILER_STANDARD'] = destination_with_trailer['TRAILER'].map(custom_mapping)
                    
                    # Convert state abbreviations to full names for merging
                    destination_with_trailer['STATE_FULL'] = destination_with_trailer['STATE_TO'].map(STATE_ABBR_TO_FULL)
                    
                    # Merge with trailer-specific rates by state
                    destination_with_trailer = destination_with_trailer.merge(trailer_state_rates, 
                                                                            left_on='STATE_FULL', 
                                                                            right_on='STATE', 
                                                                            how='left')
                    
                    # Get the appropriate rate based on trailer type
                    def get_trailer_rate(row):
                        if row['TRAILER_STANDARD'] == 'Dry Van':
                            return row['DRY_VAN_RATE']
                        elif row['TRAILER_STANDARD'] == 'Reefer':
                            return row['REEFER_RATE']
                        elif row['TRAILER_STANDARD'] == 'Flatbed':
                            return row['FLATBED_RATE']
                        else:
                            # Default to average of all rates
                            return (row['DRY_VAN_RATE'] + row['REEFER_RATE'] + row['FLATBED_RATE']) / 3
                    
                    destination_with_trailer['MARKET_RATE'] = destination_with_trailer.apply(get_trailer_rate, axis=1)
                    
                    # Calculate market quality score for each delivery
                    destination_with_trailer['MARKET_QUALITY'] = destination_with_trailer['MARKET_RATE'].apply(
                        lambda x: 'High' if x > 2.5 else 'Medium' if x > 2.0 else 'Low'
                    )
                    
                    # Group by state and market quality
                    state_quality_analysis = destination_with_trailer.groupby(['STATE_TO', 'MARKET_QUALITY']).size().reset_index(name='Deliveries')
                    
                    # Pivot to get quality breakdown by state
                    quality_pivot = state_quality_analysis.pivot(index='STATE_TO', columns='MARKET_QUALITY', values='Deliveries').fillna(0)
                    quality_pivot = quality_pivot.reset_index()
                    
                    # Merge with destination counts
                    analysis_df = filtered_destination_counts.merge(quality_pivot, on='STATE_TO', how='left')
                    
                    # Calculate average rate by state
                    state_avg_rates = destination_with_trailer.groupby('STATE_TO')['MARKET_RATE'].mean().reset_index()
                    analysis_df = analysis_df.merge(state_avg_rates, on='STATE_TO', how='left')
                    
                    st.success("✅ Using trailer-specific market rates by state for analysis")
                    
                else:
                    # Fallback to overall market rates
                    if 'MARKET_RATE' in rates_data.columns:
                        rates_subset = rates_data[['STATE', 'MARKET_RATE']].copy()
                        destination_counts_mapped = filtered_destination_counts.copy()
                        destination_counts_mapped['STATE_FULL'] = destination_counts_mapped['STATE_TO'].map(STATE_ABBR_TO_FULL)
                        analysis_df = destination_counts_mapped.merge(rates_subset, left_on='STATE_FULL', right_on='STATE', how='left')
                        analysis_df = analysis_df[['STATE_TO', 'Destination Deliveries', 'MARKET_RATE']].dropna()
                        
                    elif 'value' in rates_data.columns:
                        rates_subset = rates_data[['STATE', 'value']].copy()
                        rates_subset = rates_subset.rename(columns={'value': 'MARKET_RATE'})
                        destination_counts_mapped = filtered_destination_counts.copy()
                        destination_counts_mapped['STATE_FULL'] = destination_counts_mapped['STATE_TO'].map(STATE_ABBR_TO_FULL)
                        analysis_df = destination_counts_mapped.merge(rates_subset, left_on='STATE_FULL', right_on='STATE', how='left')
                        analysis_df = analysis_df[['STATE_TO', 'Destination Deliveries', 'MARKET_RATE']].dropna()
                        
                    else:
                        analysis_df = filtered_destination_counts[['STATE_TO', 'Destination Deliveries']]
                        st.info("Market rates data not available for analysis")
                        
            except Exception as e:
                st.error(f"Error in trailer-specific analysis: {e}")
                # Fallback to basic analysis
                analysis_df = filtered_destination_counts[['STATE_TO', 'Destination Deliveries']]
            
        except Exception as e:
            st.error(f"Error processing destination data: {e}")
            analysis_df = filtered_destination_counts[['STATE_TO', 'Destination Deliveries']]
        
        # Create three-column layout for maps and charts
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Destination deliveries by state map
            fig4a = px.choropleth(filtered_destination_counts, locations='STATE_TO', locationmode="USA-states", 
                                 color='Destination Deliveries', scope="usa", color_continuous_scale="Blues",
                                 title="Destination Deliveries by State")
            st.plotly_chart(fig4a, use_container_width=True)
        
        with col2:
            # Market rates map
            if 'MARKET_RATE' in rates_data.columns or 'value' in rates_data.columns:
                if 'MARKET_RATE' in rates_data.columns:
                    rates_viz = rates_data[['STATE', 'MARKET_RATE']].copy()
                else:
                    rates_viz = rates_data[['STATE', 'value']].copy()
                    rates_viz = rates_viz.rename(columns={'value': 'MARKET_RATE'})
                
                STATE_FULL_TO_ABBR = {v: k for k, v in STATE_ABBR_TO_FULL.items()}
                rates_viz['STATE_ABBR'] = rates_viz['STATE'].map(STATE_FULL_TO_ABBR)
                
                fig4b = px.choropleth(rates_viz, locations='STATE_ABBR', locationmode="USA-states", 
                                     color='MARKET_RATE', scope="usa", color_continuous_scale="RdYlGn",
                                     title="Market Rates by State (Green=High, Red=Low)")
                st.plotly_chart(fig4b, use_container_width=True)
        
        with col3:
            # Market quality breakdown chart
            if 'High' in analysis_df.columns and 'Medium' in analysis_df.columns and 'Low' in analysis_df.columns:
                # Calculate market quality score for map visualization
                quality_map_data = analysis_df.copy()
                quality_map_data['Market Quality Score'] = (
                    quality_map_data['High'] * 3 + 
                    quality_map_data['Medium'] * 2 + 
                    quality_map_data['Low'] * 1
                ) / quality_map_data['Destination Deliveries']
                
                # Create choropleth map showing market quality by state
                fig4c = px.choropleth(quality_map_data, locations='STATE_TO', locationmode="USA-states", 
                                     color='Market Quality Score', scope="usa", color_continuous_scale="RdYlGn",
                                     title="Market Quality by State (Green=High, Red=Low)",
                                     labels={'Market Quality Score': 'Quality Score'})
                st.plotly_chart(fig4c, use_container_width=True)
            else:
                st.info("Market quality map will appear here after analysis")
        
        # Destination market quality analysis table
        st.subheader("Destination Market Quality Analysis")
        
        if not analysis_df.empty:
            # Show comprehensive analysis table
            display_columns = ['STATE_TO', 'Destination Deliveries', 'MARKET_RATE']
            
            # Add quality columns if available
            if 'High' in analysis_df.columns:
                display_columns.extend(['High', 'Medium', 'Low'])
            
            display_df = analysis_df[display_columns].copy()
            display_df['MARKET_RATE'] = display_df['MARKET_RATE'].round(2)
            
            # Rename columns for better display
            display_df = display_df.rename(columns={
                'STATE_TO': 'State',
                'Destination Deliveries': 'Total Deliveries',
                'MARKET_RATE': 'Avg Rate ($/mile)',
                'High': 'High Quality',
                'Medium': 'Medium Quality', 
                'Low': 'Low Quality'
            })
            
            st.dataframe(display_df.sort_values('Total Deliveries', ascending=False), use_container_width=True)
            
            # Add summary statistics
            if 'High' in analysis_df.columns:
                total_high = analysis_df['High'].sum()
                total_medium = analysis_df['Medium'].sum()
                total_low = analysis_df['Low'].sum()
                
                st.info(f"""
                **Market Quality Summary:**
                - **High Quality Deliveries**: {total_high} ({(total_high/(total_high+total_medium+total_low)*100):.1f}%)
                - **Medium Quality Deliveries**: {total_medium} ({(total_medium/(total_high+total_medium+total_low)*100):.1f}%)
                - **Low Quality Deliveries**: {total_low} ({(total_low/(total_high+total_medium+total_low)*100):.1f}%)
                """)
            
            # Market Quality Score Explanation
            st.info("""
            **Market Quality Score Explanation:**
            - **Green (High Score)**: States with mostly high-quality deliveries
            - **Yellow (Medium Score)**: States with mixed quality deliveries  
            - **Red (Low Score)**: States with mostly low-quality deliveries
            - **Score Calculation**: (High×3 + Medium×2 + Low×1) ÷ Total Deliveries
            """)
            
        else:
            st.warning("No data available for analysis after merging")
            st.info("This usually means state names don't match between destinations and market rates data")
        
    except Exception as e:
            st.error(f"Error merging market rates data: {e}")
            # Fallback to destinations only
            analysis_df = destination_counts[['STATE_TO', 'Destination Deliveries']]
            st.dataframe(analysis_df.sort_values('Destination Deliveries', ascending=False), use_container_width=True)
        
    except Exception as e:
        st.error(f"Error processing destination data: {e}")
        # Fallback to basic visualization
        fig4 = px.choropleth(destination_counts, locations='STATE_TO', locationmode="USA-states", 
                            color='Destination Deliveries', scope="usa", color_continuous_scale="Blues")
        st.plotly_chart(fig4, use_container_width=True)

elif not destination_counts.empty:
    fig4 = px.choropleth(destination_counts, locations='STATE_TO', locationmode="USA-states", 
                         color='Destination Deliveries', scope="usa", color_continuous_scale="Blues")
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("No state delivery data available")

# Market Quality Heat Map based on Trucking Made Successful data
st.subheader("Market Quality Heat Map")
if 'market' in reference_data and 'market_rates' in reference_data:
    try:
        # Get market data (load volumes) and market rates
        market_data = reference_data['market']
        rates_data = reference_data['market_rates']
        
        # Create market quality analysis
        # Check if using converted files (different column names)
        if 'LOAD_VOLUME' in market_data.columns and 'MARKET_RATE' in rates_data.columns:
            # Using converted files format
            market_quality = market_data[['STATE', 'LOAD_VOLUME']].copy()
            rates_subset = rates_data[['STATE', 'MARKET_RATE']].copy()
            
            # Convert full state names to abbreviations for choropleth map
            STATE_FULL_TO_ABBR = {v: k for k, v in STATE_ABBR_TO_FULL.items()}
            market_quality['STATE_ABBR'] = market_quality['STATE'].map(STATE_FULL_TO_ABBR)
            rates_subset['STATE_ABBR'] = rates_subset['STATE'].map(STATE_FULL_TO_ABBR)
            
        elif 'value' in market_data.columns and 'value' in rates_data.columns:
            # Using original Trucking Made Successful format
            market_quality = market_data[['STATE', 'value']].copy()
            market_quality = market_quality.rename(columns={'value': 'LOAD_VOLUME'})
            
            rates_subset = rates_data[['STATE', 'value']].copy()
            rates_subset = rates_subset.rename(columns={'value': 'MARKET_RATE'})
            
            # Convert full state names to abbreviations for choropleth map
            STATE_FULL_TO_ABBR = {v: k for k, v in STATE_ABBR_TO_FULL.items()}
            market_quality['STATE_ABBR'] = market_quality['STATE'].map(STATE_FULL_TO_ABBR)
            rates_subset['STATE_ABBR'] = rates_subset['STATE'].map(STATE_FULL_TO_ABBR)
            
        else:
            st.error("❌ Unexpected data format. Please check your data files.")
            st.stop()
        
        # Merge load volumes with rates
        market_quality = market_quality.merge(rates_subset, on='STATE_ABBR', how='left')
        
        # Calculate market quality score (higher load volume + higher rate = better market)
        if not market_quality.empty:
            # Normalize values for scoring (0-100 scale)
            market_quality['LOAD_VOLUME_NORM'] = (market_quality['LOAD_VOLUME'] - market_quality['LOAD_VOLUME'].min()) / (market_quality['LOAD_VOLUME'].max() - market_quality['LOAD_VOLUME'].min()) * 100
            market_quality['RATE_NORM'] = (market_quality['MARKET_RATE'] - market_quality['MARKET_RATE'].min()) / (market_quality['MARKET_RATE'].max() - market_quality['MARKET_RATE'].min()) * 100
            
            # Calculate overall market quality score
            market_quality['MARKET_QUALITY_SCORE'] = (market_quality['LOAD_VOLUME_NORM'] * 0.6 + market_quality['RATE_NORM'] * 0.4)
            
            # Debug: Show merged data info (after calculation)
            with st.expander("🔍 Debug: Market Quality Data", expanded=False):
                st.write("**Merged Market Quality Data:**")
                st.write(f"Columns: {list(market_quality.columns)}")
                st.write(f"Total rows: {len(market_quality)}")
                st.write(f"Sample data:")
                st.dataframe(market_quality.head(), use_container_width=True)
                
                # Show which columns are available for the heat map
                st.write("**Available columns for heat map:**")
                if 'STATE_ABBR' in market_quality.columns:
                    st.write("✅ STATE_ABBR column found")
                if 'MARKET_QUALITY_SCORE' in market_quality.columns:
                    st.write("✅ MARKET_QUALITY_SCORE column found")
                else:
                    st.write("❌ MARKET_QUALITY_SCORE column missing")
            
            # Create heat map
            fig4c = px.choropleth(market_quality, locations='STATE_ABBR', locationmode="USA-states", 
                                 color='MARKET_QUALITY_SCORE', scope="usa", 
                                 color_continuous_scale="RdYlGn",  # Red (bad) to Green (good)
                                 title="Market Quality Heat Map (Green=Good, Red=Bad)",
                                 labels={'MARKET_QUALITY_SCORE': 'Market Quality Score'})
            st.plotly_chart(fig4c, use_container_width=True)
            
            # Show market quality table
            with st.expander("📊 Market Quality Analysis Table", expanded=False):
                # Use the correct column name for state
                state_col = 'STATE' if 'STATE' in market_quality.columns else 'STATE_ABBR'
                quality_table = market_quality[[state_col, 'LOAD_VOLUME', 'MARKET_RATE', 'MARKET_QUALITY_SCORE']].sort_values('MARKET_QUALITY_SCORE', ascending=False)
                quality_table['MARKET_QUALITY_SCORE'] = quality_table['MARKET_QUALITY_SCORE'].round(1)
                st.dataframe(quality_table, use_container_width=True)
            
            # Add explanation
            st.info("""
            **Market Quality Score Explanation:**
            - **Green (High Score)**: Good markets with high load volume and good rates
            - **Yellow (Medium Score)**: Average markets
            - **Red (Low Score)**: Poor markets (Dead Zones) with low load volume or poor rates
            - **Score Calculation**: 60% load volume + 40% market rate
            """)
        
    except Exception as e:
        st.error(f"Error creating market quality heat map: {e}")
        st.info("Market quality analysis requires both market data (load volumes) and market rates data to be uploaded.")
else:
    st.info("📊 Upload market data and market rates data in the sidebar to see the Market Quality Heat Map")

# --- KPI 5: Idle Days per Driver per Dispatcher ---
st.subheader("5. Idle Days per Driver per Dispatcher")

    # Get drivers for this dispatcher
# Use the globally filtered data (no need for individual dispatcher selection)
if not df.empty:
    # Get drivers from the globally filtered data
    drivers_idle = sorted(df['DRIVER NAME'].dropna().astype(str).unique())
    
    # Driver selection with multi-select
    selected_drivers_idle = st.multiselect(
        "Select Drivers for Idle Days (remove to exclude):",
        drivers_idle,
        default=drivers_idle,
        key="idle_drivers",
        help="Select which drivers to include in the idle days chart. Remove drivers to exclude them."
    )
    
    if selected_drivers_idle:
        # Filter data for selected drivers
        filtered_idle_data = df[df['DRIVER NAME'].isin(selected_drivers_idle)]
        df_sorted = filtered_idle_data.sort_values(['DRIVER ID', 'DELIVERY DATE']).copy()
    else:
        df_sorted = pd.DataFrame()
else:
    df_sorted = pd.DataFrame()

    drivers_idle = sorted(dispatcher_idle_data['DRIVER NAME'].dropna().astype(str).unique())
    
    # Driver selection with multi-select
    selected_drivers_idle = st.multiselect(
        "Select Drivers for Idle Days (remove to exclude):",
        drivers_idle,
        default=drivers_idle,
        key="idle_drivers",
        help="Select which drivers to include in the idle days chart. Remove drivers to exclude them."
    )
    
    if selected_drivers_idle:
        # Filter data for selected drivers
        filtered_idle_data = dispatcher_idle_data[dispatcher_idle_data['DRIVER NAME'].isin(selected_drivers_idle)]
        df_sorted = filtered_idle_data.sort_values(['DRIVER ID', 'DELIVERY DATE']).copy()
    else:
        df_sorted = pd.DataFrame()
else:
    # Use all data for all dispatchers
    df_sorted = df.sort_values(['DRIVER ID', 'DELIVERY DATE']).copy()

if not df_sorted.empty:
    try:
        df_sorted['NEXT PICKUP'] = df_sorted.groupby('DRIVER ID')['PICK-UP DATE'].shift(-1)
        
        # Remove timezone info if present
        if df_sorted['NEXT PICKUP'].dt.tz is not None:
            df_sorted['NEXT PICKUP'] = df_sorted['NEXT PICKUP'].dt.tz_localize(None)
        if df_sorted['DELIVERY DATE'].dt.tz is not None:
            df_sorted['DELIVERY DATE'] = df_sorted['DELIVERY DATE'].dt.tz_localize(None)
        
        # Calculate idle days only for valid datetime pairs
        mask = df_sorted['NEXT PICKUP'].notna() & df_sorted['DELIVERY DATE'].notna()
        df_sorted.loc[mask, 'IDLE DAYS'] = (df_sorted.loc[mask, 'NEXT PICKUP'] - df_sorted.loc[mask, 'DELIVERY DATE']).dt.days
        
        idle_df = df_sorted[df_sorted['IDLE DAYS'] > 0]
        
        if not idle_df.empty:
            # Group by dispatcher, driver, and week for week-by-week visualization
            idle_summary = idle_df.groupby(['FC NAME', 'DRIVER NAME', 'WEEK'])['IDLE DAYS'].sum().reset_index()
            idle_summary = idle_summary.dropna(subset=['WEEK'])
            
            # Format week for display
            idle_summary['Week Display'] = idle_summary['WEEK'].dt.strftime('%b %d, %Y')
            
            # Create stacked bar chart with one bar per dispatcher per week
            fig5 = px.bar(idle_summary, x='FC NAME', y='IDLE DAYS', color='DRIVER NAME', 
                          facet_col='Week Display',  # Separate chart for each week
                          barmode='stack',  # Stacked bars
                          hover_data=['WEEK', 'DRIVER NAME', 'IDLE DAYS'])
            
            # Update layout for better presentation
            fig5.update_layout(
                title="Idle Days by Dispatcher (Stacked by Driver) - Week by Week",
                xaxis_title="Dispatcher (FC)",
                yaxis_title="Idle Days",
                showlegend=True,
                legend_title="Driver Name"
            )
            
            st.plotly_chart(fig5, use_container_width=True)
            
            # Show weekly summary table
            with st.expander("Weekly Idle Days Summary", expanded=False):
                weekly_idle_summary = idle_summary.groupby(['WEEK', 'FC NAME'])['IDLE DAYS'].sum().reset_index()
                weekly_idle_summary['Week Display'] = weekly_idle_summary['WEEK'].dt.strftime('%b %d, %Y')
                weekly_idle_summary['IDLE DAYS'] = weekly_idle_summary['IDLE DAYS'].apply(lambda x: f"{x:.1f} days")
                weekly_idle_summary = weekly_idle_summary.sort_values(['WEEK', 'IDLE DAYS'], ascending=[True, False])
                
                st.dataframe(weekly_idle_summary[['Week Display', 'FC NAME', 'IDLE DAYS']], 
                            use_container_width=True, hide_index=True)
            
            # Show overall summary table
            with st.expander("Overall Idle Days Summary by Dispatcher", expanded=False):
                total_idle = idle_summary.groupby('FC NAME')['IDLE DAYS'].sum().reset_index()
                summary_table = total_idle.sort_values('IDLE DAYS', ascending=False)
                summary_table['IDLE DAYS'] = summary_table['IDLE DAYS'].apply(lambda x: f"{x:.1f} days")
                st.dataframe(summary_table, use_container_width=True)
            
        else:
            st.info("No idle days data available")
            
    except Exception as e:
        st.error(f"Error calculating idle days: {e}")
        st.info("No idle days data available")
else:
    st.info("No data available for selected dispatcher/drivers")

# --- KPI 6: Prebooked Loads ---
with st.expander("6. Hours Prebooked (Time Between Booking and Pickup)", expanded=False):
    try:
        # Create a copy to avoid modifying the original dataframe
        df_temp = df.copy()
        
        # Ensure BOOKING TIME exists
        if 'BOOKING TIME' not in df_temp.columns:
            st.error("BOOKING TIME column not found. Please check data loading.")
            prebook_df = pd.DataFrame()
        else:
            # Ensure PICK-UP DATE is timezone-naive
            df_temp['PICK-UP DATE'] = pd.to_datetime(df_temp['PICK-UP DATE'], errors='coerce')
            if df_temp['PICK-UP DATE'].dt.tz is not None:
                df_temp['PICK-UP DATE'] = df_temp['PICK-UP DATE'].dt.tz_localize(None)
            
            # Ensure BOOKING TIME is timezone-naive
            if df_temp['BOOKING TIME'].dt.tz is not None:
                df_temp['BOOKING TIME'] = df_temp['BOOKING TIME'].dt.tz_localize(None)
            
            # Calculate prebook hours only for valid datetime pairs
            mask = df_temp['BOOKING TIME'].notna() & df_temp['PICK-UP DATE'].notna()
            df_temp.loc[mask, 'PREBOOK HOURS'] = (df_temp.loc[mask, 'PICK-UP DATE'] - df_temp.loc[mask, 'BOOKING TIME']).dt.total_seconds() / 3600
            
            prebook_df = df_temp[df_temp['PREBOOK HOURS'] >= 0]
    except Exception as e:
        st.error(f"Error calculating prebook hours: {e}")
        prebook_df = pd.DataFrame()
    if not prebook_df.empty:
        fig6 = px.histogram(prebook_df, x='PREBOOK HOURS', color='FC NAME', nbins=50)
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info("No prebook data available")

# --- KPI 7: Latest Booking Time per Dispatcher ---
with st.expander("7. Latest Booking Time per Dispatcher (Average Hour)", expanded=False):
    try:
        # Ensure BOOKING TIME exists and is timezone-naive
        if 'BOOKING TIME' not in df.columns:
            st.error("BOOKING TIME column not found. Please check data loading.")
            st.info("No booking hour data available")
        else:
            # Ensure BOOKING TIME is timezone-naive
            if df['BOOKING TIME'].dt.tz is not None:
                df['BOOKING TIME'] = df['BOOKING TIME'].dt.tz_localize(None)
            
            df['BOOKING HOUR'] = df['BOOKING TIME'].dt.hour
            avg_booking_hour = df.groupby('FC NAME')['BOOKING HOUR'].mean().reset_index()
            avg_booking_hour = avg_booking_hour.dropna()
            if not avg_booking_hour.empty:
                fig7 = px.bar(avg_booking_hour, x='FC NAME', y='BOOKING HOUR', labels={'BOOKING HOUR': 'Avg Booking Hour'})
                st.plotly_chart(fig7, use_container_width=True)
            else:
                st.info("No booking hour data available")
    except Exception as e:
        st.error(f"Error calculating booking hours: {e}")
        st.info("No booking hour data available")

# --- KPI 8: Cancellation per Dispatcher and per Driver ---
st.subheader("8. Load Cancellations")

# Use the main data but include canceled loads for this analysis
# We need to load the original data without filtering out canceled loads
try:
    # Load the original data without filtering out canceled loads
    if hasattr(file_to_use, 'read'):
        # Reset file pointer to beginning
        file_to_use.seek(0)
        df_with_cancellations = pd.read_csv(file_to_use)
    else:
        df_with_cancellations = pd.read_csv(file_to_use)
    
    # Apply the same preprocessing as main data but don't filter out canceled loads
    df_with_cancellations['DELIVERY DATE'] = pd.to_datetime(df_with_cancellations['DELIVERY DATE'], errors='coerce')
    df_with_cancellations['PICK-UP DATE'] = pd.to_datetime(df_with_cancellations['PICK-UP DATE'], errors='coerce')
    df_with_cancellations['DATE UPLOADED TO THE SYSTEM'] = pd.to_datetime(df_with_cancellations['DATE UPLOADED TO THE SYSTEM'], errors='coerce')
    
    # Convert timezone-aware datetimes to timezone-naive
    for col in ['DATE UPLOADED TO THE SYSTEM', 'PICK-UP DATE', 'DELIVERY DATE']:
        if col in df_with_cancellations.columns and df_with_cancellations[col].dt.tz is not None:
            df_with_cancellations[col] = df_with_cancellations[col].dt.tz_localize(None)
    
    # Filter out AMAZON RELAY loads but keep canceled loads
    if 'BROKER NAME' in df_with_cancellations.columns:
        df_with_cancellations = df_with_cancellations[~df_with_cancellations['BROKER NAME'].str.contains('AMAZON RELAY', case=False, na=False)]
    
    # Convert currency columns
    df_with_cancellations['BROKER RATE (FC) [$]'] = pd.to_numeric(df_with_cancellations['BROKER RATE (FC) [$]'].astype(str).str.replace(',', '').str.replace('$', ''), errors='coerce')
    df_with_cancellations['DRIVER RATE [$]'] = pd.to_numeric(df_with_cancellations['DRIVER RATE [$]'].astype(str).str.replace(',', '').str.replace('$', ''), errors='coerce')
    df_with_cancellations['FULL MILES TOTAL'] = pd.to_numeric(df_with_cancellations['FULL MILES TOTAL'], errors='coerce')
    
except Exception as e:
    st.error(f"Error loading data for cancellation analysis: {e}")
    df_with_cancellations = pd.DataFrame()

# Check if LOAD STATUS column exists
if 'LOAD STATUS' in df_with_cancellations.columns:
    cancelled = df_with_cancellations[df_with_cancellations['LOAD STATUS'].str.contains("cancel", case=False, na=False)]
else:
    cancelled = pd.DataFrame()
    st.warning("LOAD STATUS column not found in data. Cancellation analysis will not be available.")
if not cancelled.empty:
    cancel_fc = cancelled.groupby('FC NAME').size().reset_index(name='Cancellations')
    cancel_fc = cancel_fc.sort_values('Cancellations', ascending=False)
    cancel_driver = cancelled.groupby('DRIVER NAME').size().reset_index(name='Cancellations')
    cancel_driver = cancel_driver.sort_values('Cancellations', ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        fig8a = px.bar(cancel_fc, x='FC NAME', y='Cancellations', title="By Dispatcher",
                      color='Cancellations', color_continuous_scale='Reds')
        fig8a.update_traces(texttemplate='%{y:.0f}', textposition='outside')
        st.plotly_chart(fig8a, use_container_width=True)
    with col2:
        fig8b = px.bar(cancel_driver, x='DRIVER NAME', y='Cancellations', title="By Driver",
                      color='Cancellations', color_continuous_scale='Reds')
        fig8b.update_traces(texttemplate='%{y:.0f}', textposition='outside')
        st.plotly_chart(fig8b, use_container_width=True)
else:
    st.info("No cancellation data available")

# --- Additional KPIs ---
st.subheader("9. Additional Performance Metrics")

# Toggle for PAULO BONILLA
include_paulo = st.checkbox("Include PAULO BONILLA in Total Revenue by Dispatcher", value=True)

# Get the latest week for analysis
if 'WEEK' in df.columns and not df.empty:
    latest_week = df['WEEK'].max()
    latest_week_data = df[df['WEEK'] == latest_week]
    
    # Week-to-week comparison
    if len(df['WEEK'].unique()) >= 2:
        previous_week = df[df['WEEK'] < latest_week]['WEEK'].max()
        previous_week_data = df[df['WEEK'] == previous_week]
        
        # Calculate week-to-week variations
        latest_revenue = latest_week_data['BROKER RATE (FC) [$]'].sum()
        previous_revenue = previous_week_data['BROKER RATE (FC) [$]'].sum()
        revenue_change = ((latest_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
        
        latest_loads = len(latest_week_data)
        previous_loads = len(previous_week_data)
        loads_change = ((latest_loads - previous_loads) / previous_loads * 100) if previous_loads > 0 else 0
        
        # Display week-to-week summary
        st.info(f"""
        **Week-to-Week Comparison (Latest Week: {latest_week.strftime('%b %d, %Y')})**
        - **Revenue**: ${latest_revenue:,.2f} ({revenue_change:+.1f}% vs previous week)
        - **Loads**: {latest_loads} ({loads_change:+.1f}% vs previous week)
        """)
    
    # Revenue by Dispatcher for Latest Week
    col1, col2 = st.columns(2)
    with col1:
        revenue_by_fc_latest = latest_week_data.groupby('FC NAME')['BROKER RATE (FC) [$]'].sum().reset_index()
        
        # Filter out PAULO BONILLA if toggle is off
        if not include_paulo:
            revenue_by_fc_latest = revenue_by_fc_latest[revenue_by_fc_latest['FC NAME'] != 'PAULO BONILLA']
        
        revenue_by_fc_latest = revenue_by_fc_latest.sort_values('BROKER RATE (FC) [$]', ascending=False)
        fig9a = px.bar(revenue_by_fc_latest, x='FC NAME', y='BROKER RATE (FC) [$]', 
                      title=f"Total Revenue by Dispatcher - Latest Week ({latest_week.strftime('%b %d, %Y')})",
                      color='BROKER RATE (FC) [$]', color_continuous_scale='Greens')
        st.plotly_chart(fig9a, use_container_width=True)

    with col2:
        # Average load value by dispatcher for latest week
        avg_load_by_fc_latest = latest_week_data.groupby('FC NAME')['BROKER RATE (FC) [$]'].mean().reset_index()
        avg_load_by_fc_latest = avg_load_by_fc_latest.sort_values('BROKER RATE (FC) [$]', ascending=False)
        fig9b = px.bar(avg_load_by_fc_latest, x='FC NAME', y='BROKER RATE (FC) [$]', 
                      title=f"Average Load Value by Dispatcher - Latest Week ({latest_week.strftime('%b %d, %Y')})",
                      color='BROKER RATE (FC) [$]', color_continuous_scale='Greens')
        st.plotly_chart(fig9b, use_container_width=True)
    
    # Week-over-week trend chart
    if len(df['WEEK'].unique()) >= 2:
        st.subheader("Week-over-Week Revenue Trend")
        weekly_revenue = df.groupby('WEEK')['BROKER RATE (FC) [$]'].sum().reset_index()
        weekly_revenue['WEEK_DISPLAY'] = weekly_revenue['WEEK'].dt.strftime('%b %d, %Y')
        
        fig9c = px.line(weekly_revenue, x='WEEK_DISPLAY', y='BROKER RATE (FC) [$]', 
                       title="Weekly Revenue Trend", markers=True)
        fig9c.update_layout(xaxis_title="Week", yaxis_title="Total Revenue ($)")
        st.plotly_chart(fig9c, use_container_width=True)

else:
    # Fallback to overall data if no week information
    col1, col2 = st.columns(2)
    with col1:
        revenue_by_fc = df.groupby('FC NAME')['BROKER RATE (FC) [$]'].sum().reset_index()
        
        # Filter out PAULO BONILLA if toggle is off
        if not include_paulo:
            revenue_by_fc = revenue_by_fc[revenue_by_fc['FC NAME'] != 'PAULO BONILLA']
        
        revenue_by_fc = revenue_by_fc.sort_values('BROKER RATE (FC) [$]', ascending=False)
        fig9a = px.bar(revenue_by_fc, x='FC NAME', y='BROKER RATE (FC) [$]', title="Total Revenue by Dispatcher (All Data)",
                      color='BROKER RATE (FC) [$]', color_continuous_scale='Greens')
        st.plotly_chart(fig9a, use_container_width=True)

    with col2:
        # Average load value by dispatcher
        avg_load_by_fc = df.groupby('FC NAME')['BROKER RATE (FC) [$]'].mean().reset_index()
        avg_load_by_fc = avg_load_by_fc.sort_values('BROKER RATE (FC) [$]', ascending=False)
        fig9b = px.bar(avg_load_by_fc, x='FC NAME', y='BROKER RATE (FC) [$]', title="Average Load Value by Dispatcher (All Data)",
                      color='BROKER RATE (FC) [$]', color_continuous_scale='Greens')
        st.plotly_chart(fig9b, use_container_width=True)

# Load Status Distribution
st.subheader("10. Load Status Distribution")
if 'LOAD STATUS' in df_with_cancellations.columns:
    status_counts = df_with_cancellations['LOAD STATUS'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    fig10 = px.pie(status_counts, values='Count', names='Status', title="Load Status Distribution (Including Cancellations)")
    st.plotly_chart(fig10, use_container_width=True)
else:
    st.warning("LOAD STATUS column not found. Status distribution will not be available.")

# Summary Statistics
st.subheader("11. Summary Statistics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_loads = len(df)
    st.metric("Total Loads", f"{total_loads:,}")

with col2:
    total_revenue = df['BROKER RATE (FC) [$]'].sum()
    st.metric("Total Revenue", f"${total_revenue:,.2f}")

with col3:
    avg_revenue_per_load = df['BROKER RATE (FC) [$]'].mean()
    st.metric("Avg Revenue/Load", f"${avg_revenue_per_load:,.2f}")

with col4:
    total_miles = df['FULL MILES TOTAL'].sum()
    st.metric("Total Miles", f"{total_miles:,.0f}")

# Data table for detailed view
with st.expander("12. Detailed Load Data", expanded=False):
    if st.checkbox("Show detailed data table"):
        st.dataframe(df, use_container_width=True)

# Reference Data Information
if reference_data:
    with st.expander("13. Reference Data Information", expanded=False):
        
        if 'market' in reference_data:
            st.write("**Market Data:**")
            st.write(f"- Rows: {len(reference_data['market'])}")
            st.write(f"- Columns: {list(reference_data['market'].columns)}")
            if st.checkbox("Show market data preview"):
                st.dataframe(reference_data['market'].head(), use_container_width=True)
        
        if 'dead_zones' in reference_data:
            st.write("**Dead Zones Data:**")
            st.write(f"- Rows: {len(reference_data['dead_zones'])}")
            st.write(f"- Columns: {list(reference_data['dead_zones'].columns)}")
            if st.checkbox("Show dead zones data preview"):
                st.dataframe(reference_data['dead_zones'].head(), use_container_width=True)
        
        if 'market_rates' in reference_data:
            st.write("**Market Rates Data:**")
            st.write(f"- Rows: {len(reference_data['market_rates'])}")
            st.write(f"- Columns: {list(reference_data['market_rates'].columns)}")
            if st.checkbox("Show market rates data preview"):
                st.dataframe(reference_data['market_rates'].head(), use_container_width=True)
        
        if 'driver_fc' in reference_data:
            st.write("**Driver-FC Mapping:**")
            st.write(f"- Rows: {len(reference_data['driver_fc'])}")
            st.write(f"- Columns: {list(reference_data['driver_fc'].columns)}")
            if st.checkbox("Show driver-FC mapping preview"):
                st.dataframe(reference_data['driver_fc'].head(), use_container_width=True)
        
        if 'load_history' in reference_data:
            st.write("**Load History:**")
            st.write(f"- Rows: {len(reference_data['load_history'])}")
            st.write(f"- Columns: {list(reference_data['load_history'].columns)}")
            if st.checkbox("Show load history preview"):
                st.dataframe(reference_data['load_history'].head(), use_container_width=True)

# --- KPI 14: Trucking Made Successful Market Analysis ---
if any(key in reference_data for key in ['market', 'dead_zones', 'market_rates']):
    with st.expander("14. Trucking Made Successful Market Analysis", expanded=False):
        
        # Market rate comparison
        if 'market_rates' in reference_data:
            try:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Market Rate Comparison**")
                    market_rates = reference_data['market_rates']
                    
                    # Handle Trucking Made Successful format
                    if 'value' in market_rates.columns:
                        # Use 'value' as rate and 'name' as state
                        fig14a = px.bar(market_rates.head(10), x='name', y='value', 
                                       title="Top 10 States by Market Rate")
                    elif 'STATE' in market_rates.columns and 'RATE' in market_rates.columns:
                        # Standard format
                        fig14a = px.bar(market_rates.head(10), x='STATE', y='RATE', 
                                       title="Top 10 States by Market Rate")
                    elif 'STATE' in market_rates.columns and 'value' in market_rates.columns:
                        # Processed Trucking Made Successful format
                        fig14a = px.bar(market_rates.head(10), x='STATE', y='value', 
                                       title="Top 10 States by Market Rate")
                    elif 'STATE' in market_rates.columns and 'MARKET_RATE' in market_rates.columns:
                        # Converted files format
                        fig14a = px.bar(market_rates.head(10), x='STATE', y='MARKET_RATE', 
                                       title="Top 10 States by Market Rate")
                    else:
                        st.info("Market rates data format not recognized")
                        fig14a = None
                    
                    if fig14a is not None:
                        st.plotly_chart(fig14a, use_container_width=True)
                
                with col2:
                    st.write("**Load Volume Analysis**")
                    if 'market' in reference_data:
                        market_data = reference_data['market']
                        
                        # Handle Trucking Made Successful format for load data
                        if 'value' in market_data.columns:
                            fig14b = px.histogram(market_data, x='value', 
                                                 title="Load Volume Distribution by State")
                        elif 'LOAD_TO_TRUCK_RATIO' in market_data.columns:
                            fig14b = px.histogram(market_data, x='LOAD_TO_TRUCK_RATIO', 
                                                 title="Load-to-Truck Ratio Distribution")
                        elif 'STATE' in market_data.columns and 'LOAD_VOLUME' in market_data.columns:
                            # Converted files format
                            fig14b = px.histogram(market_data, x='LOAD_VOLUME', 
                                                 title="Load Volume Distribution by State")
                        else:
                            st.info("Load data format not recognized")
                            fig14b = None
                        
                        if fig14b is not None:
                            st.plotly_chart(fig14b, use_container_width=True)
            
            except Exception as e:
                st.error(f"Error in market analysis: {e}")
        
        # Dead zone profitability analysis
        if 'dead_zones' in reference_data:
            try:
                st.write("**Dead Zone Analysis**")
                dead_zones = reference_data['dead_zones']
                
                # Handle different data formats
                if 'value' in dead_zones.columns and 'name' in dead_zones.columns:
                    # Trucking Made Successful format - show state vs value
                    fig14c = px.scatter(dead_zones, x='name', y='value', 
                                       title="Dead Zone Analysis by State")
                elif 'STATE' in dead_zones.columns and 'value' in dead_zones.columns:
                    # Processed format
                    fig14c = px.scatter(dead_zones, x='STATE', y='value', 
                                       title="Dead Zone Analysis by State")
                elif 'STATE' in dead_zones.columns and 'DEAD_DELIVERIES' in dead_zones.columns:
                    # Converted files format
                    fig14c = px.scatter(dead_zones, x='STATE', y='DEAD_DELIVERIES', 
                                       title="Dead Zone Analysis by State")
                elif 'PROFITABILITY_SCORE' in dead_zones.columns:
                    # Standard format with profitability
                    fig14c = px.scatter(dead_zones, x='MARKET_RATE', y='PROFITABILITY_SCORE', 
                                       color='STATE', title="Dead Zone Profitability vs Market Rate")
                else:
                    st.info("Dead zone data format not recognized")
                    fig14c = None
                
                if fig14c is not None:
                    st.plotly_chart(fig14c, use_container_width=True)
            except Exception as e:
                st.error(f"Error in dead zone analysis: {e}")
        
        # Show data preview
        with st.expander("📊 Data Preview", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                if 'market_rates' in reference_data:
                    st.write("**Market Rates Data Preview**")
                    st.dataframe(reference_data['market_rates'].head(), use_container_width=True)
            
            with col2:
                if 'market' in reference_data:
                    st.write("**Market Data Preview**")
                    st.dataframe(reference_data['market'].head(), use_container_width=True)

# Sidebar information
st.sidebar.title("ℹ️ Dashboard Info")
st.sidebar.markdown("---")
st.sidebar.markdown("""
**Data Summary:**
- Total Loads: {:,}
- Total Revenue: ${:,.2f}
- Unique Drivers: {}
- Unique Dispatchers: {}
- Date Range: {} to {}
""".format(
    len(df),
    df['BROKER RATE (FC) [$]'].sum(),
    df['DRIVER NAME'].nunique(),
    df['FC NAME'].nunique(),
    df['DELIVERY DATE'].min().strftime('%Y-%m-%d') if pd.notna(df['DELIVERY DATE'].min()) else 'N/A',
    df['DELIVERY DATE'].max().strftime('%Y-%m-%d') if pd.notna(df['DELIVERY DATE'].max()) else 'N/A'
))

st.sidebar.markdown("---")
st.sidebar.markdown("**Need Help?**")
st.sidebar.markdown("Check the README.md file for detailed instructions.") 