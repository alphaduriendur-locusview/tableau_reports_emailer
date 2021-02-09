import argparse
import os
import json
import tableauserverclient as TSC
import argparse
from email_setup import NoticeEmail
from datetime import date


__version__ = "1.0"
__working_dir__ = os.getcwd()
__save_directory__ = os.path.join(__working_dir__,'downloads', date.today().isoformat())
__email_body__ = """<h3>Please find the attached Tableau report.</h3>
                 <br />
                 <br />
                 <p>This is an automated notification. Please do not directly reply to this email.</p>"""



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
    parser.add_argument('--generateViewConfig', '-gVC', nargs=1, help='generate config for a certain view.'
                                                                      'This will create a config for a single view. '
                                                                      'Required Argument: "<workbook-name>". Use -q '
                                                                      'option to query Views/Reports within a Workbook')
    parser.add_argument('--emailList', '-e', nargs='*', help = 'add email list. This is required by the -gWC/-gWV '
                                                               'options')
    parser.add_argument('--runConfig', '-r', nargs=1, help='run tableau reports emailer job. '
                                                           'Required Argument: <config-file> '
                                                           'For Example: USIC-FailedTaskReport.json')
    return parser


def _list_workbook(tableau_server, wb):
    print("Processing Workbook: {0}".format(wb.name))
    tableau_server.workbooks.populate_views(wb)
    for view in wb.views:
        print("---------------------------------------")
        print('Report Name: "{}"'.format(view.name))
        print("Report ID: {}".format(view.id))
        print("---------------------------------------")


def _dump_view_to_config(view, email_list=["arko.basu@locusview.com"]):
    print("Writing Config for view: {}".format(view.name))
    write_dict = {
        "workbook_id": view.workbook_id,
        "views": [{
            "view_id": view.id,
            "view_name": view.name,
        }],
        "to": email_list,
        "body": "<HTML>Please find the attachment below. Do not reply to this message."
                " This is an automated email</HTML>",
        "subject": view.name,
        "test": True
    }
    json_obj = json.dumps(write_dict, indent=4)
    filename = os.path.join(__working_dir__,'configs',view.name.replace(" ","")+".json")
    with open(filename, "w") as f:
        f.write(json_obj)
    print("Config successfully generated at: {}".format(filename))


def _create_output_directory():
    try:
        os.makedirs(__save_directory__, exist_ok=True)
    except OSError as e:
        print("Could not validate download location. Error!\n {}.".format(str(e)))
        raise


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

    def process_view(self, view_name, email_list):
        print("Attempting to generate config for View name: {}".format(view_name))
        with self.server.auth.sign_in(self.auth):
            view_req_opt = TSC.RequestOptions()
            view_req_opt.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                               TSC.RequestOptions.Operator.Equals,
                                               view_name))
            self.processing_view, x = self.server.views.get(req_options=view_req_opt)
            _dump_view_to_config(self.processing_view[0], email_list)

    def download(self,tableau_export_config):
        if len(tableau_export_config['views']) == 1:
            view_id = tableau_export_config['views'][0]['view_id']
            view_name = tableau_export_config['views'][0]['view_name']
            print("------------------------------------------")
            print("Attepting download of View ID: {0}\tView Name: {1}".format(view_id, view_name))
            with self.server.auth.sign_in(self.auth):
                view_req_opt = TSC.RequestOptions()
                view_req_opt.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                                   TSC.RequestOptions.Operator.Equals,
                                                   view_name))
                self.processing_view, x = self.server.views.get(req_options=view_req_opt)
                self.server.views.populate_pdf(self.processing_view[0], self.pdf_req_option)
                download_file = os.path.join(__save_directory__,self.processing_view[0].name + ".pdf")
                with open(download_file, 'wb') as f:
                    f.write(self.processing_view[0].pdf)
                    print("Download successful. File downloaded at: {}".format(download_file))
                email_job = NoticeEmail(msg_subject=tableau_export_config['subject'],
                                        msg_to=tableau_export_config['to'],
                                        msg_filename=self.processing_view[0].name + ".pdf",
                                        msg_attachment=download_file,
                                        msg_content = __email_body__,
                                        key=__default_config__['sendgrid'],
                                        is_test=tableau_export_config['test'])
                email_job.send_mail()
                print("------------------------------------------")


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


def generate_view_config(view_name, email_list):
    print("Generating Tableau Export Config for View: {}".format(view_name))
    try:
        tableau_obj = TableauObject(__default_config__['tableau_user'],
                                    __default_config__['tableau_password'],
                                    __default_config__['tableau_server'])
        tableau_obj.set_server_version('3.9')
        tableau_obj.process_view(view_name,email_list)
    except Exception as e:
        print("Error in Generating config for View: {}\n".format(view_name), e)


def tableau_emailer(config_file):
    config_filepath = os.path.join(__working_dir__, 'configs', config_file)
    print(config_filepath)
    if not os.path.exists(config_filepath):
        print("Error: Couldn't find the config file! Please generate config first! Use -h for help")
        return

    with open(config_filepath, 'r') as tableau_config:
        data = json.load(tableau_config)

    try:
        tableau_obj = TableauObject(__default_config__['tableau_user'],
                                    __default_config__['tableau_password'],
                                    __default_config__['tableau_server'])
        tableau_obj.set_server_version('3.9')
        _create_output_directory()
        tableau_obj.download(data)
    except Exception as e:
        print("Error in running tableau email job for config: {}\n".format(config_file),e)

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
    if args.generateViewConfig:
        if args.emailList:
            print("Email list provided: {}".format(args.emailList))
            generate_view_config(args.generateViewConfig[0],args.emailList)
        else:
            __parser__.error("Email list was not provided. Please enter a default email address and try again!")
    if args.runConfig:
        tableau_emailer(args.runConfig[0])
