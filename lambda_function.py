# Importing the modules we'll need
from pathlib import Path
import os
from datetime import datetime

# Local Import
from mailsender import Mailsender
from gsheet_integration import GSheetIntegration
from jira_integration import JiraIntegration
from env import load_env


# Today date format 2022-03-19 09:05:50.453682
today_date = datetime.today()
# Format 2022-07-15
date_format_for_jql = today_date.strftime("%Y-%m-%d")
# date_format_for_jql = "2023-02-15"

# Format 18-03-2022
date_format_for_mail = today_date.strftime("%d/%m/%Y")
# date_format_for_mail = "16-08-2022"

# Warning msg - Log the time and send by manually
Is_this_warning_msg = False

if int(today_date.strftime("%H")) >= 18:  # Following UTC 18.30 UTC => 12.00AM IST
    Is_this_warning_msg = True


# Get the directory of the current Python file
current_dir = Path(__file__).parent


def lambda_handler(event, lambda_context):
    print(datetime.today())
    print("Today date", date_format_for_jql)
    print("Time", today_date)
    print("Is this warning msg? ", Is_this_warning_msg)

    # Load environment variables
    env_vars = load_env()
    server = env_vars['JIRA_SERVER']
    email = env_vars['JIRA_EMAIL']
    api_token = env_vars['JIRA_API_TOKEN']
    xl_creds_file_path = os.path.join(current_dir, env_vars['XL_CREDS_FILE_PATH'])
    print("Loaded environment variables")

    # Authenticate to JIRA(<Your JIRA Server>) using Basic_auth
    jira = JiraIntegration(server, email, api_token, date_format_for_mail)
    print("Authenticated with JIRA")

    # Opening excel sheet
    gsheet = GSheetIntegration()
    gsheet.authenticate(xl_creds_file_path)
    print("Authenticated with Gspread")

    date_row = len(gsheet.xlsheet_obj.row_values(1))
    name_column = len(gsheet.xlsheet_obj.col_values(1))

    date_column_value = gsheet.xlsheet_obj.cell(1, date_row).value

    if str(date_column_value) != date_format_for_mail:
        date_row += 1
        gsheet.xlsheet_obj.add_cols(1)
        gsheet.xlsheet_obj.update_cell(1, date_row, date_format_for_mail)
        print("New day => ", gsheet.xlsheet_obj.cell(1, date_row).value)
        print("New Column Has Been INSERTED")

    today_worklog_status = gsheet.xlsheet_obj.get_values(f"A{1}:F{name_column}")

    date_column_values = gsheet.xlsheet_obj.range(1, date_row, name_column, date_row)

    final_data = {}

    for x in range(1, len(today_worklog_status)):
        mail_to, mail_cc, reporting_managers = []
        username = today_worklog_status[x][0]
        user_email = today_worklog_status[x][1]
        lead = False
        old_status = date_column_values[x].value
        old_status = int(old_status) if old_status else old_status

        print("For user => ", username, user_email, old_status)
        final_data = None
        try:
            if old_status == 1:
                print("{} Already Logged".format(username))
                print(
                    "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",
                    end="\n\n",
                )
                continue

            if old_status == 2:
                print("{} On leave".format(username))
                print(
                    "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",
                    end="\n\n",
                )
                continue

            if today_worklog_status[x][2]:
                mail_to.extend(today_worklog_status[x][2].split(","))
            if today_worklog_status[x][3]:
                mail_cc.extend(today_worklog_status[x][3].split(","))
            if today_worklog_status[x][4]:
                reporting_managers.extend(today_worklog_status[x][4].split(","))
            if today_worklog_status[x][5]:
                lead = True

            final_data = jira.user(username, user_email, lead, date_format_for_jql)
            mailsender = Mailsender(username, user_email, date_format_for_mail)

            # IF Not Work logged
            if final_data["worklogged"] == 0:
                mailsender.remainder_mail(Is_this_warning_msg, reporting_managers)
                mailsender.send_mail()
                print("{} Not logged => 0".format(username))

            # IF worklogged is less than 6 hours
            if final_data["worklogged"] == -1:
                mailsender.remainder_mail(
                    Is_this_warning_msg,
                    reporting_managers,
                    final_data["total_worklogged_time"],
                )
                mailsender.send_mail()
                print("{} Worklogged less than 6 hours => -1".format(username))

            # IF Work logged
            if final_data["worklogged"] == 1:
                if not lead:
                    mailsender.status_mail(mail_to, mail_cc, final_data["soup"])
                    mailsender.send_mail()
                print("{} Worklogged => 1".format(username))

            # IF Work logged for Vacation
            if final_data["worklogged"] == 2:
                print("Worklogged for Vacation => 2")

            date_column_values[x].value = final_data["worklogged"]
            print(
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",
                end="\n\n",
            )

        except Exception as e:
            print(e, "Error in user => ", username)
            print(
                "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",
                end="\n\n",
            )
            
    gsheet.xlsheet_obj.update_cells(date_column_values)

    return {"statusCode": 200}


lambda_handler(None, None)
