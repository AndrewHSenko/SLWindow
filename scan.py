with open('window_data.txt', 'r') as tfile:
    checks = []
    for line in tfile.readlines():
        rawline = line.split()
        if len(rawline) == 2:
            t = rawline[0][2:-2]
            if t in checks:
                print(t)
            else:
                checks.append(t)