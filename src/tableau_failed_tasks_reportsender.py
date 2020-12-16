import tableauserverclient as TSC
from tableau_config import tableau_user,\
    tableau_passwd, tableau_server_site,\
    tableau_server, tableau_server_workbook,\
    tableau_server_workbook_id

tableau_auth = TSC.TableauAuth(tableau_user, tableau_passwd, tableau_server_site)
server = TSC.Server(tableau_server)

def tableau_export():

    try:
        with server.auth.sign_in(tableau_auth):
            wb = server.workbooks.get_by_id(tableau_server_workbook_id)
            print("Workbook found!")
            
            server.workbooks.populate_views(wb)
            print("\nThe views for {0}".format(wb.name))
            print([view.name for view in wb.views])
    except Exception as e:
        print("Could not get Exelon Failed task report workbook!\nError: \n{}".format(str(e)))

if __name__ == "__main__":
    tableau_export()

