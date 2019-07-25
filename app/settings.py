#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from os.path import join, dirname

# for make path to .env file
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

### Basic Information on SlackBot ###
# port
PORT = int(os.environ.get("PORT", 5000))

# bot account's TOKEN
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')

# client secret, app credentials
VERIFICATION_TOKEN = os.environ.get('VERIFICATION_TOKEN')

# signing secret
SIGINING_SECRET = os.environ.get('SIGINING_SECRET')

# default reply when there is no matching pattern
DEFAULT_REPLY = "何言ってんだこいつ"

# list of the name of subdirectory consists of plugins
PLUGINS = ['plugins']

### Google Sheets ###
# sheet file name
SCHEDULE_SHEET_FILE_NAME = os.environ.get('SCHEDULE_SHEET_FILE_NAME')
SUBJECT_SHEET_FILE_NAME = os.environ.get('SUBJECT_SHEET_FILE_NAME')

# credentials
PROJECT_ID = os.environ.get('PROJECT_ID')
PRIVATE_KEY_ID = os.environ.get('PRIVATE_KEY_ID')
PRIVATE_KEY = os.environ.get('PRIVATE_KEY')
CLIENT_EMAIL = os.environ.get('CLIENT_EMAIL')
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_X509_CERT_URL = os.environ.get('CLIENT_X509_CERT_URL')
