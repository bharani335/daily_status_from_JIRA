# Importing the modules we'll need
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials


class GSheetIntegration:
    def __init__(self):
        self.xl_creds_file_path = None
        self.xlsheet_obj = None

    # Authenticate with Daily status Tracking Google Sheets
    def authenticate(self, xl_creds_file_path):
        # use creds to create a client to interact with the Google Drive API
        # client = pygsheets.authorize('/home/rently/Downloads/daily-status-project-2a7a55dd3f5a.json')
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            xl_creds_file_path, scope
        )
        client = gspread.authorize(creds)
        print("Authorized with Gspread", client)

        # Find a workbook by name and open the given Sheet
        # Make sure you use the right name here.
        wb = client.open("<Your Google WorkBook Name>")
        print("Opened the Excel Sheet")
        self.xlsheet_obj = wb.worksheet("<Your Sheet Name>")
        return self.xlsheet_obj

    # Update the cell with the given row, column and value
    # This function will keep trying to update the cell until it succeeds
    # or the maximum number of attempts is reached
    def update_test_case_sheet(self, row, col, value):
        while True:
            try:
                self.xlsheet_obj.update_cell(row, col, value)
                print(
                    "\U0001f4af" * 25,
                    f"Updated cell {col}:{row} with value {value}",
                    "\U0001f4af" * 25,
                )
                break
            except Exception as e:
                print(
                    "\U0001f4af" * 22,
                    f"While updating cell {col}:{row} with value {value} got an error",
                    "\U0001f4af" * 22,
                )
                print(e)
                print("Sleeping for a Sec")
                time.sleep(1)
