from sys import argv

filename_state = ''
if len(argv) > 2:
    filename_state = argv[2]
if len(argv) > 1:
    filename_log = argv[1]
else:
    filename_log = input('filtered log file: ')
    filename_state = input('state file: ')

pools_enabled = set()
pools_disabled = set()
username_sid = {}
user_pool = {}
user_pool_deprived = {}
vdi = {}
report = []
err = []
if filename_state:
    with open(filename_state) as input_state:
        for state in input_state:
            label, __, data = state.partition('\t')
            if data.strip():
                if 'pools_enabled' == label:
                    pools_enabled = set(data.strip().split())
                elif 'pools_disabled' == label:
                    pools_disabled = set(data.strip().split())
                else:
                    key, __, value = data.partition('\t')
                    if 'username_sid' == label:
                        username_sid[key] = value.strip()
                    elif 'user_pool' == label:
                        user_pool[key] = set(value.split())
                    elif 'user_pool_deprived' == label:
                        user_pool_deprived[key] = set(value.split())
                    elif 'vdi' == label:
                        vdi[key] = value.split('\t')
                        vdi[key][-1] = vdi[key][-1].strip()
                    else:
                        err.append(state)

def parser(data):
    return (
        data.split()[5].partition('+')[0],
        data.partition('UserSID="')[2].partition('"')[0].lower(),
        data.partition('UserDisplayName="')[2].partition('"')[0]
        .split('\\')[-1].lower(),
        data.partition('DesktopId="')[2].partition('"')[0].lower(),
        data.partition('EntitlementSID="')[2].partition('"')[0].lower(),
        data.partition('EntitlementDisplay="')[2].partition('"')[0]
        .split('\\')[-1].lower(),
        data.partition('MachineId="')[2].partition('"')[0].lower(),
        data.partition('MachineName="')[2].partition('"')[0].lower(),
        data.partition('UserName="')[2].partition('"')[0]
        .split('\\')[-1].lower(),
    )

# functions using side effects

def enable_pool(data):
    timestamp, sid_admin, name_admin, pool = parser(data)[:4]

    if sid_admin and sid_admin not in username_sid:
        username_sid[sid_admin] = ''
    if sid_admin and name_admin:
        username_sid[sid_admin] = name_admin
    if pool and pool not in user_pool:
        user_pool[pool] = set()
    if pool and pool not in user_pool_deprived:
        user_pool_deprived[pool] = set()
    if pool and timestamp:
        pools_enabled.add(pool)
        pools_disabled.discard(pool)
        for vm in sorted(vdi):
            if vdi[vm][1] == pool and vdi[vm][2]:
                report.append('\t'.join([vm] + vdi[vm] + [timestamp]) + '\n')
            if vdi[vm][1] == pool:
                vdi[vm][2:] = '', '', ''
    else:
        err.append(data)

    return pool

def disable_pool(data):
    timestamp, sid_admin, name_admin, pool = parser(data)[:4]

    if sid_admin and sid_admin not in username_sid:
        username_sid[sid_admin] = ''
    if sid_admin and name_admin:
        username_sid[sid_admin] = name_admin
    if pool and pool not in user_pool:
        user_pool[pool] = set()
    if pool and pool not in user_pool_deprived:
        user_pool_deprived[pool] = set()
    if pool and timestamp:
        pools_disabled.add(pool)
        pools_enabled.discard(pool)
        for vm in sorted(vdi):
            if vdi[vm][1] == pool and vdi[vm][2]:
                report.append('\t'.join([vm] + vdi[vm] + [timestamp]) + '\n')
            if vdi[vm][1] == pool:
                vdi[vm][2:] = '', '', ''
    else:
        err.append(data)

    return pool

def add_pool(data):
    pool = enable_pool(data)

    if pool:
        user_pool_deprived[pool] |= user_pool[pool]
        user_pool[pool] = set()

    return None

def remove_pool(data):
    pool = disable_pool(data)

    if pool:
        user_pool_deprived[pool] |= user_pool[pool]
        user_pool[pool] = set()

    return None

