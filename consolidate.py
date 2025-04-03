import ReadQSRSoS as qsr
import ReadSquirrelSoS as squirrel
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
check_data = {}
start_time = 1320 # time.strftime('%Y%H%M') # Not using %I to make it easier to handle AM to PM hour change
while start_time != 1915:
    end_time = start_time + 5 if str(start_time)[-2:] != '60' else start_time + 40 # To fix xx:60 situations
    date = '20250314' # To be current date
    sq_checks = squirrel.get_check_data(f'{date}{start_time}00', f'{date}{end_time}00')
    # sq_checks now has all checks within 5 minute window that have SL items
    # sq_checks key: saletime
    # sq_checks values: check_no, check_name, qty #
    for sq_check in sq_checks:
        if sq_check not in check_data: # Add check
            check_data[sq_check] = {'Name': sq_checks[sq_check][1], 'START' : '', 'FINISH' : '', 'PLATESVILLE': '', 'ANCHOR' : ''}
    for check in check_data:
        qsr.get_QSR_data(check, check_data[check]['Name']) # Saletime & Name
        # Parse for which station
        # Update check_data station entries
        # If check_data entry is filled, update quantities


    start_time += 5
    if str(start_time)[-2:] == '60':
        start_time += 40


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