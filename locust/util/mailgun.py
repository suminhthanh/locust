# -*- coding: utf-8 -*-
import os
from datetime import datetime
from logging import getLogger

import pytz
import requests

logger = getLogger('S3')

# Send email
MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')
MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_STATS_BUCKET = "stats"

REPORT_TO_EMAIL = os.getenv('REPORT_TO_EMAIL')
LOCUST_HOST = os.getenv('LOCUST_HOST')
LOCUST_USERS = os.getenv('LOCUST_USERS')
LOCUST_SPAWN_RATE = os.getenv('LOCUST_SPAWN_RATE')
LOCUST_RUN_TIME = os.getenv('LOCUST_RUN_TIME')


def send_simple_message(to, subject, content):
    return requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={"from": f"Report <no-reply@{MAILGUN_DOMAIN}>",
              "to": [to],
              "subject": subject,
              "text": content})


def send_test_report(report_file_name):
    try:
        logger.info(f"Sending email to {REPORT_TO_EMAIL}")
        mailgun_response = send_simple_message(
            REPORT_TO_EMAIL,
            f"Test Report {timestring()} - {LOCUST_HOST} ",
            f"Number of users: {LOCUST_USERS}\n"
            f"Spawn rate (users started/second): {LOCUST_SPAWN_RATE}\n"
            f"Run time: {LOCUST_RUN_TIME}\n"
            f"More detail: https://html-render.deno.dev/?url={SUPABASE_URL}/storage/v1/object/public/{SUPABASE_STATS_BUCKET}/{report_file_name}")
        logger.info(f"Sent email to {REPORT_TO_EMAIL}, {mailgun_response.text}")
    except Exception as e:
        logger.error(f"Failed to sent test report {e}")


def timestring():
    return datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%H:%M:%S")
