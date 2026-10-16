import streamlit as st
import pandas as pd


st.title("OLA Project") 

import streamlit as st

conn = st.connection(
    "mysql",
    type="sql",
    url="mysql+mysqlconnector://root:Root@localhost:3306/sample"
)

st.title("Overview of the Data")

df = conn.query("SELECT * FROM booking_data;", ttl=600)
st.dataframe(df)

st.subheader("Retrieve All Successful Bookings")

df_successful = conn.query(
    "SELECT * FROM booking_data WHERE booking_status = 'success';",
    ttl=600
)

st.dataframe(df_successful)
print(df)

st.subheader("Find the average ride distance for each vehicle type")

df_avg_distance = conn.query(
    "SELECT vehicle_type, AVG(ride_distance) as avg_distance FROM booking_data WHERE booking_status = 'success' GROUP BY vehicle_type;",
    ttl=600
)

st.dataframe(df_avg_distance)
print(df)

st.subheader("Get the total number of cancelled rides by customers")

df_cancelled = conn.query(
    "SELECT customer_id, COUNT(*) as total_cancelled FROM booking_data WHERE booking_status = 'Canceled by Customer' GROUP BY customer_id;",
    ttl=600
)

st.dataframe(df_cancelled)
print(df)

st.subheader("List the top 5 customers who booked the highest number of rides")

df_top_customers = conn.query("""
SELECT 
    Customer_ID,
    COUNT(*) AS total_rides
FROM 
    booking_data
WHERE 
    Customer_ID IS NOT NULL
GROUP BY 
    Customer_ID
ORDER BY 
    total_rides DESC
LIMIT 5;""",
    ttl=600                         

)
st.dataframe(df_top_customers)   
print(df)   

st.subheader("Get the number of rides cancelled by drivers due to personal and car-related issues")

df_driver_cancelled = conn.query("""SELECT 
    COUNT(*) AS total_driver_cancelled_rides
FROM 
    booking_data
WHERE 
    Incomplete_Rides_Reason LIKE '%%Personal%%' 
    AND Incomplete_Rides_Reason LIKE '%%Car%%';
""",
    ttl=600
)
st.dataframe(df_driver_cancelled)
print(df)

st.subheader("Find the maximum and minimum driver ratings for Prime Sedan bookings")

df_driver_ratings = conn.query("""SELECT 
    MAX(Driver_Ratings) AS max_driver_rating,
    MIN(Driver_Ratings) AS min_driver_rating
FROM 
    booking_data
WHERE 
    Vehicle_Type = 'Prime Sedan'
    AND Driver_Ratings IS NOT NULL;
""",

    ttl=600
)

st.dataframe(df_driver_ratings)
print(df)


st.subheader("Retrieve all rides where payment was made using UPI:")

df_upi_payments = conn.query("""
SELECT 
    * 
FROM 
    booking_data 
WHERE 
    Payment_Method = 'UPI';
""",
ttl=600

)

st.dataframe(df_upi_payments)
print(df)

st.subheader("Find the average customer rating per vehicle type:")

df_avg_customer_rating = conn.query("""SELECT 
    Vehicle_Type,
    ROUND(AVG(Customer_Rating), 2) AS avg_customer_rating
FROM 
    booking_data
WHERE 
    Vehicle_Type IS NOT NULL
    AND Customer_Rating IS NOT NULL
GROUP BY 
    Vehicle_Type
ORDER BY 
    avg_customer_rating DESC;
""",
ttl=600

)

st.dataframe(df_avg_customer_rating)
print(df)

st.subheader("Calculate the total booking value of rides completed successfully")

df_total_booking_value = conn.query("""SELECT 
    ROUND(SUM(Booking_Value), 2) AS total_successful_booking_value
FROM 
    booking_data
WHERE 
    Booking_Status = 'Success';
""",
ttl=600
)

st.dataframe(df_total_booking_value)
print(df)   

st.subheader("List all incomplete rides along with the reason")

df_incomplete_rides = conn.query("""SELECT 
    Booking_ID,
    Customer_ID,
    Vehicle_Type,
    Booking_Status,
    Incomplete_Rides_Reason
FROM 
    booking_data
WHERE 
    Incomplete_Rides_Reason IS NOT NULL
    AND TRIM(Incomplete_Rides_Reason) != ''
    AND Incomplete_Rides_Reason != 'null';
""",
ttl=600
)   

st.dataframe(df_incomplete_rides)
print(df)

