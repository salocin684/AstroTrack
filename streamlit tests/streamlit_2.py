import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import folium
from streamlit_folium import st_folium
from datetime import datetime
import pytz

data = {
    'Mission Name': ['Artemis I', 'Starlink 15', 'Mars Rover', 'James Webb', 'Crew-7'],
    'Launch Date': ['2024-09-20', '2024-09-22', '2024-10-10', '2024-11-01', '2024-12-15'],
    'Objective': ['Moon Exploration', 'Satellite Deployment', 'Mars Exploration', 'Space Observation', 'Manned Mission'],
    'Status': ['Scheduled', 'Scheduled', 'Scheduled', 'Delayed', 'Launched'],
    'Predicted Outcome': ['95%', '98%', '90%', '80%', 'Completed'],
    'Agency': ['NASA', 'SpaceX', 'NASA', 'ESA', 'SpaceX'],
    'Launch Site': ['Kennedy Space Center', 'Cape Canaveral', 'Vandenberg', 'Kourou', 'Baikonur'],
    'Latitude': [28.5721, 28.5623, 34.6321, 5.236, 45.964],
    'Longitude': [-80.648, -80.5774, -120.610, -52.768, 63.305],
}

df = pd.DataFrame(data)
df['Launch Date'] = pd.to_datetime(df['Launch Date'])

st.set_page_config(page_title="Space Mission Tracker", layout="wide")

st.title("🚀 Space Mission Tracker")
st.markdown("""
    **Track Space Missions with AI-powered Predictions**  
    Get real-time updates, mission insights, and predicted outcomes of global space missions.
    """)

st.sidebar.header("Mission Filters")

agency_filter = st.sidebar.multiselect("Select Agencies", df['Agency'].unique(), default=df['Agency'].unique())

status_filter = st.sidebar.multiselect("Select Mission Status", df['Status'].unique(), default=df['Status'].unique())

launch_date_filter = st.sidebar.slider("Launch Date Range", 
                                       min_value=df['Launch Date'].min().date(), 
                                       max_value=df['Launch Date'].max().date(),
                                       value=(df['Launch Date'].min().date(), df['Launch Date'].max().date()))

st.sidebar.header("Timezone Settings")
timezones = pytz.all_timezones
selected_timezone = st.sidebar.selectbox("Select your timezone", options=timezones, index=timezones.index('UTC'))

df['Launch Date (Local)'] = df['Launch Date'].dt.tz_localize('UTC').dt.tz_convert(selected_timezone)

filtered_df = df[
    (df['Agency'].isin(agency_filter)) & 
    (df['Status'].isin(status_filter)) & 
    (df['Launch Date'].dt.date.between(launch_date_filter[0], launch_date_filter[1]))
]

st.subheader("Upcoming Space Missions")
st.write(f"The table below shows space missions with their predicted outcomes and launch times in your selected timezone: **{selected_timezone}**.")

st.dataframe(filtered_df[['Mission Name', 'Launch Date (Local)', 'Objective', 'Status', 'Predicted Outcome']])

st.subheader("Launch Sites Map")
st.write("An interactive map displaying the global launch sites for upcoming missions.")

m = folium.Map(location=[20, 0], zoom_start=2)

for idx, row in filtered_df.iterrows():
    folium.Marker([row['Latitude'], row['Longitude']], 
                  popup=f"{row['Mission Name']} ({row['Agency']}) - {row['Launch Site']}", 
                  tooltip=row['Launch Site']).add_to(m)

st_folium(m, width=700, height=500)

st.subheader("Mission Success Predictions")
st.write("This graph shows the predicted success rates of upcoming missions.")

filtered_numeric_df = filtered_df[filtered_df['Predicted Outcome'].str.contains('%')]
filtered_numeric_df['Predicted Outcome (%)'] = filtered_numeric_df['Predicted Outcome'].str.rstrip('%').astype(float)

fig = go.Figure()

for mission in filtered_numeric_df['Mission Name'].unique():
    mission_data = filtered_numeric_df[filtered_numeric_df['Mission Name'] == mission]
    fig.add_trace(go.Scatter(x=mission_data['Launch Date (Local)'], y=mission_data['Predicted Outcome (%)'],
                             mode='lines+markers', name=mission))

fig.update_layout(
    title="Predicted Mission Success Rates",
    xaxis_title="Launch Date (Local Time)",
    yaxis_title="Predicted Success Rate (%)",
    legend_title="Mission",
    template="plotly_dark"
)

st.plotly_chart(fig)

st.subheader("Mission Objectives Breakdown")
st.write("A pie chart showing the distribution of mission objectives.")

objective_counts = filtered_df['Objective'].value_counts()
fig_pie = px.pie(names=objective_counts.index, values=objective_counts.values, 
                 title="Mission Objective Distribution",
                 template="plotly_dark")
fig_pie.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(fig_pie)

st.sidebar.header("Mission Notifications")
st.sidebar.write("Get alerts for specific missions based on your timezone.")
mission_alert = st.sidebar.selectbox("Choose Mission to Track", df['Mission Name'])
alert_time = st.sidebar.time_input("Set Alert Time", datetime.now().time())
st.sidebar.write(f"You will receive an alert for **{mission_alert}** at {alert_time} in **{selected_timezone}** time.")

st.subheader("AI Predictions")
st.write("Future AI-driven features will predict the likelihood of launch delays, mission success rates, and more. Stay tuned for updates!")
st.info("AI prediction functionality is coming soon!")
