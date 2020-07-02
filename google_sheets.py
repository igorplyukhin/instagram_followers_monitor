from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1BhNYOpeEsv4XoPjNlQJDpfIzkKVn35YlHQTiHcgIxJw'
SAMPLE_RANGE_NAME = 'Лист1!A1:D5'
value_input_option = 'USER_ENTERED'


def main():
    creds = init_credentials()
    service = build('sheets', 'v4', credentials=creds)


def init_credentials():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def create_new_spreadsheet(service):
    spreadsheet = {
        'properties': {
            'title': 'abc'
        }
    }
    spreadsheet = service.spreadsheets().create(body=spreadsheet,
                                                fields='spreadsheetId').execute()
    print('Spreadsheet ID: {0}'.format(spreadsheet.get('spreadsheetId')))


def fill_sheet_range(service):
    values = [
        ["Item", "Cost", "Stocked", "Ship Date"],
        ["Wheel", "$20.50", "4", "3/1/2016"],
        ["Door", "$15", "2", "3/15/2016"],
        ["Engine", "$100", "1", "3/20/2016"],
        ["Totals", "=SUM(B2:B4)", "=SUM(C2:C4)", "=MAX(D2:D4)"],
    ]
    body = {
        'values': values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME,
        valueInputOption=value_input_option, body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))


if __name__ == '__main__':
    main()
