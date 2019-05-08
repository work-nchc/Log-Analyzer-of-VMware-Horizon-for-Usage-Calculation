from sys import argv

if len(argv) > 3:
    filename_usage = argv[1]
    filename_accounts = argv[2]
    filename_sort = argv[3]
else:
    filename_usage = input('usage file: ')
    filename_accounts = input('accounts file: ')
    filename_sort = input('sorted usage output: ')

usage = {}
with open(filename_usage) as input_usage:
    for data in input_usage:
        data = data.split()
        name = data[1]
        su = data[2]
        usage[name] = su

with open(filename_accounts) as input_accounts:
    accounts = [name.strip() for name in input_accounts]

table = [''] * len(accounts)
for name in usage:
    table[accounts.index(name)] = usage[name]

with open(filename_sort, 'w') as output_usage:
    output_usage.write('\n'.join(table))
