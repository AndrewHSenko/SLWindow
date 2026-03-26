# import pyodbc
# from dotenv import load_dotenv
# import os
# from datetime import datetime

def get_cancelled_checks(cursor, start, end):
    query = '''
    SELECT ch.OpenDate, ch.CheckNo, ch.CheckID, vh.VoidID, iv.MenuID, iv.Quantity
    FROM ((Squirrel.dbo.X_CheckHeader AS ch
    JOIN Squirrel.dbo.X_VoidHeader AS vh ON ch.CheckID = vh.CheckID)
    JOIN Squirrel.dbo.X_ItemVoids AS iv ON vh.VoidID = iv.VoidID)
    WHERE ch.OpenDate BETWEEN ? AND ?
    ORDER BY OpenDate ASC
    '''
    cursor.execute(query, start, end)
    return cursor.fetchall()

# def test():
#     date = '20260220'
#     load_dotenv()
#     SERVER = os.getenv('SERVER')
#     DATABASE = os.getenv('DB')
#     connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;TrustServerCertificate=yes;'
#     with pyodbc.connect(connectionString) as conn:
#         cursor = conn.cursor()
#         start_time = datetime.strptime(f'{date}0700', '%Y%m%d%H%M%S')
#         end_time = datetime.strptime(f'{date}1900', '%Y%m%d%H%M%S')
#         cursor.execute(get_cancelled_checks(start_time, end_time))
#         rows = cursor.fetchall() # Could iterate using fetchone, but # of rows should never be too large
#         for row in rows:
#             print(row)