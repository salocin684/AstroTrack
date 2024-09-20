import streamlit as st
import requests
import pytz
from datetime import datetime, timezone
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

st.title("AstroTrack")
st.write("Tracking the future of space, one mission at a time.")
st.write("Track upcoming space launches with real-time updates and personalized time zones.")

st.sidebar.header("Filter Options")
user_timezone = st.sidebar.selectbox("Select Timezone", options=["UTC", "Europe/Brussels", "America/New_York"])
time_range = st.sidebar.slider("Launches within the next days", 1, 30, 7) # Not functional yet

st.subheader(f"Upcoming Launches (in {user_timezone} timezone)")

url = "https://ll.thespacedevs.com/2.2.0/launch/upcoming/"
response = requests.get(url)

if response.status_code == 200:
    launches = response.json()
    current_date = datetime.now(timezone.utc)

    mission_names = []
    launch_dates = []
    launch_sites = []

    for launch in launches['results']:
        launch_date = datetime.strptime(launch['net'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

        if launch_date > current_date:
            mission_names.append(launch['name'])
            launch_dates.append(launch['net'])
            launch_sites.append(launch['pad']['location']['name'])

    launch_df = pd.DataFrame({
        "Mission Name": mission_names,
        "Launch Date (UTC)": launch_dates,
        "Launch Site": launch_sites
    })

    def convert_timezone(launch_time, target_timezone):
        launch_time = datetime.strptime(launch_time, "%Y-%m-%dT%H:%M:%SZ")
        utc_time = launch_time.replace(tzinfo=pytz.UTC)
        return utc_time.astimezone(pytz.timezone(target_timezone))

    converted_times = [convert_timezone(time, user_timezone) for time in launch_df["Launch Date (UTC)"]]
    launch_df["Launch Date (Local)"] = converted_times

    st.table(launch_df)
else:
    st.write(f"Error fetching data: {response.status_code}")

# Sample data for a bar chart
missions = ["Satellite", "Crewed", "Cargo", "Exploration"]
counts = [12, 5, 8, 3]

fig, ax = plt.subplots()
ax.bar(missions, counts)
st.pyplot(fig)

count = st_autorefresh(interval=1800000, limit=None, key="fdata")
st.write(f"Auto-refreshing every 30 minutes...")
st.write(f"Refresh {count}")
