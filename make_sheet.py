from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font
import time

# Maybe add column for best production per hour?
def create_sheet(workbook_name, s_name, data):
    WORKBOOK = load_workbook(filename=workbook_name)
    WORKBOOK.create_sheet(s_name)
    SHEET = WORKBOOK[s_name]
    NUM_ROWS = 12
    NUM_COLS = 14
    SHEET.insert_rows(idx = 1, amount = NUM_ROWS)
    SHEET.insert_cols(idx = 1, amount = NUM_COLS)
    # For column headers
    SHEET['B1'] = 'Total'
    minute = 0
    end_min = minute + 5
    for col in SHEET.iter_cols(min_col = 3, max_col = 14):
        col[0].value = 'xx:{minute}-xx:{end_min}'.format(minute = f'0{minute}' if minute < 10 else minute, end_min = f'0{end_min}' if end_min < 10 else end_min) # Col header cells
        minute += 5
        end_min = minute + 5
    # For row filling
    hour = 10
    PRODS = data
    prods_i = 0
    for row in SHEET.iter_rows(min_row = 2, max_row = 11):
        # Handles row headers (Why use another loop outside of this one to do row headers when we already grab every data row here?)
        row_header = row[0]
        if hour >= 10 and hour < 12:
            row_header.value = f'{hour}AM'
            hour += 1
        elif hour == 12:
            row_header.value = '12PM'
            hour = 1
        else:
            row_header.value = f'{hour}PM'
            hour += 1
        # Fills "total" column
        total_col_cell = row[1]
        total_col_cell.value = f'=SUM(C{row[0].row}:N{row[0].row})'
        # Fills data for each row
        for i in range(2, NUM_COLS): # From start of data column to last data column
            if prods_i >= len(PRODS): # No more data to use to fill
                row[i].value = 0
            else:
                row[i].value = PRODS[prods_i]
                prods_i += 1
    SHEET['A12'] = 'Total'
    SHEET['B12'] = f'=SUM(B2:B{NUM_ROWS - 1})' # Last row of data
    SHEET.freeze_panes = 'C13'
    # To autoformat column widths and centering
    for col in SHEET.columns:
        max_len = 0
        col_letter = col[0].column_letter
        for cell in col:
            cell.alignment = Alignment(horizontal = 'center')
            cell.font = Font(name = 'Arial', size = 16)
            if len(str(cell.value)) > max_len:
                max_len = len(str(cell.value))
            else:
                continue
        adj_width = (max_len + 4) # Based on font size 16
        SHEET.column_dimensions[col_letter].width = adj_width
    SHEET['B12'].font = Font(name = 'Arial', size = 16, bold = True)
    if 'Button_Data' not in workbook_name: # daily output file
        if 'Summary' in WORKBOOK.sheetnames:
            WORKBOOK.remove(WORKBOOK['Summary'])
    WORKBOOK.save(filename=workbook_name)

def create_workbook(wb):
    workbook = Workbook()
    workbook.active.title = 'Summary'
    workbook.save(filename=wb)

def generate_daily_sheet(wb_name, data, new_wb, sheet_name):
    if new_wb:
        create_workbook(wb_name)
    just_prods = [int(float(data[d])) for d in data]
    create_sheet(wb_name, sheet_name, just_prods)

# Tester Code #
#create_workbook()
#generate_daily_sheet(clean_stamps.get_cleaned_stamps())
'''
workbook = Workbook()
workbook.active.title = 'Summary'
workbook.save(filename = 'Mar_2024_Button_Data.xlsx')
for i in range(5, 31):
#with open('03_30_2024 Sandwich Report', 'r') as the_file:
    with open('03_{day}_2024 Sandwich Report'.format(day = f'0{i}' if i < 10 else i)) as the_file:
        stamps = []
        for line in the_file.readlines():
            if line == '\n':
                continue
            line_contents = line.split()
            if line_contents[0] == 'Item': # A timestamp entry                                                                                                                           
                timestamp = line_contents[2]
                hour = timestamp[:2]
                if line_contents[-1] == 'PM' and hour != '12': # 1pm or later                                                                                                            
                    hour = int(hour)
                    hour += 12
                    hour = str(hour)
                minute = timestamp[3:5]
                second = timestamp[6:8]
                stamps.append(hour + minute + second)
        print(f'03_{i} started')
        create_sheet('Mar_2024_Button_Data.xlsx', stamps, f'03_{i}_2024')
        print('Sheet finished!')
'''

'''
workbook = load_workbook(filename=time.strftime('%m_%Y_Button_Data'))
sheets = workbook.sheetnames # All sheets in workbook
workbook.create_sheet('Something') # title should be the date of the data
sheet = workbook.active # first sheet in workbook
# Cycle through and check if cell has a value greater than x (15, 18, etc.): if so, bold/highlight it
# ^ Should create a template to style these cells
# Need from openpyxl.styles.differential import DifferentialStyle, from openpyxl.formatting.rule import Rule
'''
'''
from openpyxl.styles import PatternFill
>>> from openpyxl.styles.differential import DifferentialStyle
>>> from openpyxl.formatting.rule import Rule

>>> red_background = PatternFill(fgColor="00FF0000")
>>> diff_style = DifferentialStyle(fill=red_background)
>>> rule = Rule(type="expression", dxf=diff_style)
>>> rule.formula = ["$H1<3"]
>>> sheet.conditional_formatting.add("A1:O100", rule)
>>> workbook.save("sample_conditional_formatting.xlsx")

Check these out too:
ColorScale
IconSet
DataBar (like a progress bar)
'''