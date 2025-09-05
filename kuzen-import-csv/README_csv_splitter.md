# CSV Splitter

CSVファイルを指定されたサイズ（デフォルト1MB）以下に分割するPythonスクリプトです。

## 機能

- CSVファイルを指定されたサイズ（デフォルト1MB）以下に分割します
- 各分割ファイルにはヘッダー行が含まれます
- 元のファイルは保持されます
- 分割されたファイルは元のファイル名に _part1, _part2 などの接尾辞が付きます
- CP932エンコーディング（Shift-JIS）に対応しています

## 必要条件

- Python 3.6以上

## 使い方

### コマンドライン

```bash
python csv_splitter.py input.csv [--max-size 1.0] [--encoding CP932]
```

### 引数

- `input.csv`: 分割するCSVファイルのパス（必須）
- `--max-size`: 分割後の各ファイルの最大サイズ（MB単位、デフォルト: 1.0）
- `--encoding`: CSVファイルのエンコーディング（デフォルト: CP932）

### 使用例

```bash
# デフォルト設定（1MB以下に分割、CP932エンコーディング）
python csv_splitter.py large_file.csv

# 最大サイズを2MBに設定
python csv_splitter.py large_file.csv --max-size 2.0

# エンコーディングをUTF-8に設定
python csv_splitter.py large_file.csv --encoding utf-8
```

### Pythonコードからの使用

```python
from csv_splitter import split_csv_by_size

# CSVファイルを分割
split_files = split_csv_by_size('large_file.csv', max_size_mb=1.0, encoding='CP932')

# 分割されたファイルのパスを表示
for file_path in split_files:
    print(file_path)
```

## 出力例

```
分割ファイルを作成しています: large_file_part1.csv
分割ファイルを作成しています: large_file_part2.csv
CSVファイルを2個のファイルに分割しました。

分割されたファイル:
- large_file_part1.csv
- large_file_part2.csv
```

## 注意事項

- 元のCSVファイルは変更されません
- 分割されたファイルは元のファイルと同じディレクトリに作成されます
- 各分割ファイルには元のファイルのヘッダー行が含まれます
- エラーが発生した場合、作成途中のファイルは削除されます