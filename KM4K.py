#!/usr/bin/python3
# -*- coding: utf-8 -*-
import nfc
import binascii
import sqlite3
import sys
import time
import requests
from requests.exceptions import Timeout
import json
import os
import discord
from wirservo import DoorGPIOContoroller as Door

# Felicaであることの設定
suica = nfc.clf.RemoteTarget("212F")
# スイカであることの設定
suica.sensf_req = bytearray.fromhex("0000030000")
# webhookのurl(wiki参照)
webhook_url = 'url'

# webhookの設定
def webhook(name, door):
    if door:    #ドアの状態(物理鍵で開け閉めした場合は変わる)
        message = "closed the door"
    else:
        message = "opened the door"
    
    if name == 1:   #オートロック
        mention = "autolocked the door"
    elif name == 0:    #登録されていないICカードがタッチされたとき全員に通知
        mention = "@everyone Your ID is not registered"
    else:
        mention = "<@"+name+"> "+message
    
    main_content = {'content': mention, "allowed_mentions": {"parse": ["everyone"]}}
    headers      = {'Content-Type': 'application/json'}
    #b = time.time()
    try:
        response     = requests.post(webhook_url, json.dumps(main_content), headers=headers, timeout=3.0)
        #print(response.status_code)
    except Exception as e:
        print(e)
    #a = time.time()
    #print(a-b)
#sql追加(名前(DiscordのID)、id(Felicaのidm)
def sql_add(cur, name, idm):
    cur.execute("INSERT INTO users (name, idm) VALUES (?, ?)", (name, idm))

# nfcの読み取りを行い、sql_addを実行する
def add_nfc(cnur):
    name = input("name> ")
    print("Touch your Suica")
    idm = read_nfc()
    if idm:
        cur.execute("SELECT * FROM users WHERE idm=?", (idm,))
        res = cur.fetchall()
        if len(res) > 0:
            print("This key has already registered.")
        else:
            sql_add(cur, name, idm)
            print("Registered (idm:" + idm.decode() + ")")

# データ削除
def delete_nfc(cur):
    name = input("name> ")
    cur.execute("SELECT * FROM users WHERE name=?", (name,))
    res = cur.fetchall()
    if len(res) == 0:
        print("Unregistered name:" + name)
    else:
        cur.execute("DELETE FROM users WHERE name=?", (name,))
        print("Deleted (name:" + name + ")")

# nfcを読取り、idを返す(ここでwhileが回る)
def read_nfc(autolocked=True):
    #s_time = time.time()   #呼び出された時間
    while True:
        #if not autolocked and time.time() - s_time > 30:   #オートロックされていなくて，30秒経った時(多分バグの原因)
            #return 0
        with nfc.ContactlessFrontend("usb") as clf:    #usbから接続されたnfcをclfとして読む
            target = clf.sense(suica, iterations=3, interval=1.0)               
            while target:
                tag = nfc.tag.activate(clf, target)
                tag.sys = 3
                idm = binascii.hexlify(tag.idm)
                return idm

# IDがdatabaseに入ってるか確認し，パスワード確認(未実装&パスワードどうすんだ問題) => BLEを使ったスマホアプリ作ってみたい
def inquiry_id(cur):
    name = input("name> ")
    cur.execute("SELECT * FROM users WHERE name=?", (name,))
    res = cur.fetchall()
    if len(res) == 0:
        print("Unregistered name:" + name)
    else:
        print("Registered name\n")
        print("If the door is open, input something.")
        isopen = bool(input("status> "))
        __door = Door()
        webhook(name, isopen)
        if (isopen):
            __door.open()
            isopen = not isopen
            print("opened")
        else:
            __door.close()
            isopen = not isopen
            print("closed")
        del __door

# Mentionを飛ばさないようにする(不審者対策のため使わない)
def not_mention(cur):
    on = input("If you want to restart mention, input something.")
    name = input("name> ")
    cur.execute("SELECT * FROM users WHERE name=?", (name,))
    res = cur.fetchall()
    if len(res) != 0:
        mention = res[0][3]                                                        
        if mention == None:    #メンションされる
            if on == "":    #メンションを止めたい
                cur.execute("UPDATE users SET mention = 1 WHERE name=?", (name,))
                print("Mention is stopped")
            else:   #メンションを止めたくない
                print("Mention have been already restarted")
        elif mention == 1:  #メンションされない
            if on == "":    #メンションを止めたい
                print("Mention have been already stopped")
            else:   #メンションを止めたくない
                cur.execute("UPDATE users SET mention = Null WHERE name=?", (name,))
                print("Mention is restarted")
    else:   #登録されていないなかった
        print("Unregistered")

# Felicaが登録されているかどうか確かめる
def start_system(cur, isopen):
    sql = """SELECT * FROM users WHERE idm=?"""
    autolocked = False    #はじめはオートロックされていない
    while True:    #ずっとWhileループでぶん回す
        idm = read_nfc(autolocked)    #ここでもループ．autolocked=Falseかつ，最後に鍵を操作してから30秒経ったらオートロックする
        __door = Door()    #Doorのインスタンス作成
        if idm != 0:    #autolocked=Trueで，最後に鍵を操作してから30秒経ってなかったら
            autolocked = False
            cur.execute(sql, (idm,))
            res = cur.fetchall()
            if len(res) > 0:    #ちゃんと結果が返ってきてたら
                name = str(res[0][0])   #idmがマッチした時のnameを取り出す
                #mention = res[0][3]    #idmがマッチしたときのmentionを返す
                if not isopen:    #ドアが閉まってるとき
                    __door.open()
                    #if mention == None:    #mentionカラムに何も書かれていなければmentionする．
                    webhook(name, isopen)
                    isopen = not isopen    #最後にドアの状態も統一
                else:   #ドアが開いているとき
                    __door.close()
                    #if mention == None:    #mentionカラムに何も書かれていなければmentionする．
                    webhook(name, isopen)                                       
                    isopen = not isopen    #最後にドアの状態も統一
            else:   #idmがデータベースになかったら
                print("Unregistered (idm:" + idm.decode() + ")")    #raspberrypiにprint
                webhook(0, "")    #Discordにも通知(ここら辺クラス化してわかりやすく)
        else:   #autolocked=Falseかつ，最後に鍵を操作してから30秒経ったら
            __door.close()
            isopen = False    #オートロックされているから
            autolocked = True
            print("The door is autolocked")
            webhook(1, "")
        del __door    #Doorのインスタンスをデストラクト

def main(argv):
    mode = 3
    dir = os.path.dirname(os.path.abspath(__file__))
    dbname = os.path.normpath(os.path.join(dir, "./test.db"))
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    isopen = True     #再起動した時に誤作動が一度だけ起こっても閉じている状態で済むように初期状態は開いている状態とした
    
    if len(argv) == 2:
        mode = int(argv[1]) 
    try:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS users (name INTEGER NOT NULL, idm BLOB NOT NULL, date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, mention INTEGER NULL)"
        )
        if mode == 0:
            print("Add User")
            add_nfc(cur)
        elif mode == 1:
            print("Delete User")
            delete_nfc(cur)
        #elif mode == 2:
        #    print("Stop to mention")
        #    not_mention(cur)
        else:
            print("Welcome!!")
            start_system(cur, isopen)
    except Exception as e:
        print("An error has occured!")
        print(e)
    finally:
        conn.commit()
        conn.close()


if __name__ == "__main__":
    main(sys.argv)
