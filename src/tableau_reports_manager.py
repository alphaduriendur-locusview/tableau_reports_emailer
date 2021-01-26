import argparse
import os
import json
import tableauserverclient as TSC
import argparse

__version__ = "1.0"
__working_dir__ = os.getcwd()


def load_default_config():
    with open(os.path.join(__working_dir__, 'configs', 'default_config.json')) as f:
        return json.load(f)


def get_parser(version):
    parser = argparse.ArgumentParser(description="This is tableau one stop report manager",
                                     prog='Tableau Reports Manager')
    parser.add_argument('--version', '-v', action='version', version='%(prog)s - {0}'.format(version))
    parser.add_argument('--list', '-l', help='list all workbooks from the server', action='store_true')
    parser.add_argument('--search', '-s', help='search for Tableau workbook of name. <string>', nargs=1)
    parser.add_argument('--query', '-q', nargs=1, help='Prints all Views/Reports in a certain workbook (by ID). '
                                                       'Required Argument: <workbook-id>. Use the '
                                                       '-s/-l option to find the ID of a workbook')
    parser.add_argument('--generateWorkbookConfig', '-gWC', nargs=1, help='generate config for the entire workbook. '
                                                                          'This will create a master config for all '
                                                                          'the views within the workbook. Required '
                                                                          'Argument: <workbook-id>')
    parser.add_argument('--generateViewConfig', '-gVC', nargs=1, help='generate config for a certain view.'
                                                                      'This will create a config for a single view. '
                                                                      'Required Argument: "<workbook-name>". Use -q '
                                                                      'option to query Views/Reports within a Workbook')
    return parser


def _list_workbook(tableau_server, wb):
    print("Processing Workbook: {0}".format(wb.name))
    tableau_server.workbooks.populate_views(wb)
    for view in wb.views:
        print("---------------------------------------")
        print('Report Name: "{}"'.format(view.name))
        print("Report ID: {}".format(view.id))
        print("---------------------------------------")


class TableauObject:
    workbook_ids = None

    def __init__(self, tableau_user, tableau_password, tableau_server):
        self.auth = TSC.TableauAuth(username=tableau_user, password=tableau_password)
        self.server = TSC.Server(tableau_server)
        self.workbook_ids = []
        self.processing_workbook = None
        self.processing_view = None
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

    def search_for_matching_workbook_name(self, search_str):
        with self.server.auth.sign_in(self.auth):
            for wb_id in self.workbook_ids:
                wb = self.server.workbooks.get_by_id(wb_id)
                if search_str.upper() in wb.name.upper():
                    print("Matching Workbook found: {0}".format(wb.name))
                    print(" ->Workbook id: {0}".format(wb_id))

    def query_workbook(self, wb_id):
        print("Querying Workbook with ID: ", wb_id)
        with self.server.auth.sign_in(self.auth):
            wb = self.server.workbooks.get_by_id(wb_id)
            _list_workbook(self.server, wb)

    def process_workbook(self, wb_id):
        print("Attempting to generate config for Workbook ID: {}".format(wb_id))
        with self.server.auth.sign_in(self.auth):
            fetch_workbook = self.server.workbooks.get_by_id(wb_id)
            self.processing_workbook = fetch_workbook
            print("------------------------")
            print("Workbook Name: {}".format(self.processing_workbook.name))
            self.server.workbooks.populate_views(self.processing_workbook)
            print("{0} Views were detected in this workbook".format(len(self.processing_workbook.views)))
            if len(self.processing_workbook.views) > 1:
                while True:
                    inp = input("More than 1 view was detected in this workbook. Press\n -> (Y)es - want to generate "
                                "1 master config OR\n -> (N)o - generate separate configs for each view inside workbook"
                                " OR\n -> (E)xit - to cancel this step\n")
                    if inp.upper() == "Y":
                        print("TODO: Generating Master config for entire workbook")
                        break
                    elif inp.upper() == "N":
                        print("TODO: Generating config for each view inside workbook")
                        break
                    elif inp.upper() == "E":
                        print("Exiting")
                        return
                    else:
                        print("Error: Bad input!")
            print("------------------------")

    def process_view(self, view_name):
        print("Attempting to generate config for View name: {}".format(view_name))
        with self.server.auth.sign_in(self.auth):
            view_req_opt = TSC.RequestOptions()
            view_req_opt.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                               TSC.RequestOptions.Operator.Equals,
                                               view_name))
            self.processing_view, x = self.server.views.get(req_options=view_req_opt)
            print("------------------------")
            print("View Name: {}".format(self.processing_view[0].name))
            print("------------------------")


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
        print("Error in Printing all Workbooks found at the server\n", e)


def search_for_workbook_name(search_str):
    print("Searching at server for workbook names matching:", search_str)
    try:
        tableau_obj = TableauObject(__default_config__['tableau_user'],
                                    __default_config__['tableau_password'],
                                    __default_config__['tableau_server'])
        tableau_obj.set_server_version('3.9')
        tableau_obj.get_all_workbooks()
        tableau_obj.search_for_matching_workbook_name(search_str)
    except Exception as e:
        print("Error in Searching for Workbook name\n", e)


def query_workbook_by_id(workbook_id):
    print("Querying Server for Workbook ID: ", workbook_id)
    try:
        tableau_obj = TableauObject(__default_config__['tableau_user'],
                                    __default_config__['tableau_password'],
                                    __default_config__['tableau_server'])
        tableau_obj.set_server_version('3.9')
        tableau_obj.get_all_workbooks()
        tableau_obj.query_workbook(workbook_id)
    except Exception as e:
        print("Error in Querying for Workbook by ID\n", e)


def generate_workbook_config(workbook_id):
    print("Generating Tableau Export Config for Workbook: {}".format(workbook_id))
    try:
        tableau_obj = TableauObject(__default_config__['tableau_user'],
                                    __default_config__['tableau_password'],
                                    __default_config__['tableau_server'])
        tableau_obj.set_server_version('3.9')
        tableau_obj.process_workbook(workbook_id)
    except Exception as e:
        print("Error in Generating config for Workbook: {}".format(workbook_id), e)


def generate_view_config(view_name):
    print("Generating Tableau Export Config for View: {}".format(view_name))
    try:
        tableau_obj = TableauObject(__default_config__['tableau_user'],
                                    __default_config__['tableau_password'],
                                    __default_config__['tableau_server'])
        tableau_obj.set_server_version('3.9')
        tableau_obj.process_view(view_name)
    except Exception as e:
        print("Error in Generating config for View: {}\n".format(view_name), e)


__parser__ = get_parser(__version__)
__default_config__ = load_default_config()

if __name__ == "__main__":

    args = __parser__.parse_args()
    if args.list:
        list_all_workbooks_on_server()
    if args.search:
        search_for_workbook_name(args.search[0])
    if args.query:
        query_workbook_by_id(args.query[0])
    if args.generateWorkbookConfig:
        generate_workbook_config(args.generateWorkbookConfig[0])
    if args.generateViewConfig:
        generate_view_config(args.generateViewConfig[0])

