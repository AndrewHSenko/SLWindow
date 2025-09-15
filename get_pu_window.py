# https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit?gid=SHEET_ID#gid=SHEET_ID #
import os.path
import re
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive']
# SPREADSHEET_ID = '11RDkPuupd7lq8TnkAagahZSBuOfzXGGLOhZGvdroOp4' # Should be dynamic # Dev Change #
# RAW_RANGE = 'D5:L126' # Trims surrounding empty rows
TOTAL_RANGE = 'M6:M125' # Should be 10:00am - 8:00pm, 120 total entries
WINDOW_RANGE = 'O6:O125'
DEFAULT = 'M1'
DEFAULT_VAL = '18'

TOKE_PATH = 'C:/Users/Squirrel/Documents/VSCode Scripts/SLWindow/token.json'
CREDS_PATH = 'C:/Users/Squirrel/Documents/VSCode Scripts/SLWindow/credentials.json'

def login(creds):
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          CREDS_PATH, SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
      token.write(creds.to_json())

def aggregate(spreadsheet, spreadsheet_id, range_name): # Will need to modify to separate out instructions for different data
    result = (
        spreadsheet.values()
        .get(spreadsheetId=spreadsheet_id, range=range_name)
        .execute()
    )
    values = result.get('values', [])
    if not values:
        print('No data found.')
        return None
    try:
        window_data = {}
        window_i = 0
        for row in values: # Each row should just be one value since we aren't using raw data
            if len(row) > 0:
                window_data[window_i] = row[0]
            else:
                window_data[window_i] = DEFAULT_VAL
            window_i += 1
        return window_data
    except Exception as e:
        with open('pu_errors.txt', 'a') as puf:
            puf.write(str(time.time()) + ':' + str(e) + '\n')

def get_weekly_sheet_id(week):
    creds = None
    if os.path.exists(TOKE_PATH):
        creds = Credentials.from_authorized_user_file(TOKE_PATH, SCOPES)
    if not creds or not creds.valid:
        login(creds)
    try:
        drive = build('drive', 'v3', credentials=creds)
        files = []
        # First, get the folder ID by querying by mimeType and name
        while True: # Will change to not be a loop
            page_token = None
            month_folder_req = f'mimeType = "application/vnd.google-apps.folder" and trashed=false and name = \"{time.strftime("%B")} {time.strftime("%Y")[-2:]}\"'
            month_folder_result = drive.files().list(
                q = month_folder_req,
                spaces="drive",
                pageSize=3, # Arbitrary
                fields="nextPageToken, files(id, name)",
                pageToken=page_token
            ).execute().get('files', [])
            if month_folder_result == []: # No results found
                with open('pu_errors.txt', 'a') as puf:
                    puf.write(f'Could not find {time.strftime("%B")} {time.strftime("%Y")[-2:]}. Double check the folder name is correct.\n')
                month_folder_req = f'mimeType = "application/vnd.google-apps.folder" and trashed=false and name contains \"{time.strftime("%b")}\"' # Backup request
                month_folder_result = drive.files().list(
                    q = month_folder_req,
                    spaces="drive",
                    pageSize=20, # Arbitrary
                    fields="nextPageToken, files(id, name)",
                    pageToken=page_token
                ).execute().get('files', [])
                for result in month_folder_result:
                    if time.strftime('%Y')[-2:] in result.get('name'):
                        month_folder_id = result.get('id')
                        break
            else:
               month_folder_id = month_folder_result[0].get('id')
            spreadsheet_id_req = f'mimeType = "application/vnd.google-apps.spreadsheet" and trashed=false and "{month_folder_id}" in parents'
            spreadsheet_id_result = drive.files().list(
                q = spreadsheet_id_req,
                orderBy = "createdTime",
                spaces="drive",
                pageSize=7, # Max is 5 weeks for the fiscal month, plus extra cushion
                fields="nextPageToken, files(id, name)",
                pageToken=page_token
            ).execute()
            pattern = re.compile(r'[\W_]+')
            all_sheets = [(x['id'], pattern.sub('', x['name'])) for x in spreadsheet_id_result.get('files', [])]
            weekly_sheet_id = all_sheets[week - 1][0]
            return weekly_sheet_id
            # page_token = folderIdResult.get("nextPageToken", None)
            # if page_token is None:
            #     break
    except Exception as e:
        with open('pu_errors.txt', 'a') as puf:
            puf.write(str(time.time()) + ':' + str(e) + '\n')
    

def get_data(week_num, sheet_num):
    days = [
        'MON',
        'TUE',
        'WED',
        'THU',
        'FRI',
        'SAT',
        'SUN'
    ]
    creds = None
    if os.path.exists(TOKE_PATH):
        creds = Credentials.from_authorized_user_file(TOKE_PATH, SCOPES)
    if not creds or not creds.valid:
        login(creds)
    try:
        service = build('sheets', 'v4', credentials=creds)
        # test_searching_drive(service)
        spreadsheet_id = get_weekly_sheet_id(week_num)
        spreadsheet = service.spreadsheets()
        sheet_metadata = spreadsheet.get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', '')
        # Sheets is a list of the sheets within the Google Spreadsheet. 0 - Mon, 1 - Tue, etc.
        sheet = sheets[sheet_num]
        title = sheet.get('properties', {}).get('title', 'Sheet1')
        is_day = False
        for day in days:
            if day in title:
                is_day = True
                break
        if not is_day:
            return False
        # sheet_id = sheet.get('properties', {}).get('sheetId', 0)
        window_range_name = f'{title}!{WINDOW_RANGE}'
        total_range_name = f'{title}!{TOTAL_RANGE}'
        default = aggregate(spreadsheet, spreadsheet_id, DEFAULT)
        if not default[0].isnumeric():
            default[0] = DEFAULT_VAL # 18
        planned = aggregate(spreadsheet, spreadsheet_id, window_range_name)
        actual = aggregate(spreadsheet, spreadsheet_id, total_range_name)
        total = len(actual)
        if len(planned) < total:
            for i in range(len(planned), total): # Will replace trailing blanks (normally ommitted) with the correct default window setting
                planned[i] = default[0] # Should be the default window setting found in cell M1
        i = 0
        for i in range(total): # Assumes size of planned and actual match, which they do by design
            if not planned[i].isnumeric():
                planned[i] = DEFAULT_VAL
            if not actual[i].isnumeric():
                actual[i] = DEFAULT_VAL
            actual[i] = int(planned[i]) - int(actual[i])
        return (planned, actual)
    except Exception as e:
        with open('pu_errors.txt', 'a') as errtext:
            errtext.write(str(time.time()) + ':' + str(e) + '\n')
        return False

if __name__ == '__main__':
    j = 0
    while j < 7:
        result = get_data(2, j)
        if not result: # Returned False from error
            continue
        i = 0
        for value in result[0].values():
            if i % 10 == 0 and i != 0:
                i = 0
                print()
            print(value, end=' | ')
        print('-- BREAK --')
        i = 0
        for value in result[1].values():
            if i % 10 == 0 and i != 0:
                i = 0
                print()
            print(value, end=' | ')
        print()
        j += 1

# 2236 Woodview Apt. 362