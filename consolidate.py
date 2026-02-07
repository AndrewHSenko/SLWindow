import ReadQSRSoS as qsr
import ReadSquirrelSoS as squirrel
import overlay
import get_pu_window as pu
import make_sheet
import make_graph
import time
import json
import numpy as np
from os import mkdir

from decimal import Decimal
import ast
from copy import deepcopy

# HEADERS #
MONTH_H = '12_06_2025' # time.strftime('%m_%d_%Y')
M_NAME_H = 'Dec_06_2025' # time.strftime('%b_%d_%Y')
NO_DAY = 'Dec_2025' # time.strftime('%b_%Y')
WEEK_NUM = 1
SHEET_NUM = 5
DATE = '20251206'
WINDOW_START = 'M5'
WINDOW_END = 'M125' # M135
ACTUAL_START = 'O5'
ACTUAL_END = 'O125' # O135
NUM_ROWS = 12 # 13
START_HOUR = 10 # 9
# DATE = time.strftime('%Y%m%d')

DIR_NAME = "G:/Window Data/" + time.strftime('%m_%Y')

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
            for d in data[:-1]:
                saletime = d[0]
                name = d[1]
                bl_items = ['None'] if not d[2] else d[2]
                pv_items = ['None'] if not d[3] else d[3]
                qty = int(d[-1])
                window_file.write(f'+ {saletime} ({name}): {qty}\n')
                window_file.write(f'   Backline Items:\n')
                for item in bl_items:
                    window_file.write(f'   - {item}\n')
                window_file.write(f'   PV Items:\n')
                for item in pv_items:
                    window_file.write(f'   - {item}\n')
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

