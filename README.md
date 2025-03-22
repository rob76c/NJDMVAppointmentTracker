# NJDMVAppointmentTracker

Tracks appointments for NJ DMVs specifically for the RealID.

## Overview

This project leverages Python and the free Twilio SendGrid API to manage appointment notifications. It includes a batch script to launch the process, a Python script for appointment handling, and an environment file for secure configuration.

## Prerequisites

- **Python Environment:** Ensure you have Python installed. It is recommended to use your preferred conda environment or any other virtual environment.
- **Twilio SendGrid Account:** Sign up for a free SendGrid account to obtain your API credentials. More details can be found on the [SendGrid Pricing Page](https://sendgrid.com/en-us/pricing).
- **Operating System:** This project includes a Windows batch file (`run3.bat`). If you are using a Unix-based system, you can adapt the instructions for a cron job.

## Setup Instructions

### 1. Modify the Batch File

- Open the `run3.bat` file.
- **Change the working directory:** Update the path to reflect your own project directory.
- **Update Python path:** Modify the file to point to your own conda environment or wherever your `Python.exe` is located.

### 2. Configure the Environment File

Create a file named `.env` in the root directory of your project with the following contents:

```ini
username=apikey
password=SG.yourpassword
sender_email=youremail@whateveremail.com
receiver_email=recieveremail@whateveremail.com
```
### 3. Important
Ensure there are no extra spaces in the `.env` file, as they can prevent it from working correctly.
Replace `SG.yourpassword`, `youremail@whateveremail.com`, and `recieveremail@whateveremail.com` with your actual SendGrid API key and email addresses.

### 4. Update the Target Date if needed in the Python Script
Open the `test.py` file.
Locate the section where the target date is set.
Modify the target date so that the script filters appointments on or before that date.

### 5. Configuration
You can configure the appointment types and locations like this in the crawler.py:

```python
# Appointment requirement
APPOINTMENT_TYPES = {"TRANSFER FROM OUT OF STATE", "REAL ID"} # Can be not set and all supported types will be checked
LOCATION = "NEWARK" # Can be empty and all locations will be checked
```

### 6. Scheduling the task
On Windows: Use the Windows Task Scheduler to schedule the run3.bat file to run at your desired intervals.
On Mac/Linux: You can set up a cron job to run the equivalent script as needed.

### 6. LETS GOOOOOOOOO
From here you are all set and you can use Windows task scheduler or cron on Mac :). Happy Hunting.