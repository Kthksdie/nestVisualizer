import requests
import json
import time
import os

from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# ==============================================================================
# CONFIGURATION
# You must obtain these from the Google Device Access Console and Google Cloud.
# Guide: https://developers.google.com/nest/device-access/get-started
# ==============================================================================

# Your Device Access Project ID (UUID format)
PROJECT_ID = os.getenv("PROJECT_ID")

# Your Google Cloud OAuth 2.0 Client ID and Secret
CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")

# The long-lived token obtained during the initial OAuth setup
REFRESH_TOKEN = os.getenv("OAUTH_REFRESH_TOKEN")

# ==============================================================================

def get_access_token():
    """
    Exchanges the refresh token for a short-lived access token.
    """
    url = "https://www.googleapis.com/oauth2/v4/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token",
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        print(f"Error getting access token: {e}")
        return None

def get_devices(access_token):
    """
    Queries the SDM API for all devices in the project.
    """
    url = f"https://smartdevicemanagement.googleapis.com/v1/enterprises/{PROJECT_ID}/devices"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # print(f"Response: {response.json()}")
        return response.json().get("devices", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching devices: {e}")
        return []

def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def parse_thermostat_data(device):
    """
    Extracts relevant traits from the device JSON.
    """
    traits = device.get("traits", {})
    name = device.get("parentRelations", [{}])[0].get("displayName", "Unknown Room")
    
    info = {
        "name": name,
        "type": device.get("type"),
        "temperature_c": None,
        "temperature_f": None,
        "humidity": None,
        "mode": None,
        "hvac_status": None,
        "connectivity": None,
        "fan_timer_mode": None,
        "eco_mode": None
    }

    # Temperature (Ambient)
    if "sdm.devices.traits.Temperature" in traits:
        temp_c = traits["sdm.devices.traits.Temperature"].get("ambientTemperatureCelsius")
        info["temperature_c"] = round(temp_c, 1)
        info["temperature_f"] = round(celsius_to_fahrenheit(temp_c), 1)

    # Humidity
    if "sdm.devices.traits.Humidity" in traits:
        info["humidity"] = traits["sdm.devices.traits.Humidity"].get("ambientHumidityPercent")

    # Thermostat Mode (Heat, Cool, HeatCool, Off)
    if "sdm.devices.traits.ThermostatMode" in traits:
        info["mode"] = traits["sdm.devices.traits.ThermostatMode"].get("mode")

    # HVAC Status (Heating, Cooling, Off)
    if "sdm.devices.traits.ThermostatHvac" in traits:
        info["hvac_status"] = traits["sdm.devices.traits.ThermostatHvac"].get("status")

    # Connectivity
    if "sdm.devices.traits.Connectivity" in traits:
        info["connectivity"] = traits["sdm.devices.traits.Connectivity"].get("status")

    # Fan
    if "sdm.devices.traits.Fan" in traits:
        info["fan_timer_mode"] = traits["sdm.devices.traits.Fan"].get("timerMode")

    # Eco Mode
    if "sdm.devices.traits.ThermostatEco" in traits:
        info["eco_mode"] = traits["sdm.devices.traits.ThermostatEco"].get("mode")

    return info

def main():
    print("\033[H\033[J", end="")
    print("--- Nest Thermostat Query (SDM API) ---")
    
    # 1. Authenticate
    print("Refreshing access token...")
    token = get_access_token()
    if not token:
        return

    # 2. Get Data
    print("Querying devices...")
    devices = get_devices(token)
    
    if not devices:
        print("No devices found. Check your permissions or Project ID.")
        return

    # 3. Parse and Display
    found_thermostat = False
    for device in devices:
        if "sdm.devices.types.THERMOSTAT" in device.get("type", ""):
            found_thermostat = True
            data = parse_thermostat_data(device)
            
            print(f"\nDevice: {data['name']}")
            print(f"--------------------------------")
            print(f"Temperature: {data['temperature_f']}°F ({data['temperature_c']}°C)")
            print(f"Humidity:    {data['humidity']}%")
            print(f"System Mode: {data['mode']}")
            print(f"HVAC Status: {data['hvac_status']}")
            print(f"Connectivity:{data['connectivity']}")
            print(f"Fan Mode:    {data['fan_timer_mode']}")
            print(f"Eco Mode:    {data['eco_mode']}")
            print(f"--------------------------------")

    if not found_thermostat:
        print("\nNo thermostats found in your account.")

if __name__ == "__main__":
    main()