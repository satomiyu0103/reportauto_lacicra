
# service_account.jsonについて

{
  "type": "service_account",
  "project_id": "",
  "private_key_id": "",
  "private_key": "",
  "client_email": "",
  "client_id": "",
  "auth_uri": "",
  "token_uri": "",
  "auth_provider_x509_cert_url": "",
  "client_x509_cert_url": "",
  "universe_domain": ""
}

## 概要

このファイルは Google Cloud Platform (GCP) のサービスアカウント認証情報を含みます。
Google Sheets API や Google Drive API にアクセスするために必要です。

## 各フィールドの説明

| フィールド | 説明 |
| --- | --- |
| `type` | 認証タイプ（常に `service_account`） |
| `project_id` | GCPプロジェクトID |
| `private_key_id` | 秘密鍵ID |
| `private_key` | RSA秘密鍵（PEM形式） |
| `client_email` | サービスアカウントのメールアドレス |
| `client_id` | サービスアカウントの一意識別子 |
| `auth_uri` | Google認証エンドポイント |
| `token_uri` | トークン取得エンドポイント |
| `auth_provider_x509_cert_url` | 認証プロバイダー証明書URL |
| `client_x509_cert_url` | クライアント証明書URL |
| `universe_domain` | ユニバース（通常は `googleapis.com`） |

## セットアップ方法

1. GCP Console でサービスアカウントを作成
2. JSON 形式の認証キーをダウンロード
3. このファイルに貼り付け（`.gitignore` で除外）

## セキュリティ注意事項

⚠️ **重要**: 秘密鍵は絶対にGitリポジトリにコミットしないでください

- 環境変数または `.gitignore` で管理する
- 本番環境では安全に保管する
