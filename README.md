# driveMimeRepair
This code aim to repair broken mimeType in Google Drive.
It uses python to authenticate and connect to Drive API.

## Install
1. Create credentials at https://console.developers.google.com/apis/credentials.
2. Save JSON file in working dir.
3. Rename JSON file to 'client_secret.json'
4. Install using `pip`:
```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```
5. Run python code.

## Limitations
Won't work for big files (>900M).
Will only work for common file types.

## Credits
Most of the work based on: https://github.com/googleapis/google-api-python-client
