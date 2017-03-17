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
    """
    JSONの入力ファイル中の"_id"要素を削除する
    [複数のJSONファイルをmongoimportした時にduplicate key errorを吐くため]
    @param  input_file:str[File PATH]
    """
    output_file = input_file + "_replace.json"

    # 出力ファイルの初期化（削除）
    if os.path.exists(output_file):
        os.remove(output_file)

    f_output_file = open(output_file, "a")
    f_input_file = open(input_file, 'r')

    # 1行ずつ処理．
    for line in f_input_file:
        encoded = json.loads(line)
        if ("_id" in encoded):
            del(encoded["_id"])
        decoded = json.dumps(encoded)+"\n"
        f_output_file.write(decoded)

    f_input_file.close()
    f_output_file.close()

    # delete input_file and rename output to input
    os.remove(input_file)
    os.rename(output_file, input_file)

# python ./del_id.py [File PATH]
if __name__ == "__main__":
    args = exec_argparse()
    replace(args.input_file)