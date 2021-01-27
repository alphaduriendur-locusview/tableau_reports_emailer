# Tableau Reports Tool

This tool is to extract/download and send Tableau reports (by Views) from the TOOLS Server located on 173.31.0.2
<br>
This tool can be used for listing(all accessible workbooks), searching (using a string keyword), querying (all views in a workbook), generating a config for this tool to perform 
## Usage
`Tableau Reports Manager [-h] [--version] [--list] [--search SEARCH]
                               [--query QUERY]
                               [--generateViewConfig GENERATEVIEWCONFIG]
                               [--emailList [EMAILLIST [EMAILLIST ...]]]
                               [--runConfig RUNCONFIG]`

The overall usage of the script can be categorized as:
1. ___Listing:___ List all workbooks accessbile on the server<br>For example: `python tableau_reports_manager.py -l`
1. ___Searching:___ Search for Tableau workbook on the server with name that matches <string><br>For example: `python tableau_reports_manager.py -s NJNG`
1. ___Querying:___ Prints all Views/Reports in a certain workbook (by ID). Required Argument: <workbook-id>. Use the -s/-l option to find the ID of a workbook.<br>For example: `python tableau_reports_manager.py -q 7c68542d-83e7-42c1-b4fb-6972d7b7e1e3`
1. ___Generating Configs for Views:___ This generates the config that the script uses with a separate argument to download a certain view and email them to a list of emails provided. Required Argument: "<workbook-name>". Note that the double quote is mandatory. Simply copy the filename exactly how it appears when you run the -q (query) option.<br>_Extra Note:_ This argument required an additional argument which specifies the list of emails that this view is to be sent to.<br>For example: `python tableau_reports_manager.py -gVC "Gray Inspections" -e arko.basu@locusview.com andrew.dunham@locusview.com`
1. ___Run a config:___ This runs a previously generated config. Running the config causes download of the view and then is send to the list of email ids provided in the config. Required Argument: <config-filename>. Note: Only the file name. No path necessary. For the filename refer to the previous step where the config is generated<br>For example: `python tableau_reports_manager.py -r GrayInspections.json`

## Modifying Configs manually
Please note that the tool was to create the configs automatically. Please only change the "to" tag inside the config to alter the email list.

