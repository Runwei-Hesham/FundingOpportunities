from flask import Flask, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

app = Flask(__name__)

# Path to your service account key file
SERVICE_ACCOUNT_FILE = 'credentials.json'

# The ID and range of your Google Sheet
SPREADSHEET_ID = '1zU5SUCYBopz64FM4q_nqp2wvILmcdItq_PRWQRXFUB4'
RANGE_NAME = 'A1:H11'  # Update the range as needed

# Authenticate using the service account
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
)

# Build the service
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()


def get_sheet_data():
    # Call the Sheets API
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])
    return values


@app.route('/api/data', methods=['GET'])
# def get_data():
#     try:
#         data = get_sheet_data()
#         if not data:
#             return jsonify({"error": "No data found"}), 404
#         return jsonify(data)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

def get_data():
    try:
        data = get_sheet_data()
        if not data:
            return jsonify({"error": "No data found"}), 404
        
        # Write data to a text file
        with open('output.txt', 'w') as file:
            for row in data:
                file.write(', '.join(row) + '\n')
        
        return jsonify({"message": "Data written to output.txt"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
