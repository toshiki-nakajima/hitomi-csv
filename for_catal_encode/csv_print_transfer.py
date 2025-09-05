from traceback import print_tb

import chardet
import pandas as pd


def update_customer_data(system_a_csv, system_b_csv, output_csv,
                         key_a='顧客番号', key_b='顧客番号',
                         columns_to_update=None):
    """
    システムAのデータを使ってシステムBのデータを上書き更新する関数

    Parameters:
    - system_a_csv: システムAのCSVファイルパス（更新元）
    - system_b_csv: システムBのCSVファイルパス（更新先）
    - output_csv: 出力CSVファイルパス
    - key_a: システムAでの顧客番号カラム名
    - key_b: システムBでの顧客番号カラム名
    - columns_to_update: 更新するカラムのマッピング辞書 {'システムBのカラム名': 'システムAのカラム名'}
    """
    try:
        # システムAのCSVファイルを読み込む
        print(f"システムAのCSVファイル '{system_a_csv}' を読み込んでいます...")
        # 1行目がカテゴリ情報で2行目がカラム名の場合
        temp_df_a = pd.read_csv(system_a_csv, header=None, nrows=2, encoding="shift-jis")
        categories = temp_df_a.iloc[0].tolist()
        column_names_a = temp_df_a.iloc[1].tolist()

        # カテゴリと列名の対応を表示
        category_dict = dict(zip(column_names_a, categories))
        print("\n--- システムAの列情報 ---")
        for col, cat in category_dict.items():
            print(f"{col}: {cat}")

        # データ部分を読み込む
        df_a = pd.read_csv(system_a_csv, header=1, encoding="CP932", dtype={key_a: str})
        print(f"システムAのデータ: {len(df_a)}行, {len(df_a.columns)}列")
        print(df_a[[key_a]].head())  # 顧客番号のカラムを表示

        # システムBのCSVファイルを読み込む
        print(f"\nシステムBのCSVファイル '{system_b_csv}' を読み込んでいます...")
        with open(system_b_csv, 'rb') as f:
            result = chardet.detect(f.read())

        print(f"検出されたエンコーディング: {result['encoding']} (信頼度: {result['confidence']})")

        # 検出されたエンコーディングを使用
        df_b = pd.read_csv(system_b_csv, header=1, encoding=result['encoding'], dtype={key_b: str})

        # キー列の存在チェック
        if key_a not in df_a.columns:
            raise ValueError(f"システムAのCSVに '{key_a}' という列が見つかりません。")
        if key_b not in df_b.columns:
            raise ValueError(f"システムBのCSVに '{key_b}' という列が見つかりません。")

        # 更新対象カラムの設定
        if columns_to_update is None:
            # デフォルトでは、システムAの全カラム（キー列以外）をシステムBに同名のカラムがあれば更新
            columns_to_update = {}
            for col in df_a.columns:
                if col != key_a and col in df_b.columns:
                    columns_to_update[col] = col

        print("\n--- 更新対象カラム ---")
        for b_col, a_col in columns_to_update.items():
            print(f"システムB '{b_col}' ← システムA '{a_col}'")

        nan_rows = df_a[df_a[key_a].isna()]
        if not nan_rows.empty:
            print(f"\n警告: システムAのデータにNaNの顧客番号が{len(nan_rows)}件あります")
            print("--- NaNを含む行のデータ ---")
            print(nan_rows[[key_a, "氏名"]].to_string())  # NaNを含む行の顧客番号を表示
            print("以上の行は除外されます")

        # NaNを除外してから辞書を作成
        df_a_clean = df_a.dropna(subset=[key_a])
        print(f"\n有効なデータ行数: {len(df_a_clean)}行（除外された行数: {len(df_a) - len(df_a_clean)}行）")

        # 顧客番号をキーにして辞書を作成（高速なルックアップのため）
        system_a_dict = df_a_clean.set_index(key_a).to_dict(orient='index')

        # 更新前の状態をバックアップ
        df_b_original = df_b.copy()

        # 更新カウンタ
        updated_rows = 0
        updated_cells = 0

        # システムBの各行を処理
        for idx, row in df_b.iterrows():
            customer_id = row[key_b]

            # システムAにこの顧客番号が存在する場合、データを更新
            if customer_id in system_a_dict:
                row_updated = False

                for b_col, a_col in columns_to_update.items():
                    if a_col in system_a_dict[customer_id]:
                        # 元の値と新しい値を取得
                        original_value = df_b.at[idx, b_col]
                        new_value = system_a_dict[customer_id][a_col]

                        # 値が異なる場合のみ更新
                        if original_value != new_value:
                            df_b.at[idx, b_col] = new_value
                            updated_cells += 1
                            row_updated = True

                if row_updated:
                    updated_rows += 1
            # システムAに顧客番号が存在しない場合、データを表示したい
            if type(customer_id) == float:
                print(f"システムBの顧客番号 '{customer_id}' はシステムAに存在しません。")

        # 更新統計
        print(f"\n更新統計: {len(df_b)}行中{updated_rows}行が更新されました（更新セル数: {updated_cells}）")

        # 結果を出力CSVに保存
        df_b.to_csv(output_csv, index=False)
        print(f"\n結果を '{output_csv}' に保存しました。")

        return df_b

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None


