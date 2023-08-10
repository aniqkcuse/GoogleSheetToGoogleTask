from __future__ import print_function

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/drive","https://www.googleapis.com/auth/tasks","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = ""

def create():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
        
    try:
        if os.path.exists("sheet_id.txt"):
            with open("sheet_id.txt", "r") as sheet_id:
                SPREADSHEET_ID = sheet_id.read()
        else:
            service_sheet = build("sheets", "v4", credentials=creds)
            service_drive = build("drive", "v3", credentials=creds)

            sheet_created = service_sheet.spreadsheets().create(body={"properties":{"title":"Google Task List"}, "sheets": [{"properties": {"title":"Task List"}}]}).execute()
            SPREADSHEET_ID = sheet_created["spreadsheetId"]

            service_sheet.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range="A1", valueInputOption="USER_ENTERED", body={'values':[['Title of the task']]}).execute()
            service_sheet.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range="B1", valueInputOption="USER_ENTERED", body={'values':[['Description of the task']]}).execute()

            with open("sheet_id.txt", "w") as sheet_id:
                sheet_id.write(SPREADSHEET_ID)

    except HttpError as error:
        print(error)

    print(SPREADSHEET_ID)
    return SPREADSHEET_ID