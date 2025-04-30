import ReadQSRSoS as qsr
import ReadSquirrelSoS as squirrel
import time
# NEED TO ADD #
    # Every 5 minutes, update Squirrel entries
    # - For every Squirrel entry:
    #   - QSR Start
    #   - QSR Finish
    #   - QSR PV
    #   - QSR Anchor
    # - When all 4 are filled, remove Squirrel entry
    #   - Flag if any of the 4 are missing (PV might be absent for some tickets)
    #       - Might check if PV items are present on check before this
    #   - Add qty of check to 5 min interval based on Anchor Bump Time
    #       - May do it based on joint Finish/PV time too
    #       - Also record bump time / on-screen time for other stations
    # - Flag if Squirrel check doesn't have corresponding QSR Check #
active_checks = {}
bad_checks = {}
window = {}
# To update window
def add_to_window():
    start_time = 1000
    while start_time != 1915:
        end_time = start_time + 5 if str(start_time)[-2:] != '55' else start_time + 45 # To fix xx:60 situations
        date = '20250315' # To be current date
        window_start, window_end = f'{date}{start_time}00', f'{date}{end_time}00'
        intvl = window_start + ' - ' + window_end
        window[intvl] = []
        for check in active_checks:
            anchor = active_checks[check]['ANCHOR']
            if int(anchor) < int(window_start) - 100:
                continue
            elif int(anchor) > int(window_end) + 100:
                break
            elif int(window_start) < int(anchor) < int(window_end):
                window[intvl].append((check, active_checks[check]['Qty']))
        sum = 0
        for entry in window[intvl]:
            sum += entry[1]
        window[intvl].append(sum)
        start_time += 5
        if str(start_time)[-2:] == '60':
        # print(clean_checks(str(start_time)[:2]))
            start_time += 40
    with open('window_data.txt', 'a') as file:
        for intvl, data in window.items():
            file.write(f'||| {intvl} |||\n')
            for d in data:
                file.write(str(d) + '\n')


def clean_checks(curr_hour):
    delete_checks = []
    target_hr = int(curr_hour) - 2
    for saletime in active_checks:
        if int(saletime[8:10]) == target_hr and active_checks[saletime]['HOT START'] and active_checks[saletime]['HOT FINISH'] and active_checks[saletime]['PLATESVILLE'] and active_checks[saletime]['ANCHOR']:
            delete_checks.append(saletime)
    checks_delete = len(delete_checks)
    for check in delete_checks:
        del active_checks[check]
    return checks_delete

def find_bad_checks():
    return

st = time.time()
startline = 0
start_time = 1000 # Not using %I to make it easier to handle AM to PM hour change
while start_time != 1915:
    stt = time.time()
    print('On:', start_time)
    end_time = start_time + 5 if str(start_time)[-2:] != '55' else start_time + 45 # To fix xx:60 situations
    date = '20250315' # To be current date
    sq_checks = squirrel.get_check_data(f'{date}{start_time}00', f'{date}{end_time}00')
    # sq_checks now has all checks within 5 minute window that have SL items
    # sq_checks key: saletime
    # sq_checks values: check_no, check_name, qty #
    if sq_checks:
        for sq_check in sq_checks:
            if sq_check not in active_checks : # Add check
                active_checks[sq_check] = {'Name': sq_checks[sq_check][1], 'Qty': sq_checks[sq_check][2], 'HOT START' : '', 'HOT FINISH' : '', 'PLATESVILLE': '', 'ANCHOR' : ''}
    ett = time.time()
    print('After squirrel:', ett-stt)
    for sale_time in active_checks:
        this_check = qsr.get_QSR_data(sale_time, active_checks[sale_time]['Name'], startline)
        for qsr_info, qsr_data in this_check.items():
            saletime, station = qsr_info[0], qsr_info[1]
            if station in active_checks[saletime]:
                active_checks[saletime][station] = qsr_data['bumped']
            # startline += 1
    start_time += 5
    ett = time.time()
    print('After QSR:', ett-stt)
    if str(start_time)[-2:] == '60':
        # print(clean_checks(str(start_time)[:2]))
        start_time += 40
        # HERE HERE HERE #
        # Figure out why Staff Curtis is blank for everything besides 1450-1510 #
et = time.time()
print('Active checks:', len(active_checks))
for check in active_checks:
    check_data = active_checks[check]
    if not check_data['HOT START'] or not check_data['HOT FINISH'] or not check_data['PLATESVILLE'] or not check_data['ANCHOR']: # incomplete check
        if check in bad_checks:
            print('Check repeated:', check)
            print(check)
        else:
            bad_checks[check] = check_data
# Based on Anchor bump (Will later integrate Finish/PV for shits and gigs)
with open('badchecks.txt', 'a') as f:
    for check in bad_checks:
        f.write(check + ' | ' + str(bad_checks[check]) + '\n')
print(et, '-', st, '=', et - st)
add_to_window()

'''
    for check_num in checks:
        date_time = checks[check_num]['entered']
        saletime = datetime.strptime(date_time, '%Y%m%d%H%M%S')
        active_checks = squirrel.get_active_checks(check_num, saletime)
        if active_checks:
            active_checks = active_checks[check_num]
            five_min_prod += active_checks[-1] # Gets item count
        else:
            print(check_num)
    start_time, end_time, five_min_prod = str(start_time), str(end_time), str(five_min_prod)
    # Do something with the five_min_prod #
    if len(five_min_prod) == 1:
        five_min_prod = '0' + five_min_prod
    top_border = '-'*20 # Amount of dashes matches entry length
    entry = f'| {start_time[:2]}:{start_time[2:]}-{end_time[:2]}:{end_time[2:]} | {five_min_prod} |'
    with open('window.txt', 'a') as window:
        if start_time[2:] == '00':
            window.write('-'*12 + '\n')
            hour = start_time[:2]
            meridian = 'PM' if int(start_time[:2]) >= 12 else 'AM'
            # hour = time.strftime('%I') # For readability
            # meridian = time.strftime('%p')
            window.write(f'| {hour}:00 {meridian} |')
            window.write('-'*12 + '\n')
        window.write(top_border + '\n')
        window.write(entry + '\n')'''