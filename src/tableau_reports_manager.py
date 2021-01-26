import argparse
import os
import json
import tableauserverclient as TSC
import argparse

__version__ = "1.0"
__working_dir__ = os.getcwd()


def load_default_config():
    with open(os.path.join(__working_dir__,'configs','default_config.json')) as f:
        return json.load(f)


def get_parser(version):
    parser = argparse.ArgumentParser(description="This is tableau one stop report manager",
                                     prog='Tableau Reports Manager')
    parser.add_argument('--version', '-v', action='version', version='%(prog)s - {0}'.format(version))
    parser.add_argument('--list', '-l', help='list all workbooks from the server', action='store_true')
    return parser


class TableauObject:
    workbook_ids = None

    def __init__(self,tableau_user, tableau_password, tableau_server):
        self.auth = TSC.TableauAuth(username=tableau_user, password=tableau_password)
        self.server = TSC.Server(tableau_server)
        self.__setdefaults__()

    def __setdefaults__(self):
        #print("Setting Defaults")
        self.workbook_ids = []
        self.pdf_req_option = TSC.PDFRequestOptions(page_type=TSC.PDFRequestOptions.PageType.A4,
                                               orientation=TSC.PDFRequestOptions.Orientation.Landscape,
                                               maxage=1)

    def get_server_version(self):
        return self.server.version

    def set_server_version(self, version):
        print("Setting Server Version: {0}".format(version))
        self.server.version = version


    def get_all_workbooks(self):
        with self.server.auth.sign_in(self.auth):
            for wb in TSC.Pager(self.server.workbooks):
                self.workbook_ids.append(wb.id)

    def print_all_workbooks(self):
        with self.server.auth.sign_in(self.auth):
            for wb_id in self.workbook_ids:
                wb = self.server.workbooks.get_by_id(wb_id)
                print("# Workbook id: {0}".format(wb_id))
                print("# Workbook name: {0}".format(wb.name))


def list_all_workbooks_on_server():
    print("Listing all workbooks on the server")
    try:
        tableau_obj = TableauObject(__default_config__['tableau_user'],
                                    __default_config__['tableau_password'],
                                    __default_config__['tableau_server'])
        tableau_obj.set_server_version('3.9')
        tableau_obj.get_all_workbooks()
        tableau_obj.print_all_workbooks()
    except Exception as e:
        print("Error", e)


__parser__ = get_parser(__version__)
__default_config__ = load_default_config()

if __name__ == "__main__":

    args = __parser__.parse_args()
    if args.list:
        list_all_workbooks_on_server()


