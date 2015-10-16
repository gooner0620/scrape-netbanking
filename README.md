# Scrape Netbanking

ネットバンキングをスクレイピングして入出金明細を取得します。

* 三菱東京UFJ銀行
* 住信SBIネット銀行

## 必須

* PhantomJS

## 使い方

```sh
$ pip install -r requirements.txt

$ export MUFG_ID={Your id}
$ export MUFG_PASSWORD={Your passowrd}

$ export SBI_ID={Your id}
$ export SBI_PASSWORD={Your passowrd}

$ ./example.py
```