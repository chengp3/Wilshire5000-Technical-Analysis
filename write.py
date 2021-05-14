# FinSheet API

import gspread
from google.oauth2 import service_account
import sys
import os
import configparser


def get_settings(): #settings in config.cfg
    parser = configparser.ConfigParser()
    parser.read(resource_path("config.cfg"))

    workbook = parser.get("config", "workbookname")

    return workbook

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def write_to_sheet(df, index):
    workbook = get_settings()[1:-1]

    SCOPES = ['https://www.googleapis.com/auth/drive']

    creds = None
    creds = service_account.Credentials.from_service_account_file(
        resource_path('keys.json'), scopes=SCOPES)

    client = gspread.authorize(creds)

    sheet = client.open(workbook).sheet1

    df.fillna('-1', inplace=True)
    aoa = df.values.tolist() #array of arrays

    # Call the Sheets API
    sheet.update(f'A{index}', aoa) #send it