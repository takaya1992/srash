# srash

search rank api 

## DEVELOPMENT

### パッケージのインストール

```
$ docker-compose run --rm lambda pip install -r requirements.txt -t functions/srash/lib/
```

### ローカルでの実行

```
$ docker-compose run --rm lambda
```

### XPathのデバッグ

Chromeの開発者ツールのコンソールで以下のようにすることで確認できる

```
$x('count(//li[@class="b_algo"])')
```
