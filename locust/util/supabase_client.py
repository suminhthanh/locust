# -*- coding: utf-8 -*-
import os
import tempfile
import time
from logging import getLogger

from supabase import create_client, Client

logger = getLogger('supabase_client')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_LOCUSTFILE_PATH = os.getenv('SUPABASE_LOCUSTFILE_PATH')

SUPABASE_STATS_BUCKET = "stats"
SUPABASE_LOCUSTFILE_BUCKET = "locustfiles"

RUN_ID = os.getenv("RUN_ID")
APP_SERVER_URL = os.getenv("APP_SERVER_URL")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_to_bucket(path, file, bucket_name, file_options):
    try:
        supabase.storage().from_(bucket_name).upload(
            path=path,
            file=file,
            file_options=file_options
        )
    except Exception as e:
        logger.error(f"Failed to upload file to Supabase {e}")


def upload_html_report(html_content):
    report_file_name = f"report_{time.time()}.html"

    try:
        logger.info(f"Uploading {report_file_name} to {SUPABASE_STATS_BUCKET}")
        temp_file, filename = tempfile.mkstemp()
        os.write(temp_file, html_content)
        os.close(temp_file)
        upload_to_bucket(report_file_name, filename, SUPABASE_STATS_BUCKET,
                         file_options={
                             "CacheControl": "max-age=0,no-cache,no-store,must-revalidate",
                             "ContentType": "text/html"
                         })
        logger.info(f"Uploaded {report_file_name} to Supabase")
        update_html_url(report_file_name)
    except Exception as e:
        logger.error(f"Failed to upload html report {e}")

    return report_file_name


def get_file_from_bucket(path, bucket_name="locustfiles"):
    try:
        return supabase.storage().from_(bucket_name).download(
            path=path
        )
    except Exception as e:
        logger.error(f"Failed to get file from Supabase {e}")


def get_main_file():
    try:
        logger.info("Downloading main.py from Supabase")
        file = get_file_from_bucket(SUPABASE_LOCUSTFILE_PATH, SUPABASE_LOCUSTFILE_BUCKET)
        f = open("/home/locust/main.py", "w")
        f.write(file.decode("utf-8"))
        f.close()
        logger.info("Downloaded main.py from Supabase")
    except Exception as e:
        logger.error(f"Failed to download main.py from Supabase {e}")


def update_run_status(status):
    try:
        logger.info(f"Updating run status: {status}")
        supabase.table("results").update({
            "run_status": status,
        }).eq("run_id", RUN_ID).execute()
        logger.info(f"Updated run status: {status}")
    except Exception as e:
        logger.error(f"Failed to update run status {e}")


def update_html_url(report_file_name):
    try:
        logger.info(f"Updating html_url: {report_file_name}")
        supabase.table("results").update({
            "html_url": f"{APP_SERVER_URL}?url={SUPABASE_URL}/storage/v1/object/public/{SUPABASE_STATS_BUCKET}/{report_file_name} "
        }).eq("run_id", RUN_ID).execute()
        logger.info(f"Updated html_url: {report_file_name}")
    except Exception as e:
        logger.error(f"Failed to update html_url {e}")
