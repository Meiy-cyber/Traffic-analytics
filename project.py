import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

st.title("Traffic Analysis")


connection_string = "mysql+pymysql://root:Root@localhost/crash_db"

engine = create_engine(connection_string)

st.header("Traffic_crash_data")

df = pd.read_sql("""
    SELECT *
    FROM traffic_crash_data
""", engine)

st.write(df)

st.subheader("""Find the top 5 most dangerous combinations of weather and
crash type based on total crashes""")

df = pd.read_sql("""
    SELECT
        weather_condition,
        crash_type,
        COUNT(*) AS total_crashes
    FROM traffic_crash_data
    GROUP BY
        weather_condition,
        crash_type
    ORDER BY
        total_crashes DESC
    LIMIT 5;
""", engine)

st.write(df)

st.bar_chart(
    data=df,
    x='weather_condition',
    y='total_crashes',
    color='crash_type'
)

st.subheader("""Identify the top 10 streets with the highest number of injury
crashes""")

df = pd.read_sql("""
    SELECT 
        street_name,
        COUNT(*) AS total_injury_crashes
    FROM 
        traffic_crash_data
    WHERE 
        injuries_total > 0
    GROUP BY 
        street_name
    ORDER BY 
        total_injury_crashes DESC
    LIMIT 10;
""", engine)

st.write(df)

st.bar_chart(
    data=df,
    x='street_name',
    y='total_injury_crashes'
)

st.subheader("""Find the percentage of crashes that resulted in injuries for each
crash type""")

df = pd.read_sql("""
    SELECT 
    crash_type,
    AVG(injuries_total > 0) * 100 AS injury_percentage
FROM 
    traffic_crash_data
GROUP BY 
    crash_type;
    """, engine)

st.write(df)

st.line_chart(
    data=df,
    x='crash_type',
    y='injury_percentage'
)

st.subheader("""Determine the peak crash hour for each month""")

df = pd.read_sql("""
SELECT
    DATE_FORMAT(crash_date, '%%m') AS crash_month,
    DATE_FORMAT(crash_date, '%%H') AS peak_hour,
    COUNT(*) AS total_crashes
FROM
    traffic_crash_data
GROUP BY
    DATE_FORMAT(crash_date, '%%m'),
    DATE_FORMAT(crash_date, '%%H')
ORDER BY
    total_crashes DESC;
""", engine)

st.write(df)



st.subheader(""" Find the top 5 primary causes of crashes during night time (CRASH_HOUR ≥ 18)""")

df = pd.read_sql("""
SELECT 
    FIRST_CRASH_TYPE,
    COUNT(*) AS total_crashes
FROM 
    traffic_crash_data
WHERE 
    CRASH_HOUR >= 18
GROUP BY 
    FIRST_CRASH_TYPE
ORDER BY 
    total_crashes DESC
LIMIT 5;
""", engine)

st.write(df)

st.bar_chart(
    data=df,
    x='FIRST_CRASH_TYPE',
    y='total_crashes'
)

st.subheader("""Compare average number of injuries in daylight vs darkness conditions""")

df = pd.read_sql("""SELECT 
    LIGHTING_CONDITION,
    AVG(INJURIES_TOTAL) AS avg_injuries
FROM 
    traffic_crash_data
WHERE 
    LIGHTING_CONDITION LIKE '%%DAYLIGHT%%' 
    OR LIGHTING_CONDITION LIKE '%%DARK%%'
GROUP BY 
    LIGHTING_CONDITION;
    """, engine)

st.write(df)

st.line_chart(
    data=df,
    x='LIGHTING_CONDITION',
    y='avg_injuries'
)


st.subheader("""Find which traffic control device type has the highest average injuries per crash""")

df = pd.read_sql("""
SELECT 
    TRAFFIC_CONTROL_DEVICE,
    AVG(INJURIES_TOTAL) AS avg_injuries
FROM 
    traffic_crash_data
GROUP BY 
    TRAFFIC_CONTROL_DEVICE
ORDER BY 
    avg_injuries DESC
LIMIT 1;
""", engine)

st.write(df)

st.subheader("""Identify the top 5 locations (latitude/longitude) with the highest crash frequency""")

df = pd.read_sql("""
SELECT 
    LATITUDE,
    LONGITUDE,
    COUNT(*) AS total_crashes
FROM 
    traffic_crash_data
WHERE 
    LATITUDE IS NOT NULL 
    AND LONGITUDE IS NOT NULL
GROUP BY 
    LATITUDE, 
    LONGITUDE
ORDER BY 
    total_crashes DESC
LIMIT 5;
""", engine)

st.write(df)

st.subheader("""Find the top 5 streets with the highest injury rate, considering only streets with more than 100 crashes""")

df = pd.read_sql("""
SELECT 
    STREET_NAME,
    COUNT(*) AS total_crashes,
    AVG(INJURIES_TOTAL > 0) * 100 AS injury_rate
FROM 
    traffic_crash_data
WHERE 
    STREET_NAME IS NOT NULL
GROUP BY 
    STREET_NAME
HAVING 
    total_crashes > 100
ORDER BY 
    injury_rate DESC
LIMIT 5;
""", engine)

