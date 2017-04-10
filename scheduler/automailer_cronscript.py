#!/usr/bin/python

import os, sqlite3
from datetime import date
from django.conf import settings
if not settings.configured:
    settings.configure()

from scheduler import views


def my_scheduled_email_sender():
    # Open the logger file, enter first log entry
    script_logger = open('automailer_cronscript_logfile', 'a')
    script_logger.write(date.today().strftime('%Y-%m-%d') + "			Script was called \n")

    # Get the date when the next meeting is planned from the DB
    con = sqlite3.connect('/var/www/wai.few.vu.nl/waibase.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cur = con.cursor()
    nextDate = cur.execute('SELECT date FROM scheduler_meeting WHERE date >= DATE("now") LIMIT 2;')
    next = nextDate.fetchall()

    # Calculate the timediff and send email if it is the right day
    timediff_nextweek = next[0][0] - date.today()
    timediff_weekafter = next[1][0] - date.today()


    # Send the announcement on the monday
    if timediff_nextweek.days == 0:
        views.send_announce(next[0][0].strftime('%Y-%m-%d'))
        script_logger.write(date.today().strftime('%Y-%m-%d') + "                       Announcement was sent \n")

    # Send the announcement on the friday
    if timediff_nextweek.days == 3:
        views.send_announce(next[0][0].strftime('%Y-%m-%d'))
        script_logger.write(date.today().strftime('%Y-%m-%d') + "			Announcement was sent \n")

    # Send a request for abstracts to the presenters in two weeks time
    if timediff_weekafter.days == 12:
        views.send_request(next[1][0].strftime('%Y-%m-%d'))
        script_logger.write(
            date.today().strftime('%Y-%m-%d') + "			Request for abstract for week after next was sent \n")

    # Resend the request to both. The function checks and stops the script if both abstracts have already been received
    if timediff_nextweek.days == 5:
        script_logger.write("Wednesday -> only the function is not working\n")
	views.send_request(next[0][0].strftime('%Y-%m-%d'))
        script_logger.write(
            date.today().strftime('%Y-%m-%d') + "			Request for abstract next week was sent \n")

    # This function only gets called for the first meeting in a period (e.g. after holidays). Otherwise the request for abstract wouldn't be sent until a week beforehand
    if timediff_nextweek.days == 12:
        views.send_request(next[0][0].strftime('%Y-%m-%d'))
        script_logger.write(
            date.today().strftime('%Y-%m-%d') + "			Request for abstract for week after next was sent \n")

    # Close the database connection
    con.close()

    # Close the logfile
    script_logger.close()
