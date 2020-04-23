import os
import numpy as np


def parse(content):
    line_cnt = len(content)
    x = [int(line[5]) for line in content]
    if len(x) <= 1:
        return
    for i in range(6, 13):
        y = [line[i] for line in content]
        if y[0] != '-':
            y = list(map(float, y))
            xi = []
            yi = []
            for j in range(line_cnt):
                if y[j] != 0:
                    xi.append(x[j])
                    yi.append(y[j])
            if yi:
                k, b = np.polyfit(xi, yi, 1)
                for j in range(line_cnt):
                    if y[j] == 0:
                        content[j][i] = '{:.1f}'.format(k * x[j] + b)
            else:
                for j in range(line_cnt):
                    content[j][i] = '-'


def gao():
    errors = []
    for root, subFolders, files in os.walk('/Users/macmo/Workspace/SUSTech/CS307/proj2/12307_new'):
        for file in files:
            if file[0] == '.' or not file.endswith('.csv'):
                continue
            try:
                print(file, end=' ')
                with open(os.path.join(root, file), 'r') as f:
                    raw_content = list(filter(lambda x: x[-13:] != '-,-,-,-,-,-,-', set(f.read().splitlines())))
                    if not raw_content:
                        print('skip')
                        continue
                    content = sorted(map(lambda x: x.split(','), raw_content), key=lambda x: int(x[5]))
                    parse(content)
                    lines = len(content)
                    with open(os.path.join('/Users/macmo/Workspace/SUSTech/CS307/proj2/12307_intervals', file), 'w') as out:
                        if not content:
                            print('error')
                            continue
                        out.write(','.join(content[0]) + '\n')
                        for i in range(lines - 1):
                            new_line = [content[i][0], content[i + 1][1], content[i + 1][2], content[i][1],
                                        content[i][2]]
                            for j in range(5, 13):
                                if content[i][j] == '-':
                                    new_line.append('-')
                                else:
                                    new_line.append('{:.1f}'.format(abs(float(content[i + 1][j]) - float(content[i][j]))))
                            out.write(','.join(new_line) + '\n')
                print('done')
            except:
                errors.append(file)
    print(errors)


if __name__ == '__main__':
    gao()