def entitle(data):
    timestamp, sid_admin, name_admin, pool, sid, username = parser(data)[:6]

    if sid_admin and sid_admin not in username_sid:
        username_sid[sid_admin] = ''
    if sid and sid not in username_sid:
        username_sid[sid] = ''
    if sid_admin and name_admin:
        username_sid[sid_admin] = name_admin
    if sid and username:
        username_sid[sid] = username
    if pool and pool not in user_pool:
        user_pool[pool] = set()
    if pool and pool not in user_pool_deprived:
        user_pool_deprived[pool] = set()
    if pool and sid:
        user_pool[pool].add(sid)
        user_pool_deprived[pool].discard(sid)
    if pool and sid and timestamp:
        for vm in sorted(vdi):
            if vdi[vm][1] == pool and vdi[vm][2] == sid:
                report.append('\t'.join([vm] + vdi[vm] + [timestamp]) + '\n')
                vdi[vm][2:] = '', '', ''
    else:
        err.append(data)
    
    return None

def deprive(data):
    timestamp, sid_admin, name_admin, pool, sid, username = parser(data)[:6]
    
    if sid_admin and sid_admin not in username_sid:
        username_sid[sid_admin] = ''
    if sid and sid not in username_sid:
        username_sid[sid] = ''
    if sid_admin and name_admin:
        username_sid[sid_admin] = name_admin
    if sid and username:
        username_sid[sid] = username
    if pool and pool not in user_pool:
        user_pool[pool] = set()
    if pool and pool not in user_pool_deprived:
        user_pool_deprived[pool] = set()
    if pool and sid:
        user_pool_deprived[pool].add(sid)
        user_pool[pool].discard(sid)
    if pool and sid and timestamp:
        for vm in sorted(vdi):
            if vdi[vm][1] == pool and vdi[vm][2] == sid:
                report.append('\t'.join([vm] + vdi[vm] + [timestamp]) + '\n')
                vdi[vm][2:] = '', '', ''
    else:
        err.append(data)
    
    return None

def log_in(data):
    timestamp, sid, username, pool, *__, vm, name_vm = parser(data)[:8]
    
    if sid and sid not in username_sid:
        username_sid[sid] = ''
    if sid and username:
        username_sid[sid] = username
    if pool and pool not in user_pool:
        user_pool[pool] = set()
    if pool and pool not in user_pool_deprived:
        user_pool_deprived[pool] = set()
    if vm and vm not in vdi:
        vdi[vm] = ['', '', '', '', '']
    if vm and name_vm:
        vdi[vm][0] = name_vm
    if vm and pool:
        vdi[vm][1] = pool
    if vm and sid:
        vdi[vm][3] = username_sid[sid]
    if vm and sid and timestamp:
        if not vdi[vm][2]:
            vdi[vm][2] = sid
            vdi[vm][4] = timestamp
        elif vdi[vm][2] != sid:
            err.append(vdi[vm][2] + '\t' + data)
            report.append('\t'.join([vm] + vdi[vm] + [timestamp]) + '\n')
            vdi[vm][2] = sid
            vdi[vm][4] = timestamp
    else:
        err.append(data)
    
    return None

def log_off(data):
    timestamp, *__, pool, __, __, vm, name_vm = parser(data)[:8]

    if pool and pool not in user_pool:
        user_pool[pool] = set()
    if pool and pool not in user_pool_deprived:
        user_pool_deprived[pool] = set()
    if vm and vm not in vdi:
        vdi[vm] = ['', '', '', '', '']
    if vm and name_vm:
        vdi[vm][0] = name_vm
    if vm and pool:
        vdi[vm][1] = pool
    if vm and timestamp and vdi[vm][2]:
        report.append('\t'.join([vm] + vdi[vm] + [timestamp]) + '\n')
    if vm and timestamp:
        vdi[vm][2:] = '', '', ''
    else:
        err.append(data)
    
    return None

