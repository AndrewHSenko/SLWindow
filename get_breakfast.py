import pyodbc
import os
from dotenv import load_dotenv
from datetime import datetime

breakfast_ids = {
    8001 : 'Cheese Burrito',
    8002 : 'Meat Burrito',
    9673 : 'CB Hash Burrito',
    9595 : 'Breakfast Sandwich',
    10299 : 'Bacon Side',
    2587 : 'Irish Oatmeal 1/2',
    562 : 'Oatmeal',
    9543 : 'Vanilla Yogurt'
}

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
    load_dotenv()
    SERVER = os.getenv('SERVER')
    DATABASE = os.getenv('DB')
    connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;TrustServerCertificate=yes;'
    checks = {}
    with pyodbc.connect(connectionString) as conn:
        cursor = conn.cursor()
        start_time = datetime.strptime(start, '%Y%m%d%H%M%S')
        end_time = datetime.strptime(end, '%Y%m%d%H%M%S')
        cursor.execute(get_check(start_time, end_time))
        rows = cursor.fetchall() # Could iterate using fetchone, but # of rows should never be too large
        if rows == []: # Empty row
            return
        for check in rows:
            sale_time = check[2]
            if not check[1]: # No name
                # print(check[0])
                continue
            if sale_time not in checks: 
                checks[sale_time] = {'check_no' : check[0], 'check_name' : check[1].strip(), 'menu_ids' : {check[3] : int(check[4])}}
            else:
                if check[3] in checks[sale_time]['menu_ids']:
                    checks[sale_time]['menu_ids'][check[3]] += check[4]
                else:
                    checks[sale_time]['menu_ids'][check[3]] = check[4]
    breakfast_items = {product : [] for product in breakfast_ids.values()}
    for check, check_data in checks.items():
        full_time = check.strftime('%Y%m%d%H%M%S')[-6:]
        sale_time = f'{full_time[:2]}:{full_time[2:4]}:{full_time[4:]}'
        for menu_id, qty in check_data['menu_ids'].items():
            if menu_id in breakfast_ids:
                for i in range(int(qty)):
                    breakfast_items[breakfast_ids[menu_id]].append(sale_time)
    return breakfast_items

def make_breakfast_text_file(b_date, b_data):
    # Key: Breakfast item names
    # Values: Sale time
    with open(f'{b_date}_Breakfast.txt', 'w') as b_file:
        b_file.write(f'{b_date}:\n')
        for item, saletimes in b_data.items():
            b_file.write(f'| {item} |\n')
            qty = 0
            for saletime in saletimes:
                b_file.write(f'   +{saletime}\n')
                qty += 1
            b_file.write(f'TOTAL SOLD: {qty}\n\n')

