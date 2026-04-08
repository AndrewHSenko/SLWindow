import json

with open('03_29_latkes.txt', 'r') as l:
    total = 0
    window = 0
    for line in l.readlines():
        qty = float(line.split()[-1])
        total += qty
        while qty > 4:
            window += 1
            qty -= 4
        window += 1
    print(f'Total: {total}')
    print(f'Window: {window}')
with open('03_29_knishes.txt', 'r') as l:
    total = 0
    window = 0
    for line in l.readlines():
        qty = float(line.split()[-1])
        total += qty
        while qty > 3:
            window += 1
            qty -= 3
        window += 1
    print(f'Total: {total}')
    print(f'Window: {window}')


# with open('data.json') as json_file:
#     data = json.load(json_file)
#     prefix = '20260328'
#     start = '130000'
#     end = '133000'
#     qty = 0
#     for d, dat in data.items():
#         if int(d) > int(prefix + start) and int(d) < int(prefix + end):
#             print(d, dat['Qty'], dat['BL Items'], dat['PV Items'])
#             qty += int(dat['Qty'])
#     print(qty)

# import send_email

# send_email.send_stamps('C:/Users/Squirrel/Desktop/Window Data/11_28_2025')