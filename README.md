# xml2liqmanifest プロジェクト概要

本プロジェクトは、液状化判定に必要な各種データ（XML、CSV、XLSX）を読み込み、  
土層情報および標準貫入試験（SPT）データの解析を通じて、液状化リスクの評価を行うツールです。

## 主な機能
- **データロード**  
  - XML ファイルからの緯度・経度、調査開始日、孔口標高、土層情報、観察記事、SPTデータのパース  
  - 将来的に CSV や XLSX 形式への対応を実装予定

- **データ統合**  
  - `merge.py` にて、各土層データと SPT データの統合を実施

- **液状化判定計算**  
  - `calc.py` で JRA 法（および今後他手法）の液状化判定アルゴリズムを実装
  - `core.py` の `LiquefactionManifest` クラスが全体の流れを管理

- **フロントエンドサンプル**  
  - HTML/JavaScript による入力フォームやチャート表示（`index.html`, `sample.html`, `patterns.js` など）

## ファイル構成
- **soil_properties.csv**  
  土質パラメータ（密度、粒径、細分量など）の基準値を定義

- **merge.py**  
  土層情報と SPT データのマージ処理を定義

- **load.py**  
  XML から各種情報をロードする処理を実装  
  ※ CSV、XLSX 読み込み機能は将来的に実装予定

- **calc.py**  
  液状化判定計算（特に JRA 手法）を担当  
  ※ AIJ、Idriss and Boulanger などの手法も未実装の状態

- **core.py**  
  プロジェクト全体の制御を行う `LiquefactionManifest` クラスを実装

- **その他**  
  フロントエンド用の HTML、JavaScript ファイル（例：`index.html`, `patterns.js`）および  
  サンプル実行用の `main.py` など

## 使い方
1. 対象ファイル（XML 等）を指定してデータをロード  
2. `set_method()` で計算手法とパラメータを設定  
3. `calculate_FL()` により液状化判定解析を実行  
4. `export_result()` により計算結果を出力（CSV、JSON 形式）

## 今後の展開
- CSV や XLSX の読み込み機能の実装  
- AIJ、Idriss and Boulanger 手法など、追加計算手法の実装  
- Web UI の機能拡充による操作性の向上
