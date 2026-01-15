# 毎日の報告自動化プログラム

Lacicraへの勤怠入力および日報作成を自動化し、Slackへの通知を行うツールです。
GoogleスプレッドシートやGoogle Driveからデータを取得し、Seleniumを用いて自動入力を行います。

## 🚀 主な機能

- 勤怠入力の自動化：タスクスケジューラに設定して指定時間にLacicraに入力
- 日報作成と送信：その日の活動報告を作成する
- Slack連携：始業時と終業時にSlackへ通知
- ログ管理：実行ログを自動でローテーション保存（30日）

## 📦 前提条件

- OS：Windows / macOS / Linux
- Python：3.12↑
- Google Chrome：最新版
- uv：パッケージ管理ツール

## セットアップ手順

このリポジトリはパッケージ管理に 'uv' を使用しています

### 1. リポジトリのクローン

git clone [https://github.com/satomiyu0103/reportauto_lacicra.git](https://github.com/satomiyu0103/reportauto_lacicra.git)
cd reportauto_lacicra

### 2. uv のインストールと依存関係の同期

Python環境とライブラリを一括で構築します。

- uv が未インストールの場合
  - pip install uv
- 仮想環境の作成とライブラリのインストール
  - uv sync

### 3. 環境変数の設定 (.env)

.env.template をコピーして .env ファイルを作成し、必要な情報を入力してください。

- Mac/Linux
  - cp config/.env.template .env
- Windows (PowerShell)
  - Copy-Item config/.env.template .env

- 設定項目
  - LACICRA_ID, LACICRA_PASS: Lacicraのログイン情報
  - SLACK_BOT_TOKEN, SLACK_CHANNEL_ID: Slack通知用
  - SPREADSHEET_KEY: データ参照元のスプレッドシートID
  - LOG_DIR: ログ出力先 (デフォルト: logs)

### 4. Google Cloud 認証設定

Google Drive/Sheets APIを利用するためのサービスアカウントキーが必要です。

- GCPコンソールからJSONキーを発行。
- ファイル名を service_account.json に変更。
- config/ ディレクトリ配下に配置する。

⚠️ 注意: service_account.json と .env は機密情報を含むため、Gitにはコミットしないでください（.gitignore 設定済み）。

## 💻 実行方法 (Usage)

uv run コマンドを使用してスクリプトを実行します。

### 日報自動記入 (Lacicra入力 + 日報送信)

uv run main_1_lacicra.py

### Slack通知のみ (手動トリガー)

- 朝の挨拶
  - uv run main_2_morning_post.py
- 夕方の日報通知
  - uv run main_2_evening_post.py

## 📂 ディレクトリ構成

reportauto_lacicra/
├── common/             # 共通モジュール (データ変換, ログ, 定数)
├── config/             # 設定ファイル (.env, service_account.json)
├── logs/               # 実行ログ (自動生成)
├── services/           # 外部サービス連携 (Lacicra, Slack)
├── main_1_lacicra.py      # メイン処理スクリプト
├── main_2_..._post.py     # Slack通知用サブスクリプト
├── pyproject.toml      # 依存関係定義 (uv)
└── uv.lock             # ロックファイル

## 🛡️ 開発ガイド (Development)

このプロジェクトでは、コード品質の維持に [Ruff](https://docs.astral.sh/ruff/) を使用しています。
コミットする前に、以下のコマンドでコードのチェックと整形を行ってください。

### リンター (Lint) & フォーマッター (Format)

すべて `uv run` を通して実行します。

#### 1. コードの静的解析 (Check)

バグやコードスタイルの違反がないかチェックします。
uv run ruff check

#### 2. 自動修正 (Auto-fix)

検出されたエラー（未使用のimportや変数の削除など）を自動で修正します。
uv run ruff check --fix

#### 3. コード整形 (Format)

インデントや改行位置を統一します（Black互換）。
uv run ruff format .

### 💡 VS Code 推奨設定

VS Code拡張機能 Ruff をインストールすると、ファイル保存時に自動で整形と修正が行われ、開発効率が向上します。

.vscode/settings.json (ワークスペース設定) の例:
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    },
    "editor.defaultFormatter": "charliermarsh.ruff"
  }
}
