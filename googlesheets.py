from oauth2client import tools
import httplib2
import os, io
import gspread
import re
# import auth
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
from apiclient import discovery
from oauth2client import client
from oauth2client.file import Storage
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery

# try:
#     import argparse
#     flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
# except ImportError:
#     flags = None
class auth:
    def __init__(self,SCOPES,CLIENT_SECRET_FILE,APPLICATION_NAME):
        self.SCOPES = SCOPES
        self.CLIENT_SECRET_FILE = CLIENT_SECRET_FILE
        self.APPLICATION_NAME = APPLICATION_NAME
    def getCredentials(self):
        """Gets valid user credentials from storage.
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
        Returns:
            Credentials, the obtained credential.
        """

        cwd_dir = os.getcwd()
        credential_dir = os.path.join(cwd_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'google-drive-credentials.json')
        
        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials


def get_credentials():
    """Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Google Drive API.
    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    results = service.files().list(
        pageSize=10,fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print('{0} ({1})'.format(item['name'], item['id']))




def createSheet(name,credentials):
    http = credentials.authorize(httplib2.Http())
    gss_client = gspread.authorize(credentials)
    drive_service = discovery.build('drive', 'v3', http=http)
    file_metadata = {
    'name': name,
    'parents':['1NhfpSCc-dHUNqxRs4tapfsg9kRgeTCMr'],
    'mimeType': 'application/vnd.google-apps.spreadsheet',
    'capabilities.canDelete':False
    }
    file = drive_service.files().create(body=file_metadata,
                                        fields='id').execute()

    
    sheet = gss_client.open_by_key(file.get('id')).sheet1
    # Google Sheet 資料表
    sheet.clear() # 清除 Google Sheet 資料表內容
    listtitle=["照片","內容(內容被遮掩，點儲存格兩下即可看完整內容)","講師名稱","筆記","問題討論"]
    sheet.append_row(listtitle)  # 標題
    print ('Sheet Url: ' + "https://docs.google.com/spreadsheets/d/" + file.get('id') + "/edit#gid=0")
    return file.get('id')

def pt_column(id,credentials):
    http = credentials.authorize(httplib2.Http())
    gss_client = gspread.authorize(credentials)
    drive_service = discovery.build('sheets', 'v4', http=http)
    ss = gss_client.open_by_key(id)
    body1 = {
        "requests": [
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId":0,
                        "dimension": "COLUMNS",
                        "startIndex":0,
                        "endIndex": 1
                    },
                    "properties": {
                        "pixelSize":220
                    },
                    "fields": "pixelSize"
                },
                
               
            }   
        ]
    }
    
    drive_service.spreadsheets().batchUpdate(spreadsheetId=id, body=body1).execute()
    #drive_service.spreadsheets().batchUpdate(spreadsheetId=id, body=body2).execute()  

def text_column(id,credentials):
    http = credentials.authorize(httplib2.Http())
    gss_client = gspread.authorize(credentials)
    drive_service = discovery.build('sheets', 'v4', http=http)
    ss = gss_client.open_by_key(id)
    body1 = {
        "requests": [
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId":0,
                        "dimension": "COLUMNS",
                        "startIndex":1,
                        "endIndex": 2
                    },
                    "properties": {
                        "pixelSize":380
                    },
                    "fields": "pixelSize"
                },
                
               
            }   
        ]
    }
    
    drive_service.spreadsheets().batchUpdate(spreadsheetId=id, body=body1).execute()
    #drive_service.spreadsheets().batchUpdate(spreadsheetId=id, body=body2).execute()  

def rowauto(id,credentials):

    http = credentials.authorize(httplib2.Http())
    gss_client = gspread.authorize(credentials)
    drive_service = discovery.build('sheets', 'v4', http=http)
    ss = gss_client.open_by_key(id)
    body1 = {
        "requests": [
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId":0,
                        "dimension": "ROWS",
                        "startIndex":1,
                        "endIndex": 80  
                    },
                    "properties": {
                        "pixelSize":215
                    },
                    "fields": "pixelSize"
                },
              
               
            }   
        ]
    }
    
    drive_service.spreadsheets().batchUpdate(spreadsheetId=id, body=body1).execute()

def talk(id,credentials):

    http = credentials.authorize(httplib2.Http())
    gss_client = gspread.authorize(credentials)
    drive_service = discovery.build('sheets', 'v4', http=http)
    ss = gss_client.open_by_key(id)
    body1 = {
        "requests": [
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId":0,
                        "dimension": "COLUMNS",
                        "startIndex":3,
                        "endIndex": 5
                    },
                    "properties": {
                        "pixelSize":300
                    },
                    "fields": "pixelSize"
                },
                
            }   
        ]
    }
    drive_service.spreadsheets().batchUpdate(spreadsheetId=id, body=body1).execute()


def insertImage(id,photourl,text,name,note,credentials):
    
    spreadsheet_key = id
    gss_client = gspread.authorize(credentials)
    url='=IMAGE("'+photourl+'"'+',4,215,220)'
    sheet = gss_client.open_by_key(spreadsheet_key).sheet1
    listdata=[url,text,name+"\n\n\n\n\n",note+"\n\n\n\n\n",""]
    sheet.append_row(listdata,value_input_option='USER_ENTERED')
    pt_column(id,credentials)
    text_column(id,credentials)
    talk(id,credentials)
    rowauto(id,credentials)
    #sheet.append_row(x) 

def googlesh():
    try:
        import argparse
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    except ImportError:
        flags = None
    # spreadsheet api
    auth_json_path = 'C:\\inetpub\\wwwroot\\test-vision-api-f989a5d4665e.json'
    gss_scopes = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(auth_json_path,gss_scopes)
    gss_client = gspread.authorize(credentials)

    # google drive
    SCOPES = 'https://www.googleapis.com/auth/drive.file'
    CLIENT_SECRET_FILE = "C:\\inetpub\\wwwroot\\client_secret.json"
    APPLICATION_NAME = 'Drive API Python Quickstart'
    authInst = auth(SCOPES,CLIENT_SECRET_FILE,APPLICATION_NAME)
    credentials = authInst.getCredentials()
    http = credentials.authorize(httplib2.Http())
    
    drive_service = discovery.build('drive', 'v3', http=http)
    return credentials
