# Importing the modules we'll need
import json
from jira import JIRA

import requests
from requests.auth import HTTPBasicAuth

# Local Import
from htmlformatter import HTMLFrame


class JiraIntegration:
    def __init__(self, server, email, api_token, date_format_for_mail):
        self.server = server
        self.email = email
        self.api_token = api_token
        self.date_format_for_mail = date_format_for_mail
        self.auth = None
        self.jira = None
        self.authenticate()

    def authenticate(self):
        self.auth = HTTPBasicAuth(self.email, self.api_token)
        self.jira = JIRA(
            options={"server": self.server}, basic_auth=(self.email, self.api_token)
        )

    # Func for looping through the comment contents
    def call_until_type_is_text(self, content, temp):
        if content["type"] == "text":
            return content["text"]
        if content["type"] == "inlineCard":
            temp2 = []
            for y in content["attrs"].values():
                temp2.append(y)
            temp2 = "".join(y for y in temp2)
            return temp2
        else:
            if "content" in content:
                if content["type"] == "paragraph":
                    temp1 = []
                    for i in content["content"]:
                        data = self.call_until_type_is_text(i, temp)
                        if data:
                            temp1.append(data + "\n")
                    temp.extend(temp1)

                else:
                    for i in content["content"]:
                        self.call_until_type_is_text(i, temp)
            else:
                return None

    def user(self, username, user_email, lead, date_for_jql):
        data_dict = {
            "total_worklogged_time": 0,
            "mail": None,
            "soup": None,
        }  # JQL Query to a project, author(user), worklog date
        jql = 'worklogAuthor="{}" AND worklogDate = {}'.format(username, date_for_jql)

        # Search for issues using above JQL
        jira_issues = self.jira.search_issues(jql)

        print("Worklogged tickets = > ", jira_issues)
        data_list = []
        time_spent = []
        total_worklogged_time = 0

        # Loop through the issues that are logged today and get the last worklog comment and sprint name
        for x in jira_issues:
            data_list1 = []
            issue_id_or_key = x.id
            url = "{server}/rest/api/3/issue/{issueIdOrKey}/worklog".format(
                self.server, issueIdOrKey=issue_id_or_key
            )
            url1 = "{server}/rest/api/3/issue/{issueIdOrKey}".format(
                self.server, issueIdOrKey=issue_id_or_key
            )
            headers = {"Accept": "application/json"}

            # Getting worklogs
            response = requests.request("GET", url, headers=headers, auth=self.auth)
            worklog = json.loads(response.text)
            print("Response for worklog request => ", response.status_code)

            # Getting Sprint Name
            response1 = requests.request("GET", url1, headers=headers, auth=self.auth)

            for_sprint_name = json.loads(response1.text)
            print("Response for Sprint name request => ", response1.status_code)

            # worklogs(list of worklogs in that ticket) -> [-1](last log) -> comment -> content(list of comments on a day) -> text
            user_flag_for_worklog = 0
            user_flag_for_comment = 0

            comments = []
            for i in worklog["worklogs"][::-1]:
                author = i["author"]["displayName"]
                if username.lower()[:-5] in author.lower():
                    user_flag_for_worklog = 0
                    if i["started"][:10] == date_for_jql:
                        print("Worklog Author matched ", username[:-5], author.lower())
                        time_spent.append(i["timeSpentSeconds"])
                        if "comment" in i:
                            comments.append(i["comment"])
                            print("Got an comment on this current ticket {}".format(x))
                            user_flag_for_comment = 1
                        else:
                            user_flag_for_comment = 0
                            print("No comment on this current ticket {}".format(x))
                    else:
                        continue
                else:
                    if user_flag_for_worklog == 0:
                        continue
                    user_flag_for_worklog = 1

            # If the current user has no worklog comment is this ticket. Continue with next ticket
            if user_flag_for_worklog:
                print(
                    "No worklog for the user {} in this current ticket {}".format(
                        user_email, x
                    )
                )
                continue

            # Checking for Holiday or vacation
            vacation = for_sprint_name["fields"]["summary"].lower()
            if (
                "leave" in vacation
                or "holiday" in vacation
                or "vacation" in vacation
                or "time off" in vacation
            ):
                print("User is on vacation")
                if len(jira_issues) == 1:
                    print("Vacation ticket only")
                    data_dict["worklogged"] = 2
                    return data_dict

            sprint_custom_field = for_sprint_name["fields"]
            if (
                "customfield_10007" in sprint_custom_field
                and sprint_custom_field["customfield_10007"]
            ):
                temp = 1
                for items in sprint_custom_field["customfield_10007"]:
                    if temp == 1:
                        data_list1.append(items["name"])
                    temp += 1
            else:
                print("Can't find Sprint Custom field this current ticket {}".format(x))
                print("Hence adding default name N/A ", data_list1)
                data_list1.append("N/A")
            print("Sprint name => ", data_list1[0])

            # ticket
            data_list1.append(x.key)
            print("Adding Ticket => ", data_list1[-1])

            # Loop through the contents to get worklogs
            # Comment(dict) => content(list) => each item is a dict => content(list) => each item is a dict => pattern continues until ["type"]=="text"
            temp = []
            if user_flag_for_comment:
                for comment in comments:
                    if comment["type"] == "text":
                        temp.append(comment["text"])

                    if comment["type"] == "inlineCard":
                        for y in comment["attrs"].values():
                            temp.append(y)

                    else:
                        if "content" in comment:
                            for i in comment["content"]:
                                self.call_until_type_is_text(i, temp)
                    print("temp before editing => ", temp)
                    temp = [
                        i.strip("\n. ")
                        for i in temp
                        if i.strip(").\n ") and i.strip(". ")
                    ]
                    print("temp After editing => ", temp)
                data_list1.append(temp)

            else:
                data_list1.append(["N/A"])

            print("Comment Added => ", data_list1[-1])

            data_list.append(data_list1)

            print("---------------------------------------------------------")
            print(data_list1[0], data_list1[1], data_list1[2], sep="  ")
            print("---------------------------------------------------------")

        # Total worklog seconds
        for time_ in time_spent:
            total_worklogged_time += time_

        # Total worklog Hours
        total_worklogged_time = total_worklogged_time / (60 * 60)
        print("Total Worklogged Hours : ", total_worklogged_time)

        data_dict["total_worklogged_time"] = total_worklogged_time

        # If worklogged is less than 6 hours
        if len(data_list) > 0 and total_worklogged_time < 6:
            data_dict["worklogged"] = -1
            return data_dict

        # IF Not Work logged
        if not data_list:
            data_dict["worklogged"] = 0
            return data_dict

        # IF Work logged
        else:
            if not lead:
                soup = HTMLFrame().setdata(
                    self.date_format_for_mail, data_list, username
                )
                data_dict["soup"] = soup
            data_dict["worklogged"] = 1
            return data_dict
