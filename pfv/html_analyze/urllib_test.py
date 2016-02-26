# -*- coding: utf-8 -*-
import urllib.request

# # GET
# page_text = ""
# # urlopenはurllib.responseオブジェクトを返す
# # urllib.responseはfileのようなオブジェクトで、infoメソッドとgeturlが追加されたもの
# with urllib.request.urlopen('http://www.google.co.jp') as page:
#     # WebページのURLを取得する
#     print(page.geturl())
#     # infoメソッドは取得したページのメタデータを返す
#     print(page.info())
#     # readlinesでWebページを取得する
#     for line in page.readlines():
#         page_text = page_text + line.decode('Shift_JIS')
# print(page_text)

# # POST
# # はてなのログインURL
# LOGIN_URL = "https://www.hatena.ne.jp/login"
# post_data = {
#              'name': 'san_posttest',
#              'password': 'san_flab',
#              'persistent': '1',
#              'location': 'http://b.hatena.ne.jp/?&login_date=1371363089666',
#             }


# # POSTで送信するデータをURLエンコードする
# encoded_post_data = urllib.parse.urlencode(post_data).encode(encoding='ascii')

# page_text = []
# # urlopenのdata引数を指定するとHTTP/POSTを送信できる
# with urllib.request.urlopen(url=LOGIN_URL, data=encoded_post_data) as page:
#     # WebページのURLを取得する
#     print(page.geturl())
#     # infoメソッドは取得したページのメタデータを返す
#     print(page.info())
#     # readlinesでWebページを取得する
#     for line in page.readlines():
#         page_text.append(line.decode('utf-8'))

# for line in page_text:
# 	print(line)


# PCWLにPOSTするテスト
LOGIN_URL = "http://10.0.11.25/ja/private/nmsetinfo"
post_data = {
             'cmd':"/usr/sbin/station_list -i ath0",
            }


# POSTで送信するデータをURLエンコードする
encoded_post_data = urllib.parse.urlencode(post_data).encode(encoding='utf-8')



# Basic認証用のパスワードマネージャーを作成
url = LOGIN_URL
username = "root"
password = ""
password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
password_mgr.add_password(None, url, username, password)

# openerの作成とインストール
# HTTPS通信とBasic認証用のHandlerを使用
opener = urllib.request.build_opener(urllib.request.HTTPSHandler(),
                              urllib.request.HTTPBasicAuthHandler(password_mgr))
urllib.request.install_opener(opener)

page_text = []
# urlopenのdata引数を指定するとHTTP/POSTを送信できる
with urllib.request.urlopen(url=LOGIN_URL, data=b'cmd=/usr/sbin/station_list%20-i%20ath0') as page:
    for line in page.readlines():
        page_text.append(line.decode('utf-8'))

for line in page_text:
	print(line)