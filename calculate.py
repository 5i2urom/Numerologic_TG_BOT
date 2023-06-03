from datetime import datetime

from numers import numers

def check_date(date_str):
    try:
        datetime.strptime(date_str, '%d.%m.%Y')
        return True
    except ValueError:
        return False

def calculate(date_str):
    dict_info={}

    digits = ''.join([s for s in date_str if s != '.'])
    for_sum = digits
    while len(for_sum) > 1: 
        for_sum = str(sum(map(int, list(for_sum))))
        digits = digits + for_sum

    for x in ['1', '2', '3', '5', '6', '7', '8', '9']:
        str_n = ''.join([x]*digits.count(x)) # 11 | 22 | 333
        if str_n == '': str_n = '(' + x + ')' # (5)
        n = len(str_n)
        str_copy = str_n
        while str_copy not in numers:
            str_copy = str_copy[:-1]
        key_str = numers[str_copy] 
        if 'x' in key_str:
            ind = key_str.find('x') + 1
            key_str = key_str[:ind] + str(n) + key_str[ind+1:]   
        dict_info[str_n] = key_str
    return dict_info   