# Google Workspace DFIR Tool

## Configuring the API
**Note** This requires an admin account for the Google Workspace organization.
1. Log in to [https://console.developers.google.com/cloud-resource-manager](https://console.developers.google.com/cloud-resource-manager) and log in with admin credentials.
2. Create a new project
3. Go to [https://console.developers.google.com/apis/dashboard](https://console.developers.google.com/apis/dashboard) and ensure the created project is selected at the top left.
4. Select `Credentials` on the left and choose `OAuth Client ID`.
5. Choose `Web application` for the application type
6. Download the JSON credentials file (rename if desired, to something such as `credentials.json`).
7. Put the file in the path you designated in the `config.json` file 

## Program Configuration
- The `config.json` file allows you to define the file path where credential and MaxMind DB files are located
- The `Geolite2-City.mmdb` file can be downloaded from the MaxMind website.

## Running the Progam
```
python3 google_dfir.py -o <output file>
```
**Note**: The output option should should provide the full path and file name (XLSX). Ex. `/User/bob/results.xlsx`