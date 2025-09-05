#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for csv_splitter.py

This script creates a sample CSV file and tests the split_csv_by_size function.
"""

import os
import sys
import tempfile
from csv_splitter import split_csv_by_size

def create_test_csv(file_path, size_kb=500, encoding='CP932'):
    """
    テスト用のCSVファイルを作成する関数
    
    Parameters:
    - file_path: 作成するCSVファイルのパス
    - size_kb: 作成するファイルのおおよそのサイズ（KB単位）
    - encoding: ファイルのエンコーディング
    """
    # ヘッダー行
    header = "ID,名前,メールアドレス,電話番号,住所"
    category = "識別子,氏名,連絡先,連絡先,住所情報"
    
    # データ行のテンプレート
    data_template = '{},テスト太郎{},test{}@example.com,090-1234-5678,東京都渋谷区テスト町1-2-3'
    
    with open(file_path, 'w', encoding=encoding) as f:
        # ヘッダー行を書き込む
        f.write(header + '\n')
        f.write(category + '\n')
        
        # 指定されたサイズになるまでデータ行を書き込む
        current_size = len((header + '\n').encode(encoding)) + len((category + '\n').encode(encoding))
        target_size = size_kb * 1024  # KBをバイトに変換
        
        i = 1
        while current_size < target_size:
            data_line = data_template.format(i, i, i)
            f.write(data_line + '\n')
            current_size += len((data_line + '\n').encode(encoding))
            i += 1
    
    print(f"テスト用CSVファイル '{file_path}' を作成しました（サイズ: {os.path.getsize(file_path) / 1024:.2f} KB）")
    return os.path.getsize(file_path)

def test_split_csv():
    """
    split_csv_by_size関数をテストする関数
    """
    # 一時ディレクトリにテスト用CSVファイルを作成
    temp_dir = tempfile.gettempdir()
    test_csv_path = os.path.join(temp_dir, "test_large.csv")
    
    try:
        # 約1.5MBのテスト用CSVファイルを作成
        file_size = create_test_csv(test_csv_path, size_kb=1500)
        print(f"作成されたファイルサイズ: {file_size / (1024*1024):.2f} MB")
        
        # 1MB以下に分割
        print("\nCSVファイルを1MB以下に分割します...")
        split_files = split_csv_by_size(test_csv_path, max_size_mb=1.0)
        
        # 分割結果を確認
        if split_files:
            print(f"\n分割されたファイル数: {len(split_files)}")
            for file_path in split_files:
                file_size = os.path.getsize(file_path)
                print(f"- {os.path.basename(file_path)}: {file_size / (1024*1024):.2f} MB")
            
            # 分割されたファイルの内容を確認（最初の数行）
            print("\n最初の分割ファイルの内容（最初の5行）:")
            with open(split_files[0], 'r', encoding='CP932') as f:
                for i, line in enumerate(f):
                    if i < 5:
                        print(line.strip())
                    else:
                        break
            
            # テスト成功
            print("\nテスト成功: CSVファイルが正常に分割されました。")
            return True
        else:
            print("\nテスト失敗: CSVファイルの分割に失敗しました。")
            return False
    
    except Exception as e:
        print(f"\nテスト中にエラーが発生しました: {e}")
        return False
    
    finally:
        # テスト用ファイルのクリーンアップ
        try:
            if os.path.exists(test_csv_path):
                os.remove(test_csv_path)
                print(f"\nテスト用ファイル '{test_csv_path}' を削除しました。")
            
            # 分割されたファイルも削除
            base_name, extension = os.path.splitext(test_csv_path)
            i = 1
            while True:
                split_file = f"{base_name}_part{i}{extension}"
                if os.path.exists(split_file):
                    os.remove(split_file)
                    print(f"分割ファイル '{split_file}' を削除しました。")
                    i += 1
                else:
                    break
        except Exception as e:
            print(f"クリーンアップ中にエラーが発生しました: {e}")

if __name__ == "__main__":
    print("CSV Splitterのテストを開始します...\n")
    test_split_csv()