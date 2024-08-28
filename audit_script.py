'''This script runs an audit on the Selenium Grid to determine whether or not
it is in adequate physical condition to operate properly.'''

import sys
import pysftp

# This dictionary stores the ip_addr addresses of each grid's hub and all nodes
# contained in it, used for easy iteration through all hubs and each of their
# nodes.
# ALL_GRIDS = {
#     '141.137.235.222' : {
#         'grid222Nodes' : [
#             "141.137.235.215",
#             "141.137.235.243",
#             "141.137.235.248",
#             "141.137.235.186"
#         ],
#         'grid222SikuliNodes' : [
#             "141.137.235.216",
#             "141.137.235.187"]
#     },
#     '141.137.235.254' : {
#         'grid254Nodes' : [
#             "141.137.235.207",
#             "141.137.235.181",
#             "141.137.235.208",
#             "141.137.235.184"
#         ],
#         'grid254SikuliNodes' : [
#             "141.137.235.141",
#             "141.137.235.172"
#         ]
#     },
#     '141.137.235.185' : {
#         'grid185Nodes' : [
#             "141.137.235.213",
#             "141.137.235.218",
#             "141.137.235.197",
#             "141.137.235.247"
#         ]
#     },
#     '141.137.235.191' : {
#         'grid191Nodes' : [
#             "141.137.235.193"
#         ],
#         'grid191SikuliNodes' : [
#             "141.137.235.192"
#         ]
#     },
#     '141.137.235.173' : {
#         'grid173Nodes' : [
#             "141.137.235.174",
#             "141.137.235.137",
#             "141.137.235.149",
#             "141.137.235.148"
#         ],
#         'grid173SikuliNodes' : [
#             "141.137.235.189",
#             "141.137.235.165"
#         ]
#     },
#     '141.137.235.136' : {
#         'grid136Nodes' : [
#             "141.137.235.142",
#             "141.137.235.168",
#             "141.137.235.169",
#             "141.137.235.166"
#         ],
#         'grid136SikuliNodes' : [
#             "141.137.235.164",
#             "141.137.235.162"
#         ]
#     }
# }

# Below are all of the constant values used in the test cases, values need only
# be changed/updated here.
MY_USERNAME = 'root'
MY_PASSWORD = 'shroot'
CNOPTS = pysftp.CnOpts()
CNOPTS.hostkeys = None
RECOMMENDED_SELENIUM_VERSION = 'selenium-server-standalone-2.53.0.jar'
#MAX_NUMBER_DAYS_UPTIME = 14
HUB_RAM_MIN_VALUE = 6
HUB_CPU_MIN_VALUE = 5.9
# NODE_RAM_MIN_VALUE = 2.3
# NODE_CPU_MIN_VALUE = 3.9
# S_NODE_RAM_MIN_VALUE = 1.4
# S_NODE_CPU_MIN_VALUE = 1.9
# FIREFOX_VERSION = '45.8.0esr'
# CHROME_VERSION = '57.0'
# Leaving space and comma below that should be included in the output string to
# ensure it's actually just 1 that's present and not 11 or 21.
# NUM_S_FIREFOX_INSTANCES = ' 1,'
# NUM_NS_FIREFOX_INSTANCES = ' 5,'
# NUM_NODE_CHROME_INSTANCES = ' 5,'
PASSED_STR = ' - PASSED'
FAILED_STR = ' - FAILED'

