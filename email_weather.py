import logging
import os
import smtplib
from email.mime.text import MIMEText

import requests
from dotenv import load_dotenv

# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

CITIES = os.getenv("CITIES", "Hyderabad").split(",")
RECIPIENTS = [email.strip() for email in os.getenv("RECIPIENTS", "").split(",") if email.strip()]

# --------------------------------------------------
# Logging
# --------------------------------------------------

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/weather.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

# --------------------------------------------------
# Weather Function
# --------------------------------------------------


def get_weather(city):
    """Fetch weather for a single city."""

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric"
    )

    response = requests.get(url, timeout=10)
    data = response.json()

    if response.status_code != 200:
        return (
            f"📍 {city}\n"
            f"Weather unavailable.\n"
            f"Reason: {data.get('message','Unknown Error')}\n"
        )

    main = data["main"]
    weather = data["weather"][0]
    wind = data["wind"]

    return f"""
========================================
📍 {city.title()}
========================================
🌡 Temperature : {main['temp']}°C
🤗 Feels Like : {main['feels_like']}°C
⬇ Min Temp    : {main['temp_min']}°C
⬆ Max Temp    : {main['temp_max']}°C

💧 Humidity   : {main['humidity']}%
🧭 Pressure   : {main['pressure']} hPa
💨 Wind Speed : {wind['speed']} m/s

🌥 Condition  : {weather['description'].title()}

"""


# --------------------------------------------------
# Generate Complete Report
# --------------------------------------------------


def generate_report():

    report = "\n******** DAILY WEATHER REPORT ********\n\n"

    for city in CITIES:

        city = city.strip()

        logging.info(f"Fetching weather for {city}")

        report += get_weather(city)
        report += "\n"

    return report


# --------------------------------------------------
# Send Email
# --------------------------------------------------


def send_email(subject, body):

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = ", ".join(RECIPIENTS)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:

        smtp.login(EMAIL, EMAIL_PASSWORD)

        smtp.sendmail(
            EMAIL,
            RECIPIENTS,
            msg.as_string(),
        )


# --------------------------------------------------
# Main
# --------------------------------------------------


def main():

    if not API_KEY:
        raise ValueError("Missing OPENWEATHER_API_KEY")

    if not EMAIL:
        raise ValueError("Missing EMAIL")

    if not EMAIL_PASSWORD:
        raise ValueError("Missing EMAIL_PASSWORD")

    if not RECIPIENTS:
        raise ValueError("No RECIPIENTS specified")

    report = generate_report()

    send_email(
        "Daily Weather Report",
        report,
    )

    logging.info("Email sent successfully.")

    print("✅ Weather report emailed successfully!")


if __name__ == "__main__":

    try:

        main()

    except requests.exceptions.Timeout:

        logging.error("Weather API timeout.")

        print("❌ Request timed out.")

    except requests.exceptions.ConnectionError:

        logging.error("Internet connection failed.")

        print("❌ Internet connection failed.")

    except smtplib.SMTPAuthenticationError:

        logging.error("Invalid Gmail App Password.")

        print("❌ Gmail authentication failed.")

    except Exception as e:

        logging.error(str(e))

        print(f"❌ {e}")