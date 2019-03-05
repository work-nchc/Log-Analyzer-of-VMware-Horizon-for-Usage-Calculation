# The Log Analyzer of VMware Horizon for Usage Calculation from NCHC

Tested in Python 3.6

Log Filtering:

```
PATH/TO/python.exe filter_logs.py [dir_logs [output.log]]
```

Filter logs in the log files in [dir_logs], excluding subdirectory.  If no output name is given, it will be [dir_logs]_filtered.log.  There will be an input dialogue if arguments are absent.

The log files must be named in chronological order.

This script looks at the following event types or keywords:

```
ADMIN_DESKTOP_ADDED
ADMIN_REMOVE_DESKTOP_SUCCEEDED
ADMIN_ADD_DESKTOP_ENTITLEMENT
ADMIN_REMOVE_DESKTOP_ENTITLEMENT
ADMIN_DESKTOP_SESSION_LOGOFF
AGENT_CONNECTED
AGENT_ENDED
AGENT_SHUTDOWN
AGENT_STARTUP
BROKER_MACHINE_OPERATION_DELETED
(MODIFY: desktopSettings.enabled = true)
(MODIFY: desktopSettings.enabled = false)
```

---
Log Parsing:

```
PATH/TO/python.exe parser_logs.py [filtered.log [state.sav]]
```

Parse the filtered log.  A initial vdi state file can be delivered.  There will be an input dialogue if arguments are absent.

Four files will present after running this script, a .csv report with login/out data, a .err error file logging insufficient or inconsistent data, a .sav state file, and an entitlement.csv recording the entitlements of the users.

The following is the format of the state file:

```
pools_enabled	pool_1	pool_2	...
pools_disabled	pool_a	pool_b	...
username_sid	sid_1	username_1
username_sid	sid_2	username_2
...
user_pool	pool_1	sid_1   sid_2   ...
user_pool	pool_2	sid_a   sid_b   ...
...
user_pool_deprived	pool_1	sid_i   sid_j   ...
user_pool_deprived	pool_2	sid_x   sid_y   ...
...
vdi	id_vm1	name_vm1	pool_vm1	sid_1	username_1	timestamp_1
vdi	id_vm2	name_vm2	pool_vm2	sid_2	username_2	timestamp_2
...
```

---
Usage Calculation:

```
PATH/TO/python.exe usage_vdi.py [report.csv [CPD file]]
```

Calculate the vdi usage from [report.csv].  A csv file with cores per desktop data can be delivered.  There will be an input dialogue if arguments are absent.

A .usage file listing the usage consumed by each user will present after running this script.  If there is a record of which begin time later than its end time, it will be printed on the standard output.

---
[More about the events in VMware Horizon](https://docs.vmware.com/en/VMware-Horizon-7/7.7/horizon-integration/GUID-27B7E9C6-DEE4-4E0D-BA65-41C5DB06EF0E.html)

2019-03-0 by 1803031@narlabs.org.tw
