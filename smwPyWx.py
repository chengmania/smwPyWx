#!/usr/bin/env python3

# Created by Chengmania on Sunday afternoon on 2024

import sys
import os
import requests
import configparser
import time  # For converting UNIX timestamp
import xml.etree.ElementTree as ET  # For parsing solar weather XML data
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, 
                             QTabWidget, QDialog, QFormLayout, QLineEdit, QComboBox, 
                             QPushButton, QMessageBox, QHBoxLayout)
from PyQt6.QtGui import QPixmap, QAction, QFont
from PyQt6.QtCore import Qt
import pgeocode  # For retrieving state information

# Base API URLs
BASEGEOURL = "http://api.openweathermap.org/geo/1.0/zip?"
BASEOPENWEATHER = "https://api.openweathermap.org/data/3.0/onecall?"
ICON_URL = "http://openweathermap.org/img/wn/"
SOLAR_DATA_URL = "https://www.hamqsl.com/solarxml.php"

# Configuration file path
CONFIG_FILE = 'wxconfig.ini'

# Default Settings
default_zip_code = "10001"
default_units = "metric"  # Default to Celsius ("metric" for Celsius, "imperial" for Fahrenheit)
default_api_key = ''

# Initialize variables to hold settings
zip_code = default_zip_code
units = default_units
API_KEY = default_api_key

# Function to load settings from wxconfig.ini
def load_settings():
    global zip_code, units, API_KEY
    config = configparser.ConfigParser()

    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        if 'Settings' in config:
            zip_code = config['Settings'].get('zip_code', default_zip_code)
            units = config['Settings'].get('units', default_units)
            API_KEY = config['Settings'].get('api_key', default_api_key)
    else:
        prompt_for_initial_settings()

# Function to prompt user for settings if config file doesn't exist
def prompt_for_initial_settings():
    settings_dialog = SettingsDialog()
    if settings_dialog.exec() == QDialog.DialogCode.Accepted:
        save_settings()

# Function to save settings to wxconfig.ini
def save_settings():
    config = configparser.ConfigParser()
    config['Settings'] = {
        'zip_code': zip_code,
        'units': units,
        'api_key': API_KEY
    }

    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

# Function to geocode location using zip code
def geocode_location(zip_code):
    url = f"{BASEGEOURL}zip={zip_code},US&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        QMessageBox.warning(None, "Error", "Failed to get geocode data.")
        return None

# Function to get weather data using OpenWeather API 3.0
def get_weather(lat, lon):
    url = f"{BASEOPENWEATHER}lat={lat}&lon={lon}&units={units}&exclude=minutely,hourly&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        QMessageBox.warning(None, "Error", "Failed to get weather data.")
        return None

# Function to fetch solar weather data
def get_solar_weather():
    response = requests.get(SOLAR_DATA_URL)
    if response.status_code == 200:
        return response.content  # Return XML data
    else:
        QMessageBox.warning(None, "Error", "Failed to get solar weather data.")
        return None

# Function to fetch state from pgeocode library
def get_state_from_zip(zip_code):
    nomi = pgeocode.Nominatim('US')
    location = nomi.query_postal_code(zip_code)
    if location is not None and not location.isnull().all():
        return location.state_code, location.state_name
    return None, None

