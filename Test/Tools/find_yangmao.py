import os
from os.path import join


def gao():
    yangmao = set()
    cnt = 0
    for root, subFolders, files in os.walk('/Users/macmo/Workspace/SUSTech/CS307/proj2/12307_intervals'):
        for file in files:
            if file.endswith('.csv') and file != 'station.csv':
                with open(join(root, file), 'r') as f:
                    content = map(lambda x: x.split(',')[6:], f.read().splitlines())
                    for line in content:
                        for x in line:
                            if x != '-' and float(x) <= 0:
                                print(x)
                                cnt += 1
                                yangmao.add(file)
    print(*yangmao)
    print(len(yangmao))
    print(cnt)


if __name__ == '__main__':
    gao()
