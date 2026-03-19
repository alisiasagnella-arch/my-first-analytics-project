import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    trips = pd.read_csv("datasets/trips.csv")
    cars = pd.read_csv("datasets/cars.csv")
    cities = pd.read_csv("datasets/cities.csv")
 
    return trips, cars, cities

trips, cars, cities = load_data()

trips_merged = trips.merge(cars, left_on="car_id", right_on="id")
trips_merged = trips_merged.merge(cities, on="city_id")
trips_merged = trips_merged.drop(columns=["id_x", "id_y", "city_id", "customer_id"])
trips_merged["pickup_date"] = pd.to_datetime(trips_merged["pickup_time"]).dt.date

st.sidebar.header("Filters")
cars_brand = st.sidebar.multiselect(
    "Select Car Brand",
    options=trips_merged["brand"].unique(),
    default=trips_merged["brand"].unique()
)
trips_merged = trips_merged[trips_merged["brand"].isin(cars_brand)]

total_trips    = len(trips_merged)
total_distance = trips_merged["distance"].sum()
top_car        = trips_merged.groupby("model")["revenue"].sum().idxmax()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Trips", total_trips)
with col2:
    st.metric("Top Car Model by Revenue", top_car)
with col3:
    st.metric("Total Distance (km)", f"{total_distance:,.2f}")

st.subheader("Data Preview")
st.write(trips_merged.head())

st.subheader("Trips Over Time")
st.line_chart(trips_merged.groupby("pickup_date").size().reset_index(name="trips").set_index("pickup_date"))

st.subheader("Revenue Per Car Model")
st.bar_chart(trips_merged.groupby("model")["revenue"].sum())

st.subheader("Cumulative Revenue Growth")
st.area_chart(trips_merged.sort_values("pickup_date").groupby("pickup_date")["revenue"].sum().cumsum())

st.subheader("Number of Trips Per Car Model")
st.bar_chart(trips_merged.groupby("model").size())

st.subheader("Revenue by City")
st.bar_chart(trips_merged.groupby("city_name")["revenue"].sum())

st.subheader("Average Trip Duration by City")
trips_merged["duration_hours"] = (
    pd.to_datetime(trips_merged["dropoff_time"]) - 
    pd.to_datetime(trips_merged["pickup_time"])
).dt.total_seconds() / 3600
st.bar_chart(trips_merged.groupby("city_name")["duration_hours"].mean())

st.subheader("Revenue by Car Brand")
st.bar_chart(trips_merged.groupby("brand")["revenue"].sum())

st.subheader("Trips Per City")
st.bar_chart(trips_merged.groupby("city_name").size())

year_filter = st.sidebar.multiselect(
    "Select Car Year",
    options=sorted(trips_merged["year"].unique()),
    default=sorted(trips_merged["year"].unique())
)

min_distance, max_distance = st.sidebar.slider(
    "Select Distance Range (km)",
    min_value=float(trips_merged["distance"].min()),
    max_value=float(trips_merged["distance"].max()),
    value=(float(trips_merged["distance"].min()), float(trips_merged["distance"].max()))
)

trips_merged = trips_merged[
    trips_merged["year"].isin(year_filter) &
    (trips_merged["distance"] >= min_distance) &
    (trips_merged["distance"] <= max_distance)
]

st.subheader("Revenue Over Time")
st.line_chart(trips_merged.groupby("pickup_date")["revenue"].sum())

st.subheader("Average Distance by Brand")
st.bar_chart(trips_merged.groupby("brand")["distance"].mean())

st.subheader("Average Revenue by City")
st.bar_chart(trips_merged.groupby("city_name")["revenue"].mean())

st.subheader("Trips Per Car Year")
st.bar_chart(trips_merged.groupby("year").size())

st.subheader("Average Daily Price by Brand")
st.bar_chart(trips_merged.groupby("brand")["daily_price"].mean())

min_price, max_price = st.sidebar.slider(
    "Select Daily Price Range",
    min_value=float(trips_merged["daily_price"].min()),
    max_value=float(trips_merged["daily_price"].max()),
    value=(float(trips_merged["daily_price"].min()), float(trips_merged["daily_price"].max()))
)
trips_merged = trips_merged[
    (trips_merged["daily_price"] >= min_price) &
    (trips_merged["daily_price"] <= max_price)
]

st.subheader("Distance Distribution by Brand")
st.bar_chart(trips_merged.groupby("brand")["distance"].sum())

st.subheader("Number of Trips by Day of Week")
trips_merged["day_of_week"] = pd.to_datetime(trips_merged["pickup_time"]).dt.day_name()
st.bar_chart(trips_merged.groupby("day_of_week").size())

st.subheader("Average Distance by City")
st.bar_chart(trips_merged.groupby("city_name")["distance"].mean())

st.subheader("Revenue per km by Brand")
trips_merged["revenue_per_km"] = trips_merged["revenue"] / trips_merged["distance"]
st.bar_chart(trips_merged.groupby("brand")["revenue_per_km"].mean())

st.subheader("Pickup Locations Map")
map_data = trips_merged[["pickup_lat", "pickup_lon"]].rename(
    columns={"pickup_lat": "lat", "pickup_lon": "lon"}
).dropna()
st.map(map_data)

day_filter = st.sidebar.multiselect(
    "Select Day of Week",
    options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
)
trips_merged["day_of_week"] = pd.to_datetime(trips_merged["pickup_time"]).dt.day_name()
trips_merged = trips_merged[trips_merged["day_of_week"].isin(day_filter)]

month_filter = st.sidebar.multiselect(
    "Select Month",
    options=["January", "February", "March", "April", "May", "June", 
             "July", "August", "September", "October", "November", "December"],
    default=["January", "February", "March", "April", "May", "June", 
             "July", "August", "September", "October", "November", "December"]
)
trips_merged["month"] = pd.to_datetime(trips_merged["pickup_time"]).dt.month_name()
trips_merged = trips_merged[trips_merged["month"].isin(month_filter)]

min_dist = st.sidebar.number_input(
    "Minimum Distance (km)", 
    min_value=0.0, 
    max_value=float(trips_merged["distance"].max()), 
    value=0.0
)
trips_merged = trips_merged[trips_merged["distance"] >= min_dist]
