from flask import Flask, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
import json

app = Flask(__name__)

# Path to your service account key file
SERVICE_ACCOUNT_FILE = 'credentials.json'

# The ID of your Google Sheet
SPREADSHEET_ID = '1zU5SUCYBopz64FM4q_nqp2wvILmcdItq_PRWQRXFUB4'

# Authenticate using the service account
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
)

# Build the service
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

def get_sheet_data():
    # Call the Sheets API
    try:
        # Get the data starting from row 6, column A (A6)
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='open!A6:H').execute()
        values = result.get('values', [])
        print("Retrieved data:", values)  # Debug print statement
        return values
    except Exception as e:
        print(f"An error occurred: {e}")
        raise e

def group_data_by_region(data):
    if not data:
        return {}

    # Manually include the column name for column A
    header = ["Name"] + data[0][1:]
    print("Header Row:", header)  # Debug print statement
    rows = data[1:]
    
    # Identify the correct index for the region column
    try:
        region_index = header.index("State/Country")  # Assuming the region is stored in a column named "State/Country"
    except ValueError:
        region_index = header.index("State")  # Check for "State" if "State/Country" not found
    
    grouped_data = {}

    for row in rows:
        if len(row) < len(header):
            # Add a placeholder for the "Name" column if it's missing
            row = [""] + row
        region = row[region_index]
        if region not in grouped_data:
            grouped_data[region] = []
        # Include the data for column A under "Name"
        grouped_data[region].append({header[i]: row[i] for i in range(len(header)) if i < len(row)})
    
    return grouped_data

@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        data = get_sheet_data()
        if not data:
            return jsonify({"error": "No data found"}), 404
        
        grouped_data = group_data_by_region(data)

        # Write grouped data to a file
        with open('grouped_output.txt', 'w') as file:
            json.dump(grouped_data, file, indent=4)
        
        return jsonify({"message": "Data processed and written to grouped_output.txt"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