# If errors occur, the ip_addr addresses at which they occur are stored in the
# dedicated lists for each error type, which are all a part of a master error
# dictionary for convenient error checking at the end of the audit.
CONNECTION_ERRORS = []
RAM_ERRORS = []
CPU_ERRORS = []
UPTIME_ERRORS = []
SELENIUM_VERSION_ERRORS = []
SELENIUM_SERVICE_ERRORS = []
FIREFOX_VERSION_ERRORS = []
CHROME_VERSION_ERRORS = []
NUM_NODES_ERRORS = []
FIREFOX_INSTANCES_ERRORS = []
CHROME_INSTANCES_ERRORS = []
BROWSER_INSTANCE_CREATION_FAILURES = []
ROOT_DIRECTORY_ERRORS = []
TOTAL_ERRORS_STORAGE = {
    'Hubs/Nodes that are not powered on/pingable' : CONNECTION_ERRORS,
    'Hubs/Nodes with incorrect RAM' : RAM_ERRORS,
    'Hubs/Nodes with incorrect CPU' : CPU_ERRORS,
    'Uptime > 14 days' : UPTIME_ERRORS,
    'Incorrect version of Selenium' : SELENIUM_VERSION_ERRORS,
    'Selenium service not running properly' : SELENIUM_SERVICE_ERRORS,
    'Incorrect version of Firefox' : FIREFOX_VERSION_ERRORS,
    'Incorrect version of Chrome' : CHROME_VERSION_ERRORS,
    'Incorrect required number of nodes' : NUM_NODES_ERRORS,
    'Incorrect number of Firefox instances' : FIREFOX_INSTANCES_ERRORS,
    'Incorrect number of Chrome instances' : CHROME_INSTANCES_ERRORS,
    'Failed to create browser instance' : BROWSER_INSTANCE_CREATION_FAILURES,
    'Root directory > 75% full' : ROOT_DIRECTORY_ERRORS
}


def test_failed(error_array, ip_addr):
    '''This function is used to avoid code repetition upon each test failure.'''
    print FAILED_STR
    error_array.append(ip_addr)


def check_if_string_in_output(what_to_find, where_to_look, error_array, ip_addr):
    '''This function also avoids code repetition, as many functions use the same end
    test (if this string is present in output, test has passed).'''
    if what_to_find in where_to_look:
        print PASSED_STR
    else:
        test_failed(error_array, ip_addr)


def check_connection(ip_addr):
    '''This method creates a server object using the constant credentials, and
    attempts to use this server object to execute a simple command (to test if
    a successful connection has been made).'''
    connection = ''
    try:
        srv = pysftp.Connection(ip_addr, username=MY_USERNAME, password=MY_PASSWORD, cnopts=CNOPTS)
        srv.execute('ls')
        connection = 'success'
        print PASSED_STR
    except:
        srv = None
        connection = 'failure'
    srv_and_connection_status = [connection, srv]
    # To avoid having to connect to the server at the start of every function,
    # the same server object is instead passed back into all functions (that
    # require a server connection) as the variable 'srv'.
    return srv_and_connection_status


def check_storage(ip_addr, srv, min_value, error_array, what_to_look_for):
    '''Gets the CPU/RAM values from the server and compares them to the
    recommended values (defined as constants at the top of the script).'''
    print 'Checking ' + what_to_look_for + ' ...  '
    if what_to_look_for == 'RAM':
        units = 'GB'
        storage_string = str(srv.execute('cat /proc/meminfo | grep MemFree'))
        storage_vals = [float(s) for s in storage_string.split() if s.isdigit()]
        storage = float(round((storage_vals[0] / 1000000), 1))
    else:
        units = 'CPU'
        storage_string = str(srv.execute('nproc'))
        storage = float(filter(str.isdigit, storage_string))
    print 'Expected: >' + str(min_value) + units + ',    Result: ' + str(storage) + units,
    # Not all RAM/CPU values are exactly the required value, and to allow a
    # small region for error (-0.1), minimum values are used (as the constants
    # defined at the top of the scrip_addrt) instead of exact values.
    if not storage >  min_value:
        test_failed(error_array, ip_addr)
    else:
        print PASSED_STR


def check_uptime(ip_addr, srv):
    '''Retrieved the uptime of the hub/node using the "uptime" command, and
    compares the output to the desired max. number of days uptime (14).'''
    print 'Checking uptime ...  '
    uptime_str = str(srv.execute('uptime'))
    # Below check counteracts possible errors due to '27 min' or '16 hours' being
    # mis-interpreted as 27 or 16 days (rounds mins/hrs up to 1 day).
    if 'days' in uptime_str:
        # Look for the end of the word 'up' and start from there, ending when a
        # ' ' is encountered (i.e. number has all been contained in the sliced
        # string).
        end_index = uptime_str.index('p') + 2
        while end_index != (len(uptime_str) + 1):
            if uptime_str[end_index + 1] != ' ':
                end_index += 1
            else:
                break
        uptime_str = uptime_str[(uptime_str.index('p') + 2):(end_index + 1)]
        uptime_value = int(filter(str.isdigit, uptime_str))
    else:
        uptime_value = 1
    print 'Expected: <' + str(MAX_NUMBER_DAYS_UPTIME) + ' days,',
    print '    Result: ' + str(uptime_value) + ' days',
    if uptime_value > MAX_NUMBER_DAYS_UPTIME:
        test_failed(UPTIME_ERRORS, ip_addr)
    else:
        print PASSED_STR


