# Notes:

This module uses Yahoo Finance API for financial data.

You'll need a Google Cloud API service account credentials in 
'keys.json' in the project root folder to post things to Google Sheets. 

Add new indicators in calc.

Also need to change the 

Workbook name in config.cfg. Will always write to sheet "sheet1"

# Requirements:

gspread
google.oauth2
bs4
requests
pandas
configparser
yfinance
