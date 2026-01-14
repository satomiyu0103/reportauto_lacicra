
# Web日報サイトらしくらに日報を自動記入する


# ディレクトリ構成
reportauto_lacicra/ (Project Root)
│
├── config/                 <-- [新設] 設定・環境変数
│   ├── .env                <-- (移動)
│   ├── service_account.json <-- (移動)
│   └── settings.py         <-- [新規] ルート定義・定数定義
│
├── common/                 <-- [新設] 汎用ライブラリ
│   ├── __init__.py
│   ├── data_loader.py      <-- data_io.py + ndf_report_core.py
│   ├── data_converter.py   <-- (Lacicra版ベース)
│   └── logger.py           <-- log_handler.py + ndfのログ機能
│
├── services/               <-- [新設] 業務ロジック
│   ├── __init__.py
│   ├── lacicra_service.py  <-- webui.py (クラス化推奨)
│   └── slack_service.py    <-- ndf_report_delivery.py + utils
│
├── logs/                   <-- ログ出力先
│
├── main_lacicra.py         <-- (移動・リファクタ) 日報入力実行用
├── main_morning.py         <-- (移動・リファクタ) 朝報告(op_ndf)用
└── main_evening.py         <-- (移動・リファクタ) 夕報告(ed_ndf)用