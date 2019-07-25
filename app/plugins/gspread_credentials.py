#!/usr/bin/env python3
import json
import settings
from oauth2client.service_account import ServiceAccountCredentials

class GSpreadCredentials(object):
    def __init__(self):
        credentials_json = {
            "type": "service_account",
            "project_id": settings.PROJECT_ID,
            "private_key_id": settings.PRIVATE_KEY_ID,
            "private_key": settings.PRIVATE_KEY,
            "client_email": settings.CLIENT_EMAIL,
            "client_id": settings.CLIENT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": settings.CLIENT_X509_CERT_URL
        }
        
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        self._credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_json, scope)

    def get_credentials(self):
        return self._credentials
        
