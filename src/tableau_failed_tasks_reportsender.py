import os
from datetime import date
import json
import tableauserverclient as TSC
from tableau_config import tableau_user,\
    tableau_passwd, tableau_server, tableau_server_workbook_id
from email_setup import NoticeEmail

tableau_auth = TSC.TableauAuth(tableau_user, tableau_passwd, '')
server = TSC.Server(tableau_server)
print("Tableau server: {}".format(tableau_server))
server.version = '3.9'
print("Server version: {}".format(server.version))
current_date=date.today()
print("Today's date: ", current_date)
save_directory = os.path.join(os.getcwd(),"download",current_date.isoformat())
pdf_req_option = TSC.PDFRequestOptions(page_type=TSC.PDFRequestOptions.PageType.A4,
                                       orientation=TSC.PDFRequestOptions.Orientation.Landscape,
                                       maxage=1)
email_body = """<h3>Please find the weekly failed task report attached.</h3>
            <br />
            <br />
            <p>This is an automated notification. Please do not directly reply to this email.</p>"""


def read_list():
    with open('email_list.json') as f:
        data = json.load(f)
    return data


def create_email_obj(data):
    email_list2 = {}
    for k, v in data.items():
        report_name = str(k) +  " - Failed Task Report"
        temp_obj = {
            "report": report_name,
            "emails": v,
            "filepath": os.path.join(save_directory, report_name+".pdf"),
            "filename": report_name+".pdf"
        }
        if report_name not in email_list2:
            email_list2[report_name] = temp_obj

    return email_list2


def create_out_dir():
    try:
        print("Validating save location:{0}".format(save_directory))
        os.makedirs(save_directory, exist_ok=True)
    except OSError as e:
        print("Could not validate save location. Error!\n {}.".format(str(e)))
        raise


def download_and_send(workbook):
    if not workbook:
        print("No workbook found!")
        return

    create_out_dir()
    emails = create_email_obj(read_list())

    try:
        server.workbooks.populate_views(workbook)
        print("\nThe views for {0}\n".format(workbook.name))
        for view in workbook.views:
            print("-------------------------------------------------------------")
            print("Report Name: {}".format(view.name))
            server.views.populate_pdf(view, pdf_req_option)
            download_file = os.path.join(save_directory,view.name+".pdf")
            print("Downloading at: {}".format(download_file))
            with open(download_file,'wb') as f:
                f.write(view.pdf)
                print("Download Successfull!\n")
                if view.name in emails:
                    print("Attempting to send it as an email.")
                    weekly_email = NoticeEmail(msg_subject="Weekly Failed Task Report",
                                             msg_to=emails[view.name]['emails'],
                                             msg_filename=emails[view.name]['filename'],
                                             msg_attachment=emails[view.name]['filepath'],
                                             msg_content=email_body)
                    weekly_email.send_mail()
            print("-------------------------------------------------------------")
    except Exception as e:
        print("Failure in downloading and sending workbook!\nError: \n")
        print(e)


def tableau_export():

    try:
        with server.auth.sign_in(tableau_auth):
            wb = server.workbooks.get_by_id(tableau_server_workbook_id)
            print("Workbook found!")
            download_and_send(wb)
    except Exception as e:
        print("Could not get Exelon Failed task report workbook!\nError: \n{}".format(str(e)))

if __name__ == "__main__":
    tableau_export()

