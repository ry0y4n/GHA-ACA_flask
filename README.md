# Azure Container AppsのCI/CD体験レポジトリ

スターター用ブランチ（[start-point](https://github.com/ry0y4n/GHA-ACA_flask/tree/start-point)）を使って以下のフローを体験することができます
## Azure CLIを用いたAzure Container Appsの手動デプロイ

### 環境構築
このレポジトリをフォークするか，クローンして以下の手順で自分のレポジトリを作ってください．

```bash
git clone https://github.com/ry0y4n/GHA-ACA_flask.git -b start-point
rm -rf .git
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin <自分のレポジトリURL>
git push -u origin main
```
### ログイン

```bash
az login
```
### 環境変数設定

```bash
RESOURCE_GROUP="リソースグループ名"
LOCATION="リソースロケーション"
CONTAINERAPPS_ENVIRONMENT="Container Apps環境名"
CONTAINER_APP_NAME="コンテナーアプリ名"
CONTAINER_REGISTRY="コンテナレジストリ名"
```

### リソースグループ作成

```bash
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

### ACRインスタンス作成

```bash
az acr create --resource-group $RESOURCE_GROUP --name $CONTAINER_REGISTRY --sku Basic --admin-enabled true
```

### ACRログイン

```bash
az acr login --name $CONTAINER_REGISTRY
```

### Dockerイメージ確認

```bash
docker images
```

### ビルド&タグつける

```bash
docker build -t flask-hello-world .
docker tag flask-hello-world $CONTAINER_REGISTRY.azurecr.io/flask-hello-world:v1
```

### DockerイメージをACRにpush

```bash
docker push $CONTAINER_REGISTRY.azurecr.io/flask-hello-world:v1
```

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
  --image $CONTAINER_REGISTRY.azurecr.io/flask-hello-world:v1 \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINERAPPS_ENVIRONMENT \
	--ingress external \
	--target-port 80
```
## デプロイ自動化の実装
サービスプリンシパルを発行（出力されるJSONデータの中身は次のコマンドで使います）
```bash
az ad sp create-for-rbac --name momoServicePrincipal \  
                         --role contributor \
                         --scopes /subscriptions/<サブスクリプションID>/resourceGroups/$RESOURCE_GROUP
```

GitHub Actions ワークフローをリポジトリに追加して，コンテナー アプリをデプロイ
```bash
az containerapp github-action add -g $RESOURCE_GROUP \
                                  -n $CONTAINER_APP_NAME \
                                  --repo-url <リポジトリURL> \
                                  --branch main \
                                  --registry-url $CONTAINER_REGISTRY.azurecr.io \ 
                                  --service-principal-client-id <前のコマンドで出力された値（appID）> \
                                  --service-principal-tenant-id <前のコマンドで出力された値（tenant）> \
                                  --service-principal-client-secret <前のコマンドで出力された値（password）> \
                                  --login-with-github
```

## テスト自動化の実装
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

## 体験

1. 適当な作業ブランチ(e.g. `develop`or`feature/hoge`)でコミットした後，`main`ブランチに対してPRを立てる
2. テストが動作することを確認してマージ
3. デプロイワークフローと脆弱性チェックが動作することを確認する
