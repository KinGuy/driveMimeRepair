# driveMimeRepair
This code aim to repair broken mimeType in Google Drive.
It uses python to authenticate and connect to Drive API.

## Install
1. Create credentials at https://console.developers.google.com/apis/credentials.
2. Save JSON file in working dir.
3. Rename JSON file to 'client_secret.json'
4. Run python code.

## Limitations
Won't work for big files (>900M).
Will only work for common file types.
