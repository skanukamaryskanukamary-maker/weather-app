import requests
import streamlit as st

st.title("Weather Information App")

city = st.text_input("Enter a city name")

if st.button("Get Weather"):
    if not city.strip():
        st.warning("Please enter a city name.")
    else:
        try:
            # Find the city's latitude and longitude
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"
            geo_response = requests.get(
                geo_url,
                params={"name": city, "count": 1, "language": "en"},
                timeout=10,
            )
            geo_response.raise_for_status()
            places = geo_response.json().get("results", [])

            if not places:
                st.error("City not found. Check the spelling and try again.")
            else:
                place = places[0]
                latitude = place["latitude"]
                longitude = place["longitude"]

                # Get current weather for those coordinates
                weather_url = "https://api.open-meteo.com/v1/forecast"
                weather_response = requests.get(
                    weather_url,
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
                        "timezone": "auto",
                    },
                    timeout=10,
                )
                weather_response.raise_for_status()
                current = weather_response.json()["current"]

                st.subheader(f"Weather in {place['name']}, {place.get('country', '')}")
                st.metric("Temperature", f"{current['temperature_2m']} °C")
                st.write(f"Humidity: {current['relative_humidity_2m']}%")
                st.write(f"Wind speed: {current['wind_speed_10m']} km/h")

        except requests.RequestException as error:
            st.error(f"Could not get weather data: {error}")
