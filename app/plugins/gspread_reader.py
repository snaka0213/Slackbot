#!/usr/bin/env python3
import gspread
from .gspread_credentials import GSpreadCredentials

class GSpreadReader(object):
    def __init__(self, client: gspread.Client = None):
        self._client = client
        self._sheet = None # gspread.models.Spreadsheet object

    def authorize(self):
        gspread_credentials = GSpreadCredentials()
        credentials = gspread_credentials.get_credentials()
        self._client = gspread.authorize(credentials)

    def login(self):
        self.authorize()
        self._client.login()

    def open(self, sheet_name: str):
        self._sheet = self._client.open(sheet_name)

    def get_worksheet(self, worksheet_name: str) -> gspread.models.Worksheet:
        return self._sheet.worksheet(worksheet_name)
        
    def get_worksheet_title_list(self) -> list:
        return [wks.title for wks in self._sheet.worksheets()]
    

    
            
    
