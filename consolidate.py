import ReadQSRSoS as qsr
import ReadSquirrelSoS as squirrel
from os import mkdir
import overlay
import get_pu_window as pu
import make_sheet
import make_graph
import time

# HEADERS #
MONTH_H = '09_13_2025' # time.strftime('%m_%d_%Y')
M_NAME_H = 'Sep_13_2025' # time.strftime('%b_%d_%Y')
NO_DAY = 'Sep_2025' # time.strftime('%b_%Y')
WEEK_NUM = 2
SHEET_NUM = 5
DATE = '20250913'
# DATE = time.strftime('%Y%m%d')

DIR_NAME = 'C:/Users/Squirrel/Desktop/Window Data'
DEST_PATH = f'{DIR_NAME}/{MONTH_H}/'

# Finds bad checks (missing a station bump) #
def find_bad_checks(active_checks):
    bad_checks = {}
    for check in active_checks: 
        check_data = active_checks[check]
        if not check_data['HOT START'] or not check_data['HOT FINISH'] or not check_data['PLATESVILLE'] or not check_data['ANCHOR']: # incomplete check
            if check in bad_checks:
                continue
            else:
                bad_checks[check] = check_data
    # Based on Anchor bump (Will later integrate Finish/PV for shits and gigs)
    with open(DEST_PATH + M_NAME_H + '_Missing_Bumps.txt', 'a') as badchecks_file:
        badchecks_file.write('MISSING BUMPS\n')
        badchecks_file.write('-------------\n')
        for saletime in bad_checks:
            check = bad_checks[saletime]
            missing_bumps = []
            if not check['HOT START']:
                missing_bumps.append('Start')
            if not check['HOT FINISH']:
                missing_bumps.append('Finish')
            if not check['PLATESVILLE']:
                missing_bumps.append('Platesville')
            if not check['ANCHOR']:
                missing_bumps.append('Expo')
            badchecks_file.write(f'{saletime[-6:-4]}:{saletime[-4:-2]}:{saletime[-2:]} ({check["Name"]}): |')
            for bump in missing_bumps:
                badchecks_file.write(f' {bump} |')
            badchecks_file.write('\n')
    # Will add return statement with try/catch blocks #

def create_raw_text(window, file_name):
    sums = {}
    total = 0
    with open(f'{DEST_PATH}Raw_{M_NAME_H}_{file_name}_Data.txt', 'a') as window_file: # For Window
        window_file.write(f'Raw {file_name} Data\n')
        window_file.write('---------')
        for intvl, data in window.items():
            window_file.write(f'\n||| {intvl} |||\n')
            # TO DO: Should add which menu items were ordered #
            for d in data[:-1]:
                saletime = d[0]
                name = d[1]
                qty = int(d[-1])
                window_file.write(f'+ {saletime} ({name}): {qty}\n')
            window_file.write(f'[ Total: {int(data[-1])} ]\n')
            total += int(data[-1])
            sums[intvl] = str(data[-1])
    return (sums, total)

def create_window_text(sums, ssum, file_name):
    with open(f'{DEST_PATH}{MONTH_H}_{file_name}_Summary.txt', 'a') as summary_file:
        summary_file.write(f'Summary\n')
        summary_file.write('-------\n')
        intvl_sum, best, worst = 0, 0, 1000 # If we're making 1000+ sandwiches every 5 minutes, give us a medal
        for intvl, sum in sums.items():
            if intvl[-2:] == '05':
                if intvl[1] == ':':
                    summary_file.write(f'| {intvl[0]}:00 - {int(intvl[0]) + 1}:00 |\n')
                else:
                    head = int(intvl[:2])
                    if head == 12:
                        head -= 12
                    summary_file.write(f'| {intvl[:2]}:00 - {head + 1}:00 |\n')
            int_sum = int(float(sum)) 
            summary_file.write(f'{intvl}: {int_sum}\n')
            intvl_sum += int_sum
            if int_sum > best:
                best = int_sum
            if int_sum < worst:
                worst = int_sum
            if intvl[-2:] == '00':
                summary_file.write(f'* Total: {intvl_sum} *\n')
                summary_file.write(f'* Best: {best} *\n')
                summary_file.write(f'* Worst: {worst} *\n\n')
                intvl_sum, best, worst = 0, 0, 1000
        summary_file.write(f'TOTAL: {ssum}\n')

