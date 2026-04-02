import json

with open('latkes.txt', 'r') as l:
    l.readlines()

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