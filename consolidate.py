import ReadQSRSoS as qsr
import ReadSquirrelSoS as squirrel
import time

# Crontab should run this script every 5 minutes between 10:35am and 7:25pm

start_time = time.strftime('%H%M') # Not using %I to make it easier to handle AM to PM hour change
end_time = start_time += 5 if start_time[-2:] != '60' else start_time += 40 # To fix xx:60 situations
five_min_prod = 0

checks = qsr.get_QSR_data(start_time, end_time) # Should return all QSR parsed tickets between start and end time parameters
for check_num in checks:
    five_min_prod += squirrel.get_check_data(check_num)[-1] # Gets item count
# Do something with the five_min_prod #
if len(five_min_prod) == 1:
    five_min_prod = '0' + str(five_min_prod)
top_border = '-'*20 # Amount of dashes matches entry length
entry = f'| {start_time[:2]}:{start_time[2:]}-{end_time[:2]}:{end_time[2:]} | {five_min_prod} |'
with open('window.txt', 'a') as window:
    if start_time[2:] == '00':
        window.write('-'*12 + '\n')
        hour = time.strftime('%I') # For readability
        meridian = time.strftime('%p')
        window.write(f'| {hour}:{start_time[2:]} {meridian} |')
        window.write('-'*12 + '\n')
    window.write(top_border + '\n')
    window.write(entry + '\n')