def create_foh_entries_text(entered):
    with open(DEST_PATH + M_NAME_H + '_FoH_Entries.txt', 'a') as entry_file: # For FoH entries
        qtys = {}
        entry_file.write('FoH Entries\n')
        entry_file.write('-----------')
        for ivl, entry in entered.items():
            check_sum = 0
            item_sum = 0
            entry_file.write(f'\n||| {ivl} |||\n')
            for vals in entry:
                check_sum += 1
                item_sum += int(vals[-1])
                entry_file.write(f'+ {vals[1]}: {vals[0]}\n')
            entry_file.write(f'Checks: {check_sum}\nItem Qty: {item_sum}\n')
            qtys[ivl] = (check_sum, item_sum)
        entry_file.write(f'\nSUMMARY\n')
        entry_file.write('-------\n')
        for ivl, entry_qty in qtys.items():
            entry_file.write(f'|{ivl}| TOTAL CHECKS: {entry_qty[0]} / TOTAL QTY: {entry_qty[1]}\n')
    return qtys

def create_sheets(sums=None, foh_items=None, pu_window=None, pu_actual=None, fsums=None, pvsums=None):
    monthly_wb = False # Change to false
    if time.strftime('%d') == '01': # Dev Change #
        monthly_wb = True
    # monthly_window_wb_name = f'{DIR_NAME}/{NO_DAY}_Window_Data.xlsx'
    daily_window_wb_name = f'{DEST_PATH}{MONTH_H}_Window.xlsx'
    window_name = MONTH_H + '_Window_Items'
    finish_name = MONTH_H + '_Finish_Items'
    pv_name = MONTH_H + '_PV_Items'
    # Window Data #
    if sums:
        print('On Sums')
        start = time.time()
        # make_sheet.generate_daily_sheet(monthly_window_wb_name, sums, monthly_wb, window_name) # To add to monthly workbook
        # make_graph.make_daily_prod(monthly_window_wb_name, sums, window_name)
        make_sheet.generate_daily_sheet(daily_window_wb_name, sums, True, window_name) # To add to daily workbook
        make_graph.make_daily_prod(daily_window_wb_name, sums, window_name)
    # Finish Data #
    if fsums:
        make_sheet.generate_daily_sheet(monthly_window_wb_name, sums, monthly_wb, finish_name) # To add to monthly workbook
        make_graph.make_daily_prod(monthly_window_wb_name, sums, finish_name)
        make_sheet.generate_daily_sheet(daily_window_wb_name, sums, True, finish_name) # To add to daily workbook
        make_graph.make_daily_prod(daily_window_wb_name, sums, finish_name)
    # PV Data #
    if pvsums:
        make_sheet.generate_daily_sheet(monthly_window_wb_name, sums, monthly_wb, pv_name) # To add to monthly workbook
        make_graph.make_daily_prod(monthly_window_wb_name, sums, pv_name)
        make_sheet.generate_daily_sheet(daily_window_wb_name, sums, True, pv_name) # To add to daily workbook
        make_graph.make_daily_prod(daily_window_wb_name, sums, pv_name)
    # FoH Data #
    # Checks (retired) #
    # monthly_foh_wb_name = f'{DIR_NAME}/{NO_DAY}_FoH_Data.xlsx'
    daily_foh_wb_name = f'{DEST_PATH}{MONTH_H}_FoH.xlsx'
    # foh_checks_name = MONTH_H + '_Checks'
    foh_items_name = MONTH_H + '_Items'
    # if foh_checks:
    #     make_sheet.generate_daily_sheet(monthly_foh_wb_name, foh_checks, monthly_wb, foh_checks_name) # To add to monthly workbook
    #     make_graph.make_daily_prod(monthly_foh_wb_name, foh_checks, foh_checks_name)
    #     make_sheet.generate_daily_sheet(daily_foh_wb_name, foh_checks, True, foh_checks_name) # To add to daily workbook
    #     make_graph.make_daily_prod(daily_foh_wb_name, foh_checks, foh_checks_name)
    # Items #
    if foh_items:
        print('On FoH Items')
        # make_sheet.generate_daily_sheet(monthly_foh_wb_name, foh_items, monthly_wb, foh_items_name) # To add to monthly workbook
        # make_graph.make_daily_prod(monthly_foh_wb_name, foh_items, foh_items_name)
        make_sheet.generate_daily_sheet(daily_foh_wb_name, foh_items, True, foh_items_name) # To add to daily workbook
        make_graph.make_daily_prod(daily_foh_wb_name, foh_items, foh_items_name)
    if sums and foh_items and pu_window and pu_actual:
        print('On Overlay')
        overlay.create_overlay(daily_window_wb_name, sums, foh_items, pu_window, pu_actual, MONTH_H) # GO HERE TO TOGGLE PU WINDOW #
    # Will add return statement with try/catch blocks #

