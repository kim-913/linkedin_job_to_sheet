Step 1: Setting Up Google Cloud Platform
Create a New Project:

Go to the GCP Console.
Click on the project drop-down and select "New Project".
Enter a project name and click "Create".
Enable Google Sheets API and Google Drive API:

In the GCP Console, go to APIs & Services > Library.
Search for "Google Sheets API" and click "Enable".
Search for "Google Drive API" and click "Enable".

Step 2: Creating a Service Account
Create Service Account:

Go to IAM & Admin > Service Accounts.
Click "Create Service Account".
Enter a service account name and description, then click "Create".
Grant Permissions:

For the "Select a role" dropdown, choose Project > Editor.
Click "Continue", then click "Done".
Create Key:

In the service account list, click the three dots on the right of your newly created service account and select "Manage Keys".
Click "Add Key" > "Create new key".
Choose the JSON key type and click "Create".
A JSON file will be downloaded. Save this file securely as it contains credentials for your service account.

Step 3: Sharing the Google Sheet
Create a Google Sheet:

Go to Google Sheets.
Create a new sheet or use an existing one.
Share the Google Sheet:

Click the "Share" button in the top right corner.
Share it with the service account email (found in your JSON key file).

Step 4: Installing Required Python Packages
Run the following pip commands to install the necessary Python packages:

sh
Copy code
pip install selenium
pip install beautifulsoup4
pip install gspread
pip install oauth2client

Step 4: Modify the script and run
Modify from line 119-123 and you are're good to go
