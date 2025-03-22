In run3.bat file, change the working directory to your own and change location to your own conda environment or wherever you have Python.exe

Crete a .env file with these specifications, you can get the username and password from the FREE twilio sendgrid api. That is what I used. Here is the link: https://sendgrid.com/en-us/pricing
Make sure there are no extra spaces in the .env file or it will not work.
username=apikey
password=SG.yourpassword
sender_email=youremail@whateveremail.com
receiver_email=recieveremail@whateveremail.com

You can also change the target date in test.py so that it only gives you appointments on or before that target date.

From here you are all set and you can use Windows task scheduler to schedule a task to run the run3.bat file whenever you want, or cron on Mac :). Happy Hunting.