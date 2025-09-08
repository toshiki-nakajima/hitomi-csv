#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CSV File Splitter

This script splits a CSV file into multiple smaller files, each under a specified size limit.
It preserves the header rows in each split file and maintains the original file encoding (CP932).

Usage:
    python csv_splitter.py input.csv [max_size_mb]

Arguments:
    input.csv   - Path to the CSV file to split
    max_size_mb - Maximum size of each split file in MB (default: 1)
"""

import os
import sys
import argparse


def split_csv_by_size(csv_file_path, max_size_mb=1, encoding='CP932'):
    """
    CSVファイルを指定されたサイズ（デフォルト1MB）以下に分割する関数

    Parameters:
    - csv_file_path: 分割するCSVファイルのパス
    - max_size_mb: 分割後の各ファイルの最大サイズ（MB単位）
    - encoding: CSVファイルのエンコーディング（デフォルト: CP932）

    Returns:
    - 分割されたファイルのパスのリスト

    Note:
    - 元のファイルは保持されます
    - 分割されたファイルは元のファイル名に _part1, _part2 などの接尾辞が付きます
    - 各分割ファイルにはヘッダー行が含まれます
    """
    max_size_bytes = max_size_mb * 1024 * 1024  # MBをバイトに変換

    # 元のファイルが存在するか確認
    if not os.path.exists(csv_file_path):
        print(f"エラー: ファイル '{csv_file_path}' が見つかりません。")
        return []

    # 元のファイルが既に指定サイズ以下の場合は分割しない
    if os.path.getsize(csv_file_path) <= max_size_bytes:
        print(f"ファイルサイズは既に{max_size_mb}MB以下です。分割は不要です。")
        return [csv_file_path]

    # 元のファイル名から拡張子を分離
    base_name, extension = os.path.splitext(csv_file_path)

    try:
        # ヘッダー行を取得
        with open(csv_file_path, 'r', encoding=encoding) as f:
            header_line = f.readline().strip()
            second_line = f.readline().strip()  # 2行目（カテゴリ行）も取得
    except UnicodeDecodeError:
        print(f"エラー: ファイル '{csv_file_path}' を '{encoding}' エンコーディングで読み込めません。")
        return []

    # 分割ファイルのパスリスト
    split_files = []

    try:
        # 元のファイルを読み込んで分割
        with open(csv_file_path, 'r', encoding=encoding) as f:
            # ヘッダー行をスキップ（既に読み取り済み）
            f.readline()
            f.readline()

            part_num = 1
            current_file = None
            current_size = 0

            # 新しいファイルを作成する関数
            def create_new_file():
                nonlocal current_file, current_size, part_num
                file_path = f"{base_name}_part{part_num}{extension}"
                current_file = open(file_path, 'w', encoding=encoding)
                # ヘッダー行を書き込む
                current_file.write(header_line + '\n')
                current_file.write(second_line + '\n')
                # ヘッダーのサイズを計算
                current_size = len((header_line + '\n').encode(encoding)) + len((second_line + '\n').encode(encoding))
                split_files.append(file_path)
                part_num += 1
                return file_path

            # 最初のファイルを作成
            current_file_path = create_new_file()
            print(f"分割ファイルを作成しています: {current_file_path}")

            # max_size_bytesに余裕を持たせる
            effective_max_size = max_size_bytes * 0.95  # 5%の余裕を持たせる

            # 行ごとに処理
            for line in f:
                # 行のサイズを計算
                line_size = len(line.encode(encoding))

                # 現在のファイルに行を追加するとサイズ制限を超える場合、新しいファイルを作成
                if current_size + line_size > effective_max_size:
                    current_file.close()
                    current_file_path = create_new_file()
                    print(f"分割ファイルを作成しています: {current_file_path}")

                # 行を書き込む
                current_file.write(line)
                current_size += line_size

            # 最後のファイルを閉じる
            if current_file:
                current_file.close()

        print(f"CSVファイルを{len(split_files)}個のファイルに分割しました。")
        return split_files

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        # 作成途中のファイルをクリーンアップ
        for file_path in split_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"一時ファイル '{file_path}' を削除しました。")
                except:
                    pass
        return []


def main():
    """コマンドライン引数を解析して実行する関数"""
    parser = argparse.ArgumentParser(description='CSVファイルを指定されたサイズに分割します。')
    parser.add_argument('csv_file', help='分割するCSVファイルのパス')
    parser.add_argument('--max-size', type=float, default=1.0, help='分割後の各ファイルの最大サイズ（MB単位、デフォルト: 1.0）')
    parser.add_argument('--encoding', default='CP932', help='CSVファイルのエンコーディング（デフォルト: CP932）')
    
    args = parser.parse_args()
    
    # CSVファイルを分割
    split_files = split_csv_by_size(args.csv_file, args.max_size, args.encoding)
    
    if split_files:
        print("\n分割されたファイル:")
        for file_path in split_files:
            print(f"- {file_path}")


if __name__ == "__main__":
    main()