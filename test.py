from datetime import datetime, date
from bs4 import BeautifulSoup
from time import sleep
import urllib.request
import argparse
import pandas as pd
import sys

import crawler as config
from h import send_email

# Define target date
TARGET_DATE = date(2025, 5, 28)

PARSER = argparse.ArgumentParser()
PARSER.add_argument("--slack", help="print the availble slots information to the configured slack channel", default=True, action="store_true")
ARGS = PARSER.parse_args()

APPOINTMNET_URL_PREFIX = "https://telegov.njportal.com"

TYPE_CODES = {
  "INITIAL PERMIT (NOT FOR KNOWLEDGE TEST)": 15,
  "CDL PERMIT OR ENDORSEMENT - (NOT FOR KNOWLEDGE TEST)": 14,
  "REAL ID": 12,
  "NON-DRIVER ID": 16,
  "KNOWLEDGE TESTING (NOT CDL)": 19,
  "RENEWAL: LICENSE OR NON-DRIVER ID": 11,
  "RENEWAL: CDL": 6,
  "TRANSFER FROM OUT OF STATE": 7,
  "NEW TITLE OR REGISTRATION": 8,
  "SENIOR NEW TITLE OR REGISTRATION (65+)": 9,
  "REGISTRATION RENEWAL": 10,
  "TITLE DUPLICATE/REPLACEMENT": 13,
}

MVC_LOCATION_CODES = {
  "KNOWLEDGE TESTING (NOT CDL)": {
    "BAYONNE": 268,
    "NEWARK": 281,
    "NORTH BERGEN": 282,
    "ELIZABETH": 290,
    "EDISON": 275,
    "WAYNE": 283,
    "PATERSON": 285,
    "LODI": 279,
  },
  "TRANSFER FROM OUT OF STATE": {
    "ELIZABETH": 263,
    "ELIZABETH": 263,
    "OAKLAND": 58,
    "PATERSON": 59,
    "LODI": 55,
    "WAYNE": 67,
    "RANDOLPH": 61,
    "NORTH BERGEN": 57,
    "NEWARK": 56,
    "BAYONNE": 47,
    "RAHWAY": 60,
    "SOUTH PLAINFIELD": 63,
    "EDISON": 52,
    "FLEMINGTON": 53,
    "BAKERS BASIN": 46,
    "FREEHOLD": 54,
    "EATONTOWN": 51,
    "TOMS RIVER": 65,
    "DELANCO": 50,
    "CAMDEN": 49,
    "WEST DEPTFORD": 68,
    "SALEM": 64,
    "VINELAND": 66,
    "CARDIFF": 48,
    "RIO GRANDE": 62
  },
  "RENEWAL: LICENSE OR NON-DRIVER ID": {
    "BAYONNE": 102,
    "ELIZABETH": 261,
    "NEWARK": 116,
    "NORTH BERGEN": 117,
    "PATERSON": 120,
    "WAYNE": 118,
    "SOUTH PLAINFIELD": 109
  },
  "REAL ID": {
    "OAKLAND": 141,
    "PATERSON": 142,
    "LODI": 136,
    "WAYNE": 140,
    "RANDOLPH": 145,
    "NORTH BERGEN": 139,
    "NEWARK": 138,
    "BAYONNE": 125,
    "RAHWAY": 144,
    "SOUTH PLAINFIELD": 131,
    "EDISON": 132,
    "FLEMINGTON": 133,
    "BAKERS BASIN": 124,
    "FREEHOLD": 135,
    "EATONTOWN": 130,
    "TOMS RIVER": 134,
    "DELANCO": 129,
    "CAMDEN": 127,
    "WEST DEPTFORD": 143,
    "SALEM": 128,
    "VINELAND": 137,
    "CARDIFF": 146,
    "RIO GRANDE": 126
  },
  "INITIAL PERMIT (NOT FOR KNOWLEDGE TEST)": {
    "OAKLAND": 203,
    "PATERSON": 204,
    "LODI": 198,
    "WAYNE": 202,
    "RANDOLPH": 207,
    "NORTH BERGEN": 201,
    "NEWARK": 200,
    "BAYONNE": 187,
    "RAHWAY": 206,
    "SOUTH PLAINFIELD": 193,
    "EDISON": 194,
    "FLEMINGTON": 195,
    "BAKERS BASIN": 186,
    "FREEHOLD": 197,
    "EATONTOWN": 192,
    "TOMS RIVER": 196,
    "DELANCO": 191,
    "CAMDEN": 189,
    "WEST DEPTFORD": 205,
    "SALEM": 190,
    "VINELAND": 199,
    "CARDIFF": 208,
    "RIO GRANDE": 188
  }
}

APPOINTMENT_TEMPLATE_URL = "https://telegov.njportal.com/njmvc/AppointmentWizard/{type_code}/{location_code}"