st.write(df)

st.bar_chart(
    data=df,
    x='STREET_NAME',
    y='injury_rate'
)

st.subheader("""For each year, identify the most common crash type""")

df = pd.read_sql("""
SELECT 
    year AS CRASH_YEAR,
    FIRST_CRASH_TYPE AS most_common_crash_type,
    COUNT(*) AS total_crashes
FROM 
    traffic_crash_data
GROUP BY 
    CRASH_YEAR, 
    FIRST_CRASH_TYPE
ORDER BY 
    CRASH_YEAR ASC, 
    total_crashes DESC
""",engine)

st.write(df)

st.bar_chart(
    data=df,
    x='CRASH_YEAR',
    y='total_crashes',
    color='most_common_crash_type'
)


st.subheader("""Find the day of the week with the highest average crashes per hour""")

df = pd.read_sql("""
SELECT 
    CRASH_DAY_OF_WEEK,
    ROUND(COUNT(*) / 24.0, 2) AS avg_crashes_per_hour
FROM 
    traffic_crash_data
GROUP BY 
    CRASH_DAY_OF_WEEK
ORDER BY 
    avg_crashes_per_hour DESC
LIMIT 1;
""", engine)

st.write(df)

st.subheader("""Identify high-risk time slots:
● Group hours into buckets (Morning, Afternoon, Evening, Night)
● Find which bucket has the highest injury crashes
""")

df = pd.read_sql("""
SELECT 
    CASE 
        WHEN CRASH_HOUR BETWEEN 6 AND 11 THEN 'Morning'
        WHEN CRASH_HOUR BETWEEN 12 AND 16 THEN 'Afternoon'
        WHEN CRASH_HOUR BETWEEN 17 AND 21 THEN 'Evening'
        ELSE 'Night'
    END AS time_bucket,
    SUM(INJURIES_TOTAL) AS total_injuries
FROM 
    traffic_crash_data
GROUP BY 
    time_bucket
ORDER BY 
    total_injuries DESC;
    """, engine)

st.write(df)

st.bar_chart(
    data=df,
    x='time_bucket',
    y='total_injuries'
)

st.subheader(""" Find the top 3 contributing causes for each crash type""")

df = pd.read_sql("""
SELECT 
    FIRST_CRASH_TYPE,
    PRIM_CONTRIBUTORY_CAUSE,
    total_crashes
FROM (
    SELECT 
        FIRST_CRASH_TYPE,
        PRIM_CONTRIBUTORY_CAUSE,
        COUNT(*) AS total_crashes,
        ROW_NUMBER() OVER (
            PARTITION BY FIRST_CRASH_TYPE 
            ORDER BY COUNT(*) DESC
        ) AS rnk
    FROM 
        traffic_crash_data
    GROUP BY 
        FIRST_CRASH_TYPE,
        PRIM_CONTRIBUTORY_CAUSE
) AS ranked_crashes
WHERE 
    rnk <= 3;
""", engine)

st.write(df)

st.bar_chart(
    data=df,
    x='FIRST_CRASH_TYPE',
    y='total_crashes',
    color='PRIM_CONTRIBUTORY_CAUSE'
)

st.subheader("""Calculate the year-over-year growth rate of crashes""")

df = pd.read_sql("""
    SELECT 
    year AS CRASH_YEAR,
    COUNT(*) AS total_crashes,
    LAG(COUNT(*)) OVER (ORDER BY year) AS prev_year_crashes,
    ROUND(
        (COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY year)) * 100.0 / 
        LAG(COUNT(*)) OVER (ORDER BY year), 
        2
    ) AS yoy_growth_percentage
FROM 
    traffic_crash_data
GROUP BY 
    year
ORDER BY 
    year;
""", engine)

st.write(df)

st.bar_chart(
    data=df,
    x='CRASH_YEAR',
    y='total_crashes'
)

st.subheader("""Identify hotspot zones:
● Group nearby locations (round latitude & longitude to 2 decimal
places)
● Find top 10 zones with highest crashes""")

df = pd.read_sql("""
SELECT 
    ROUND(LATITUDE, 2) AS lat_zone,
    ROUND(LONGITUDE, 2) AS long_zone,
    COUNT(*) AS total_crashes
FROM 
    traffic_crash_data
WHERE 
    LATITUDE IS NOT NULL 
    AND LONGITUDE IS NOT NULL
GROUP BY 
    lat_zone, 
    long_zone
ORDER BY 
    total_crashes DESC
LIMIT 10;
""", engine)

st.write(df)

df['zone'] = df['lat_zone'].astype(str) + ", " + df['long_zone'].astype(str)

st.bar_chart(
    data=df,
    x='zone',
    y='total_crashes'
)

fig = px.line(
    df,
    x='zone',
    y='total_crashes',
    markers=True,
    title='Top 10 Crash Zones (Trend View)',
    labels={'zone': 'Zone (Lat, Long)', 'total_crashes': 'Total Crashes'}
)

st.plotly_chart(fig, use_container_width=True)