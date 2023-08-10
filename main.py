from __future__ import print_function

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from create_sheet import create
import create_sheet
import keyboard

SCOPES = ["https://www.googleapis.com/auth/tasks","https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive","https://www.googleapis.com/auth/drive.file"]

def main(id_sheet:str):
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
        service_sheet = build("sheets", "v4", credentials=creds)
        service_task = build("tasks", "v1", credentials=creds)

        task_list_get = service_task.tasklists().list().execute()
        task_list = task_list_get.get("items")
        exist_list_task = None
        id_list = ""
        for i in range(len(task_list)):
            if task_list[i]["title"] == 'sheetToTask':
                exist_list_task = True
                id_list = task_list[i]["id"]
            else:
                exist_list_task = False
        if exist_list_task == False:
            add_task_list = service_task.tasklists().insert(body={'title':'sheetToTask'}).execute()
            print(add_task_list)

        tasks = service_task.tasks().list(tasklist=id_list).execute()
        for task in tasks.get("items"):
            service_task.tasks().delete(tasklist=id_list, task=task["id"]).execute()

        for lists in range(1,40000):
            try:
                title = service_sheet.spreadsheets().values().get(spreadsheetId=id_sheet, range=f"A{lists+1}").execute()
                content = service_sheet.spreadsheets().values().get(spreadsheetId=id_sheet, range=f"B{lists+1}").execute()
                title_text = title.get('values')[0][0]
                content_text = content.get('values')[0][0]
                task_list_get = service_task.tasklists().list().execute()
                task_list = task_list_get.get("items")
                id_task_list = ""
                for i in range(len(task_list)):
                    if task_list[i]["title"] == 'sheetToTask':
                        id_task_list = task_list[i]["id"]
                service_task.tasks().insert(tasklist=id_task_list, body={'title':f'{title_text}', 'notes':f'{content_text}'}).execute()
            except:
                break

    
    except HttpError as error:
        print(error)

if __name__ == "__main__":
    id_sheet = create()
    main(id_sheet)