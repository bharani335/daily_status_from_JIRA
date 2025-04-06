import os
import smtplib
from email.mime.text import MIMEText

from env import load_env

# Load environment variables
env_vars = load_env()
FROM_MAIL_ADR = env_vars["FROM_MAIL_ADR"]
MAIL_APP_PASSWORD = env_vars["MAIL_APP_PASSWORD"]
SMTP = env_vars["SMTP"]
SMTP_PORT = env_vars["SMTP_PORT"]
SMTP_EMAIL = env_vars["SMTP_EMAIL"]


class Mailsender:
    def __init__(self, username, user_email, date):
        # Create a text/plain message
        self.msg = MIMEText("")
        self.msg["From"] = FROM_MAIL_ADR
        self.username = username
        self.user_email = user_email
        self.date = date

    def remainder_mail(self, warning_msg, reporting_managers, total_worklogged_time=0):
        if warning_msg and not total_worklogged_time:
            self.msg = MIMEText(
                "Hi,\n You Haven't logged time today {}. Please time log and send daily status mail manually or if you are in a vacation kindly time log to the respective vacation ticket".format(
                    self.date
                )
            )
            self.msg["Subject"] = "Warning - No Worklog logged for today " + self.date
            print("Warning mail => ", self.username)
            if len(reporting_managers) > 0:
                self.msg["Cc"] = ",".join(x for x in reporting_managers)

        elif total_worklogged_time < 6 and total_worklogged_time > 0:
            self.msg = MIMEText(
                "Hi,\n Your total worklogged time is {}, which is less than 6 hours. So kindly log your time as soon as possible".format(
                    total_worklogged_time
                )
            )
            self.msg["Subject"] = (
                "Reminder - Worklog logged less than 6hrs " + self.date
            )
            print("Pending time log mail => ", self.username)

        else:
            self.msg = MIMEText(
                "Hi,\n You Haven't logged time for today {}. Please log your time as soon as possible".format(
                    self.date
                )
            )
            self.msg["Subject"] = "Reminder - No worklog logged for today " + self.date
            print("Reminder mail => ", self.username)

        self.msg["To"] = self.user_email

    def status_mail(self, mail_to, mail_cc, soup):
        print("Mail to => ", mail_to)
        print("Mail cc => ", mail_cc)
        self.msg = MIMEText(soup, "html")
        self.msg["To"] = ",".join(x for x in mail_to)
        self.msg["Cc"] = ",".join(x for x in mail_cc)
        self.msg["Bcc"] = self.user_email
        self.msg["Subject"] = (
            self.username + " - " + "Daily Status Report - " + self.date
        )
        # Bharani kumar Sathanantham - Daily Status Report - 11/05/2022
        print("Daily staus mail => ", self.username)

    def send_mail(self):
        s = smtplib.SMTP(SMTP, SMTP_PORT)
        s.ehlo()
        s.starttls()
        s.ehlo()

        # Login using App passwords(Gmail)
        s.login(SMTP_EMAIL, MAIL_APP_PASSWORD)
        s.send_message(self.msg)

        print("Mail Sent for the user => ", self.username)