def create_sheets(sums=None, foh_items=None, pu_window=None, pu_actual=None, ssums=None, fsums=None, pvsums=None, fpvsums=None):
    monthly_wb = False
    if time.strftime('%d') == '01':
        monthly_wb = True
    monthly_window_wb_name = f'{DIR_NAME}/{NO_DAY}_Window_Data.xlsx'
    daily_window_wb_name = f'{DEST_PATH}{MONTH_H}_Window.xlsx'
    daily_station_wb_name = f'{DEST_PATH}{MONTH_H}_Stations.xlsx'
    window_name = MONTH_H + '_Window_Items'
    start_name = MONTH_H + '_Start_Items'
    finish_name = MONTH_H + '_Finish_Items'
    pv_name = MONTH_H + '_PV_Items'
    fpv_name = MONTH_H + '_FPV_Items'
    # Window Data #
    if sums:
        smoothed_sums = {}
        desired_intvls = np.linspace(0.5, 109.5, 110, endpoint=True)
        smoothed = np.interp(desired_intvls, np.linspace(0, 110, 111, endpoint=True), [int(float(x)) for x in sums.values()])
        for i in range(len(smoothed)):
            smoothed_sums[i] = smoothed[i]
        print('On Sums')
        make_sheet.generate_daily_sheet(monthly_window_wb_name, sums, monthly_wb, window_name) # To add to monthly workbook
        make_graph.make_daily_prod(monthly_window_wb_name, sums, window_name)
        make_sheet.generate_daily_sheet(daily_window_wb_name, sums, True, window_name, NUM_ROWS, START_HOUR) # To add to daily workbook
        make_graph.make_daily_prod(daily_window_wb_name, sums, window_name, 'Expo Items/5 mins', MONTH_H, START_HOUR)
        make_graph.make_daily_prod(daily_window_wb_name, smoothed_sums, f'{window_name} Smoothed', 'Expo Items/5 mins', MONTH_H, START_HOUR, smooth_it=True)
    # Start Data #
    if ssums:
        make_sheet.generate_daily_sheet(monthly_window_wb_name, ssums, monthly_wb, finish_name) # To add to monthly workbook
        make_graph.make_daily_prod(monthly_window_wb_name, ssums, finish_name)
        make_sheet.generate_daily_sheet(daily_station_wb_name, ssums, True, start_name, NUM_ROWS, START_HOUR) # To add to daily workbook
        make_graph.make_daily_prod(daily_station_wb_name, ssums, start_name, 'Start Items/5 mins', MONTH_H, START_HOUR)
    # Finish Data #
    if fsums:
        make_sheet.generate_daily_sheet(monthly_window_wb_name, sums, monthly_wb, finish_name) # To add to monthly workbook
        make_graph.make_daily_prod(monthly_window_wb_name, sums, finish_name)
        make_sheet.generate_daily_sheet(daily_station_wb_name, fsums, False, finish_name, NUM_ROWS, START_HOUR) # To add to daily workbook
        make_graph.make_daily_prod(daily_station_wb_name, fsums, finish_name, 'Finish Items/5 mins', MONTH_H, START_HOUR)
    # PV Data #
    if pvsums:
        make_sheet.generate_daily_sheet(monthly_window_wb_name, sums, monthly_wb, pv_name) # To add to monthly workbook
        make_graph.make_daily_prod(monthly_window_wb_name, sums, pv_name)
        make_sheet.generate_daily_sheet(daily_station_wb_name, pvsums, False, pv_name, NUM_ROWS, START_HOUR) # To add to daily workbook
        make_graph.make_daily_prod(daily_station_wb_name, pvsums, pv_name, 'PV Items/5 mins', MONTH_H, START_HOUR)
    # FPV Data #
    if fpvsums:
        make_sheet.generate_daily_sheet(monthly_window_wb_name, sums, monthly_wb, pv_name) # To add to monthly workbook
        make_graph.make_daily_prod(monthly_window_wb_name, sums, pv_name)
        make_sheet.generate_daily_sheet(daily_station_wb_name, fpvsums, False, fpv_name, NUM_ROWS, START_HOUR) # To add to daily workbook
        make_graph.make_daily_prod(daily_station_wb_name, fpvsums, fpv_name, 'Finish & PV Items/5 mins', MONTH_H, START_HOUR)
    # FoH Data #
    monthly_foh_wb_name = f'{DIR_NAME}/{NO_DAY}_FoH_Data.xlsx'
    daily_foh_wb_name = f'{DEST_PATH}{MONTH_H}_FoH.xlsx'
    # Number of Tickets/Checks (retired) #
    # foh_checks_name = MONTH_H + '_Checks'
    foh_items_name = MONTH_H + '_FOH_Items'
    # if foh_checks:
    #     make_sheet.generate_daily_sheet(monthly_foh_wb_name, foh_checks, monthly_wb, foh_checks_name) # To add to monthly workbook
    #     make_graph.make_daily_prod(monthly_foh_wb_name, foh_checks, foh_checks_name)
    #     make_sheet.generate_daily_sheet(daily_foh_wb_name, foh_checks, True, foh_checks_name) # To add to daily workbook
    #     make_graph.make_daily_prod(daily_foh_wb_name, foh_checks, foh_checks_name)
    # Items #
    if foh_items:
        print('On FoH Items')
        make_sheet.generate_daily_sheet(monthly_foh_wb_name, foh_items, monthly_wb, foh_items_name) # To add to monthly workbook
        make_graph.make_daily_prod(monthly_foh_wb_name, foh_items, foh_items_name)
        make_sheet.generate_daily_sheet(daily_foh_wb_name, foh_items, True, foh_items_name, NUM_ROWS, START_HOUR) # To add to daily workbook
        make_graph.make_daily_prod(daily_foh_wb_name, foh_items, foh_items_name, 'FoH Entries/5 mins', MONTH_H, START_HOUR)
    daily_pending_wb_name = f'{DEST_PATH}{MONTH_H}_Pending.xlsx'
    pending_items_name = f'{MONTH_H}_Pending'
    if sums and foh_items and pu_window and pu_actual:
        ratio = overlay.ratio(sums, foh_items)
        make_sheet.generate_daily_sheet(daily_pending_wb_name, ratio, True, pending_items_name, NUM_ROWS, START_HOUR)
        make_graph.make_daily_prod(daily_pending_wb_name, ratio, pending_items_name, pending_items_name, 'Pending Items', START_HOUR, ylimit=150)
        if sums and fpvsums:
            overlay.create_overlay(daily_station_wb_name, fpvsums, None, pu_window, pu_actual, MONTH_H, f'{MONTH_H} Finish/PV', 'Finish & PV', '', START_HOUR) # GO HERE TO TOGGLE PU WINDOW #
            overlay.create_overlay(daily_station_wb_name, sums, fpvsums, None, None, f'{MONTH_H} Finish_Expo', f'{MONTH_H} Finish_Expo', 'Expo', 'Finish & PV', START_HOUR)
        overlay.create_overlay(daily_pending_wb_name, ratio, None, pu_window, pu_actual, pending_items_name, pending_items_name, 'Pending Items', '', START_HOUR, ylimit=100)
        overlay.create_overlay(daily_window_wb_name, sums, None, pu_window, pu_actual, MONTH_H, MONTH_H, 'Expo', '', START_HOUR) # GO HERE TO TOGGLE PU WINDOW #
        overlay.create_overlay(daily_window_wb_name, smoothed_sums, None, pu_window, pu_actual, f'{MONTH_H} Smoothed', f'{MONTH_H} Smoothed', 'Expo (Smoothed)', '', START_HOUR)
        overlay.create_overlay(daily_foh_wb_name, None, foh_items, pu_window, pu_actual, MONTH_H, MONTH_H, '', 'FoH Entries', START_HOUR)
    # Will add return statement with try/catch blocks #