# def check_selenium_version(srv, ip_addr, ip_type):
#     '''Checks that Selenium version (retrieved from server) is the recommended one.'''
#     print 'Checking selenium version ...  '
#     execute_str = 'cat start-selenium-' + ip_type + '.sh | grep selenium-server-standalone'
#     output = str(srv.execute(execute_str))
#     # Find / and start slicing from there (selenium version follows this).
#     # Slice off the last 5 characters also purely for presentation
#     # (they are "  ]').
#     output = output[(output.index("/") + 1):-5]
#     print 'Expected: ' + RECOMMENDED_SELENIUM_VERSION + ',    Result: ' + output,
#     error_array = SELENIUM_VERSION_ERRORS
#     check_if_string_in_output(RECOMMENDED_SELENIUM_VERSION, output, error_array, ip_addr)


def is_selenium_service_running(ip_addr, command, msg):
    '''Checks that the selenium service is running OK.'''
    print 'Checking that selenium service is running ...\n',
    # For only this test to be run, user must be 'root' rather than 'seluser'
    # so a different connection object is used.
    connection = pysftp.Connection(ip_addr, username='root', password=MY_PASSWORD, cnopts=CNOPTS)
    hub_output_str = str(int(connection.execute("ps -efl " + " | grep " + command + " | grep hub.json | wc -l")[0].rstrip()) - 1)
    node_output_str = str(int(connection.execute("ps -efl " + " | grep " + command + " | grep node-1.json | wc -l")[0].rstrip()) - 1)
    hub_expected_output = str(int(connection.execute("docker ps -a | grep hub | wc -l")[0].rstrip()))
    node_expected_output = str(int(connection.execute("docker ps -a | grep node | wc -l")[0].rstrip()))
    print msg,
    error_array = SELENIUM_SERVICE_ERRORS
    print "Checking Hub Service status: Expected output : " + hub_expected_output + " Actual Output: " + hub_output_str
    check_if_string_in_output(str(hub_expected_output), hub_output_str, error_array, ip_addr)
    print "Checking Node(s) Service status: Expected output : " + node_expected_output + " Actual Output: " + node_output_str
    check_if_string_in_output(node_expected_output, node_output_str, error_array, ip_addr)



def check_selenium_service_running(ip_addr, ip_type):
    '''Applies appropriate parameters to the "is_selenium_service_running"
    method based on the IP type (hub, non-sikuli node or sikuli node).'''
    is_selenium_service_running(ip_addr, RECOMMENDED_SELENIUM_VERSION, '')


# def check_create_instance_failures(srv, ip_addr):
#     '''Checks logs to ensure that no browser instance creation failures occurred.'''
#     print 'Checking that no browser instance creation failures are present in logs ... ',
#     srv.execute('cd selenium')
#     output = str(srv.execute("cat selenium.log | grep 'failed to create browser instance'"))
#     if 'failed to create browser instance' in output:
#         # If output contains the string we're looking for, then the grep command
#         # returned that message and it is present in the log.
#         test_failed(BROWSER_INSTANCE_CREATION_FAILURES, ip_addr)
#     else:
#         print PASSED_STR


def check_root_directory(srv, ip_addr):
    '''Checks that the root directory isn't >75% full.'''
    print "Checking root directory's used storage value ...  "
    used_storage_str = str(srv.execute('df -hk | grep root'))
    index = used_storage_str.index("%")
    # Starting at the % sign, step backwards until a space (' ') is found,
    # where the number starts. This is done to allow for floating point
    # percentage values (or anything greater than two-digit integer percentage
    # values).
    while index != 0:
        if used_storage_str[index - 1] != ' ':
            index -= 1
        else:
            break
    # Slicing string and casting to an int rather than extracting all numbers
    # from string, as various other numeric values are also present in the
    # string so we would be unable to isolate the '% storage used' value.
    used_storage_str = used_storage_str[index:used_storage_str.index("%")]
    used_storage_value = int(filter(str.isdigit, used_storage_str))
    print 'Expected: <75% full,    Result: ' + str(used_storage_value) + '% full',
    if used_storage_value > 75:
        test_failed(ROOT_DIRECTORY_ERRORS, ip_addr)
    else:
        print PASSED_STR

