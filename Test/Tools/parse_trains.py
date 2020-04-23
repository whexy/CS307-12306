import os
from functools import reduce


def gao():
    for root, subFolders, files in os.walk('/Users/macmo/Workspace/SUSTech/CS307/proj2/12307'):
        for file in files:
            if file.endswith('.csv') and file != 'station.csv':
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read().splitlines()[13:]
                    for line in content:
                        entries = line.split(',')
                        train_name = entries[0].split()[0]
                        start = entries[3]
                        dep_time = entries[4]
                        end_time = entries[6]
                        duration = str(reduce(lambda x, y: x * 60 + y, map(int, entries[8].split(':'))))
                        stop = entries[5]
                        ying = entries[-4]
                        ruan = entries[-3]
                        if entries[-2] != '-':
                            ying_up, ying_mid, ying_down = entries[-2].split('/')
                        else:
                            ying_up, ying_mid, ying_down = ['-'] * 3
                        if entries[-1] != '-':
                            ruan_up, ruan_down = entries[-1].split('/')
                        else:
                            ruan_up, ruan_down = ['-'] * 2
                        with open('/Users/macmo/Workspace/SUSTech/CS307/proj2/12307_new/{}.csv'.format(train_name),
                                  'a+') as out:
                            out.write(','.join(
                                [train_name, start, dep_time, stop, end_time, duration,
                                 ying, ruan, ying_up, ying_mid, ying_down, ruan_up, ruan_down]) + '\n')
                print(file, 'done')


if __name__ == '__main__':
    gao()