# def download_checks(ac):
#     rawchecks = deepcopy(ac)
#     with open(f'{MONTH_H}_Raw_Checks.txt', 'w') as wfile:
#         for saletime in rawchecks:
#             curr_check = rawchecks[saletime]
#             curr_check['Qty'] = str(curr_check['Qty'])
#             curr_check['has_start'] = str(curr_check['has_start'])
#             curr_check['has_finish'] = str(curr_check['has_finish'])
#             curr_check['has_pv'] = str(curr_check['has_pv'])
#             curr_check['bl_qty'] = str(curr_check['bl_qty'])
#             curr_check['pv_qty'] = str(curr_check['pv_qty'])
#             curr_check['BL Items'] = str(curr_check['BL Items'])
#             curr_check['PV Items'] = str(curr_check['PV Items'])
#         json.dump(rawchecks, wfile)

# def read_in_checks(wfile):
#     rawchecks = json.load(wfile)
#     for saletime in rawchecks:
#         curr_check = rawchecks[saletime]
#         curr_check['Qty'] = Decimal(curr_check['Qty'])
#         curr_check['has_start'] = True if curr_check['has_start'] == 'True' else False
#         curr_check['has_finish'] = True if curr_check['has_finish'] == 'True' else False
#         curr_check['has_pv'] = True if curr_check['has_pv'] == 'True' else False
#         curr_check['bl_qty'] = Decimal(curr_check['bl_qty'])
#         curr_check['pv_qty'] = Decimal(curr_check['pv_qty'])
#         curr_check['BL Items'] = ast.literal_eval(curr_check['BL Items'])
#         curr_check['PV Items'] = ast.literal_eval(curr_check['PV Items'])
#     return rawchecks

def create_text(window, w_name):
    raw_data = create_raw_text(window, f'{w_name} Window')
    sums = raw_data[0]
    stotal = raw_data[1]
    create_window_text(sums, stotal, f'{w_name} Window')
    return sums

