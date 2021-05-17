import click
import os
from collections import defaultdict, Counter


def dir_make(path):
    sort_dir = sorted(os.listdir(path))   
    print(', '.join(sort_dir)) 
    start, end = map(int, click.prompt('변경 범위를 입력하세요', type=str).split(','))

    table = defaultdict(list)
    for i in range(start, end+1):
        number = '{:0>3}'.format(i)
        for dir in sort_dir:
            if number in dir:
                table[number].append(dir)
    
    for key in table.keys():
        temp = []
        if len(table[key]) > 1:
            while len(table[key]) > 1:
                prompt_type = click.IntRange(min=1, max=len(table[key]))
                prompt_text = '{}:\n{}\n'.format(
                    key,
                    '\n'.join(f'{idx: >4}: {c}' for idx, c in enumerate(table[key], start=1))
                )
                select = click.prompt(prompt_text, type=prompt_type, show_choices=False)
                temp.append(table[key][select-1])
                del table[key][select-1]
                if len(table[key]) == 1:
                    temp.append(table[key][0])
                    print(temp)
            table[key] = temp

    op = click.prompt('증가량을 입력해주세요', type=int)

    count = 0
    try:
        for values in table.values():
            i = count
            for value in values:
                names = value.split('-')
                old_n = int(names[0])
                new_n = '{:0>3}'.format(old_n+op+i)
                os.rename('{}/{}'.format(path, value), '{}/{}-{}'.format(path, new_n, names[1]))
                i += 1
            count += i - count - 1
    except OSError as e:
        filename_1 = e.filename.split('/')[-1]
        filename_2 = e.filename2.split('/')[-1]
        print('{}, {}'.format(filename_1, filename_2))
        print('중복되는 요소가 있습니다.')
        return
    
    print(sorted(os.listdir(path)))

def csv_make(path):
    pass

@click.command()
@click.argument('path', type=click.Path(exists=True))
def main(path):
    """디렉토리 넘버링을 변경합니다."""
    path_list = path.split('/')

    if '.csv' in path_list[-1]:
        return csv_make(path)

    if not '.rule' in path_list[-2]:
        print('룰셋이여야합니다')
        return
    
    return dir_make(path)
    

if __name__ == '__main__':
    main()