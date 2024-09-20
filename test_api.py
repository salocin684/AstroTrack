import requests
from datetime import datetime, timezone

url = "https://ll.thespacedevs.com/2.2.0/launch/upcoming/"
response = requests.get(url)

if response.status_code == 200:
    launches = response.json()

    current_date = datetime.now(timezone.utc)

    print("Upcoming Launches:")
    for launch in launches['results']:
        launch_date = datetime.strptime(launch['net'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

        if launch_date > current_date:
            print(f"Mission: {launch['name']}, Launch Date: {launch['net']}")
else:
    print(f"Error: {response.status_code}")