# 使用例
if __name__ == "__main__":
    # ファイルパスを設定
    system_a_csv = "Salesforce_渋谷塾生.csv"  # システムAのCSV（更新元）
    system_b_csv = "member_202504241801_20250424180127.csv"  # システムBの既存CSV（更新先）
    output_csv = "system_b_updated.csv"  # 更新後のCSV

    # キー列名を設定（顧客番号のカラム名）
    key_column_system_a = "顧客番号"  # システムAでの顧客番号カラム名
    key_column_system_b = "生徒1_顧客番号"  # システムBでの顧客番号カラム名

    # 更新するカラムのマッピングを設定
    columns_to_update = {
        # Linyのカラム名: SalesForceのカラム名
        '生徒1_氏名': '氏名',
        '生徒1_ふりがな': 'ふりがな',
        '生徒1_性別': '性別',
        '生徒1_生年月日': '生年月日',
        '生徒1_Entry時の学年': 'Entry時の学年',
        '保護者氏名': '保護者氏名',
        '電話番号': '電話番号',
        'メールアドレス': 'メールアドレス',
        '郵便番号': '郵便番号',
        '都道府県': '都道府県',
        '市町村区': '市町村区',
        '町域': '町域',
        '生徒1_休会/退会種別': '休会/退会種別',
        '生徒1_体験レッスン申込日': '体験レッスン申込日',
        '生徒1_レギュラー_初回レッスン日': 'レギュラー_初回レッスン日',
        '生徒1_継続月数（既存用）': '継続月数（既存用）',
        '生徒1_英語学習の目標・目的': '英語学習の目標・目的',
        '生徒1_他塾名': '他塾名',
        '生徒1_学校の英語の成績': '学校の英語の成績',
        '生徒1_取得英検級': '取得英検級',
        '生徒1_直近の受験英検級': '直近の受験英検級',
        '生徒1_お子さまの性格・モチベーション': 'お子さまの性格・モチベーション',
        '生徒1_スタッフと保護者様だけで相談したい話': 'スタッフと保護者様だけで相談したい話',
        '生徒1_キャタルを知ったきっかけ': 'キャタルを知ったきっかけ',
        '生徒1_紹介元の氏名': '紹介元の氏名',
        '生徒1_体験レッスンに申し込んだ決め手': '体験レッスンに申し込んだ決め手',
        '生徒1_体験レッスン申し込みまでに分かりづらかった点': '体験レッスン申し込みまでに分かりづらかった点',
    }

    # データ更新を実行
    result_df = update_customer_data(
        system_a_csv,
        system_b_csv,
        output_csv,
        key_a=key_column_system_a,
        key_b=key_column_system_b,
        columns_to_update=columns_to_update
    )