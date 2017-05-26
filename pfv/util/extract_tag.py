# -*- coding: utf-8 -*-
import argparse
import os
import json
import re

# mongoDBに接続
from pymongo import *
client = MongoClient()
db = client.nm4bd

tag_mac_pattern = r"00:11:81:10:01:"

def exec_argparse():
    '''
    引数をパースした結果を連想配列で返す．
    input_file : 入力ファイルパス
    '''
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('input_file', help='入力するjsonファイル')
    return parser.parse_args()

def replace(input_file):
    '''
    テキストファイルの全ての行に共通の置換処理を行う．
    '''
    output_file = input_file + "_replace.json"
    # 出力ファイルの初期化（削除）
    if os.path.exists(output_file):
        os.remove(output_file)

    f_output_file = open(output_file, "a")
    f_input_file = open(input_file, 'r')

    repattern = re.compile(tag_mac_pattern)
    # 1行ずつ処理．
    for line in f_input_file:
        encoded = json.loads(line)
        matchOB = repattern.match(encoded["mac"])
        if matchOB != None:
            # del(encoded["rssi"])
            decoded = json.dumps(encoded)+"\n"
            f_output_file.write(decoded)

    f_input_file.close()
    f_output_file.close()

    # delete input_file and rename output to input
    os.remove(input_file)
    os.rename(output_file, input_file)

"""
jsonファイルからタグのmacアドレスに対応するのみを抽出する
"""
if __name__ == "__main__":
    args = exec_argparse()
    replace(args.input_file)