import os


def get_val(x):
    for i in range(5, 12):
        try:
            return float(x[i])
        except ValueError:
            pass


def gao():
    errors = []
    for root, subFolders, files in os.walk('/Users/whexy/Downloads/12307_new'):
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
                    content = sorted(map(lambda x: x.split(','), raw_content), key=get_val)
                    lines = len(content)
                    with open(os.path.join('/Users/whexy/Downloads/12307_intervals', file), 'w') as out:
                        if not content:
                            print('error')
                            continue
                        out.write(','.join(content[0]) + '\n')
                        for i in range(lines - 1):
                            new_line = [content[i][0], content[i + 1][1], content[i + 1][2], content[i][1],
                                        content[i][2]]
                            for j in range(5, 12):
                                if content[i][j] == '-':
                                    new_line.append('-')
                                else:
                                    new_line.append(str(float(content[i + 1][j]) - float(content[i][j])))
                            out.write(','.join(new_line) + '\n')
                print('done')
            except:
                errors.append(file)
    print(errors)


if __name__ == '__main__':
    gao()
