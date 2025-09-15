import pyodbc
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

finish_ids = {
    "SOM SEPT" : 10012,
    # "SOM AUG" : 9981,
    # "SOM JULY" : 9950,
    # "SOM JUNE" : 9921,
    # "SOM MAY" : 9887,
    # "SOM MARCH" : 9798,
    # "SOM APRIL" : 9849
    "CUSTOM" : 1146,
    "#1" : 353,
    "#2" : 379,
    "#4" : 350,
    "#5" : 662,
    "#13" : 346,
    "#14" : 407,
    "#18" : 430,
    "#22" : 345,
    "#23" : 424,
    "#26" : 632,
    "#27" : 375,
    "#34" : 426,
    "#36" : 656,
    "#40" : 387,
    "#48" : 374,
    "#51" : 612,
    "#54" : 614,
    "#55" : 652,
    "#64" : 5382,
    "#66" : 634,
    "#73" : 366,
    "#74" : 618,
    "#75" : 654,
    "#79" : 4006,
    "#81" : 365,
    "#81.5" : 4439,
    "#82" : 413,
    "#84" : 616,
    "#85" : 610,
    "#88" : 377,
    "#97" : 384,
    "#123" : 398,
    "#234" : 5104,
    "#236" : 3828,
    "#246" : 7572,
    "#272" : 4792,
    "#1000" : 4856,
    "Adult PB&J" : 3089,
    "Latke" : 1638,
    "KG" : 977,
    "KG MD" : 978,
    "Kid Brst" : 965,
    "Kid Brst MD" : 966,
    "Kid CB" : 963,
    "Kid CB MD" : 964,
    "Kid Chix" : 969,
    "Kid Chix MD" : 970,
    "Kid Ham" : 971,
    "Kid Ham MD" : 972,
    "Kid Sal" : 975,
    "Kid Sal MD" : 976,
    "Kid Tuna" : 967,
    "Kid Tuna MD" : 968,
    "Kid Turk" : 961,
    "Kid Turk MD" : 962,
    "Zing Taters" : 905
    }
pv_ids = {
    "#30" : 393,
    "#100" : 648,
    "#420" : 584,
    "#422" : 8622,
    "#600" : 673,
    "#606" : 675,
    "#607" : 687,
    "#608" : 680,
    "#616" : 677,
    "#623" : 688,
    "KD" : 981,
    "KD MD" : 982,
    "Kid PB&J" : 979,
    "Kid PB&J MD" : 980,
    "Knish Heated" : 4444,
    "Knish 3 Pack" : 4443
    # Specific Knishes should be defunct #
    # "Knish Chix" : 4089,
    # "Knish Kasha" : 4090,
    # "Knish Pastrami" : 4435,
    # "Knish Potato" : 2129,
    # End defunct knishes #
}

checks = {}

def get_check(start, end):
    query = f'''
    SELECT ch.CheckNo, ct.Name, ci.SaleTime, ci.MenuID, ci.Quantity
    FROM ((Squirrel.dbo.X_CheckHeader AS ch
    JOIN Squirrel.dbo.X_CheckTable AS ct ON ch.CheckID = ct.CheckID)
    JOIN Squirrel.dbo.X_CheckItem AS ci ON ch.CheckID = ci.CheckID)
    WHERE ci.SaleTime BETWEEN '{start}' AND '{end}'
    ORDER BY ci.SaleTime ASC
    '''
    return query

def get_check_data(start, end):
    SERVER = os.getenv('SERVER')
    DATABASE = os.getenv('DB')
    connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;TrustServerCertificate=yes;'
    with pyodbc.connect(connectionString) as conn:
        cursor = conn.cursor()
        start_time = datetime.strptime(start, '%Y%m%d%H%M%S')
        end_time = datetime.strptime(end, '%Y%m%d%H%M%S')
        cursor.execute(get_check(start_time, end_time))
        rows = cursor.fetchall() # Could iterate using fetchone, but # of rows should never be too large
        if rows == []:
            return
        for check in rows:
            sale_time = check[2]
            if sale_time not in checks: 
                checks[sale_time] = {'check_no' : check[0], 'check_name' : check[1].strip(), 'menu_ids' : {check[3] : int(check[4])}}
            else:
                if check[3] in checks[sale_time]['menu_ids']:
                    checks[sale_time]['menu_ids'][check[3]] += check[4]
                else:
                    checks[sale_time]['menu_ids'][check[3]] = check[4]
    # Now checks is filled with every check entered between start and end #
    checks_data = {}
    for check, check_data in checks.items():
        has_finish = False
        has_PV = False
        latke = 0 # Every 4 latkes are rung in as one item
        knish = 0 # Every 4 knishes are rung in as one item
        check_qty = 0
        for menu_id, qty in check_data['menu_ids'].items():
            if menu_id in finish_ids.values():
                if menu_id == 1638: # Latke
                    latke += qty
                    continue
                check_qty += qty
                has_finish = True
            elif menu_id in pv_ids.values():
                if menu_id == 4444: # Ht'd Knish
                    knish += qty
                    continue
                if menu_id == 4443: # 3 Pk Knish
                    knish += qty * 3
                    continue
                check_qty += qty
                has_PV = True
        if latke:
            while latke > 4:
                latke -= 4
                check_qty += 1
            check_qty += 1
        if knish:
            while knish > 4:
                knish -= 4
                check_qty += 1
            check_qty += 1
        if check_qty == 0: # Skip checks that don't have SL items
            continue
        sale_time = check.strftime('%Y%m%d%H%M%S')
        checks_data[sale_time] = [check_data['check_no'], check_data['check_name'], check_qty, (has_finish, has_PV)]
    # checks_data is now filled with the qty for each check (including empty checks)
    return checks_data