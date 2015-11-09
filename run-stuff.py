#!/usr/bin/env python3

import schedule
import time
import datetime
import subprocess

def send_mail():
	if datetime.date.today().weekday() < 5:
		print(datetime.datetime.now(), 'Sending mail.')
		subprocess.check_call(["/home/kantinen/venv/bin/python3", "smtp-submit.py"])

schedule.every().day.at('07:59').do(send_mail)

while True:
	schedule.run_pending()
	time.sleep(10)
