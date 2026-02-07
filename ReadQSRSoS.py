import time

def parse_entry(raw_data):
    category_indexes = {
        'trans_num' : 0,
        'entered' : (9, 10, 11, 13, 14, 15),
        'screen_time' : 22,
        'station_name' : 23,
        'check_num' : 25,
        'check_name' : 26,
        'bumped' : (28, 29, 30, 32, 33, 34),
        'day_of_week' : 31, # 0 - Sunday
        'server_name' : 36,
        'prep_time' : 45,
        'destination' : 46
    }
    sos_data = {}
    for category, index in category_indexes.items():
        if type(index) == tuple: # for dates
            t_time = ''
            for ind in index:
                t = raw_data[ind]
                t_time += '0' + t if len(t) == 1 else t # fixes single-digit entries
            sos_data[category] = t_time # YYYYMMDDhhmmss
        else:
            sos_data[category] = raw_data[index]
    return sos_data

# Removes part (ex 1/2 or 2/2) from check name
def reformat_name(name): 
    new_name = ''
    if not name.split()[-1].isalpha():
        new_name = ' '.join(name.split()[:-1])
    else: # Handles if FoH enters Josh1/2 instead of Josh 1/2
        new_name = ' '.join(name.split()[:-1]) + ' '
        for c in name.split()[-1]:
            if c.isalpha():
                new_name += c
    return new_name

def find_entry(qsr_data, saletime, check_name):
    for d in qsr_data.values():
        new_saletime = '' # For QSR entry
        new_hour = int(d['entered'][-6:-4])
        new_min = int(d['entered'][-4:-2])
        new_sec = int(d['entered'][-2:]) - 1
        if new_sec < 0:
            new_sec = 59
            new_min -= 1
            if new_min < 0:
                new_min = 59
                new_hour -= 1
        # Converts single digit times to double digit if needed
        if len(str(new_hour)) == 1:
            new_hour = '0' + str(new_hour)
        if len(str(new_min)) == 1:
            new_min = '0' + str(new_min)
        if len(str(new_sec)) == 1:
            new_sec = '0' + str(new_sec)
        new_saletime = saletime[:8] + str(new_hour) + str(new_min) + str(new_sec)
        new_sq_name = reformat_name(check_name)
        new_qsr_name = reformat_name(d['check_name'])
        if saletime == new_saletime and new_sq_name == new_qsr_name:
            return saletime[:8] + d['entered'][-6:]

def get_QSR_data():
    qsr_contents = {}
    first_line = True # for BOM check (see Line ~8)
    with open('c:/ProgramData/QSR Automations/ConnectSmart/BackOffice/SpeedofService/SpeedOfService.txt', 'r', encoding="utf-16") as qsr_file:
        for line in qsr_file:
            if first_line:
                first_line = False
                line = line.lstrip(u'\ufeff') # to strip the potential BOM at the start (shouldn't present an issue but just in case)
            raw_data = line.split(',')
            if raw_data != []:
                data = parse_entry(raw_data)
                station_name = data['station_name']
                raw_saletime = data['entered']
                qsr_contents[(raw_saletime, station_name)] = data
    # Now sos is filled with all SpeedOfService data relevant to SL (sandwich line) #
    return qsr_contents

# Checks if in valid time range
# def check_valid_entry(raw_data, start_time, end_time):
#    if raw_data[23] == 'COFFEE': # Next Door Cafe
#        return False
#    bump_time = raw_data[32:34]
#    if len(bump_time[1]) == 1: # single digit minute
#        bump_time[1] = '0' + bump_time[1]
#    bump_time = ''.join(bump_time) # gets hour and min
#    return True if int(bump_time) >= start_time and int(bump_time) < end_time else False