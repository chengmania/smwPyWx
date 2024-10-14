smwPyWx: Weather and Solar Weather App

![image](https://github.com/user-attachments/assets/0927f6f7-4d23-4614-9700-a8a68b1dfe40)
![image](https://github.com/user-attachments/assets/6fb1c0c8-c956-4255-a39e-5913fb8c1a02)
![image](https://github.com/user-attachments/assets/0e619e14-7361-43e3-8b7c-679430ce5755)



This is a Python-based weather application called smwPyWx, which uses the OpenWeather API to provide current weather, a 5-day weather forecast, weather alerts, and solar weather data fetched from HamQSL. The GUI is built using PyQt6, and weather data is displayed in a clean and organized tabbed interface.

Features

Current Weather: Displays temperature, humidity, wind speed, and other details for a specified location.

5-Day Forecast: Shows weather forecast for the next 5 days, including temperature, chance of precipitation, and weather conditions.

Weather Alerts: Displays weather alerts when available.

Solar Weather: Shows solar weather conditions such as solar flux, sunspots, aurora index, and band conditions.

Color-Coded Band Conditions: Band conditions are color-coded: blue for "Excellent", green for "Good", and yellow for "Poor".

Credit: The Solar Weather tab includes a credit to Paul N0NBH and HamQSL.com for the solar weather information.

Prerequisites
Before you begin, make sure you have Python 3.8+ installed on your system.
You will also need an OpenWeather API key. 
To get an openweathe api key go to:  https://home.openweathermap.org/users/sign_in

The base plan is 1000 free calls per day then 15cents per 100 after that.  


Installation
Clone the Repository:

    git clone https://github.com/chengmania/smwPyWx.git
    cd smwPyWx

Install Required Dependencies:

Install the necessary Python packages using pip:

    pip install -r requirements.txt
  
Run the Application:

Run the app using:

    python smwPyWx.py
    
On first start of the program, the app will search for a wxconfig.ini file.  If the file does not exist the program will load you into a settings menu and prompt you for the information, zip code, units, and api key.

Required Packages
PyQt6: For building the graphical user interface (GUI).
Requests: For making HTTP requests to the OpenWeather and HamQSL APIs.
pgeocode: For retrieving the state information from zip codes.
ConfigParser: For managing app settings through an .ini file.
XML ElementTree: For parsing XML data from the solar weather API.


Usage
Current Weather Tab: Displays the current weather for a specified zip code.
5-Day Forecast Tab: Provides the weather forecast for the next 5 days.
Weather Alerts Tab: Shows any active weather alerts.
Solar Weather Tab: Displays solar weather information, including solar flux, sunspots, and band conditions.

Solar Weather Source
Credit for the solar weather data goes to Paul N0NBH and HamQSL.com.


License
This project is licensed under the MIT License.

