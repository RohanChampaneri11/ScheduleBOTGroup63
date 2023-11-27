import requests
import datetime

BASE_URL = "https://api.openweathermap.org/data/2.5/forecast?"

# f = open("src/apifile.txt", "r")
import os
file_path = os.path.join(os.path.dirname(__file__), 'apifile.txt')
f = open(file_path, "r")

API_KEY = f.read() 

def getWeatherData(latlng, date):
    # Convert date to datetime object for comparison
    target_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

    url = f'{BASE_URL}lat={latlng[0]}&lon={latlng[1]}&appid={API_KEY}'

    response = requests.get(url).json()

    # Loop through the list of forecasts
    for item in response['list']:
        # Convert the forecast time to a date object
        forecast_date = datetime.datetime.fromtimestamp(item['dt']).date()

        # Check if the forecast date matches the target date
        if forecast_date == target_date:
            temp_kelvin = item['main']['temp']
            temp_celsius = temp_kelvin - 273.15
            temp_fahrenheit = temp_celsius * (9/5) + 32
            feels_like = (item['main']['feels_like'] - 273.15) * (9/5) + 32
            desc = item['weather'][0]['description']
            humidity = item['main']['humidity']

            return humidity, temp_celsius, temp_fahrenheit, feels_like, desc

    # Return None if no forecast is found for the target date
    return None, None, None, None, None
