import tableauserverclient as TSC

tableau_user = 'tabadmin'
tableau_passwd = 'locus123View'
tableau_server_site = ''
tableau_server = 'https://rca.locusview.com/'
tableau_auth = TSC.TableauAuth(tableau_user, tableau_passwd, tableau_server_site)
server = TSC.Server(tableau_server)

try:
    with server.auth.sign_in(tableau_auth):
        all_project_items, pagination_item = server.projects.get()
        for proj in all_project_items:
            if "Exelon" in proj.name:
                print(proj.name)
except Exception as e:
    print("Authentication failed. Error Details: {}".format(str(e)))

