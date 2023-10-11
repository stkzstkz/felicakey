# felicakey
## 操作について
`>name`のところでDiscordのユーザーIDを入力すること．
### 登録

```
$./Register
>name ******************
Touch your Suica
Registered (idm:************)
```
### 削除
```
$./Unregister.sh 
Delete User
name> **********
Deleted (name:**********)
```
## 確認について
```
systemctl status Kagi
```
で実行状況の確認ができる．
詳しくは[wiki](https://member.x68uec.org/fswiki/wiki.cgi?page=FelicaKey#p26)を確認すること．
## その他
工研の鍵を参考にしたので[KM4K](https://github.com/ueckoken/KM4K "ueckoken/KM4K")も確認してみるとよい．
### 関数の役割
- webhook
  Discordへ通知
- sql_add