#
# def get_lines_of_json_file(file_name, what_to_look_for, srv):
#     '''This function is used to avoid repetition, as many different methods search
#     the same file for different things.'''
#     return srv.execute('cat ' + file_name + ' | grep ' + what_to_look_for)


def check_browser(what_to_check, ip_addr, error_array, file_name, what_to_compare_to):
    '''Again, avoiding repetition as many of the below methods have very similar
    functionality and only require different parameters.'''
    if what_to_compare_to == CHROME_VERSION:
        index = 1
    else:
        index = 0
    # Need to make new srv object here as function can't have any more arguments
    # if it is to be optimal.
    srv = pysftp.Connection(ip_addr, username=MY_USERNAME, password=MY_PASSWORD, cnopts=CNOPTS)
    output = get_lines_of_json_file(file_name, what_to_check, srv)
    if len(output) < (index + 1):
        print 'FAILED, cannot retrieve ' + what_to_check
        error_array.append(ip_addr)
    else:
        # Index variable is used to determine which line of the output should
        # hold the desired value, e.g. for checking chrome/firefox version of
        # non-sikuli nodes the output will have the firefox version on line 0
        # and chrome version on line 1.
        output_str = str(output[index])
        print 'Expected: ' + what_to_compare_to + ',    Result: ',
        print output_str[(output_str.index(':') + 2):output_str.index(',')],
        check_if_string_in_output(what_to_compare_to, output_str, error_array, ip_addr)


# def check_firefox_version(file_name, ip_addr):
#     '''Calls 'check_browser' method with the appropriate parameters for
#     checking the Firefox version.'''
#     check_browser('version', ip_addr, FIREFOX_VERSION_ERRORS, file_name, FIREFOX_VERSION)
#     # Firefox version is located on a higher line than Chrome, so will be
#     # outputted first (at index 0 of the output object).
#
#
# def check_chrome_version(file_name, ip_addr):
#     '''Calls 'check_browser' method with the appropriate parameters for
#     checking the Chrome version.'''
#     check_browser('version', ip_addr, CHROME_VERSION_ERRORS, file_name, CHROME_VERSION)


# Checks that 'hubHost' value is equal to the hub ip_addr, this will verify that the
# correct number of nodes are present.
# def check_number_of_nodes(file_name, ip_addr):
#     '''Calls 'check_browser' method with the appropriate parameters for
#     retrieving the "hubHost" and checking that it's the same as the hub's
#     IP address (indicating that the required number of nodes are present).'''
#     to_compare_to = sys.argv[1]
#     check_browser('hubHost', ip_addr, NUM_NODES_ERRORS, file_name, to_compare_to)
#
#
# def check_num_instances(file_name, ip_addr, correct_num, error_array):
#     '''Calls 'check_browser' method with the appropriate parameters for
#     checking that the correct number of Firefox/Chrome instances are present.'''
#     check_browser('maxInstances', ip_addr, error_array, file_name, correct_num)
#
#
# def check_details_in_json_file(file_name, ip_addr, node_number, ip_type):
#     '''Calls all functions that require details from the same file.'''
#     print 'Checking Firefox version of node ' + str(node_number) + ' ...  '
#     check_firefox_version(file_name, ip_addr)
#     if ip_type != 'sikuli node':
#         print 'Checking Chrome version of node ' + str(node_number) + ' ...  '
#         check_chrome_version(file_name, ip_addr)
#     print 'Checking number of nodes of node ' + str(node_number) + ' (checking hubHost) ... '
#     check_number_of_nodes(file_name, ip_addr)
#     print 'Checking number of Firefox instances of node ' + str(node_number) + ' ...  '
#     if ip_type == 'sikuli node':
#         check_num_instances(file_name, ip_addr, NUM_S_FIREFOX_INSTANCES, FIREFOX_INSTANCES_ERRORS)
#     else:
#         check_num_instances(file_name, ip_addr, NUM_NS_FIREFOX_INSTANCES, FIREFOX_INSTANCES_ERRORS)
#         print 'Checking number of Chrome instances of node ' + str(node_number) + ' ...  '
#         check_num_instances(file_name, ip_addr, NUM_NODE_CHROME_INSTANCES, CHROME_INSTANCES_ERRORS)


