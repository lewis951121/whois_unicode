#-*- coding:utf-8 -*-
import unicodedata
import idna
import os
import json
import sys
from binascii import unhexlify

# 十六进制转成字符表达，比如unicode code point为1d750，用这个函数可以转换成字符𝝐，方便后续过滤
def hex_unicode_to_char(unicode_str):
    unicode_str = unicode_str.lstrip('0')
    hex_str = '0x'+unicode_str
    decimal_str = int(hex_str, 16)
    char = chr(decimal_str)  
    return char

def escape(s):
    result = []
    for char in s:
        result.append("\%o" % ord(char))
    return ''.join(result)

def int_hex(ints):
    int_list = ints.split('\\')[1:]
    # print(int_list)
    tmp = ''
    for item in int_list:
        tmp += str(hex(int(item))).replace('0x','')
    byte_result = unhexlify(tmp)
    utf8_result = byte_result.decode('utf-8')
    utf16_result = byte_result.decode('utf-16')

    return utf8_result, utf16_result

# 十进制数转换成utf8编码，比如\\229\\190\\136\\230\\156\\137\\231\\178\\190\\231\\165\\158的转换
def decimal_unicode_to_char(unicode_str):
    # escaped = escape(unicode_str)
    # print(escaped)
    utf8_result, utf16_result = int_hex(unicode_str)
    return utf8_result, utf16_result

# 判断是否是ascii字符
def is_ascii(s):
    try:
        s.decode('ascii')
    except UnicodeDecodeError:
        return False
    return True

# 把所有的非ascii表达提取出来
def extract_non_ascii(domain, ver_py):
    non_ascii = False
    if ver_py >= 3.7:
        if not domain.isascii():
            non_ascii = True
    else:
        if not is_ascii(domain):
            non_ascii = True
    return non_ascii

# 提取出来所有的punycode
def extract_puny(domain):
    if "xn--" in domain:
        return True
    else:
        return False

# 把我们需要的域名提取出来：1）ascii with xn--；2）non ascii
def extract_abnormal(domain, ver_py):
    is_abnormal = False
    if extract_non_ascii(domain, ver_py):
        is_abnormal = True
    elif extract_puny(domain):
        is_abnormal = True
    return is_abnormal

def main():
    
    return

if __name__=='__main__':
    main()