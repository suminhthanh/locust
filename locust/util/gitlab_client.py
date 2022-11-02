# -*- coding: utf-8 -*-
import os
from logging import getLogger

import requests

logger = getLogger('supabase_client')

GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')
TEST_ID = os.getenv('TEST_ID')


def clean_test_commit():
    try:
        logger.info(f"Starting delete commit {TEST_ID}")
        headers = {
            'PRIVATE-TOKEN': GITLAB_TOKEN,
        }
        json_data = {
            'branch': 'master',
            'author_email': f'bot@gitlab.com',
            'author_name': 'Locust Bot',
            'commit_message': f'Shutdown test {TEST_ID}',
        }
        response = requests.delete(
            f'https://gitlab.com/api/v4/projects/36398524/repository/files/dev%2Fapps%2Ftemplates%2F{TEST_ID}.yaml',
            headers=headers, json=json_data)
        logger.info(f"Deleted commit {TEST_ID}, result: {response}")
    except Exception as e:
        logger.error(f"Failed to delete commit {TEST_ID}, result: {e}")
