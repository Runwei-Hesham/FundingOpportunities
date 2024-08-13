from flask import Flask, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
from datetime import datetime
import requests

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

# Define mapping from sheet columns to API request fields
COLUMN_MAPPING = {
    '': 'title',
    'State/Country': 'countries_eligible',
    'Type': 'opportunity_type_id',
    'Description': 'description',
    'Amount': 'award_value',
    'Deadline': 'deadline',
    'Website': 'eso_website',
    'Date Posted': 'date_posted'
}

DEFAULTS = {
    'url': '',
    'logo_url': '',
    'short_description': '',
    'eligibility': '',
    'cash_award': 0,
    'contact_email': 'user@example.com',
    'contact_names': '',
    'opportunity_type_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    'industry_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    'target_community_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    'time_zone': 'UTC',
    'direct_apply_link': '',
    'opportunity_gap': '',
    'global_opportunity': True,
    'global_locations': '',
    'location_details': '',
    'sdg_alignment': '',
    'service_provider_eso': '',
    'approval_status': 'draft',
    'cost': 0,
    'financial_terms': '',
    'area_of_focus': '',
    'tags': '',
    'industry': '',
    'slug': ''
}
# Define the mapping of opportunity types to IDs
opportunity_type_mapping = {
    "Accelerator": "018ec1bd-42b2-788c-a196-bfc131777515",
    "accelerator": "018ec1bd-42b2-788c-a196-bfc131777515",
    "Business Advisor": "018ec1bd-9d2a-7a61-9ccf-f9212c3600c3",
    "business advisor": "018ec1bd-9d2a-7a61-9ccf-f9212c3600c3",
    "Competition": "018ec1bd-dcfa-77ab-bac0-4787840fa2cb",
    "competition": "018ec1bd-dcfa-77ab-bac0-4787840fa2cb",
    "Grants": "018f0c52-113c-7fbc-8f6c-3bb9942882c8",
    "grants": "018f0c52-113c-7fbc-8f6c-3bb9942882c8",
    "Grant": "018f0c8d-698b-71b9-8969-ee96855039f0",
    "grant": "018f0c8d-698b-71b9-8969-ee96855039f0",
    "African Diaspora": "018f0c5b-0603-7a2a-ae1a-43a1ebaca683",
    "african diaspora": "018f0c5b-0603-7a2a-ae1a-43a1ebaca683",
    "Partnership": "018f0c5f-3b99-77d2-84fb-218810abb134",
    "partnership": "018f0c5f-3b99-77d2-84fb-218810abb134",
    "Program": "018f0c84-5352-7c25-84b4-ed68d7619b7c",
    "program": "018f0c84-5352-7c25-84b4-ed68d7619b7c",
    "Pre-Accelerator": "018f0c86-e7ae-7a3a-b3a5-71834150da5e",
    "pre-accelerator": "018f0c86-e7ae-7a3a-b3a5-71834150da5e",
    "Pitch": "018f0c8a-e815-7e02-b4b6-34a369b3e50e",
    "pitch": "018f0c8a-e815-7e02-b4b6-34a369b3e50e",
    "Mentorship": "018f0c8c-a233-733c-b38b-4dde960fdb07",
    "mentorship": "018f0c8c-a233-733c-b38b-4dde960fdb07",
    "Programs": "018f0c8c-a8d7-7b54-b929-793f21871fe1",
    "programs": "018f0c8c-a8d7-7b54-b929-793f21871fe1",
    "Resources": "018f0c8d-6286-75f6-bd83-81ce34e4fd4c",
    "resources": "018f0c8d-6286-75f6-bd83-81ce34e4fd4c",
    "Awards": "018f8470-f8fb-714c-ad14-1bd096804c6d",
    "awards": "018f8470-f8fb-714c-ad14-1bd096804c6d",
    "Award": "0190348d-0ff5-741f-bee6-7c0ab62c29a3",
    "award": "0190348d-0ff5-741f-bee6-7c0ab62c29a3",
    "New Category": "01903592-c87a-7569-906a-3204cab354b5",
    "new category": "01903592-c87a-7569-906a-3204cab354b5",
    "Venture capitals": "01913234-4c12-7dc4-b240-4a0c0e58e1ce",
    "venture capitals": "01913234-4c12-7dc4-b240-4a0c0e58e1ce"
}

def get_sheet_data():
    try:
        # Get the data starting from row 6, column A (A6)
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='open!A6:H').execute()
        return result.get('values', [])
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

def map_row_to_api_format(row, header):
    title_idx = header.index('')
    if title_idx == -1 or not row[title_idx].strip():
        return None  # Return None to skip this row
    
    def get_opportunity_type(str):
        if str == "grant":
            return None
        

    api_data = {
        "title": row[header.index('')] if '' in header else '',
        "url": '',
        "logo_url": '',
        "short_description": '',
        "description": row[header.index('Description')] if 'Description' in header else '',
        "eligibility": '',
        "deadline": '',
        "award_value": 0,
        "cash_award": 0,
        "contact_email": 'user@example.com',
        "contact_names": '',
        "opportunity_type_id": opportunity_type_mapping.get(row[header.index('Type')].strip(), '') if 'Type' in header else 'No Column',
        "industry_id": '3fa85f64-5717-4562-b3fc-2c963f66afa6',
        "target_community_id": '3fa85f64-5717-4562-b3fc-2c963f66afa6',
        "time_zone": 'UTC',
        "direct_apply_link": '',
        "opportunity_gap": '',
        "global_opportunity": True,
        "global_locations": '',
        "countries_eligible": row[header.index('State/Country')] if 'State/Country' in header else '',
        "location_details": '',
        "sdg_alignment": '',
        "eso_website": row[header.index('Website')] if 'Website' in header else '',
        "service_provider_eso": '',
        "approval_status": 'draft',
        "cost": 0,
        "financial_terms": '',
        "area_of_focus": '',
        "tags": '',
        "industry": '',
        "slug": '',
        "award_value_str": row[header.index('Amount')] if 'Amount' in header else '',
        "deadline_str": row[header.index('Deadline')] if 'Deadline' in header else '',
        "date_posted": row[header.index('Date Posted')] if 'Date Posted' in header else '',
        "opportunitytype": row[header.index('Type')] if 'Type' in header else ''
    }

    deadline_idx = header.index('Deadline') if 'Deadline' in header else -1
    if deadline_idx != -1 and len(row) > deadline_idx:
        try:
            api_data['deadline'] = datetime.strptime(row[deadline_idx], '%m/%d/%Y').isoformat()
        except ValueError:
            api_data['deadline'] = ''

    return api_data

def group_data_by_region(data):
    if not data:
        return {}

    header = data[0]
    rows = data[1:]
    print("headers: " , header)
    # Handle missing header columns by extending
    header = [header[i] if i < len(header) else '' for i in range(len(COLUMN_MAPPING))]
    
    grouped_data = {}
    
    for row in rows:
        if len(row) < len(header):
            row = [""] * (len(header) - len(row)) + row
        
        api_data = map_row_to_api_format(row, header)
        if api_data is None:
            continue  # Skip rows that are not valid opportunities
        
        region = api_data.get('countries_eligible', 'Unknown')
        
        if region not in grouped_data:
            grouped_data[region] = []
        
        grouped_data[region].append(api_data)
    
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
