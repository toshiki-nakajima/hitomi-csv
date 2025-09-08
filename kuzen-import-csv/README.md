# Kuzen CSV処理ツール

このツールは、KuzenのCSVファイルをLinyシステムにインポートするための処理を行います。

## 処理の流れ

1. KuzenからエクスポートされたCSVファイルを受け取る
2. CSVファイルをCP932(Shift_JIS)エンコーディングに変換する
3. 変換されたCSVファイルをLiny形式に処理する
4. 最終的なインポート用CSVファイルを生成する

## 使用方法

### 基本的な使い方（コマンド実行例）

```bash
# 1. Kuzenのエクスポートファイルをエンコーディング変換
cd kuzen-import-csv
python csv_cp932_converter.py kuzen-user-list-1.csv

# 2. 変換されたファイルをLiny形式に処理
python csv_processer_for_liny.py
```

### 詳細な手順
#### 0. 前提条件
仮想環境を作成し、その中で`chardet`などのpackageをインストールします：
# または現在のプロジェクトディレクトリに作成する場合
```bash
python3 -m venv ./venv
source ./venv/bin/activate
pip install chardet
```

#### 1. CSVファイルのエンコーディング変換

Kuzenからエクスポートされたファイルを、CP932(Shift_JIS)エンコーディングに変換します。

```bash
python csv_cp932_converter.py <Kuzenのエクスポートファイル>
```

例:
```bash
python csv_cp932_converter.py kuzen-user-list-1.csv
```

これにより、`kuzen-user-list-1_cp932.csv`という名前で変換されたファイルが生成されます。

出力ファイル名を指定することもできます:
```bash
python csv_cp932_converter.py kuzen-user-list-1.csv -o converted_kuzen.csv
```

#### 2. Liny形式への処理

変換されたCSVファイルを使用して、Linyシステム用のインポートファイルを生成します。

```bash
python csv_processer_for_liny.py
```

このスクリプトは現状以下のファイルを使用しています:
実態に合わせて変更してください。
- 入力ファイル1: `kuzen-user-list-1 (1)_cp932.csv`（Kuzenの変換済みCSV）
- 入力ファイル2: `member_202509021516_20250902151617.csv`（Linyの既存CSV）
- 出力ファイル: `BP_for_import_YYYYMMDDHHMMSS.csv`（タイムスタンプ付きの出力ファイル）

## 補足説明

### csv_cp932_converter.py

- 様々な文字コード（UTF-8, Shift_JIS, EUC-JP等）を自動検出
- BOM（Byte Order Mark）の適切な処理
- CP932で表現できない文字は代替文字に置換

### csv_processer_for_liny.py

- KuzenのユーザーIDとLinyのLINE UserIDを突合キーとして使用
- 指定されたカラムのデータのみを更新
- 日付形式の自動変換（YYYY-MM-DD → YYYY/MM/DD）

### 注意事項

- 処理前に必ずデータのバックアップを取ってください
- 大量のデータを処理する場合は、十分なメモリを確保してください
- エラーが発生した場合は、エラーメッセージを確認して適切に対処してください
