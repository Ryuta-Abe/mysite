import os, sys, glob, cmath, csv, itertools
# import Env
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from env import Env
Env()
PATH = "../../working/CSI/1/"
CSI_TYPE = "all"
CSI_LEN = 120 # 複素数表示時のCSIの要素数(Ntx2*Nrx2*Fn30)

def read_csi_from_csv(csv_file, csi_type = "phase"):
    """
    @param csv_file: str 読み込むCSVファイル
    @param csi_type: str 出力するCSIのタイプ
        phase: 位相のみ, amplitude: 振幅のみ, all: 両方
    @return csi: [float] ある瞬間、あるAPでのCSI
    Ntx = Nrx = 2の時、あるサブキャリア(計30)でのCSIは
           | a  b |
    csi_f =| c  d |
    返却するcsiは [a1,c1,b1,d1,a2,c2,b2,d2, .., a30,c30,b30,d30] (長さ120)
    """
    raw_csi = []
    with open(csv_file) as f:
        reader = csv.reader(f, delimiter = ",")
        csi_list = [row for row in reader]
    raw_csi = list(itertools.chain.from_iterable(csi_list))
    raw_csi = [complex(x.replace("i", "j")) for x in raw_csi]  # 文字列のCSIを複素数型に変換

    if csi_type == "phase":
        csi = [cmath.phase(yx) for x in raw_csi]
    
    if csi_type == "amplitude":
        csi = [abs(x) for x in raw_csi]
    
    if csi_type == "all":
        csi = []
        for x in raw_csi:
            csi.append(abs(x))
            csi.append(cmath.phase(x))
    return csi

def get_null_csi(csi_type):
    # TODO: 0埋めの妥当性検証
    csi = [0]

def get_csi(path):
    """
    @param path: str 追加対象のファイルが含まれるpath
    @every_csi_list: [[float]] 各瞬間のCSIが含まれたリスト
    """
    csi_file_list = glob.glob(PATH + "*.csv")
    if len(csi_file_list) == 0:
        return None
    previous_time = 0
    previous_AP_num = 0
    every_csi_list, csi_list = [], []
    is_first = True
    for csi_file in csi_file_list:
        csi_file_name = csi_file.split("\\")[1]
        csi_file_name = csi_file_name.split(".")[0]
        time = int(csi_file_name.split("_")[0])
        AP_num = int(csi_file_name.split("_")[1])
        if time < previous_time:
            print("ERROR: the order of time is wrong!")
        else:
            if time > previous_time and not is_first:  # csi_file_name: 新しい時刻のCSIファイル
                previous_AP_num = 0
                every_csi_list.append(csi_list)
                csi_list = []  # ある瞬間で取得されたCSIのリストを初期化 
            if is_first:  # 初回フラグをoffに
                is_first = False

            csi = read_csi_from_csv(csi_file, CSI_TYPE)
            # CSIの追加
            if AP_num - previous_AP_num != 1:
                null_csi_count = AP_num - previous_AP_num - 1
                if CSI_TYPE == "all":
                    csi_len = null_csi_count * CSI_LEN * 2
                else:
                    csi_len = null_csi_count * CSI_LEN
                csi_list.extend([0]*csi_len)
            csi_list.extend(csi)
        previous_time = time
        previous_AP_num = AP_num
    every_csi_list.append(csi_list)

    return every_csi_list

if __name__ == "__main__":
    csi = get_csi(PATH)
    print(csi[0])
    # csi = read_csi_from_csv(PATH + "12.csv", csi_type = CSI_TYPE)
    # print(csi, len(csi))