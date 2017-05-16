from datetime import datetime

filenames = ['aes128cbc', 'aes128gcm', 'aes256cbc', 'aes256gcm']

for filename in filenames:
    with open(filename, 'r') as f:
        lines = f.readlines()

    first_split = lines[0].strip('\n').split()
    last_split = lines[-1].strip('\n').split()
    prev_datetime = datetime.strptime(first_split[1][:-1], '%H:%M:%S')
    s_time = prev_datetime
    end_time = datetime.strptime(last_split[1][:-1], '%H:%M:%S')
    total_datetime = int((end_time - s_time).total_seconds())
    threshold = 0.6
    secs = [0]
    found = False
    for l in lines:
        if found:
            splitted = l.strip('\n').split()
            confidence = float(splitted[-1])
            if confidence > threshold:
                cur_time = splitted[1][:-1]
                cur_datetime = datetime.strptime(cur_time, '%H:%M:%S')
                t_diff = int((cur_datetime - prev_datetime).total_seconds())
                secs.append(t_diff)
                prev_datetime = cur_datetime
        if ':267' in l:
            found = not found

    print "('" + filename + "',", str(secs) + '),', ' #', total_datetime
