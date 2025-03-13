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

def check_valid_entry(raw_data, start_time, end_time):
    if raw_data[23].lower() == 'anchor':
        return False
    bump_time = raw_data[32:34]
    if len(bump_time[1]) == 1: # single digit minute
        bump_time[1] = '0' + bump_time[1]
    bump_time = ''.join(bump_time) # gets hour and min
    return True if bump_time > start_time and bump_time < end_time else False

def get_QSR_data(start_time, end_time):
    sos = {}
    first_line = True # for BOM check (see Line ~8)
    for line in open('c:/ProgramData/QSR Automations/ConnectSmart/BackOffice/SpeedofService/SOS20250221.txt', 'r', encoding='utf-16le'): # SoS file is UTF-16 by default
        if first_line:
            first_line = False
            line = line.lstrip(u'\ufeff') # to strip the potential BOM at the start (shouldn't present an issue but just in case)
        raw_data = line.split(',')
        if check_valid_entry(raw_data, start_time, end_time):
            sos_data = parse_entry(raw_data)
            sos[sos_data['check_num']] = sos_data # Could specify by Transaction #, but this is easier to integrate with Squirrel
    # Now sos is filled with all SpeedOfService data relevant to SL (sandwich line) #
    return sos