# To update window
def tabulate(active_checks):
    window = {}
    f_window = {}
    p_window = {}
    fpv_window = {}
    entered = {}
    missing_anchor_bumps = []
    # Collect data #
    start_time = 1000
    while start_time != 1915:
        end_time = start_time + 5 if str(start_time)[-2:] != '55' else start_time + 45 # To fix xx:60 situations
        window_start, window_end = f'{DATE}{start_time}00', f'{DATE}{end_time}00'
        easier_win_start = start_time if start_time < 1300 else start_time - 1200
        easier_win_end = end_time if end_time < 1300 else end_time - 1200
        intvl = str(easier_win_start)[:-2]+ ':' + str(easier_win_start)[-2:] + ' - ' + str(easier_win_end)[:-2] + ':' + str(easier_win_end)[-2:]
        window[intvl] = []
        f_window[intvl] = []
        p_window[intvl] = []
        fpv_window[intvl] = []
        entered[intvl] = []
        for check in active_checks:
            anchor = active_checks[check]['ANCHOR']
            '''
            if active_checks[check]['has_finish']:
                finish = active_checks[check]['HOT FINISH']
                if active_checks[check]['has_pv']:
                    pv = active_checks[check]['PLATESVILLE']
                    if finish > pv:
                        fpv = finish
                    else:
                        fpv = pv
            if active_checks[check]['has_pv']:
                pv = active_checks[check]['PLATESVILLE']
            '''
            if not anchor: 
                if active_checks[check] not in missing_anchor_bumps:
                    missing_anchor_bumps.append(active_checks[check])
                    with open(DEST_PATH + M_NAME_H + '_Missing_Bumps.txt', 'a') as badchecks_file:
                        badchecks_file.write(f'Missing Anchor bump for:\n| {active_checks[check]['Name']} | Qty: {active_checks[check]['Qty']}\n')
                continue
            if int(window_start) < int(check) < int(window_end): # FoH Entries
                check_saletime = f'{check[-6:-4]}:{check[-4:-2]}:{check[-2:]}'
                entered[intvl].append([check_saletime, active_checks[check]['Name'], active_checks[check]['Qty']])
            if int(window_start) < int(anchor) < int(window_end): # Anchor Bumps
                check_saletime = f'{check[-6:-4]}:{check[-4:-2]}:{check[-2:]}'
                window[intvl].append((check_saletime, active_checks[check]['Name'], active_checks[check]['Qty']))
            # Figure this out #
            '''
            if int(window_start) < int(finish) < int(window_end): # Finish/PV Bumps
                check_saletime = f'{check[-6:-4]}:{check[-4:-2]}:{check[-2:]}'
                fpv_window[intvl].append((check_saletime, active_checks[check]['Name'], active_checks[check]['Qty']))
            '''
        sum = 0
        for entry in window[intvl]:
            sum += entry[-1]
        window[intvl].append(sum)
        print('Testing:', start_time)
        start_time += 5
        if str(start_time)[-2:] == '60':
            start_time += 40
    # Tabulate data #
    raw_data = create_raw_text(window, 'Window')
    sums = raw_data[0]
    stotal = raw_data[1]
    create_window_text(sums, stotal, 'Window')
    '''
    finish_data = create_raw_text(window, 'Finish')
    fsums = finish_data[0]
    ftotal = finish_data[1]
    create_window_text(fsums, ftotal, 'Finish')
    pv_data = create_raw_text(window, 'PV')
    pvsums = pv_data[0]
    pvtotal = pv_data[1]
    create_window_text(pvsums, pvtotal, 'PV')
    '''
    qtys = create_foh_entries_text(entered)
    check_qtys = {}
    item_qtys = {}
    for ivl, qty in qtys.items():
        check_qtys[ivl] = qty[0]
        item_qtys[ivl] = qty[1]
    pu_window, pu_actual = pu.get_data(WEEK_NUM, SHEET_NUM)
    create_sheets(sums, item_qtys, pu_window, pu_actual)