def _check_config():
  supported_types = set(MVC_LOCATION_CODES.keys()).intersection(set(TYPE_CODES.keys()))
  if hasattr(config, "APPOINTMENT_TYPES") and config.APPOINTMENT_TYPES.difference(supported_types):
    print("Appointment types {} are not corrected. Please choose one from the following types: {}".format(
      config.APPOINTMENT_TYPES, supported_types))
    exit(1)

  if hasattr(config, "APPOINTMENT_TYPES") and config.APPOINTMENT_TYPES and hasattr(config, "LOCATION"):
    supported_locations = set()
    for type in config.APPOINTMENT_TYPES:
      if not supported_locations:
        supported_locations = set(MVC_LOCATION_CODES[type])
        continue
      supported_locations = supported_locations.intersection(set(MVC_LOCATION_CODES[type]))
    for location in config.LOCATION:
      if location not in supported_locations:
        print("Appointment location {} is not corrected. Please choose one from the following locations: {}".format(
            location, supported_locations))
        exit(1)


def _get_config_info():
  _check_config()
  info = {}
  type_candidates = [(type, TYPE_CODES[type])
                     for type in config.APPOINTMENT_TYPES] if hasattr(config, "APPOINTMENT_TYPES") and config.APPOINTMENT_TYPES else list(TYPE_CODES.items())
  for type, type_code in type_candidates:
    if type not in MVC_LOCATION_CODES:
      continue
    type_location_candidates = [(location, MVC_LOCATION_CODES[type][location]) for location in config.LOCATION] if hasattr(config,
                                                                                                  "LOCATION") and config.LOCATION else list(
    MVC_LOCATION_CODES[type].items())
    info[(type, type_code)] = type_location_candidates
  return info

def _monitor_appointments(user_config_info):
    available_slots = {}
    for (type, type_code), location_candidates in user_config_info.items():
        for location_name, location_code in location_candidates:
            timeslot_url = APPOINTMENT_TEMPLATE_URL.format(
                type_code=type_code, location_code=location_code)

            request = urllib.request.Request(timeslot_url)
            try:
                response = urllib.request.urlopen(request)
            except:
                print("Failed to request {}, skipping".format(timeslot_url))
                continue

            result_html = response.read().decode("utf8")
            soup = BeautifulSoup(result_html, "html.parser")
            timeslots_container = soup.find(id="timeslots")
            if not timeslots_container:
                message = "Failed to find timeslots container while requesting {}, probably the MVC appointment system is down, waiting for 30 minutes to continue trying".format(timeslot_url)
                print(message)
                # _send_slack_message(message)
                sleep(1800)
                continue
            # Change recursive=False to recursive=True to find nested <a> tags
            available_timeslots = timeslots_container.findChildren("a", recursive=True, href=True)
            if available_timeslots:
                for timeslot in available_timeslots:
                    url = APPOINTMNET_URL_PREFIX + timeslot["href"]
                    # Extract date from URL and check against target
                    parts = url.split('/')
                    date_str = parts[-2]
                    try:
                        appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    except ValueError:
                        continue  # Skip invalid dates
                    if appointment_date > TARGET_DATE:
                        continue  # Skip dates after target
                    time = parts[-1]
                    time_string = "0" + time[0] + ":" + time[1:] + "AM" if len(time) == 3 else time[0:2] + ":" + time[2:] + ("PM" if int(time[0:2]) >= 12 else "AM")
                    available_slots[url] = {"type": type, "location": location_name, "url": url, "date": date_str, "time": time_string}
    return available_slots


# Modify the main section
if __name__ == "__main__":
    config_info = _get_config_info()
    former_date = datetime.today().strftime("%Y-%m-%d")
    daily_found_urls = set()
    slot_count = {}
    
    while True:
        available_slots = _monitor_appointments(config_info)
        urls = set(available_slots.keys())
        new_urls = urls.difference(daily_found_urls)
        daily_found_urls = daily_found_urls.union(urls)
        
        # if len(new_urls) > 0:
        new_slots = {url: available_slots[url] for url in new_urls}
        # Create DataFrame
        df_data = [{
            'Location': slot['location'],
            'Date': slot['date'],
            'Time': slot['time'],
            'Type': slot['type'],
            'URL': url
        } for url, slot in new_slots.items()]
        
        df = pd.DataFrame(df_data)
        if not df.empty:
        # Sort and format for better display
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values(['Date', 'Time', 'Location'])
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
            
            email_subject = ("New Appointments Found:")
            email_body = "\nNew Appointments Found: \n\n" + (df[['Location', 'Date', 'Time']].to_string(index=False))
           
           #Send email
            send_email(email_subject, email_body)
            print("Email Sent!")
        else:
           print ("No new appointments found.")
           sys.exit(1)
            
            # if ARGS.slack:
                # _send_slack_message(f"New appointments found:\n{df[['Location', 'Date', 'Time']].to_markdown(index=False)}")
        
        # sleep(10)
        # current_date = datetime.today().strftime("%Y-%m-%d")
        # if current_date != former_date:
        #     print("Passing one day, resetting the daily found urls and slot count...")
        #     former_date = current_date
        #     daily_found_urls.clear()
        #     slot_count.clear()