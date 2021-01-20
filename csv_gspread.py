#-*- coding:utf-8 -*-
from creds_google import G_Service
import pandas as pd
import numpy as np
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

WORKSHEET_NAME = ''
PATH_TO_CSV = ''
SERVICE_ACCOUNT_FILE = 'json/My First Project-67d67c490cc8.json' ## 본인걸로 수정
API_SERVICE_NAME = 'sheets' ## 수정 금지
API_VERSION = 'v4' ## 수정 금지
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
] ## 수정 금지
service = G_Service(SERVICE_ACCOUNT_FILE,
                    API_SERVICE_NAME, API_VERSION, SCOPES)

spreadsheets = service.spreadsheets()
SPREADSHEET_ID = '1eJ9iT_9K37Cbp8FIuuECxpJ3WqE2PtvV-rSJA4Du4pw' ## 본인 스프레드시트 링크 {} 사이 링크
## https://docs.google.com/spreadsheets/d/{4tZdjfPWOjhd4I-adeTe53Sfks9jcRkA3298fjd}/edit#gid=404311
## 주의사항
## 스프레드시트 생성 후 공유 옵션에서 '링크가 있는 모든 사용자에게 공개' 및 '편집자'로 설정
credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)
gc = gspread.authorize(credentials)


def add_sheets(sheet_id, sheet_name, hx2rgb):
    def hex_to_rgb(hx):
        if re.compile(r'#[a-fA-F0-9]{3}(?:[a-fA-F0-9]{3})?$').match(hx):
            div = 255.0
            if len(hx) <= 4:
                return tuple(int(hx[i]*2, 16) / div for i in (1, 2, 3))
            else:
                return tuple(int(hx[i:i+2], 16) / div for i in (1, 3, 5))
        else:
            raise ValueError(f'"{hx}" is not a valid HEX code.')
    hls = hex_to_rgb(hx2rgb)
    try:
        request_body = {'requests': [{'addSheet': {'properties': {'title': sheet_name,'tabColor': {'red': hls[0],'green': hls[1],'blue': hls[2]}}}}]}
        response = spreadsheets.batchUpdate(
            spreadsheetId=sheet_id,
            body=request_body
        ).execute()

        return response
    except Exception as e:
        return 'error'


def df_sheets(sheet_id, sheet_name, sheet_cell,Data_list):
    response_date = service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        valueInputOption='RAW',
        range=f"{sheet_name}!{sheet_cell}",
        body=dict(
            majorDimension='ROWS',
            values=Data_list)
    ).execute()

def clear_sheets(sheet_id, sheet_name):
    spreadsheet = gc.open_by_key(sheet_id)
    worksheet = spreadsheet.worksheet(sheet_name)
    worksheet.clear()

def update_sheets(sheet_id, sheet_name,Data_list):
    spreadsheet = gc.open_by_key(sheet_id)
    worksheet = spreadsheet.worksheet(sheet_name)
    cell_list = worksheet.range('A1:H1000')

    for i, val in enumerate(Data_list):  #gives us a tuple of an index and value
        cell_list[i].value = val    #use the index on cell_list and the val from cell_values

    worksheet.update_cells(cell_list)

def df_start(Data_list):
    # 시트추가
    if add_sheets(SPREADSHEET_ID, WORKSHEET_NAME, '#FF0000') == 'error': ## 이미 워크시트가 존재할 시, 해당 내용을 비우고 새로 작성(오류 방지)
        clear_sheets(SPREADSHEET_ID,WORKSHEET_NAME)


    # 내용 추가
    df_sheets(SPREADSHEET_ID, WORKSHEET_NAME, 'A1',Data_list)
    #update_sheets(SPREADSHEET_ID,WORKSHEET_NAME,Data_list)
