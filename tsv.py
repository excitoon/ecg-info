def read(filename, start_time=None, end_time=None):
    tsv = open(filename, 'r')
    first_line = tsv.readline()[:-1]
    first = first_line.split('\t')
    columns = len(first)
    first_time = float(first[0])
    data = []
    for column in first:
        data.append([])
    pos = 0
    if not start_time is None and start_time > first_time:
        tsv.seek(0, 2)
        start_pos = 0
        end_pos = tsv.tell()
        while end_pos - start_pos > 1:
            pos = (end_pos + start_pos) // 2
            tsv.seek(pos)
            if pos > 0:
                tsv.readline()
            line = tsv.readline()[:-1]
            if line == '':
                return data
            values = line.split('\t')
            time = float(values[0])
            if time == start_time:
                break
            elif time < start_time:
                start_pos = pos
            else:
                end_pos = pos
    tsv.seek(pos)
    if pos > 0:
        tsv.readline()
    while True:
        line = tsv.readline()[:-1]
        if line == '':
            break
        values = line.split('\t')
        if not end_time is None and float(values[0]) >= end_time:
            break
        for column in range(0, columns):
            data[column].append(float(values[column]))
    return data

def get_first_time(filename):
    tsv = open(filename, 'r')
    first_line = tsv.readline()[:-1]
    first = first_line.split('\t')
    first_time = float(first[0])
    return first_time