def log_off_user(data):
    sid, vm = parser(data)[1::5]
    
    if sid and sid not in username_sid:
        username_sid[sid] = ''
    if vm and sid and vm in vdi and vdi[vm][2] and vdi[vm][2] != sid:
        err.append(vdi[vm][2] + '\t' + data)
    
    log_off(data)
    
    return None

def admin_kick(data):
    timestamp, sid_admin, name_admin, *__, name_vm, username = parser(data)

    if sid_admin and sid_admin not in username_sid:
        username_sid[sid_admin] = ''
    if sid_admin and name_admin:
        username_sid[sid_admin] = name_admin
    if name_vm and timestamp:
        for vm in sorted(vdi):
            if vdi[vm][0] == name_vm and vdi[vm][3]:
                if username and vdi[vm][3] != username:
                    err.append(vdi[vm][3] + '\t' + data)
                report.append('\t'.join([vm] + vdi[vm] + [timestamp]) + '\n')
            if vdi[vm][0] == name_vm:
                vdi[vm][2:] = '', '', ''
    else:
        err.append(data)
    
    return None

func_keyword = {
    'EventType="ADMIN_DESKTOP_ADDED"': add_pool,
    'EventType="ADMIN_REMOVE_DESKTOP_SUCCEEDED"': remove_pool,
    '(MODIFY: desktopSettings.enabled = true)': enable_pool,
    '(MODIFY: desktopSettings.enabled = false)': disable_pool,
    'EventType="ADMIN_ADD_DESKTOP_ENTITLEMENT"': entitle,
    'EventType="ADMIN_REMOVE_DESKTOP_ENTITLEMENT"': deprive,
    'EventType="AGENT_CONNECTED"': log_in,
    'EventType="AGENT_ENDED"': log_off_user,
    'EventType="ADMIN_DESKTOP_SESSION_LOGOFF"': admin_kick,
    'EventType="AGENT_SHUTDOWN"': log_off,
    'EventType="AGENT_STARTUP"': log_off,
    'EventType="BROKER_MACHINE_OPERATION_DELETED"': log_off,
}

with open(filename_log) as input_log:
    [func_keyword[next(filter(data_log.__contains__, func_keyword))](data_log)
     for data_log in input_log]

filename = filename_log.partition('.')[0]

with open(filename + '.csv', 'w') as output_report:
    output_report.writelines(report)

with open(filename + '.err', 'w') as output_err:
    output_err.writelines(err)

with open(filename + '.sav', 'w') as output_state:
    output_state.write('pools_enabled\t{}\n'.format(
        '\t'.join(sorted(pools_enabled))))
    output_state.write('pools_disabled\t{}\n'.format(
        '\t'.join(sorted(pools_disabled))))
    [output_state.write('username_sid\t{}\t{}\n'.format(
        sid, username_sid[sid])) for sid in sorted(username_sid)]
    [output_state.write('user_pool\t{}\t{}\n'.format(
        pool, '\t'.join(sorted(user_pool[pool]))))
     for pool in sorted(user_pool)]
    [output_state.write('user_pool_deprived\t{}\t{}\n'.format(
        pool, '\t'.join(sorted(user_pool_deprived[pool]))))
     for pool in sorted(user_pool_deprived)]
    [output_state.write('vdi\t{}\t{}\n'.format(vm, '\t'.join(vdi[vm])))
     for vm in sorted(vdi)]

pools_all = sorted(pools_enabled) + sorted(pools_disabled)
entitle = {sid: [''] * len(pools_all) for sid in username_sid}

for pool in pools_all:
    if pool in user_pool:
        for sid in user_pool[pool]:
            entitle[sid][pools_all.index(pool)] = pool
    if pool in user_pool_deprived:
        for sid in user_pool_deprived[pool]:
            entitle[sid][pools_all.index(pool)] = '#' + pool

with open('entitlement.csv', 'w') as output_entitle:
    output_entitle.write('\t'.join(['sid', 'username'] + pools_all) + '\n')
    [output_entitle.write(
        '\t'.join([sid, username_sid[sid]] + entitle[sid]) + '\n')
     for sid in sorted(username_sid)]
