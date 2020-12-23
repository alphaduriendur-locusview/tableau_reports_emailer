import os
from datetime import date
import tableauserverclient as TSC
from tableau_config import tableau_user,\
    tableau_passwd, tableau_server, tableau_server_workbook_id

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
    try:
        server.workbooks.populate_views(workbook)
        print("\nThe views for {0}".format(workbook.name))
        for view in workbook.views:
            print("Report Name: {}".format(view.name))
            print("Report ID: {}".format(view.id))
            server.views.populate_pdf(view, pdf_req_option)
            download_file = os.path.join(save_directory,view.name+".pdf")
            print("Downloading at: {}".format(download_file))
            with open(download_file,'wb') as f:
                f.write(view.pdf)
                print("Download Successfull!")
    except Exception as e:
        print("Failure in downloading workbook!\nError: \n{}".format(str(e)))


def tableau_export():

    try:
        with server.auth.sign_in(tableau_auth):
            wb = server.workbooks.get_by_id(tableau_server_workbook_id)
            print("Workbook found!")
            print("Workbook ID: {}".format(tableau_server_workbook_id))
            download_and_send(wb)
    except Exception as e:
        print("Could not get Exelon Failed task report workbook!\nError: \n{}".format(str(e)))

if __name__ == "__main__":
    tableau_export()

