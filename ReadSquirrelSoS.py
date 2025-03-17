import pyodbc

menu_ids = {
        "#1" : 353,
        "#2" : 597,
        "#4" : 605,
        "#5" : 662,
        "#13" : 346,
        "#14" : 407,
        "#18" : 430,
        "#22" : 345,
        "#23" : 424,
        "#26" : 632,
        "#27" : 375,
        "#30" : 393,
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
        "#100" : 648,
        "#123" : 398,
        "#234" : 5104,
        "#236" : 3828,
        "#246" : 7572,
        "#272" : 4792,
        "#420" : 584,
        "#422" : 8622,
        "#600" : 673,
        "#606" : 675,
        "#607" : 687,
        "#608" : 680,
        "#616" : 677,
        "#623" : 688,
        "#1000" : 4856,
        "Latke" : 1638,
        "KD" : 981,
        "KD MD" : 982,
        "KG" : 977,
        "KG MD" : 978,
        "Kid Brst" : 965,
        "Kid Brst MD" : 966,
        "Kid Chix" : 969,
        "Kid Chix MD" : 970,
        "Kid Ham" : 971,
        "Kid Ham MD" : 972,
        "Kid PB&J" : 979,
        "Kid PB&J MD" : 980,
        "Kid Sal" : 975,
        "Kid Sal MD" : 976,
        "Kid Tuna" : 967,
        "Kid Tuna MD" : 968,
        "Kid Turk" : 961,
        "Kid Turk MD" : 962,
        "Knish Chix" : ,
        "Knish Kasha" : ,
        "Knish Pastrami" : ,
        "Knish Potato" : ,
        "Zing Taters" : 905 
    }

def get_check(check_id):
    query = f'''
    SELECT ch.CheckNo, ct.Name, ci.MenuID, ci.Quantity
    FROM ((Squirrel.dbo.X_CheckHeader AS ch
    JOIN Squirrel.dbo.X_CheckTable AS ct ON ch.CheckID = ct.CheckID)
    JOIN Squirrel.dbo.X_CheckItem AS ci ON ch.CheckID = ci.CheckID)
    WHERE ch.CheckID = {check_id}
    '''
    return query

def get_check_data(check_id):
    SERVER = 'SQUIRREL-2012'
    DATABASE = 'Squirrel'
    connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;TrustServerCertificate=yes;'
    conn = pyodbc.connect(connectionString)
    cursor = conn.cursor()
    cursor.execute(get_check(check_id))
    rows = cursor.fetchall()
    check_data = {}
    check_no = rows[0][0]
    check_name = rows[0][1].strip()
    qty = 0
    for row in rows:
        if row[2] in menu_ids.values(): # item is a SL item
            qty += int(row[-1])
    check_data[check_no] = [check_name, qty]
    return check_data