def run_audit_steps(ip_addr, ip_type, ram_min_value, cpu_min_value, file_names):
    '''Runs all of the test functions on the IP address specified in the parameter.'''
    print '\nChecking connectivity of ' + ip_type + ' with ip_addr = ' + ip_addr + ' ... ',
    connection_details = check_connection(ip_addr)
    if connection_details[0] == 'success':
        srv = connection_details[1]
        check_storage(ip_addr, srv, ram_min_value, RAM_ERRORS, 'RAM')
        check_storage(ip_addr, srv, cpu_min_value, CPU_ERRORS, 'CPU')
        # check_uptime(ip_addr, srv)
        check_selenium_service_running(ip_addr, ip_type)
        # check_create_instance_failures(srv, ip_addr)
        check_root_directory(srv, ip_addr)
        # Sikuli nodes have 2 node.json files, non-sikuli have 1 and hubs have
        # none so the below if statements allow for the same function to be
        # used for all node.json files of the node/hub/sikuli node that is
        # currently being audited.
        # if file_names[0] != '':
        #     check_details_in_json_file(file_names[0], ip_addr, 1, ip_type)
        # if file_names[1] != '':
        #     check_details_in_json_file(file_names[1], ip_addr, 2, ip_type)
    else:
        print '\nAUDIT FAILED FOR THIS ' + ip_type.upper() + ': could not establish connection to ',
        print ip_type + ' with ip_addr address = ' + ip_addr
        CONNECTION_ERRORS.append(ip_addr)


# def run_audit_on_node(ip_addr, ip_type):
#     '''Applies the appropriate parameters to the 'run_audit_steps' function to
#     run the audit on a sikuli/non-sikuli node.'''
#     if ip_type == 'sikuli node':
#         file_names = ['node-1.json', 'node-2.json']
#         run_audit_steps(ip_addr, ip_type, S_NODE_RAM_MIN_VALUE, S_NODE_CPU_MIN_VALUE, file_names)
#     else:
#         # As there is no node-2.json file in non-sikuli nodes, the second file
#         # name is specified as '', and similarly both file names are specified
#         # as '' for hubs.
#         file_names = ['node-1.json', '']
#         run_audit_steps(ip_addr, ip_type, NODE_RAM_MIN_VALUE, NODE_CPU_MIN_VALUE, file_names)


def run_audit_on_hub(ip_addr):
    '''Applies the appropriate parameters to the 'run_audit_steps' function to
    run the audit on a hub.'''
    file_names = ['', '']
    run_audit_steps(ip_addr, 'hub', HUB_RAM_MIN_VALUE, HUB_CPU_MIN_VALUE, file_names)


def check_if_errors(error_message, errors, number_of_errors):
    '''Iterates through the 'total_errors_storage' master dictionary to
    determine (and then display) if/what type of errors are present.'''
    length = len(errors)
    if length != 0:
        number_of_errors += 1
        print '\nERROR: ' + error_message + ' ...  '
        for each in errors:
            print each
        print '\n'
    else:
        print 'NO ' + error_message + ' errors.'
    return number_of_errors


def main(argv):
    '''Runs the total audit script.'''
    # The IP address of the grid to perform the audit on is taken in as a system
    # argument (which is specified in each job).
    hub_ip_address = argv[0]
    number_of_errors = 0
    print '\n\n\n   ************************ Starting audit script ************************\n'
    #The audit is first run on the hub, then on all nodes in that hub.
    for grid in argv:
        print '\n------------------------------------ Hub ------------------------------------'
        run_audit_on_hub(grid)
    print '\n\n   *********************************************************************'
    print '   *************************** AUDIT RESULTS ***************************'
    print '   *********************************************************************\n'
    for error in TOTAL_ERRORS_STORAGE:
        number_of_errors = check_if_errors(error, TOTAL_ERRORS_STORAGE[error], number_of_errors)
    if number_of_errors > 0:
        print '\n  ************* AUDIT RESULT: FAIL , ',
        print 'presence of errors as seen above. *************'
    else:
        print '\n  ************* AUDIT RESULT: PASS , no errors as seen above. *************'
    print '\n  *************************************************************************\n'


if __name__ == '__main__':
    main(sys.argv[1:])
