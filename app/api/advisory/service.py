import os
import requests
from twilio.rest import Client
from sqlalchemy.orm import Session
from app import models
from dotenv import load_dotenv

load_dotenv()

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Weather Configuration
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

def get_weather(city: str):
    """Fetch current weather for a city"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url).json()

        if "main" not in response:
            return None, None

        temp = response["main"]["temp"]
        condition = response["weather"][0]["description"]
        return temp, condition
    except Exception as e:
        print(f"Weather lookup error: {e}")
        return None, None

def send_alert_sms(phone: str, msg: str):
    """Send a single SMS alert via Twilio"""
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        print("Twilio credentials not configured")
        return False
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(body=msg, from_=TWILIO_PHONE_NUMBER, to=phone)
        return True
    except Exception as e:
        print(f"SMS sending error: {e}")
        return False

def send_bulk_alerts(db: Session):
    """Send daily alerts to all registered farmers"""
    farmers = db.query(models.AdvisoryFarmer).all()
    count = 0
    
    for farmer in farmers:
        temp, condition = get_weather(farmer.city)
        
        if temp is None:
            continue
            
        msg = f"""
🌾 Daily Agri Shield Alert

Farmer: {farmer.name}
Crop: {farmer.crop}
City: {farmer.city}

Temp: {temp}°C
Condition: {condition}

Take precautions for your {farmer.crop} today.
"""
        if send_alert_sms(farmer.phone, msg):
            count += 1
            
    return count
