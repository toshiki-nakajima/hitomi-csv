import chardet
import os
import argparse


def detect_file_encoding(file_path):
    """
    ファイルの文字コードを検出し、内容を読み込む
    BOM（Byte Order Mark）も適切に処理する

    Args:
        file_path (str): 入力ファイルのパス

    Returns:
        tuple: (content, encoding) - ファイルの内容と検出された文字コード
    """
    # ファイルを読み込んで文字コードを検出
    with open(file_path, 'rb') as file:
        raw_data = file.read()

    # BOMを検出
    has_bom = False
    if raw_data.startswith(b'\xef\xbb\xbf'):
        print("UTF-8 BOMが検出されました")
        has_bom = True
        # BOMを持つUTF-8として読み込む
        try:
            content = raw_data.decode('utf-8-sig')
            print("utf-8-sig エンコーディングで正常に読み込めました")
            return content, 'utf-8-sig'
        except UnicodeDecodeError:
            print("utf-8-sig でも読み込めませんでした")

    # 文字コードを検出
    detected = chardet.detect(raw_data)
    encoding = detected['encoding']
    confidence = detected['confidence']

    print(f"検出された文字コード: {encoding}")
    print(f"信頼度: {confidence:.2%}")

    # 異なるエンコーディングで読み込みを試みる
    encodings_to_try = ['utf-8', 'utf-8-sig', 'shift_jis', 'cp932', 'euc-jp', 'iso-2022-jp']
    content = None

    for enc in encodings_to_try:
        try:
            content = raw_data.decode(enc, errors='strict')
            print(f"エンコーディング {enc} で正常に読み込めました")
            break
        except UnicodeDecodeError:
            print(f"エンコーディング {enc} では読み込めませんでした")

    if content is None:
        # どのエンコーディングでも完全に読み込めない場合は、errors='replace'で代替文字に置き換えて読み込む
        content = raw_data.decode(encoding, errors='replace')
        print(f"完全な読み込みができませんでした。{encoding} で代替文字を使用して読み込みました")

    return content, encoding


def convert_to_cp932(content, file_path, output_path=None):
    """
    文字列をCP932(Shift_JIS)に変換して保存する
    BOM（Byte Order Mark）が含まれる場合は適切に処理する

    Args:
        content (str): 変換する文字列
        file_path (str): 入力ファイルのパス（出力パスが指定されていない場合に使用）
        output_path (str): 出力ファイルのパス（Noneの場合は元ファイル名_cp932.csvとする）

    Returns:
        str: 保存されたファイルのパス
    """
    # 出力ファイル名を決定
    if output_path is None:
        base_name = os.path.splitext(file_path)[0]
        output_path = f"{base_name}_cp932.csv"

    # BOMが文字列の先頭に含まれている可能性がある場合、削除する
    # UTF-8のBOMはU+FEFFという文字で、Pythonの文字列では'\ufeff'として表現される
    if content.startswith('\ufeff'):
        print("文字列の先頭からBOMを削除します")
        content = content[1:]

    # CP932でエンコード可能か事前にチェック
    try:
        content.encode('cp932')
        print("すべての文字がCP932でエンコード可能です")
    except UnicodeEncodeError as e:
        print(f"CP932にエンコードできない文字があります: {e}")
        print("変換できない文字は置換または省略されます")

    # CP932で保存
    try:
        with open(output_path, 'w', encoding='cp932') as file:
            file.write(content)
        print(f"CP932で保存完了: {output_path}")
    except UnicodeEncodeError as e:
        print(f"CP932に変換できない文字があります: {e}")
        # エラーを無視して変換する場合
        with open(output_path, 'w', encoding='cp932', errors='replace') as file:
            file.write(content)
        print(f"一部文字を置換してCP932で保存: {output_path}")
        # どうしても保存できない場合は以下の方法も試せます
        # with open(output_path, 'wb') as file:
        #     file.write(content.encode('cp932', errors='replace'))

    return output_path


def detect_and_convert_to_cp932(file_path, output_path=None):
    """
    ファイルの文字コードを確認してCP932(Shift_JIS)に変換する

    Args:
        file_path (str): 入力ファイルのパス
        output_path (str): 出力ファイルのパス（Noneの場合は元ファイル名_cp932.csvとする）
    """
    # 文字コードを検出してファイルを読み込む
    content, _ = detect_file_encoding(file_path)

    # CP932に変換して保存
    convert_to_cp932(content, file_path, output_path)


# 文字列の文字コードを確認する関数
def check_string_encoding(text):
    """
    文字列をバイト列に変換して文字コードを推定
    """
    # UTF-8でエンコードしてから検出
    byte_data = text.encode('utf-8')
    detected = chardet.detect(byte_data)
    print(f"文字列の推定エンコーディング: {detected}")

    # 各エンコーディングでの表現を確認
    encodings = ['utf-8', 'shift_jis', 'euc-jp', 'iso-2022-jp']

    for enc in encodings:
        try:
            encoded = text.encode(enc)
            print(f"{enc}: {encoded}")
        except UnicodeEncodeError:
            print(f"{enc}: エンコードできません")


# 使用例
if __name__ == "__main__":
    # コマンドライン引数の設定
    parser = argparse.ArgumentParser(description='CSVファイルをCP932(Shift_JIS)に変換するツール')
    parser.add_argument('input_file', help='変換するCSVファイルのパス')
    parser.add_argument('-o', '--output', help='出力ファイルのパス（指定しない場合は元ファイル名_cp932.csvとなります）')

    # 引数の解析
    args = parser.parse_args()

    # ファイルの文字コード確認と変換
    detect_and_convert_to_cp932(args.input_file, args.output)
