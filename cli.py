import click
import os
import csv
import re
import io
from collections import defaultdict, Counter
from contextlib import contextmanager

def dir_make(path):
    sort_dir = sorted(os.listdir(path))   
    print(', '.join(sort_dir)) 
    start, end = map(int, click.prompt('변경 범위를 입력하세요(시작점,끝점)', type=str).split(','))

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
                if old_n + op + i < 0:
                    print('0보다 작아질 수 없습니다.')
                    return

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

@contextmanager
def inplace(filename, mode='r', buffering=-1, encoding=None, errors=None,
            newline=None, backup_extension=None):
    """ 제너레이터를 이용한 컨텍스트 관리자이다. 
        readable과 writable을 반환해 한 파일을 읽고 수정할 수 있게 한다.
        도중에 에러가 발생할 시 원래 파일로 롤백이 된다.
    """
    # read모드만 지원한다.
    if set(mode).intersection('wa+'):
        raise ValueError('Only read-only file modes can be used')
    
    backup_filename = filename + (backup_extension or os.extsep + 'bak')
    try:
        os.unlink(backup_filename)
    except OSError:
        pass

    os.rename(filename, backup_filename)
    readable = io.open(backup_filename, mode, buffering=buffering,
                        encoding=encoding, errors=errors, newline=newline)
    
    try:
        # 파일의 권한정보 가져오기. 파일 id를 통해 파일 시스템 정보에 접근하여 st_mode를 반환
        perm = os.fstat(readable.fileno()).st_mode
    except OSError:
        # os 환경에 의해 위의 구문에서 에러가 발생할 수 있다.
        writable = io.open(filename, 'w' + mode.replace('r', ''), buffering=buffering,
                            encoding=encoding, errors=errors, newline=newline)
        print(writable)
    else:
        # try에서 무사히 통과되면 else 로직을 수행
        # |를 통해 각 옵션들을 결합한다. O_CREAT = 새 파일 열기, O_WRONLY = 쓰기 전용 열기, O_TRUNC= 제로 길이로 절단
        os_mode = os.O_CREAT | os.O_WRONLY | os.O_TRUNC
        # window 환경을 위한 구문
        if hasattr(os, 'O_BINARY'):
            os_mode |= os.O_BINARY
        fd = os.open(filename, os_mode, perm)
        writable = io.open(fd, 'w' + mode.replace('r', ''), buffering=buffering,
                            encoding=encoding, errors=errors, newline=newline)
        try:
            if hasattr(os, 'chmod'):
                os.chmod(filename, perm)
        except OSError:
            pass
    try:
        # with문이 사용되면 이 이곳에서 멈추게 된다. with가 종료될 때 그 후의 로직을 수행한다.
        yield readable, writable
    except Exception:
        try:
            os.unlink(filename)
        except OSError:
            pass
        os.rename(backup_filename, filename)
        raise
    finally:
        readable.close()
        writable.close()
        try:
            os.unlink(backup_filename)
        except OSError:
            pass

def csv_make(path: str):
    title_match = re.compile(r'^\d{3}-[\w?!]+$')
    with open(path, newline='', encoding='utf-8') as csv_file:
        lines = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_NONE)
        count = 0
        for line in lines:
            for word in line:
                if re.match(title_match, word):
                    print(','.join(line))
                    count += 1
    start, end = map(int, click.prompt('변경 범위를 입력하세요(입력예시: 시작점,끝점)', type=str).split(','))
    op = click.prompt('증가량을 입력해주세요', type=int)

    # 위의 inplace 컨텍스트 관리자를 사용.
    with inplace(path, 'r', newline='') as (infh, outfh):
        reader = csv.reader(infh, delimiter=',')
        writer = csv.writer(outfh)

        for row in reader:
            if re.match(title_match, row[0]):
                number, title = row[0].split('-')
                old_n = int(number)
                if start <= old_n <= end:
                    if old_n + op < 0:
                        print('0보다 작아질 수 없습니다.')
                        raise Exception
                    new_n = '{:0>3}'.format(old_n + op)
                    row[0] = '{}-{}'.format(new_n, title)
            writer.writerow(row)

@click.command()
@click.argument('path', type=click.Path(exists=True))
def main(path):
    """디렉토리 넘버링을 변경합니다."""
    path_list = path.split('/')

    if not '.rule' in path_list[-2]:
        print('룰셋이여야합니다')
        return
    
    if '.csv' in path_list[-1]:
        return csv_make(path)
    
    return dir_make(path)
    

if __name__ == '__main__':
    main()