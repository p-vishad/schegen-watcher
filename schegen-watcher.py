import requests
from bs4 import BeautifulSoup
import os
import time

# === CONFIG ===
NETHERLANDS_URL = os.environ.get("WATCH_URL", "https://schengenappointments.com/in/london/netherlands/tourism")
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", "50")) # seconds
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
# ===============

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("Missing environment variables! Can't push notifications to phone")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def send_push_to_phone(message):
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(url, payload)

    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print("Failed to send message:", response.text)


def check_netherlands_status():
    try:
        response = requests.get(NETHERLANDS_URL, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching page: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    h5 = soup.find("h5", class_="mb-1 font-medium leading-none tracking-tight")

    if h5:
        text = h5.get_text(strip=True)
        if "No appointments available" in text:
            print("Netherlands has no availability.")
        else:
            print("Netherlands might be open")
            print("Pushing notification to phone...")
            send_push_to_phone(message="Neatherland visa application is open")
    else:
        # If <h5> not found, assume page layout changed
        print("Could not find the appointment status element")


if __name__ == "__main__":
    print(f"Monitoring {NETHERLANDS_URL} every {CHECK_INTERVAL} seconds...")
    print("Pushing test message...")
    send_push_to_phone("Script up and running...")
    while True:
        check_netherlands_status()
        time.sleep(CHECK_INTERVAL)
    