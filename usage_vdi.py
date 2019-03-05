from sys import argv
from datetime import datetime

filename_cpd = ''
if len(argv) > 2:
    filename_cpd = argv[2]
if len(argv) > 1:
    filename_report = argv[1]
else:
    filename_report = input('report file: ')
    filename_cpd = input('CPD file: ')
    cpd_universal = input('universal CPD: ')
if cpd_universal:
    cpd_universal = int(cpd_universal)
else:
    cpd_universal = 1

cpd_pool = {}
if filename_cpd:
    with open(filename_cpd) as input_cpd:
        next(input_cpd)
        for data_cpd in input_cpd:
            pool = data_cpd.split(',')[0]
            cpd = data_cpd.split(',')[-1]
            cpd_pool[pool.strip()] = int(cpd)

usage = {}
username_sid = {}
with open(filename_report) as report:
    for data in report:
        vm, name_vm, pool, sid, username, begin, end = data.strip().split('\t')
        username_sid[sid] = username
        begin = datetime.strptime(begin, '%Y-%m-%dT%H:%M:%S.%f')
        end = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S.%f')
        if begin > end:
            print(data)
        if not cpd_pool:
            if sid in usage:
                usage[sid] += (end - begin) * cpd_universal
            else:
                usage[sid] = (end - begin) * cpd_universal
        elif pool in cpd_pool:
            if sid in usage:
                usage[sid] += (end - begin) * cpd_pool[pool]
            else:
                usage[sid] = (end - begin) * cpd_pool[pool]

filename = filename_report.partition('.')[0]

with open(filename + '.usage', 'w') as output_usage:
    [output_usage.write('\t'.join((
        sid, username_sid[sid],
        str(round(usage[sid].total_seconds() / 3600, 2)),)) + '\n')
     for sid in sorted(usage)]
