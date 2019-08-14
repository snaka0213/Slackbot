#!/usr/bin/env python3
import slack
import settings
from slackclient import SlackClient
from slackbot.bot import slash_command
from slackbot.bot import interactive_message
from .gspread_reader import GSpreadReader
from .gspread_writer import GSpreadWriter

# transform {'OK', 'NG'} <--> {True, False}
def transform_bool(value):
    if type(value) == bool:
        return 'OK' if value else 'NG'
    elif type(value) == str:
        return True if value == 'OK' else False

def schedule_form(user_id):
    reader = GSpreadReader()
    reader.login()
    reader.open(settings.SCHEDULE_SHEET_FILE_NAME)

    # omit the last worksheet `TEMPLATE_SHEET`
    term_list = reader.get_worksheet_title_list()[:-1]

    '''
    We assumed that Google Sheets are the following form:
    * row 1: user_id list
    * row 2: user_name list
    '''

    def get_user_info_list(worksheet) -> list:
        user_id_list = worksheet.row_values(1)
        N = len(user_id_list)
        return [
            {
                "user_id": user_id_list[i],
                "user_name": worksheet.cell(2,i+1).value,
            } for i in range(N)
        ]

    def search_past_name(user_id: str) -> str:
        for title in term_list:
            worksheet = reader.get_worksheet(title)
            for info in get_user_info_list(worksheet):
                if info["user_id"] == user_id:
                    return info["user_name"]

        else:
            return None

    dialog = {
        "title": "スケジュール入力フォーム",
        "submit_label": "送信",
        "callback_id": "schedule_form_" + user_id,
        "elements": [
            {
                "label": "年度",
                "type": "select",
                "name": "term",
                "options": [
                    {
                        "label": term,
                        "value": term,
                    } for term in term_list
                ]
            },
            {
                "label": "氏名",
                "type": "text",
                "name": "name",
                "placeholder": "例: 上杉 風太郎",
                "value": search_past_name(user_id),
            },
            {
                "label": "担当できるコマ",
                "type": "textarea",
                "name": "schedule",
                "placeholder": "例: 月567 土1234 ... (空白区切り)",
                "hint": "平日: 4-7限 / 休日: 1-5限"
            },
        ]
    }
    return dialog

def subject_form(user_id):
    reader = GSpreadReader()
    reader.login()
    reader.open(settings.SUBJECT_SHEET_FILE_NAME)
    term_list = reader.get_worksheet_title_list()

    '''
    We assumed that Google Sheets are the following form:
    * column 1: index, subjects name
    * row 1: user_id list
    * row 2: user_name list
    * row 3-6: `担当科目-共通` {'OK', 'NG'}_list
    * row 7-10: `担当科目-大学教養` {'OK', 'NG'}_list
    * row 11: `専門科目` str_list
    '''

    '''
    # Note: API limit
    def get_user_info_list(worksheet) -> list:
        user_id_list = worksheet.row_values(1)
        N = len(user_id_list)
        return [
            {
                "user_id": user_id_list[i],
                "user_name": worksheet.cell(2, i+1).value,
                "user_subject_common": sum([
                    1 for j in range(3, 7) \
                    if transform_bool(worksheet.cell(j, i+1).value)
                ]),
                "user_subject_uncommon": [
                    worksheet.cell(j, 1).value for j in range(7,11) \
                    if transform_bool(worksheet.cell(j, i+1).value)
                ],
                "user_major": worksheet.cell(11, i+1),
            } for i in range(N)
        ]

    def search_in_past(user_id: str) -> dict:
        for title in term_list:
            worksheet = reader.get_worksheet(title)
            for info in get_user_info_list(worksheet):
                if info["user_id"] == user_id:
                    return info

        else:
            return None
    '''

    def get_user_info_list(worksheet) -> list:
        user_id_list = worksheet.row_values(1)
        N = len(user_id_list)
        return [
            {
                "user_id": user_id_list[i],
                "user_name": worksheet.cell(2,i+1).value,
            } for i in range(N)
        ]

    def search_past_name(user_id: str) -> str:
        for title in term_list:
            worksheet = reader.get_worksheet(title)
            for info in get_user_info_list(worksheet):
                if info["user_id"] == user_id:
                    return info["user_name"]

        else:
            return None

    dialog = {
        "title": "担当科目入力フォーム",
        "submit_label": "送信",
        "callback_id": "subject_form_" + user_id,
        "elements": [
            {
                "label": "氏名",
                "type": "text",
                "name": "name",
                "placeholder": "例: 上杉 風太郎",
                "value": search_past_name(user_id),
            },
            {
                "label": "専門科目",
                "type": "text",
                "name": "major",
                "placeholder": "例: 代数幾何学",
                # "value": search_in_past(user_id).get("user_major"),

            },
            {
                "label": "担当科目-共通",
                "type": "select",
                "name": "subject_common",
                # "value": search_in_past(user_id).get("user_subject_common"),
                "options": [
                    {
                        "label": "1. 中学通常まで可能",
                        "value": "1",
                    },
                    {
                        "label": "2. 高校受験対策まで可能",
                        "value": "2",
                    },
                    {
                        "label": "3. 高校通常まで可能",
                        "value": "3",
                    },
                    {
                        "label": "4. 大学受験対策まで可能",
                        "value": "4",
                    },
                ],
            },
            {
                "label": "担当科目-大学教養",
                "type": "textarea",
                "name": "subject_major",
                "placeholder": "例: 微積分 統計学 (空白区切り)",
                "hint": "選択肢: 微積分 / 線型代数学 / 集合・位相 / 統計学",
                # "value": " ".join(search_in_past(user_id).get("user_subject_uncommon"))
            },
        ]
    }
    return dialog

@slash_command("schedule")
def schedule_dialog(payload: dict, client: SlackClient):
    type = payload.get("type")
    if type is None:
        trigger_id = payload["trigger_id"]
        user_id = payload["user_id"]
        dialog = schedule_form(user_id)
        open_dialog = client.api_call(
            "dialog.open", trigger_id=trigger_id, dialog=dialog
        )
    return

@slash_command("subject")
def subject_dialog(payload: dict, client: SlackClient):
    type = payload.get("type")
    if type is None:
        trigger_id = payload["trigger_id"]
        user_id = payload["user_id"]
        dialog = subject_form(user_id)
        open_dialog = client.api_call(
            "dialog.open", trigger_id=trigger_id, dialog=dialog
        )
    return

@interactive_message("dialog_submission")
def submission_parse(payload: dict, client: SlackClient):
    submission = payload.get("submission")
    if submission:
        user = payload["user"]["id"]
        channel = payload["channel"]["id"] or "#general"
        callback_id = payload["callback_id"]
        writer = GSpreadWriter()
        writer.login()
        
        dialog_type = None
        if "schedule" in callback_id:
            writer.open(settings.SCHEDULE_SHEET_FILE_NAME)
            dialog_type = "schedule"

        if "subject" in callback_id:
            writer.open(settings.SUBJECT_SHEET_FILE_NAME)
            dialog_type = "subject"

        if dialog_type is not None:
            writer.write(submission, dialog_type)
            text = "Submission Accepted! :tada:"

        notification = client.api_call(
            "chat.postEphemeral", channel=channel, text=text, user=user
        )
    return
