#!/usr/bin/env python3
import gspread
from .gspread_credentials import GSpreadCredentials

class GSpreadWriter(object):
    def __init__(self):
        self._client = None # gspread.Client object
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

    def write(self, submission: dict, type: str):
        if type == "schedule":
            term = submission["term"]
            name = submission["name"]
            schedule = submission["schedule"]

            # parse part
            result_list = ['NG']*(4*5+5*2)
            weekday_list = ['月', '火', '水', '木', '金']
            holiday_list = ['土', '日']

            for word in schedule.split('+'):
                if word[0] in weekday_list:
                    i = weekday_list.index(word[0]) # ex: '火' -> '1'
                    for j in range(0,4):
                        result_list[4*i+j] = 'OK' if str(j+4) in word else 'NG'

                if word[0] in holiday_list:
                    i = holiday_list.index(word[0]) + 5 # ex: '日' -> '6'
                    for j in range(0,5):
                        result_list[5*(i-1)+j] = 'OK' if str(j+1) in word else 'NG'

            # write part
            '''
            We assumed that Google Sheets are the following form:
            * row 1: user_id list
            * row 2: user_name list
            '''
            worksheet = self._sheet.worksheet(term)
            try:
                column = worksheet.find(name).col
            except gspread.exceptions.CellNotFound:
                column = worksheet.col_count+1
                
            for row in range(3,33):
                worksheet.update_cell(row, column, result_list[row-3])

        if type == "subject":
            name = submission["name"]
            major = submission["major"]
            subject_common = submission["subject_common"]
            subject_major_set = set(submission["subject_major"].split('+'))

            # parse part
            result_list = ['NG']*9
            subject_major_list = ["微積分", "線形代数", "集合・位相", "統計学"]

            index = int(subject_common)
            for i in range(0,index):
                result_list[i] = 'OK'

            for i in range(4,8):
                result_list[i] = 'OK' if subject_major_list[i-4] in subject_major_set else 'NG'

            result_list[8] = major

            # write part
            '''
            We assumed that Google Sheets are the following form:
            * column 1: index, subjects name
            * row 1: user_id list
            * row 2: user_name list
            * row 3-6: `担当科目-共通` {'OK', 'NG'}_list
            * row 7-10: `担当科目-大学教養` {'OK', 'NG'}_list
            * row 11: `専門科目` str_list
            '''
            worksheet = self._sheet.sheet1
            try:
                column = worksheet.find(name).col
            except gspread.exceptions.CellNotFound:
                column = worksheet.col_count+1
                
            for row in range(3,12):
                worksheet.update_cell(row, column, result_list[row-3])
