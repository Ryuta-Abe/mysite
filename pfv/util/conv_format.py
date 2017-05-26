# -*- coding: utf-8 -*-
import argparse
import os
import json

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

    # 1行ずつ処理．
    for line in f_input_file:
        encoded = json.loads(line)
        if ("on_recv" in encoded):
            del(encoded["_id"])
            encoded["get_time_no"] = encoded["on_recv"]
            del(encoded["on_recv"])
            encoded["ip"] = encoded["ap_ip"]
            del(encoded["ap_ip"])
            del(encoded["seq"])
        decoded = json.dumps(encoded)+"\n"
        f_output_file.write(decoded)

    f_input_file.close()
    f_output_file.close()

    # delete input_file and rename output to input
    os.remove(input_file)
    os.rename(output_file, input_file)

"""
raw100(8Fデータ)を整形[key変換]
@param  arg:type
@return arg:type
"""
if __name__ == "__main__":
    args = exec_argparse()
    replace(args.input_file)