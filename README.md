# todo.py
## 依存してるものとか
- python >= 3.5
- sqlite3

(標準モジュールだけで動作します.)

## 使い方
### 初期化
```
$ python3 todo.py table
```

### 実行
```
$ python3 todo.py
Welcome to Japari Park!
> help            # helpの表示
> show            # taskの一覧表示
> list            # taskの一覧表示(titleのみ)
> add [title]     # タスクの追加
> edit [task_id]  # タスクの編集
> done [task_id]  # タスクを終了する
> quit						# 終了
Bye!
```

## 現状の問題点
- listで表示される番号と`task_id`が一致してない
- helpが色々足りない