# Main Window with tabs for current weather and 5-day forecast
class WeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SMW Weather App")
        self.setGeometry(100, 100, 600, 400)

        # Create the main widget and set background color to white
        self.main_widget = QWidget()
        self.main_widget.setStyleSheet("background-color: white;")
        self.setCentralWidget(self.main_widget)
        
        ###### Create the Tabs ########
        # Create layout and add tab widget
        self.layout = QVBoxLayout(self.main_widget)

        # Location label above the tabs
        self.location_label = QLabel("Weather Information for --, --")
        self.layout.addWidget(self.location_label)

        # Create tab widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Add current weather tab
        self.current_weather_tab = QWidget()
        self.current_weather_tab.setStyleSheet("background-color: white;")
        self.tabs.addTab(self.current_weather_tab, "Current Weather")
        self.create_current_weather_tab()

        # Add 5-day forecast tab
        self.forecast_tab = QWidget()
        self.forecast_tab.setStyleSheet("background-color: white;")
        self.tabs.addTab(self.forecast_tab, "5-Day Forecast")
        self.create_forecast_tab()

        # Add weather alerts tab
        self.alerts_tab = QWidget()
        self.alerts_tab.setStyleSheet("background-color: white;")
        self.tabs.addTab(self.alerts_tab, "Weather Alerts")
        self.create_alerts_tab()

        # Add solar weather tab
        self.solar_weather_tab = QWidget()
        self.solar_weather_tab.setStyleSheet("background-color: white;")
        self.tabs.addTab(self.solar_weather_tab, "Solar Weather")
        self.create_solar_weather_tab()

        # Create the menu bar
        self.create_menu_bar()

        # Load initial weather data
        self.load_weather_data()

        #### Done Creating Tabs ####

    def create_menu_bar(self):
        # Create menu bar
        menu_bar = self.menuBar()

        # Create "Settings" menu
        settings_menu = menu_bar.addMenu("Settings")
        settings_action = QAction("Configure", self)
        settings_action.triggered.connect(self.open_settings_dialog)
        settings_menu.addAction(settings_action)

        # Create "About" menu
        about_menu = menu_bar.addMenu("About")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.open_about_dialog)
        about_menu.addAction(about_action)

    #### Layout the Tabs ####
    # Tab for current weather
    def create_current_weather_tab(self):
        main_layout = QVBoxLayout()
        self.weather_icon_label = QLabel()
        main_layout.addWidget(self.weather_icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

        columns_layout = QHBoxLayout()

        # Column 1
        col1_layout = QVBoxLayout()
        self.tempa_label = QLabel("Temperature: --")
        col1_layout.addWidget(self.tempa_label)
        self.feels_like_label = QLabel("Feels Like: --")
        col1_layout.addWidget(self.feels_like_label)
        self.humidity_label = QLabel("Humidity: --")
        col1_layout.addWidget(self.humidity_label)
        self.dew_point_label = QLabel("Dew Point: --")
        col1_layout.addWidget(self.dew_point_label)
        self.pressure_label = QLabel("Pressure: --")
        col1_layout.addWidget(self.pressure_label)
        self.wind_speed_label = QLabel("Wind Speed: --")
        col1_layout.addWidget(self.wind_speed_label)
        self.wind_gust_label = QLabel("Wind Gusts: --")
        col1_layout.addWidget(self.wind_gust_label)
        columns_layout.addLayout(col1_layout)

        # Column 2
        col2_layout = QVBoxLayout()
        self.weather_desc_label = QLabel("Weather: --")
        col2_layout.addWidget(self.weather_desc_label)
        self.clouds_label = QLabel("Cloud Cover: --")
        col2_layout.addWidget(self.clouds_label)
        self.visibility_label = QLabel("Visibility: --")
        col2_layout.addWidget(self.visibility_label)
        self.sunrise_label = QLabel("Sunrise: --")
        col2_layout.addWidget(self.sunrise_label)
        self.sunset_label = QLabel("Sunset: --")
        col2_layout.addWidget(self.sunset_label)
        columns_layout.addLayout(col2_layout)

        main_layout.addLayout(columns_layout)
        self.current_weather_tab.setLayout(main_layout)

    # Tab for 5-day forecast
    def create_forecast_tab(self):
        layout = QHBoxLayout()
        high_temp_font = QFont()
        high_temp_font.setBold(True)
        high_temp_font.setPointSize(10)

        low_temp_font = QFont()
        low_temp_font.setPointSize(10)

        self.forecast_columns = []
        for i in range(5):
            column = QVBoxLayout()
            self.day_label = QLabel("Day --")
            column.addWidget(self.day_label, alignment=Qt.AlignmentFlag.AlignCenter)
            self.day_icon_label = QLabel()
            column.addWidget(self.day_icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
            self.temp_label = QLabel("High / Low")
            self.temp_label.setFont(high_temp_font)
            column.addWidget(self.temp_label, alignment=Qt.AlignmentFlag.AlignCenter)
            self.precip_label = QLabel("Precipitation: --%")
            self.precip_label.setFont(low_temp_font)
            column.addWidget(self.precip_label, alignment=Qt.AlignmentFlag.AlignCenter)
            layout.addLayout(column)
            self.forecast_columns.append((self.day_label, self.day_icon_label, self.temp_label, self.precip_label))

        self.forecast_tab.setLayout(layout)

    # Tab for weather alerts
    def create_alerts_tab(self):
        layout = QVBoxLayout()
        self.alerts_label = QLabel("Weather Alerts will be displayed here.")
        layout.addWidget(self.alerts_label)
        self.alerts_tab.setLayout(layout)

    # Tab for solar weather
    def create_solar_weather_tab(self):
        # Create a main vertical layout for the tab
        layout = QVBoxLayout()

        # Create placeholders for the labels that will be updated later
        self.solar_column1_label = QLabel("Loading Solar Data...")
        self.solar_column2_label = QLabel("Loading Band Conditions...")

        # Add the placeholders to the layout (two columns)
        main_layout = QHBoxLayout()

        # Column 1 (A Index, K Index, Solar Flux, etc.)
        col1_layout = QVBoxLayout()
        col1_layout.addWidget(self.solar_column1_label)
        main_layout.addLayout(col1_layout)

        # Column 2 (Band Conditions Day/Night)
        col2_layout = QVBoxLayout()
        col2_layout.addWidget(self.solar_column2_label)
        main_layout.addLayout(col2_layout)

        # Add the main_layout to the tab
        layout.addLayout(main_layout)

        # Add credit label at the bottom
        credit_label = QLabel('Credit: Paul N0NBH and HamQSL.com for providing the solar weather info')
        credit_label.setStyleSheet("font-size: 10px; color: gray;")
        layout.addWidget(credit_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set the layout for the tab
        self.solar_weather_tab.setLayout(layout)


    def load_weather_data(self):
        geocode_data = geocode_location(zip_code)
        if geocode_data:
            city = geocode_data.get('name')
            lat = geocode_data.get('lat')
            lon = geocode_data.get('lon')
            country = geocode_data.get('country')

            state_code, state_name = "", ""
            if country == "US":
                state_code, state_name = get_state_from_zip(zip_code)

            state_display = f"{state_name} ({state_code})" if state_name else country
            self.location_label.setText(f"Weather Information for {city}, {state_display}")

            weather_data = get_weather(lat, lon)
            if weather_data:
                self.update_current_weather(weather_data['current'])
                self.update_forecast(weather_data['daily'])
                self.update_alerts(weather_data.get('alerts', []))

            solar_data = get_solar_weather()
            if solar_data:
                self.update_solar_weather(solar_data)

    def update_alerts(self, alerts):
        if alerts:
            alert_text = ""
            for alert in alerts:
                event = alert.get('event', 'N/A')
                start = time.strftime('%Y-%m-%d %H:%M', time.localtime(alert.get('start', 0)))
                end = time.strftime('%Y-%m-%d %H:%M', time.localtime(alert.get('end', 0)))
                description = alert.get('description', 'No description')
                alert_text += f"Event: {event}\nStart: {start}\nEnd: {end}\n\n{description}\n\n"
            self.alerts_label.setText(alert_text)
        else:
            self.alerts_label.setText("No weather alerts available.")

    def update_solar_weather(self, solar_data):
        try:
            # Parse the XML data
            root = ET.fromstring(solar_data)
            solar_info = root.find('solardata')

            if solar_info is None:
                print("Error: No 'solardata' element found in the XML")
                QMessageBox.warning(None, "Error", "Failed to parse solar weather data.")
                return

            # Extract main solar data
            solar_flux = solar_info.find('solarflux').text
            sunspots = solar_info.find('sunspots').text
            aindex = solar_info.find('aindex').text
            kindex = solar_info.find('kindex').text
            geomag_field = solar_info.find('geomagfield').text
            signal_to_noise = solar_info.find('signalnoise').text

            # Extract band conditions and apply color coding
            conditions = solar_info.find('calculatedconditions')
            band_conditions_day = "\n".join([f"{band.get('name')}: {self.get_colored_condition(band.text)}" 
                                            for band in conditions.findall("band") if band.get("time") == "day"])
            band_conditions_night = "\n".join([f"{band.get('name')}: {self.get_colored_condition(band.text)}" 
                                            for band in conditions.findall("band") if band.get("time") == "night"])

            # Create the text for column 1 (A Index, K Index, Solar Flux, etc.)
            column1_text = (f"A Index: ............{aindex}\n"
                            f"K Index: ............{kindex}\n"
                            f"Solar Flux: .........{solar_flux}\n"
                            f"Sunspots: ...........{sunspots}\n"
                            f"Signal to Noise: ....{signal_to_noise}\n"
                            f"Geomagnetic Field: ..{geomag_field}")

            # Create the text for column 2 (Band Conditions Day/Night) and add the color-coded conditions
            column2_text = (f"Band Conditions (Day):<br>{band_conditions_day}<br><br>"
                            f"Band Conditions (Night):<br>{band_conditions_night}")

            # Update the labels with new data (using HTML for styling)
            self.solar_column1_label.setText(column1_text)
            self.solar_column2_label.setText(column2_text)

        except ET.ParseError as e:
            print(f"Error parsing solar weather data: {e}")
            QMessageBox.warning(None, "Error", "Failed to parse solar weather data.")

    # Function to return color-coded band conditions
    def get_colored_condition(self, condition):
        if condition == "Excellent":
            return f'<span style="color: blue;">{condition}<br></span>'
        elif condition == "Good":
            return f'<span style="color: green;">{condition}<br></span>'
        elif condition == "Poor":
            return f'<span style="color: red;">{condition}<br></span>'
        else:
            return condition  # Return condition unstyled if not one of the known types




    def update_current_weather(self, current):
        temp = current.get('temp', 0)
        feels_like = current.get('feels_like', 0)
        pressure = current.get('pressure', 0)
        humidity = current.get('humidity', 0)
        dew_point = current.get('dew_point', 0)
        clouds = current.get('clouds', 0)
        visibility = current.get('visibility', 0)
        wind_speed = current.get('wind_speed', 0)
        wind_gust = current.get('wind_gust', 0)
        wind_deg = current.get('wind_deg', 0)
        sunrise_unix = current.get('sunrise', 0)
        sunset_unix = current.get('sunset', 0)
        weather_desc = current['weather'][0]['description']
        weather_icon = current['weather'][0]['icon']

        sunrise = time.strftime('%I:%M %p', time.localtime(sunrise_unix))
        sunset = time.strftime('%I:%M %p', time.localtime(sunset_unix))
        degree_unit = "°C" if units == "metric" else "°F"
        visibility_km = visibility / 1000

        self.tempa_label.setText(f"Temperature: {temp}{degree_unit}")
        self.feels_like_label.setText(f"Feels Like: {feels_like}{degree_unit}")
        self.humidity_label.setText(f"Humidity: {humidity}%")
        self.dew_point_label.setText(f"Dew Point: {dew_point}{degree_unit}")
        self.pressure_label.setText(f"Pressure: {pressure} hPa")
        self.wind_speed_label.setText(f"Wind Speed: {wind_speed} m/s @ {wind_deg}°")
        self.wind_gust_label.setText(f"Wind Gusts: {wind_gust} m/s")
        self.weather_desc_label.setText(f"Weather: {weather_desc}")
        self.clouds_label.setText(f"Cloud Cover: {clouds}%")
        self.visibility_label.setText(f"Visibility: {visibility_km} km")
        self.sunrise_label.setText(f"Sunrise: {sunrise}")
        self.sunset_label.setText(f"Sunset: {sunset}")

        icon_url = f"{ICON_URL}{weather_icon}@2x.png"
        pixmap = QPixmap()
        pixmap.loadFromData(requests.get(icon_url).content)
        self.weather_icon_label.setPixmap(pixmap)

    def update_forecast(self, daily):
        degree_unit = "°C" if units == "metric" else "°F"
        for i in range(5):
            day_data = daily[i]
            dt = time.strftime('%A', time.localtime(day_data['dt']))
            temp_max = day_data['temp']['max']
            temp_min = day_data['temp']['min']
            weather_desc = day_data['weather'][0]['description']
            weather_icon = day_data['weather'][0]['icon']
            pop = int(day_data['pop'] * 100)

            day_label, day_icon_label, temp_label, precip_label = self.forecast_columns[i]
            day_label.setText(dt)
            icon_url = f"{ICON_URL}{weather_icon}@2x.png"
            pixmap = QPixmap()
            pixmap.loadFromData(requests.get(icon_url).content)
            day_icon_label.setPixmap(pixmap)
            #temp_label.setText(f"High: {temp_max}{degree_unit} / Low: {temp_min}{degree_unit}")
            # Update temperature (high/low) with dynamic unit
            temp_label.setText(f'<font color="red">{temp_max}{degree_unit}</font> / <font color="blue">{temp_min}{degree_unit}</font>')
            precip_label.setText(f"{weather_desc.title()} - {pop}%")

    def open_settings_dialog(self):
        settings_dialog = SettingsDialog(self)
        if settings_dialog.exec() == QDialog.DialogCode.Accepted:
            save_settings()
            self.load_weather_data()

    def open_about_dialog(self):
        QMessageBox.information(self, "About", "SMW Weather App\nVersion 1.0\nDeveloped by Chengmania on Sunday afternoon in October of 2024 free for use and modification")

# Settings Dialog
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(400, 200, 300, 200)

        layout = QFormLayout()
        self.zip_input = QLineEdit(zip_code)
        layout.addRow("Zip Code:", self.zip_input)

        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["Celsius", "Fahrenheit"])
        self.unit_combo.setCurrentText("Celsius" if units == "metric" else "Fahrenheit")
        layout.addRow("Units:", self.unit_combo)

        self.api_key_input = QLineEdit(API_KEY)
        layout.addRow("API Key:", self.api_key_input)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_settings(self):
        global zip_code, units, API_KEY
        zip_code = self.zip_input.text()
        units = "metric" if self.unit_combo.currentText() == "Celsius" else "imperial"
        API_KEY = self.api_key_input.text()
        QMessageBox.information(self, "Settings Saved", "Settings have been updated!")
        self.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    load_settings()
    window = WeatherApp()
    window.show()
    sys.exit(app.exec())
