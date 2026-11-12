import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# 1. Page Configuration
st.set_page_config(
    page_title="Traffic Crash Analytics",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    div[data-testid="metric-container"] {
        background-color: #1e2130;
        border: 1px solid #2e3244;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Database Connection (Cached for performance)
@st.cache_resource
def get_engine():
    connection_string = "mysql+pymysql://root:Root@localhost/crash_db"
    return create_engine(connection_string)

engine = get_engine()

# Helper function to run queries cleanly
@st.cache_data
def run_query(query):
    return pd.read_sql(query, engine)

# 3. Sidebar Navigation Dropdown
st.sidebar.title("🚦 Traffic Crash Dashboard")
st.sidebar.markdown("Select an analysis module below:")

analysis_options = [
    "0. Overview & Raw Data",
    "1. Dangerous Weather & Crash Combinations",
    "2. Top 10 Streets (Injury Crashes)",
    "3. Injury Percentage by Crash Type",
    "4. Peak Crash Hour by Month",
    "5. Top 5 Nighttime Crash Causes (Hour ≥ 18)",
    "6. Daylight vs. Darkness Injuries",
    "7. Highest Injury Traffic Control Device",
    "8. Top 5 Exact Crash Locations (Lat/Long)",
    "9. Top 5 Streets by Injury Rate (>100 Crashes)",
    "10. Most Common Crash Type by Year",
    "11. Day of Week with Highest Avg Crashes/Hr",
    "12. High-Risk Time Slots (Morning/Evening/etc.)",
    "13. Top 3 Contributing Causes per Crash Type",
    "14. Year-over-Year (YoY) Crash Growth Rate",
    "15. Top 10 Hotspot Zones (Rounded Lat/Long)"
]

selected_option = st.sidebar.selectbox("Choose Analysis:", analysis_options)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Hover over charts to see detailed metrics, zoom in, or download visuals.")

# Main Header
st.title("🚦 Traffic Crash Data Analytics")
st.markdown("---")

# Helper to display SQL inside a clean expander
def show_sql(query):
    with st.expander("🔍 View Executed SQL Query"):
        st.code(query, language="sql")

# ==========================================
# 0. OVERVIEW & RAW DATA
# ==========================================
if selected_option == "0. Overview & Raw Data":
    st.subheader("📊 Dataset Overview & Sample Records")
    
    # Quick KPI Metrics
    kpi_query = """
    SELECT 
        COUNT(*) as total_crashes,
        SUM(INJURIES_TOTAL) as total_injuries,
        COUNT(DISTINCT STREET_NAME) as total_streets
    FROM traffic_crash_data
    """
    kpi_df = run_query(kpi_query)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Recorded Crashes", f"{kpi_df['total_crashes'][0]:,}")
    col2.metric("Total Injuries", f"{int(kpi_df['total_injuries'][0]):,}")
    col3.metric("Unique Streets Affected", f"{kpi_df['total_streets'][0]:,}")
    
    st.markdown("### Sample Data (Top 100 Rows)")
    query = "SELECT * FROM traffic_crash_data LIMIT 100;"
    show_sql(query)
    df = run_query(query)
    st.dataframe(df, use_container_width=True)

# ==========================================
# 1. WEATHER & CRASH COMBINATIONS
# ==========================================
elif selected_option == "1. Dangerous Weather & Crash Combinations":
    st.subheader("⛈️ Top 5 Most Dangerous Weather & Crash Type Combinations")
    query = """
    SELECT weather_condition, crash_type, COUNT(*) AS total_crashes
    FROM traffic_crash_data
    GROUP BY weather_condition, crash_type
    ORDER BY total_crashes DESC
    LIMIT 5;
    """
    show_sql(query)
    df = run_query(query)
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.dataframe(df, use_container_width=True)
    with col2:
        fig = px.bar(df, x='weather_condition', y='total_crashes', color='crash_type',
                     barmode='group', title="Top 5 Weather & Crash Combinations", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 2. TOP 10 STREETS (INJURY CRASHES)
# ==========================================
elif selected_option == "2. Top 10 Streets (Injury Crashes)":
    st.subheader("🛣️ Top 10 Streets with Highest Number of Injury Crashes")
    query = """
    SELECT street_name, COUNT(*) AS total_injury_crashes
    FROM traffic_crash_data
    WHERE injuries_total > 0
    GROUP BY street_name
    ORDER BY total_injury_crashes DESC
    LIMIT 10;
    """
    show_sql(query)
    df = run_query(query)
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.dataframe(df, use_container_width=True)
    with col2:
        fig = px.bar(df, x='total_injury_crashes', y='street_name', orientation='h',
                     color='total_injury_crashes', color_continuous_scale='Reds',
                     title="Top 10 Streets by Injury Crashes", template="plotly_dark")
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 3. INJURY PERCENTAGE BY CRASH TYPE
# ==========================================
elif selected_option == "3. Injury Percentage by Crash Type":
    st.subheader("📈 Percentage of Crashes Resulting in Injuries by Crash Type")
    query = """
    SELECT crash_type, ROUND(AVG(injuries_total > 0) * 100, 2) AS injury_percentage
    FROM traffic_crash_data
    GROUP BY crash_type
    ORDER BY injury_percentage DESC;
    """
    show_sql(query)
    df = run_query(query)
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.dataframe(df, use_container_width=True)
    with col2:
        fig = px.bar(df, x='crash_type', y='injury_percentage', color='injury_percentage',
                     title="Injury Rate (%) by Crash Type", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 4. PEAK CRASH HOUR BY MONTH
# ==========================================
elif selected_option == "4. Peak Crash Hour by Month":
    st.subheader("🕒 Crash Frequency by Month & Hour")
    query = """
    SELECT
        DATE_FORMAT(crash_date, '%%m') AS crash_month,
        DATE_FORMAT(crash_date, '%%H') AS peak_hour,
        COUNT(*) AS total_crashes
    FROM traffic_crash_data
    GROUP BY DATE_FORMAT(crash_date, '%%m'), DATE_FORMAT(crash_date, '%%H')
    ORDER BY crash_month ASC, total_crashes DESC;
    """
    show_sql(query)
    df = run_query(query)
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.dataframe(df, use_container_width=True)
    with col2:
        fig = px.density_heatmap(df, x='peak_hour', y='crash_month', z='total_crashes',
                                 color_continuous_scale='Viridis', title="Crash Heatmap (Month vs Hour)",
                                 template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 5. NIGHTTIME CRASH CAUSES
# ==========================================
elif selected_option == "5. Top 5 Nighttime Crash Causes (Hour ≥ 18)":
    st.subheader("🌙 Top 5 Primary Causes of Crashes During Nighttime (Hour ≥ 18)")
    query = """
    SELECT FIRST_CRASH_TYPE, COUNT(*) AS total_crashes
    FROM traffic_crash_data
    WHERE CRASH_HOUR >= 18
    GROUP BY FIRST_CRASH_TYPE
    ORDER BY total_crashes DESC
    LIMIT 5;
    """
    show_sql(query)
    df = run_query(query)
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.dataframe(df, use_container_width=True)
    with col2:
        fig = px.pie(df, names='FIRST_CRASH_TYPE', values='total_crashes', hole=0.4,
                     title="Nighttime Crash Distribution", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 6. DAYLIGHT VS DARKNESS INJURIES
# ==========================================
elif selected_option == "6. Daylight vs. Darkness Injuries":
    st.subheader("☀️ vs 🌑 Average Injuries: Daylight vs. Darkness Conditions")
    query = """
    SELECT LIGHTING_CONDITION, ROUND(AVG(INJURIES_TOTAL), 3) AS avg_injuries
    FROM traffic_crash_data
    WHERE LIGHTING_CONDITION LIKE '%%DAYLIGHT%%' OR LIGHTING_CONDITION LIKE '%%DARK%%'
    GROUP BY LIGHTING_CONDITION;
    """
    show_sql(query)
    df = run_query(query)
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.dataframe(df, use_container_width=True)
    with col2:
        fig = px.bar(df, x='LIGHTING_CONDITION', y='avg_injuries', color='LIGHTING_CONDITION',
                     title="Average Injuries by Lighting Condition", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 7. TRAFFIC CONTROL DEVICE INJURIES
# ==========================================
elif selected_option == "7. Highest Injury Traffic Control Device":
    st.subheader("🚥 Traffic Control Device with Highest Average Injuries")
    query = """
    SELECT TRAFFIC_CONTROL_DEVICE, ROUND(AVG(INJURIES_TOTAL), 3) AS avg_injuries
    FROM traffic_crash_data
    GROUP BY TRAFFIC_CONTROL_DEVICE
    ORDER BY avg_injuries DESC
    LIMIT 1;
    """
    show_sql(query)
    df = run_query(query)
    
    st.metric(
        label=f"Highest Risk Device: {df['TRAFFIC_CONTROL_DEVICE'][0]}",
        value=f"{df['avg_injuries'][0]} Avg Injuries / Crash"
    )
    st.dataframe(df, use_container_width=True)

# ==========================================
# 8. TOP 5 LOCATIONS (LAT/LONG)
# ==========================================
elif selected_option == "8. Top 5 Exact Crash Locations (Lat/Long)":
    st.subheader("📍 Top 5 Exact Coordinates with Highest Crash Frequency")
    query = """
    SELECT LATITUDE, LONGITUDE, COUNT(*) AS total_crashes
    FROM traffic_crash_data
    WHERE LATITUDE IS NOT NULL AND LONGITUDE IS NOT NULL
    GROUP BY LATITUDE, LONGITUDE
    ORDER BY total_crashes DESC
    LIMIT 5;
    """
    show_sql(query)
    df = run_query(query)
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.dataframe(df, use_container_width=True)
    with col2:
        map_df = df.rename(columns={'LATITUDE': 'lat', 'LONGITUDE': 'lon'})
        st.map(map_df)

# ==========================================
# 9. TOP 5 STREETS BY INJURY RATE
# ==========================================
elif selected_option == "9. Top 5 Streets by Injury Rate (>100 Crashes)":
    st.subheader("⚠️ Top 5 Streets with Highest Injury Rate (>100 Total Crashes)")
    query = """
    SELECT STREET_NAME, COUNT(*) AS total_crashes, ROUND(AVG(INJURIES_TOTAL > 0) * 100, 2) AS injury_rate
    FROM traffic_crash_data
    WHERE STREET_NAME IS NOT NULL
    GROUP BY STREET_NAME
    HAVING total_crashes > 100
    ORDER BY injury_rate DESC
    LIMIT 5;
    """
    show_sql(query)
    df = run_query(query)
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.dataframe(df, use_container_width=True)
    with col2:
        fig = px.bar(df, x='STREET_NAME', y='injury_rate', color='total_crashes',
                     title="Top 5 Streets by Injury Rate (%)", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 10. MOST COMMON CRASH TYPE BY YEAR
# ==========================================
elif selected_option == "10. Most Common Crash Type by Year":
    st.subheader("📅 Crash Types Breakdown by Year")
    query = """
    SELECT year AS CRASH_YEAR, FIRST_CRASH_TYPE AS most_common_crash_type, COUNT(*) AS total_crashes
    FROM traffic_crash_data
    GROUP BY CRASH_YEAR, FIRST_CRASH_TYPE
    ORDER BY CRASH_YEAR ASC, total_crashes DESC;
    """
    show_sql(query)
    df = run_query(query)
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.dataframe(df, use_container_width=True)
    with col2:
        fig = px.bar(df, x='CRASH_YEAR', y='total_crashes', color='most_common_crash_type',
                     title="Yearly Crash Types", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 11. DAY OF WEEK HIGHEST AVG CRASHES
# ==========================================
elif selected_option == "11. Day of Week with Highest Avg Crashes/Hr":
    st.subheader("📆 Day of the Week with Highest Average Crashes per Hour")
    query = """
    SELECT CRASH_DAY_OF_WEEK, ROUND(COUNT(*) / 24.0, 2) AS avg_crashes_per_hour
    FROM traffic_crash_data
    GROUP BY CRASH_DAY_OF_WEEK
    ORDER BY avg_crashes_per_hour DESC
    LIMIT 1;
    """
    show_sql(query)
    df = run_query(query)
    
    st.metric(
        label=f"Peak Day (Day Index: {df['CRASH_DAY_OF_WEEK'][0]})",
        value=f"{df['avg_crashes_per_hour'][0]} Avg Crashes / Hour"
    )
    st.dataframe(df, use_container_width=True)

# ==========================================
# 12. HIGH-RISK TIME SLOTS
# ==========================================
elif selected_option == "12. High-Risk Time Slots (Morning/Evening/etc.)":
    st.subheader("⏰ High-Risk Time Slots by Total Injuries")
    query = """
    SELECT 
        CASE 
            WHEN CRASH_HOUR BETWEEN 6 AND 11 THEN 'Morning (6AM - 11AM)'
            WHEN CRASH_HOUR BETWEEN 12 AND 16 THEN 'Afternoon (12PM - 4PM)'
            WHEN CRASH_HOUR BETWEEN 17 AND 21 THEN 'Evening (5PM - 9PM)'
            ELSE 'Night (10PM - 5AM)'
        END AS time_bucket,
        SUM(INJURIES_TOTAL) AS total_injuries
    FROM traffic_crash_data
    GROUP BY time_bucket
    ORDER BY total_injuries DESC;
    """
    show_sql(query)
    df = run_query(query)
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.dataframe(df, use_container_width=True)
    with col2:
        fig = px.pie(df, names='time_bucket', values='total_injuries', hole=0.4,
                     title="Total Injuries by Time of Day", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 13. TOP 3 CONTRIBUTING CAUSES
# ==========================================
elif selected_option == "13. Top 3 Contributing Causes per Crash Type":
    st.subheader("🔍 Top 3 Contributing Causes for Each Crash Type")
    query = """
    SELECT FIRST_CRASH_TYPE, PRIM_CONTRIBUTORY_CAUSE, total_crashes
    FROM (
        SELECT 
            FIRST_CRASH_TYPE, PRIM_CONTRIBUTORY_CAUSE, COUNT(*) AS total_crashes,
            ROW_NUMBER() OVER (PARTITION BY FIRST_CRASH_TYPE ORDER BY COUNT(*) DESC) AS rnk
        FROM traffic_crash_data
        GROUP BY FIRST_CRASH_TYPE, PRIM_CONTRIBUTORY_CAUSE
    ) AS ranked_crashes
    WHERE rnk <= 3;
    """
    show_sql(query)
    df = run_query(query)
    
    st.dataframe(df, use_container_width=True)
    fig = px.bar(df, x='FIRST_CRASH_TYPE', y='total_crashes', color='PRIM_CONTRIBUTORY_CAUSE',
                 title="Top 3 Causes per Crash Type", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 14. YEAR-OVER-YEAR GROWTH RATE
# ==========================================
elif selected_option == "14. Year-over-Year (YoY) Crash Growth Rate":
    st.subheader("📈 Year-over-Year (YoY) Crash Growth Rate")
    query = """
    SELECT 
        year AS CRASH_YEAR,
        COUNT(*) AS total_crashes,
        LAG(COUNT(*)) OVER (ORDER BY year) AS prev_year_crashes,
        ROUND((COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY year)) * 100.0 / 
              LAG(COUNT(*)) OVER (ORDER BY year), 2) AS yoy_growth_percentage
    FROM traffic_crash_data
    GROUP BY year
    ORDER BY year;
    """
    show_sql(query)
    df = run_query(query)
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.dataframe(df, use_container_width=True)
    with col2:
        fig = px.line(df, x='CRASH_YEAR', y='total_crashes', markers=True,
                      text='yoy_growth_percentage', title="Yearly Crash Trend & YoY %",
                      template="plotly_dark")
        fig.update_traces(textposition="top center")
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 15. TOP 10 HOTSPOT ZONES
# ==========================================
elif selected_option == "15. Top 10 Hotspot Zones (Rounded Lat/Long)":
    st.subheader("🗺️ Top 10 Hotspot Zones (Grouped by 2 Decimal Places)")
    query = """
    SELECT ROUND(LATITUDE, 2) AS lat_zone, ROUND(LONGITUDE, 2) AS long_zone, COUNT(*) AS total_crashes
    FROM traffic_crash_data
    WHERE LATITUDE IS NOT NULL AND LONGITUDE IS NOT NULL
    GROUP BY lat_zone, long_zone
    ORDER BY total_crashes DESC
    LIMIT 10;
    """
    show_sql(query)
    df = run_query(query)
    df['zone'] = df['lat_zone'].astype(str) + ", " + df['long_zone'].astype(str)
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.dataframe(df, use_container_width=True)
        map_df = df.rename(columns={'lat_zone': 'lat', 'long_zone': 'lon'})
        st.map(map_df)
    with col2:
        fig = px.bar(df, x='zone', y='total_crashes', color='total_crashes',
                     color_continuous_scale='Magma', title='Top 10 Crash Zones', template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        
        fig2 = px.line(df, x='zone', y='total_crashes', markers=True,
                       title='Top 10 Crash Zones (Trend View)',
                       labels={'zone': 'Zone (Lat, Long)', 'total_crashes': 'Total Crashes'},
                       template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)