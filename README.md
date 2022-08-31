## Azure Container Appsの手動デプロイ
### 環境変数設定

```bash
RESOURCE_GROUP="リソースグループ名"
LOCATION="リソースロケーション"
CONTAINERAPPS_ENVIRONMENT="Container Apps環境名"
```

### リソースグループ作成

```bash
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

### ACRインスタンス作成

```bash
az acr create --resource-group $RESOURCE_GROUP --name <コンテナリポジトリ名> --sku Basic
```

### ACRログイン

```bash
az acr login --name <コンテナリポジトリ名>
```

### Dockerイメージ確認

```bash
docker images
```

### ビルド&タグつける

```bash
docker build -t flask-hello-world
docker tag flask-hello-world <コンテナリポジトリ名>.azurecr.io/flask-hello-world:v1
```

### DockerイメージをACRにpush

```bash
docker push <コンテナリポジトリ名>.azurecr.io/flask-hello-world:v1
```

### ACRアクセスキー有効化
Azure Portal上でACRのアクセスキーを有効化する

### 環境作成

```bash
az containerapp env create \
  --name $CONTAINERAPPS_ENVIRONMENT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

### コンテナーアプリ作成

```bash
az containerapp create \
  --image <コンテナリポジトリ名>.azurecr.io/flask-hello-world:v1 \
  --name aca-flask-app \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINERAPPS_ENVIRONMENT \
	--ingress external \
	--target-port 80
```
## CD
Azure Portal上でデプロイ確認&Azure Portal上で継続的デプロイを設定

## CI
### 単体テスト(PyTest)の導入
[Python のビルドとテスト](https://docs.github.com/ja/actions/automating-builds-and-tests/building-and-testing-python)を参考に単体テストを自動化

- `py_test_main.py`: テストコードファイル
- `.github/workflow/unittest.yml`: ワークフローファイル

### 静的コード解析(SonarCloud)の導入
[sonarcloudとGitHubをつなげて静的コード解析を手に入れる](https://qiita.com/You_name_is_YU/items/565419f5240d8d62f77c)を参考に静的コード解析を自動化

- `sonar-project.properties`: SonarCloud設定ファイル
- `.github/workflow/sonarCloud.yml`: ワークフローファイル

### 脆弱性チェック(OWASP ZAP)
[GitHub Actions で OWASP ZAP が動くだと!?](https://qiita.com/r-hirakawa/items/b6ae6a749a6f7a7c5db7)を参考に脆弱性チェックを自動化

CDで作成したビルド&デプロイのワークフローファイルに追記する形で，デプロイ後のURLに対して脆弱性チェックをかける