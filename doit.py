import consolidate

start_time = 1320
while start_time != 1915:
    consolidate.do_it(start_time)
    start_time += 5
    if str(start_time)[-2:] == '60':
        start_time += 40
    if start_time == 1325:
        break