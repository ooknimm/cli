import click
import os

@click.command()
@click.argument('files', type=click.Path(exists=True))
def main(files):
    """Print all FILES file names."""
    path_list = files.split('/')
    if not '.rule' in path_list[-2]:
        return '룰셋이여야합니다'

    sort_dir = sorted(os.listdir(files))   
    print(sort_dir) 
    value, value2 = map(int, click.prompt('변경 범위를 입력하세요.', type=str).split(','))

    from collections import defaultdict, Counter
    table = defaultdict(list)
    for i in range(value, value2+1):
        a = '{:0>3}'.format(i)
        for s in sort_dir:
            if a in s:
                table[a].append(s)
    
    for key in table.keys():
        temp = []
        if len(table[key]) > 1:
            while len(table[key]) > 1:
                prompt_type = click.IntRange(min=1, max=len(table[key]))
                prompt_text = '{}:\n{}\n'.format(
                    key,
                    '\n'.join(f'{idx: >4}: {c}' for idx, c in enumerate(table[key], start=1))
                )
                op = click.prompt(prompt_text, type=prompt_type, show_choices=False)
                temp.append(table[key][op-1])
                print(temp)
                del table[key][op-1]
                if len(table[key]) == 1:
                    temp.append(table[key][0])
                    print(temp)
            table[key] = temp

    op = click.prompt('증가량을 입력해주세요', type=int)
    count = 0
    for values in table.values():
        i = count
        for value in values:
            y = value.split('-')
            b = int(y[0])
            x = '{:0>3}'.format(b+op+i)
            os.rename(files + '/' + value, files + '/' + x + '-' + y[1])
            i += 1
        count += i - count - 1
    
    print(sorted(os.listdir(files)))
    

if __name__ == '__main__':
    main()