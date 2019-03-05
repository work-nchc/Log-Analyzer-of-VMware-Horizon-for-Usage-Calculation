from os import walk
from sys import argv

keywords = (
    'EventType="ADMIN_DESKTOP_ADDED"',
    'EventType="ADMIN_REMOVE_DESKTOP_SUCCEEDED"',
    '(MODIFY: desktopSettings.enabled = true)',
    '(MODIFY: desktopSettings.enabled = false)',
    'EventType="ADMIN_ADD_DESKTOP_ENTITLEMENT"',
    'EventType="ADMIN_REMOVE_DESKTOP_ENTITLEMENT"',
    'EventType="AGENT_CONNECTED"',
    'EventType="AGENT_ENDED"',
    'EventType="ADMIN_DESKTOP_SESSION_LOGOFF"',
    'EventType="AGENT_SHUTDOWN"',
    'EventType="AGENT_STARTUP"',
    'EventType="BROKER_MACHINE_OPERATION_DELETED"',
)

filename_output = ''
if len(argv) > 2:
    filename_output = argv[2]
if len(argv) > 1:
    dir_logs = argv[1]
else:
    dir_logs = input('directory of logs: ')
    filename_output = input('output file: ')
list_logs = sorted(next(walk(dir_logs))[2])
if not filename_output:
    filename_output = dir_logs + '_filtered.log'

log_filtered = []

for filename_input in list_logs:
    print(filename_input)
    with open(dir_logs + '/' + filename_input,
              errors='ignore') as input_log:
        log_filtered += [data_log for data_log in input_log
                         if any(map(data_log.__contains__, keywords))]

with open(filename_output, 'w') as output_log:
    output_log.writelines(log_filtered)
