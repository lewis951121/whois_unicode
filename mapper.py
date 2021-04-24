#!/usr/bin/python2.6
# coding: utf-8

import os, sys, json
import string
import codecs
import unicodedata
# import idna
import platform
from binascii import unhexlify

wanted_item = ["first_seen", "last_seen", "check_time",
               "createdate", "expiresdate",
               "r_whoisserver_list", "nameservers",
               "registrant_country", "status"]
# wanted_item = []
# wanted_item.append("createddate")
# wanted_item.append("r_whoisserver_list")
# wanted_item.append("check_time")

na_value = "n/a"

#####################################################################
#####################################################################
#####################################################################
#####################################################################

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
# 此处需要提供python版本，python3.7及以上可以用python自带的isascii()方法进行判断
def extract_non_ascii(domain, ver_py=None):
    if ver_py==None:
        ver_py = float(platform.python_version()[:3])
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

# 把需要的域名提取出来：1）ascii with xn--；2）non ascii
def extract_abnormal(domain, ver_py=None):
    is_abnormal = False
    if extract_non_ascii(domain, ver_py):
        # non ascii
        is_abnormal = True
    elif extract_puny(domain):
        # ascii with xn--
        is_abnormal = True
    return is_abnormal

#####################################################################
#####################################################################
#####################################################################
#####################################################################

def parse_json_whois(json_line):
    # 0307: comes from domain_data_filter_mr.mapper.py.
    # load each line as json format data.
    try:
        rec = json.loads(json_line)
    except:
        return "error"
    result = {}
    try:
        # extract wanted WHOIS info. at least we need (domain_name, iana_id).
        domain_name = rec["domainname"][0].lower()
        result["domain"] = domain_name

        # domain filter.
        if not extract_abnormal(domain_name):
            # print domain_name, "normal"
            return "error"

        # try to get the IANA ID.
        if "r_text_list" in rec:
            whois_s = rec["r_text_list"][0]
            for txt in whois_s.split("\n"):
                txt = txt.strip()
                if txt.startswith("Registrar IANA ID:"):
                    iana_id = txt.split(":")[1].strip()
                    # check the validity of IANA ID.
                    test = int(iana_id)
                    if (test > 0 and test < 4000) or test == 10007:
                        result["iana_id"] = iana_id
        # no IANA ID found. skip.
        if "iana_id" not in result:
            result["iana_id"] = "None"
    except Exception as e:
        return "error"

    # extract the wanted WHOIS items
    for key in wanted_item:
        if key in rec:
            if isinstance(rec[key], str) or isinstance(rec[key], unicode):
                result[key] = rec[key]
            if isinstance(rec[key], list):
                result[key] = ";".join(rec[key])
        else:
            result[key] = na_value

    try:
        # print the parsed data.
        self_key = result["iana_id"] + "\t" + result["domain"]
        extracted_line = ""
        for item in wanted_item:
            extracted_line = extracted_line + result[item].lower() + "\t"
        extracted_line = extracted_line.rstrip("\t")

        return self_key + "\t" + extracted_line
    except Exception as e:
        return "error"

# construct (key, value) pairs for the reducer.
# main key: (iana_id, tld_scope, registrant_cc_scope, contact_scope)
def main():
    for line in sys.stdin:
        line = parse_json_whois(line)
        if line == "error":
            continue

        encoding = sys.stdout.encoding
        print line.encode("utf-8")

main()