# To update window
def tabulate(active_checks):
    window = {}
    s_window = {}
    f_window = {}
    pv_window = {}
    fpv_window = {}
    entered = {}
    # missing_anchor_bumps = []
    # Collect data #
    start_time = int(f'{START_HOUR}00')
    while start_time != 1915:
        end_time = start_time + 5 if str(start_time)[-2:] != '55' else start_time + 45 # To fix xx:60 situations
        window_start, window_end = f'{DATE}{start_time}00', f'{DATE}{end_time}00'
        easier_win_start = start_time if start_time < 1300 else start_time - 1200
        easier_win_end = end_time if end_time < 1300 else end_time - 1200
        intvl = str(easier_win_start)[:-2]+ ':' + str(easier_win_start)[-2:] + ' - ' + str(easier_win_end)[:-2] + ':' + str(easier_win_end)[-2:]
        window[intvl] = []
        s_window[intvl] = [] # Start
        f_window[intvl] = [] # Finish
        pv_window[intvl] = [] # Platesville
        fpv_window[intvl] = [] # Start & Finish
        entered[intvl] = []
        for check in active_checks:   
            anchor = active_checks[check]['ANCHOR']
            # if not anchor: 
            #     if active_checks[check] not in missing_anchor_bumps:
            #         missing_anchor_bumps.append(active_checks[check])
            #         with open(DEST_PATH + M_NAME_H + '_Missing_Bumps.txt', 'a') as badchecks_file:
            #             badchecks_file.write(f'Missing Anchor bump for:\n| {active_checks[check]['Name']} | Qty: {active_checks[check]['Qty']}\n')
            #     continue
            check_saletime = f'{check[-6:-4]}:{check[-4:-2]}:{check[-2:]}'
            if int(window_start) < int(check) <= int(window_end): # FoH Entries
                entered[intvl].append([check_saletime, active_checks[check]['Name'], active_checks[check]['BL Items'], active_checks[check]['PV Items'], active_checks[check]['Qty']])
            if int(window_start) < int(anchor) <= int(window_end): # Anchor Bumps
                window[intvl].append((check_saletime, active_checks[check]['Name'], active_checks[check]['BL Items'], active_checks[check]['PV Items'], active_checks[check]['Qty']))
            if active_checks[check]['has_start'] and active_checks[check]['HOT START']:
                start = active_checks[check]['HOT START']
                if int(window_start) < int(start) <= int(window_end): # Start Bumps
                    s_window[intvl].append((check_saletime, active_checks[check]['Name'], active_checks[check]['BL Items'], active_checks[check]['PV Items'], active_checks[check]['bl_qty']))
            if active_checks[check]['has_finish'] and active_checks[check]['HOT FINISH']:
                finish = active_checks[check]['HOT FINISH']
                if int(window_start) < int(finish) <= int(window_end):
                    f_window[intvl].append((check_saletime, active_checks[check]['Name'], active_checks[check]['BL Items'], active_checks[check]['PV Items'], active_checks[check]['bl_qty']))
                    if active_checks[check]['has_pv']: # So Finish & PV
                        pv = active_checks[check]['PLATESVILLE']
                        if finish > pv: # Bumped at Finish last
                            fpv_window[intvl].append((check_saletime, active_checks[check]['Name'], active_checks[check]['BL Items'], active_checks[check]['PV Items'], active_checks[check]['Qty']))  
                    else: # Just Finish bumps
                        fpv_window[intvl].append((check_saletime, active_checks[check]['Name'], active_checks[check]['BL Items'], active_checks[check]['PV Items'], active_checks[check]['Qty']))
            if active_checks[check]['has_pv'] and active_checks[check]['PLATESVILLE']:
                pv = active_checks[check]['PLATESVILLE']
                if int(window_start) < int(pv) <= int(window_end): # PV Bumps
                    pv_window[intvl].append((check_saletime, active_checks[check]['Name'], active_checks[check]['BL Items'], active_checks[check]['PV Items'], active_checks[check]['pv_qty']))
                    if active_checks[check]['has_finish']: # So Finish & PV
                        finish = active_checks[check]['HOT FINISH']
                        if pv > finish: # Bumped at PV last
                            fpv_window[intvl].append((check_saletime, active_checks[check]['Name'], active_checks[check]['BL Items'], active_checks[check]['PV Items'], active_checks[check]['Qty']))
                    else: # Just PV bumps
                        fpv_window[intvl].append((check_saletime, active_checks[check]['Name'], active_checks[check]['BL Items'], active_checks[check]['PV Items'], active_checks[check]['Qty']))
        sum = 0
        for entry in window[intvl]:
            sum += entry[-1]
        window[intvl].append(sum)
        sum = 0
        for entry in s_window[intvl]:
            sum += entry[-1]
        s_window[intvl].append(sum)
        sum = 0
        for entry in f_window[intvl]:
            sum += entry[-1]
        f_window[intvl].append(sum)
        sum = 0
        for entry in pv_window[intvl]:
            sum += entry[-1]
        pv_window[intvl].append(sum)
        sum = 0
        for entry in fpv_window[intvl]:
            sum += entry[-1]
        fpv_window[intvl].append(sum)
        start_time += 5
        if str(start_time)[-2:] == '60':
            start_time += 40
    # Tabulate data #
    station_sums = []
    station_sums.append(create_text(window, 'Expo'))
    station_sums.append(create_text(s_window, 'Start'))
    station_sums.append(create_text(f_window, 'Finish'))
    station_sums.append(create_text(pv_window, 'PV'))
    station_sums.append(create_text(fpv_window, 'FPV'))
    qtys = create_foh_entries_text(entered)
    check_qtys = {}
    item_qtys = {}
    for ivl, qty in qtys.items():
        check_qtys[ivl] = qty[0]
        item_qtys[ivl] = qty[1]
    pu_window, pu_actual = pu.get_data(WEEK_NUM, SHEET_NUM, WINDOW_START, WINDOW_END, ACTUAL_START, ACTUAL_END)
    create_sheets(station_sums[0], item_qtys, pu_window, pu_actual, station_sums[1], station_sums[2], station_sums[3], station_sums[4])

