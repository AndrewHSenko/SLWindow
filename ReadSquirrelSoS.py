import pyodbc

menu_ids = {
        "#1" : 353,
        "#2" : 597,
        "#4" : 605,
        "#5" : ,
        "#13" : ,
        "#14" : ,
        "#18" : ,
        "#22" : ,
        "#23" : ,
        "#26" : ,
        "#27" : ,
        "#30" : ,
        "#34" : ,
        "#36" : ,
        "#40" : ,
        "#48" : ,
        "#51" : ,
        "#54" : ,
        "#55" : ,
        "#64" : ,
        "#66" : ,
        "#73" : ,
        "#74" : ,
        "#75" : ,
        "#79" : ,
        "#81" : ,
        "#81.5" : ,
        "#82" : ,
        "#84" : ,
        "#85" : ,
        "#88" : ,
        "#97" : ,
        "#100" : ,
        "#123" : ,
        "#234" : ,
        "#236" : ,
        "#246" : ,
        "#272" : ,
        "#420" : ,
        "#422" : ,
        "#600" : ,
        "#606" : ,
        "#607" : ,
        "#608" : ,
        "#616" : ,
        "#623" : ,
        "#1000" : ,
        "Latke" : ,
        "KD" : ,
        "KG" : ,
        "Kid Sandwich" : ,
        "Knish Chix" : ,
        "Knish Kasha" : ,
        "Knish Pastrami" : ,
        "Knish Potato" : ,
        "PB&J" : 
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
