import tableauserverclient as TSC
from tableau_config import tableau_user,\
    tableau_passwd, tableau_server, tableau_server_workbook_id

tableau_auth = TSC.TableauAuth(tableau_user, tableau_passwd, '')
server = TSC.Server(tableau_server)

def download_and_send(workbook):
    if not workbook:
        print("No workbook found!")
        return
    try:
        server.workbooks.populate_views(workbook)
        print("\nThe views for {0}".format(workbook.name))
        print([view.name for view in workbook.views])
    except Exception as e:
        print("Failure in downloading workbook!\nError: \n{}".format(str(e)))


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

