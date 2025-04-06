from copy import copy
from bs4 import BeautifulSoup

class HTMLFrame:
    def __init__(self):
        self.data_format = """<!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Title</title>
                </head>
                <body>
                <h4 class="date_for_mail"></h4>
                <table cellspacing="0" cellpadding="0" dir="ltr" border="1" style="table-layout:fixed;font-size:10pt;font-family:Arial;width:0px;border-collapse:collapse;border:none">
                    <colgroup>
                        <col width="40">
                        <col width="157">
                        <col width="100">
                        <col width="300">
                    </colgroup>
                    <tbody>
                    <tr style="font-size:13px;height:75px">
                        <td style="border:1px solid rgb(0,0,0);overflow:hidden;padding:2px 3px;vertical-align:center;background-color:rgb(255,153,0);font-weight:bold">S.No</td>
                        <td style="border-width:1px;border-style:solid;border-color:rgb(0,0,0) rgb(0,0,0) rgb(0,0,0) rgb(204,204,204);overflow:hidden;padding:2px 3px;vertical-align:center;background-color:rgb(255,153,0);font-weight:bold">Sprint</td>
                        <td style="border-width:1px;border-style:solid;border-color:rgb(0,0,0) rgb(0,0,0) rgb(0,0,0) rgb(204,204,204);overflow:hidden;padding:2px 3px;vertical-align:center;background-color:rgb(255,153,0);font-weight:bold">Jira No</td>
                        <td style="border-width:1px;border-style:solid;border-color:rgb(0,0,0) rgb(0,0,0) rgb(0,0,0) rgb(204,204,204);overflow:hidden;padding:2px 3px;vertical-align:center;background-color:rgb(255,153,0);font-weight:bold">Task Status</td>
                        </tr>
                    <tr class ="lastline" style="font-size:13px;height:62px"></tr>
                    </tbody>
                </table>
                </body>
                </html>"""

        self.data = """<tr class = 'data_row' style="font-size:13px;height:54px">
                        <td class ="s.no" style="border-width:1px;border-style:solid;border-color:rgb(204,204,204) rgb(0,0,0) rgb(0,0,0);overflow:hidden;padding:2px 3px;vertical-align:center"></td>
                        <td class ="sprint" style="border-width:1px;border-style:solid;border-color:rgb(204,204,204) rgb(0,0,0) rgb(0,0,0) rgb(204,204,204);overflow:hidden;padding:2px 3px;vertical-align:center"></td>
                        <td class ="ticket" style="border-width:1px;border-style:solid;border-color:rgb(204,204,204) rgb(0,0,0) rgb(0,0,0) rgb(204,204,204);overflow:hidden;padding:2px 3px;vertical-align:center"><div></div></td>
                        <td class ="content" style="border-width:1px;border-style:solid;border-color:rgb(204,204,204) rgb(0,0,0) rgb(0,0,0) rgb(204,204,204);overflow:hidden;padding:2px 3px;vertical-align:center">
                            <ul class ="content_list" style=“list-style-type:square” style="margin-left: 0;padding-left: 10px">
                            </ul>
                            </td>
                        </tr>"""

    def setdata(self, date, data_list, user_name):
        soup = BeautifulSoup(self.data_format, 'html.parser')
        soup.find('h4', class_="date_for_mail").string = "Hi team,\nPlease find {} daily status report for {}.".format(user_name, date)
        inc = 1
        for i in data_list:
            data = BeautifulSoup(self.data, 'html.parser')
            s_no = data.find('td', class_="s.no")
            s_no.string = str(inc)
            inc += 1

            sprint = data.find('td', class_="sprint")
            sprint.string = i[0]

            ticket = data.find('td', class_="ticket")
            ticket.string = i[1]

            content = data.find('td', class_="content")
            print("i[2]", i[2])
            for x in i[2]:
                original_tag = data.find('ul', class_='content_list')
                new_tag = data.new_tag("li")
                original_tag.append(new_tag)
                new_tag.string = x

            soup.find('tr', class_="lastline").insert_before(copy(data))

        return soup