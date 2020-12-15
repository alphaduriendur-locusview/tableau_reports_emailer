import tableauserverclient as TSC
from tableau_config import tableau_user, tableau_passwd, tableau_server_site, tableau_server, tableau_server_target

tableau_auth = TSC.TableauAuth(tableau_user, tableau_passwd, tableau_server_site)
server = TSC.Server(tableau_server)

def tableau_export():

    try:
        with server.auth.sign_in(tableau_auth):
            all_project_items, pagination_item = server.projects.get()
            for proj in all_project_items:
                if tableau_server_target in proj.name:
                    print("Target Found!")
    except Exception as e:
        print("Authentication failed. Error Details: {}".format(str(e)))

if __name__ == "__main__":
    tableau_export()