def find_production():
    qsr_data = qsr.get_QSR_data() #'20250602162500'
    active_checks = {}
    # Collect data #
    start_time = int(f'{START_HOUR}00') # Not using %I to make it easier to handle AM to PM hour change
    while start_time != 1915:
        end_time = start_time + 5 if str(start_time)[-2:] != '55' else start_time + 45 # To fix xx:60 situations
        check_start = f'{DATE}{start_time}00' if start_time >= 1000 else f'{DATE}0{start_time}00'
        check_end = f'{DATE}{end_time}00'if end_time >= 1000 else f'{DATE}0{end_time}00'
        sq_checks = squirrel.get_check_data(check_start, check_end)
        # sq_checks now has all checks within 5 minute window that have SL items
        # sq_checks key: saletime
        # sq_checks values: check_no, check_name, qty #
        if sq_checks:
            for sq_check in sq_checks:
                if sq_check not in active_checks : # Add check from Squirrel to active_checks
                    active_checks[sq_check] = {
                        'Name': sq_checks[sq_check][1],
                        'Qty': sq_checks[sq_check][2],
                        'has_start': sq_checks[sq_check][3][0],
                        'has_finish': sq_checks[sq_check][3][1],
                        'has_pv': sq_checks[sq_check][3][2],
                        'bl_qty': sq_checks[sq_check][4][0],
                        'pv_qty': sq_checks[sq_check][4][1],
                        'HOT START' : '',
                        'HOT FINISH' : '',
                        'PLATESVILLE': '',
                        'ANCHOR' : '',
                        'BL Items' : sq_checks[sq_check][5][0],
                        'PV Items' : sq_checks[sq_check][5][1]
                    }
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
    # download_checks(active_checks)
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