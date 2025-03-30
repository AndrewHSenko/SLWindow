import ReadQSRSoS as qsr
import ReadSquirrelSoS as squirrel
import time

# Crontab should run this script every 5 minutes between 10:35am and 7:25pm
def do_it(start):
    start_time = start # time.strftime('%Y%H%M') # Not using %I to make it easier to handle AM to PM hour change
    end_time = start_time + 5 if str(start_time)[-2:] != '60' else start_time + 40 # To fix xx:60 situations
    date = '20250317'
    five_min_prod = 0
    sq_checks = squirrel.get_check_data(f'{date}{start_time}00', f'{date}{end_time}00')
    # sq_checks now has all checks within 5 minute window (including blank checks)
    # Keys: check_no, check_name, menu_ids #
    qsr_checks = qsr.get_QSR_data(start_time, end_time) # Should return all QSR parsed tickets between start and end time parameters
    
    '''
    for check_num in checks:
        date_time = checks[check_num]['entered']
        saletime = datetime.strptime(date_time, '%Y%m%d%H%M%S')
        check_data = squirrel.get_check_data(check_num, saletime)
        if check_data:
            check_data = check_data[check_num]
            five_min_prod += check_data[-1] # Gets item count
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

do_it(1105)