def find_production():
    qsr_data = qsr.get_QSR_data() #'20250602162500'
    active_checks = {}
    # Collect data #
    start = time.time()
    start_time = 1000 # Not using %I to make it easier to handle AM to PM hour change
    while start_time != 1915:
        print('On:', start_time)
        end_time = start_time + 5 if str(start_time)[-2:] != '55' else start_time + 45 # To fix xx:60 situations
        sq_checks = squirrel.get_check_data(f'{DATE}{start_time}00', f'{DATE}{end_time}00')
        # sq_checks now has all checks within 5 minute window that have SL items
        # sq_checks key: saletime
        # sq_checks values: check_no, check_name, qty #
        if sq_checks:
            for sq_check in sq_checks:
                if sq_check not in active_checks : # Add check from Squirrel to active_checks
                    active_checks[sq_check] = {'Name': sq_checks[sq_check][1], 'Qty': sq_checks[sq_check][2], 'has_finish': sq_checks[sq_check][3][0], 'has_pv': sq_checks[sq_check][3][1], 'HOT START' : '', 'HOT FINISH' : '', 'PLATESVILLE': '', 'ANCHOR' : ''}
        # Set up bump times in active_checks #
        for sale_time in active_checks:
            check_name = active_checks[sale_time]['Name']
            st = sale_time
            if not (sale_time, 'ANCHOR') in qsr_data:
                st = qsr.find_entry(qsr_data, sale_time, check_name)
            if (st, 'HOT START') in qsr_data:
                active_checks[sale_time]['HOT START'] = qsr_data[(st, 'HOT START')]['bumped']
            if (st, 'HOT FINISH') in qsr_data:
                active_checks[sale_time]['HOT FINISH'] = qsr_data[(st, 'HOT FINISH')]['bumped']
            if (st, 'PLATESVILLE') in qsr_data:
                active_checks[sale_time]['PLATESVILLE'] = qsr_data[(st, 'PLATESVILLE')]['bumped']
            if (st, 'ANCHOR') in qsr_data:
                active_checks[sale_time]['ANCHOR'] = qsr_data[(st, 'ANCHOR')]['bumped']
        start_time += 5
        if str(start_time)[-2:] == '60':
            start_time += 40
    end = time.time()
    print('Time taken:', end, '-', start, '=', end - start)
    find_bad_checks(active_checks)
    tabulate(active_checks)
    return True

if __name__ == '__main__':
    if time.strftime('%d') == '01': # Dev Change #
        # Create the monthly directory
        try:
            mkdir(DIR_NAME)
        except FileExistsError:
            with open('dir_creation_failed.txt', 'a') as dir_err_file:
                dir_err_file.write(f'Monthly directory "{DIR_NAME}" already exists.\n')
        except PermissionError:
            with open('dir_creation_failed.txt', 'a') as dir_err_file:
                dir_err_file.write(f'Permission denied: Unable to create monthly dictionary: "{DIR_NAME}".\n')
        except Exception as e:
            with open('dir_creation_failed.txt', 'a') as dir_err_file:
                dir_err_file.write(f'An error occurred creating monthly dictionary: {e}\n')
    # Create the daily directory
    try:
        daily_DIR_NAME = DEST_PATH[:-1]
        mkdir(daily_DIR_NAME)
    except FileExistsError:
        with open('dir_creation_failed.txt', 'a') as dir_err_file:
                dir_err_file.write(f'Daily directory "{DIR_NAME}" already exists.\n')
    except PermissionError:
        with open('dir_creation_failed.txt', 'a') as dir_err_file:
                dir_err_file.write(f'Permission denied: Unable to create daily dictionary: "{DIR_NAME}".\n')
    except Exception as e:
        with open('dir_creation_failed.txt', 'a') as dir_err_file:
                dir_err_file.write(f'An error occurred creating daily dictionary: {e}\n')
    find_production()
    

'''
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
'''

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