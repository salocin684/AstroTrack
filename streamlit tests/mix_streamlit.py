import streamlit as st
import requests
import pytz
from datetime import datetime, timezone
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import time

known_launch_sites = {
    "Kennedy Space Center, FL, USA": (28.5721, -80.648),
    "Cape Canaveral SFS, FL, USA": (28.5623, -80.5774),
    "Vandenberg SFB, CA, USA": (34.6321, -120.610),
    "Rocket Lab Launch Complex 1, Mahia Peninsula, New Zealand": (-39.261, 177.865),
    "Tanegashima Space Center, Japan": (30.4028, 130.9764),
    "Jiuquan Satellite Launch Center, People's Republic of China": (40.9606, 100.2983),
    "Baikonur Cosmodrome, Kazakhstan": (45.9206, 63.3422),
    "Plesetsk Cosmodrome, Russian Federation": (62.927, 40.575),
}

def categorize_objective(description):
    description = description.lower()
    if "satellite" in description:
        return "Satellite Deployment"
    elif "crew" in description or "crewed" in description:
        return "Crewed Mission"
    elif "explore" in description or "exploration" in description:
        return "Exploration"
    elif "moon" in description or "mars" in description:
        return "Lunar/Mars Mission"
    else:
        return "Other"

def fetch_launch_data():
    url = "https://ll.thespacedevs.com/2.2.0/launch/upcoming/"
    params = {
        "mode": "detailed",
    }
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json(), None
        elif response.status_code == 429:
            retry_count += 1
            wait_time = 2 ** retry_count
            st.write(f"API rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            return None, response.status_code
    return None, 429

st.set_page_config(page_title="AstroTrack - Space Mission Tracker", layout="wide")
st.title("🚀 AstroTrack - Space Mission Tracker")
st.markdown("""
    **Track upcoming space launches with real-time updates and AI-powered predictions**  
    Get insights on global space missions, predicted success rates, and launch timings in your local timezone.
    """)

st.markdown("""
    <style>
    .dataframe { font-size: 16px !important; }
    .table-wrap td { white-space: normal !important; word-wrap: break-word !important; }
    </style>
""", unsafe_allow_html=True)

st.sidebar.header("Filter Options")
user_timezone = st.sidebar.selectbox("Select Timezone", options=pytz.all_timezones, index=pytz.all_timezones.index('UTC'))

time_range = st.sidebar.slider("Launches within the next days", 1, 30, 7)

st.sidebar.header("API Query Filters")
search_query = st.sidebar.text_input("Search by Launch Name, Agency, or Mission", "")
crew_filter = st.sidebar.selectbox("Is Crew Mission?", options=["All", "True", "False"], index=0)

launch_data, status_code = fetch_launch_data()

if launch_data is not None:
    launches = launch_data
    current_date = datetime.now(timezone.utc)

    mission_names = []
    launch_dates = []
    launch_sites = []
    objectives = []
    objective_categories = []
    rockets = []

    for launch in launches['results']:
        launch_date = datetime.strptime(launch['net'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

        if launch_date > current_date:
            mission_names.append(launch['name'])
            launch_dates.append(launch['net'])

            if 'pad' in launch and 'location' in launch['pad']:
                site_name = launch['pad']['location'].get('name', 'Unknown')
                launch_sites.append(site_name)
            else:
                launch_sites.append("Unknown")

            if 'mission' in launch and isinstance(launch['mission'], dict):
                objective = launch['mission'].get('description', 'Unknown')
                objectives.append(objective)
                objective_categories.append(categorize_objective(objective))
            else:
                objectives.append("Unknown")
                objective_categories.append("Other")

            if 'rocket' in launch and 'configuration' in launch['rocket']:
                rockets.append(launch['rocket']['configuration'].get('name', 'Unknown Rocket'))
            else:
                rockets.append('Unknown Rocket')

    launch_df = pd.DataFrame({
        "Mission Name": mission_names,
        "Launch Date (UTC)": launch_dates,
        "Launch Site": launch_sites,
        "Objective": objectives,
        "Objective Category": objective_categories,
        "Rocket": rockets
    })

    def convert_timezone(launch_time, target_timezone):
        launch_time = datetime.strptime(launch_time, "%Y-%m-%dT%H:%M:%SZ")
        utc_time = launch_time.replace(tzinfo=pytz.UTC)
        return utc_time.astimezone(pytz.timezone(target_timezone))

    launch_df['Launch Date (Local)'] = [convert_timezone(time, user_timezone) for time in launch_df["Launch Date (UTC)"]]

    st.sidebar.header("Mission Filters")
    category_filter = st.sidebar.multiselect("Select Objective Categories", launch_df['Objective Category'].unique(), default=launch_df['Objective Category'].unique())

    filtered_df = launch_df[
        (launch_df['Objective Category'].isin(category_filter))
    ]

    st.subheader(f"Upcoming Space Missions (in {user_timezone} timezone)")

    if filtered_df.empty:
        st.write("No missions match the selected criteria.")
    else:
        st.dataframe(filtered_df[['Mission Name', 'Launch Date (Local)', 'Objective Category', 'Rocket', 'Launch Site']])

        st.subheader("Mission Objectives Breakdown")
        st.write("A pie chart showing the distribution of mission objectives.")
        
        objective_counts = filtered_df['Objective Category'].value_counts()
        fig_pie = px.pie(names=objective_counts.index, values=objective_counts.values, 
                         title="Mission Objective Distribution",
                         template="plotly_dark")
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie)

else:
    st.write(f"Error fetching data: {status_code}")

with st.container():
    st.subheader("AI Predictions")
    st.write("Future AI-driven features will predict the likelihood of launch delays, mission success rates, and more. Stay tuned for updates!")
    st.info("AI prediction functionality is coming soon!")

count = st_autorefresh(interval=1800000, limit=None, key="fdata")
st.write(f"Auto-refreshing every 30 minutes...")
st.write(f"Refresh Count: {count}")