import pyodbc
import os
from dotenv import load_dotenv
from datetime import datetime

backline_ids = {
    # 9981 : 'SOM AUG 25',
    # 10012 : 'SOM SEP 25',
    # 10065 : 'SOM OCT 25',
    # 10121 : 'SOM NOV 25',
    # 10257 : 'SOM DEC 25',
    # 9725 : 'SOM JAN 26',
    # 10347 : 'SOM FEB 26',
    10377 : 'SOM MAR',
    1146 : 'CUSTOM',
    353 : '#1',
    379 : '#2',
    350 : '#4',
    662 : '#5',
    346 : '#13',
    407 : '#14',
    430 : '#18',
    345 : '#22',
    424 : '#23',
    632 : '#26',
    375 : '#27',
    426 : '#34',
    656 : '#36',
    387 : '#40',
    374 : '#48',
    612 : '#51',
    614 : '#54',
    652 : '#55',
    5382 : '#64',
    634 : '#66',
    366 : '#73',
    618 : '#74',
    654 : '#75',
    4006 : '#79',
    365 : '#81',
    4439 : '#81.5',
    413 : '#82',
    616 : '#84',
    610 : '#85',
    377 : '#88',
    384 : '#97',
    398 : '#123',
    5104 : '#234',
    3828 : '#236',
    7572 : '#246',
    4792 : '#272',
    4856 : '#1000',
    1638 : 'Latke',
    977 : 'KG',
    978 : 'KG MD',
    965 : 'Kid Brst',
    966 : 'Kid Brst MD',
    963 : 'Kid CB',
    964 : 'Kid CB MD',
    969 : 'Kid Chix',
    970 : 'Kid Chix MD',
    971 : 'Kid Ham',
    972 : 'Kid Ham MD',
    975 : 'Kid Sal',
    976 : 'Kid Sal MD',
    967 : 'Kid Tuna',
    968 : 'Kid Tuna MD',
    961 : 'Kid Turk',
    962 : 'Kid Turk MD',
    905 : 'Zing Taters'
}
pv_ids = {
    393 : '#30',
    648 : '#100',
    584 : '#420',
    8622 : '#422',
    673 : '#600',
    675 : '#606',
    687 : '#607',
    680 : '#608',
    677 : '#616',
    688 : '#623',
    981 : 'KD',
    982 : 'KD MD',
    979 : 'Kid PB&J',
    980 : 'Kid PB&J MD',
    3089 : 'Adult PB&J',
    4444 : 'Knish Heated',
    4443 : 'Knish 3 Pack',
    # Begin defunct knish ids #
    # 4089 : 'Knish Chix',
    # 4090 : 'Knish Kasha',
    # 4435 : 'Knish Pastrami',
    # 2129 : 'Knish Potato'
    # End defunct knish ids #
}

def get_check(cursor, start, end):
    query = '''
    SELECT ch.CheckNo, ct.Name, ci.SaleTime, ci.MenuID, ci.Quantity
    FROM ((Squirrel.dbo.X_CheckHeader AS ch
    JOIN Squirrel.dbo.X_CheckTable AS ct ON ch.CheckID = ct.CheckID)
    JOIN Squirrel.dbo.X_CheckItem AS ci ON ch.CheckID = ci.CheckID)
    WHERE ci.SaleTime BETWEEN ? AND ?
    ORDER BY ci.SaleTime ASC
    '''
    cursor.execute(query, start, end)
    return cursor.fetchall()

def get_check_data(start, end):
    load_dotenv()
    SERVER = os.getenv('SERVER')
    DATABASE = os.getenv('DB')
    connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;TrustServerCertificate=yes;'
    checks = {}
    with pyodbc.connect(connectionString) as conn:
        cursor = conn.cursor()
        start_time = datetime.strptime(start, '%Y%m%d%H%M%S')
        end_time = datetime.strptime(end, '%Y%m%d%H%M%S')
        rows = get_check(cursor, start_time, end_time) # List of all query results
        if rows == []: # No checks for this 5 minute period
            return
        for check in rows:
            sale_time = check[2]
            # if not check[1]: # No name
            #     print(check[0])
            #     continue
            if sale_time not in checks: 
                checks[sale_time] = {'check_no' : check[0], 'check_name' : check[1].strip(), 'menu_ids' : {check[3] : int(check[4])}}
            else:
                if check[3] in checks[sale_time]['menu_ids']:
                    checks[sale_time]['menu_ids'][check[3]] += check[4]
                else:
                    checks[sale_time]['menu_ids'][check[3]] = check[4]
    # Now checks is filled with every check entered between start and end #
    no_make_id = [595, 8291]
    checks_data = {}
    # check_data: check_no, check_name, menu_ids (menu_id, qty), total_price
    for check, check_data in checks.items():
        has_start = has_finish = has_PV = False
        latke = knish = 0 # Every 4 latkes and knishes are rung in as one item
        check_qty = 0
        bl_items = pv_items = [] # Backline and PV items
        bl_qty = pv_qty = 0
        pv_qty = 0
        total_price = 0
        for menu_id, item_info in check_data['menu_ids'].items():
            if menu_id in backline_ids:
                qty = item_info[0]
                price = item_info[1]
                for i in range(qty):
                    bl_items.append(backline_ids[menu_id])
                total_price += price
                if menu_id == 1638: # Latke
                    latke += qty
                    continue
                check_qty += qty
                bl_qty += qty
                has_start = True
                has_finish = True
            elif menu_id in pv_ids:
                qty = item_info[0]
                price = item_info[1]
                for i in range(qty):
                    pv_items.append(pv_ids[menu_id])
                total_price += price
                if menu_id == 4444: # Ht'd Knish
                    knish += qty
                    continue
                if menu_id == 4443: # 3 Pk Knish
                    knish += qty * 3
                    continue
                check_qty += qty
                pv_qty += qty
                has_PV = True
        if latke:
            has_start = True
            has_finish = True
            while latke > 4:
                latke -= 4
                check_qty += 1
                bl_qty += 1
            check_qty += 1
            bl_qty += 1
        if knish:
            has_PV = True
            while knish > 4:
                knish -= 4
                check_qty += 1
                pv_qty += 1
            check_qty += 1
            pv_qty += 1
        if check_qty == 0: # Skip checks that don't have SL items
            continue
        sale_time = check.strftime('%Y%m%d%H%M%S')
        # Check No, Check Name, Check Qty, Has___, BLitems / PVitems #
        checks_data[sale_time] = [check_data['check_no'], check_data['check_name'], check_qty, total_price, (has_start, has_finish, has_PV), (bl_qty, pv_qty), (bl_items, pv_items)]
    # checks_data is now filled with the qty for each check (including empty checks)
    return checks_data