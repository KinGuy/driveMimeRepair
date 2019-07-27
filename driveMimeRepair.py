### Import ###
import pickle
import os.path

from mimetypes import types_map
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient import errors

### Functions ###
def buildDrivService(serviceName='drive', version='v3'):
    """Create google API auth from JSON, using flow, and saves it to pickle file.
    You need to create a JSON credentials file and put it in the same directory as 
    the py file. Rename the JSON - "client_secret.json".
    """
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/drive']
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
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build(serviceName, version, credentials=creds)

def searchFiles(service, param={}):
    """Retrieve a list of File resources.

    Args:
        service: Drive API service instance.
        param: List of parameters for the list call.
    Returns:
        List of File resources.
        
    Ref: https://developers.google.com/drive/api/v3/reference/files/list
    """
    result = []
    page_token = None
    while True:
        try:
            if page_token:
                param['pageToken'] = page_token
            files = service.files().list(**param).execute()

            result.extend(files['files'])
            page_token = files.get('nextPageToken')
            if not page_token:
                break
        except errors.HttpError as error:
            print('An error occurred: %s' % error)
            break
    return result

def copyDrive(service, fileId, body, params={}):
    """Server side copy of a file in Google Drive.
    
    ref: https://developers.google.com/drive/api/v3/reference/files/copy
    """
    params['fileId'] = fileId
    params['body'] = body
    try:
        response = service.files().copy(**params).execute()
        print(response)
        return True
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
        return False

def fixMime(files):
    """Take all items in 'files', 
    guess correct mimeType, 
    copy item to same folder and 
    delete old item.
    
    Args:
        files: a dictionery of files recieved from searchFiles. Must contain 'fileExtension'.
    Returns:
        int: the number of files found and corrected.
    """
    copys = 0
    service = buildDrivService()
    for file in files:
        # guess new mimeType
        try:
            newMime = types_map['.'+file['fileExtension'].lower()]
        except KeyError:
            print(f"Wrong extension: Faild to copy {file['name']} with ID {file['id']}. ")
            continue
        # ignore "bin" files
        if newMime == 'application/octet-stream': 
            print(f"Wrong extension: Faild to copy {file['name']} with ID {file['id']}. ")
            continue
        # limit file size
        if int(file['size']) > 943718400:
            print(f"Too big: Faild to copy {file['name']} with ID {file['id']}.")
            continue
        # copy file with new mimeType
        seccess = copyDrive(service=service,
                            fileId=file['id'],
                            body={'mimeType':newMime}
                           )
        if seccess:
            # if seccessfull count
            copys += 1
            # only if copy completed seccessfully - delete old file 
            service.files().update(fileId=file['id'],
                                   body={'trashed':'true'}
                                  ).execute()
        else:
            print(f"Faild to copy {file['name']} with ID {file['id']}.")
    # print out    
    print(f"Corrected {copys} out of {len(files)}")
    return copys

### Main ###
def main():
    # list all files under "copy" with wrong mimeType not trashed
    params = {
        "fields": "nextPageToken, files(id, name, mimeType, fileExtension, size)",
        "q": "trashed=false and \
            mimeType='application/octet-stream'\
            ",
        "pageSize": 1000
    }
    items = searchFiles(buildDrivService(), params)

    # print the results
#     if not items:
#         print('No files found.')
#     else:
#         print('Files:')
#         for item in items:
#             print(f"{item['name']} ({item['id']}) mimeType: {item['mimeType']}, ext: {item['fileExtension']}")

    # remove too large items (>900M) and extensions not present in types_map
#     print(len(items))
    items[:] = [item for item in items if (int(item['size'])<943718400 and '.'+item['fileExtension'].lower() in types_map)]
#     print(len(items))

    # copy items with corrected mimeType
    fixMime(items)
