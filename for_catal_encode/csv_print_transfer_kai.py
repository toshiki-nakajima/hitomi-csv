import pandas as pd
import chardet
from pyasn1.type import tag


def update_customer_data(system_a_csv, system_b_csv, output_csv,
                         key_a='顧客番号', key_b1='顧客番号', key_b2='生徒2_顧客番号', key_b3='生徒3_顧客番号',
                         tags=None,
                         columns_to_update=None,
                         columns_to_update_student1=None, columns_to_update_student2=None, columns_to_update_student3=None):
    """
    システムAのデータを使ってシステムBのデータを上書き更新する関数
    システムAのデータを基準にループ処理を行う

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
        temp_df_a = pd.read_csv(system_a_csv, header=None, nrows=2, encoding="UTF-8")
        categories = temp_df_a.iloc[0].tolist()
        column_names_a = temp_df_a.iloc[1].tolist()

        # カテゴリと列名の対応を表示
        category_dict = dict(zip(column_names_a, categories))
        print("\n--- システムAの列情報 ---")
        for col, cat in category_dict.items():
            print(f"{col}: {cat}")

        # データ部分を読み込む
        df_a = pd.read_csv(system_a_csv, header=1, encoding="UTF-8", dtype=str)
        print(f"システムAのデータ: {len(df_a)}行, {len(df_a.columns)}列")
        print(df_a[[key_a]].head())  # 顧客番号のカラムを表示

        # システムBのCSVファイルを読み込む
        print(f"\nシステムBのCSVファイル '{system_b_csv}' を読み込んでいます...")
        # with open(system_b_csv, 'rb') as f:
        #     result = chardet.detect(f.read())
        #
        # print(f"検出されたエンコーディング: {result['encoding']} (信頼度: {result['confidence']})")
        with open(system_b_csv, 'r', encoding='CP932') as f:
            header_line = f.readline().strip()

        # 検出されたエンコーディングを使用
        df_b = pd.read_csv(system_b_csv, header=1, encoding="CP932", dtype=str)

        # キー列の存在チェック
        if key_a not in df_a.columns:
            raise ValueError(f"システムAのCSVに '{key_a}' という列が見つかりません。")
        if key_b1 not in df_b.columns:
            raise ValueError(f"システムBのCSVに '{key_b1}' という列が見つかりません。")
        if key_b2 not in df_b.columns:
            raise ValueError(f"システムBのCSVに '{key_b2}' という列が見つかりません。")
        if key_b3 not in df_b.columns:
            raise ValueError(f"システムBのCSVに '{key_b3}' という列が見つかりません。")

        # 更新対象カラムの設定
        if tags is None or columns_to_update is None or columns_to_update_student1 is None or columns_to_update_student2 is None or columns_to_update_student3 is None:
            raise ValueError(f"関数への入力が正しくありません。")

        # print("\n--- 更新対象カラム ---")
        # for b_col, a_col in columns_to_update.items():
        #     print(f"システムB '{b_col}' ← システムA '{a_col}'")

        nan_rows = df_a[df_a[key_a].isna()]
        if not nan_rows.empty:
            print(f"\n警告: システムAのデータにNaNの顧客番号が{len(nan_rows)}件あります")
            print("--- NaNを含む行のデータ ---")
            print(nan_rows[[key_a, "氏名"]].to_string())  # NaNを含む行の顧客番号を表示
            print("以上の行は除外されます")

        # NaNを除外してから処理
        df_a_clean = df_a.dropna(subset=[key_a])
        print(f"\n有効なデータ行数: {len(df_a_clean)}行（除外された行数: {len(df_a) - len(df_a_clean)}行）")

        # 更新前の状態をバックアップ
        # df_b_original = df_b.copy()

        # システムBの顧客番号をキーにして辞書を作成（高速なルックアップのため）
        system_b_dict1 = {str(customer_id): idx for idx, customer_id in enumerate(df_b[key_b1])}
        system_b_dict2 = {str(customer_id): idx for idx, customer_id in enumerate(df_b[key_b2])}
        system_b_dict3 = {str(customer_id): idx for idx, customer_id in enumerate(df_b[key_b3])}

        # 更新カウンタ
        updated_rows = 0
        updated_cells = 0
        missing_customers = 0

        # システムAの各行を処理 (変更部分: システムAをベースにループ)
        for idx, row in df_a_clean.iterrows():
            customer_id = row[key_a]

            # システムBにこの顧客番号が存在するか確認
            if str(customer_id) in system_b_dict1:
                b_idx = system_b_dict1[str(customer_id)]
                row_updated = False

                for b_col, a_col in columns_to_update.items():
                    if a_col in df_a_clean.columns:
                        # 元の値と新しい値を取得
                        original_value = df_b.at[b_idx, b_col]
                        new_value = row[a_col]

                        # システムAに値が存在していて、値が異なる場合のみ更新
                        if original_value != new_value and not pd.isna(new_value):
                            df_b.at[b_idx, b_col] = new_value
                            updated_cells += 1
                            row_updated = True
                for tag_a_value, tag_b_column in tags.items():
                    df_a_tag_name = row['校舎=校舎名のタグで1']
                    if tag_a_value == df_a_tag_name:
                        original_value = df_b.at[b_idx, tag_b_column]
                        new_value = 1
                        if original_value != 1:
                            # タグが一致する場合のみ更新
                            df_b.at[b_idx, tag_b_column] = new_value
                for b_col, a_col in columns_to_update_student1.items():
                    if a_col in df_a_clean.columns:
                        # 元の値と新しい値を取得
                        original_value = df_b.at[b_idx, b_col]
                        new_value = row[a_col]

                        # システムAに値が存在していて、値が異なる場合のみ更新
                        if original_value != new_value and not pd.isna(new_value):
                            df_b.at[b_idx, b_col] = new_value
                            updated_cells += 1
                            row_updated = True
                if "ステータス" in df_a_clean.columns:
                    original_value = df_b.at[b_idx, "生徒1_ステータス"]
                    new_value = row["ステータス"]
                    if original_value != new_value and not pd.isna(new_value):
                        df_b.at[b_idx, "生徒1_ステータス"] = new_value
                        updated_cells += 1
                        row_updated = True

                if row_updated:
                    updated_rows += 1
            elif str(customer_id) in system_b_dict2:
                print("2!!!!!!!!!!!!!!!" + str(customer_id))
                b_idx = system_b_dict2[str(customer_id)]
                row_updated = False

                for b_col, a_col in columns_to_update_student2.items():
                    if a_col in df_a_clean.columns:
                        # 元の値と新しい値を取得
                        original_value = df_b.at[b_idx, b_col]
                        new_value = row[a_col]

                        # システムAに値が存在していて、値が異なる場合のみ更新
                        if original_value != new_value and not pd.isna(new_value):
                            df_b.at[b_idx, b_col] = new_value
                            updated_cells += 1
                            row_updated = True
                if "ステータス" in df_a_clean.columns:
                    original_value = df_b.at[b_idx, "生徒2_ステータス"]
                    new_value = row["ステータス"]
                    if original_value != new_value and not pd.isna(new_value):
                        df_b.at[b_idx, "生徒2_ステータス"] = new_value
                        updated_cells += 1
                        row_updated = True

                if row_updated:
                    updated_rows += 1
            elif str(customer_id) in system_b_dict3:
                b_idx = system_b_dict3[str(customer_id)]
                row_updated = False

                for b_col, a_col in columns_to_update_student3.items():
                    if a_col in df_a_clean.columns:
                        # 元の値と新しい値を取得
                        original_value = df_b.at[b_idx, b_col]
                        new_value = row[a_col]

                        # システムAに値が存在していて、値が異なる場合のみ更新
                        if original_value != new_value and not pd.isna(new_value):
                            df_b.at[b_idx, b_col] = new_value
                            updated_cells += 1
                            row_updated = True

                if "ステータス" in df_a_clean.columns:
                    original_value = df_b.at[b_idx, "生徒3_ステータス"]
                    new_value = row["ステータス"]
                    if original_value != new_value and not pd.isna(new_value):
                        df_b.at[b_idx, "生徒3_ステータス"] = new_value
                        updated_cells += 1
                        row_updated = True

                if row_updated:
                    updated_rows += 1

            else:
                # システムBに顧客番号が存在しない場合
                missing_customers += 1
                print(f"システムAの顧客番号 '{customer_id}'、名前　'{row['氏名']}' はLinyのシステムに存在しません。")

        # 更新統計
        print(f"\n更新統計:")
        print(f"システムAの有効顧客データ: {len(df_a_clean)}件")
        print(f"システムBに存在しない顧客: {missing_customers}件")
        print(f"更新された顧客: {updated_rows}件")
        print(f"更新されたセル: {updated_cells}件")

        # 結果を出力CSVに保存
        # df_b.to_csv(output_csv, index=False, encoding="shift_jis")
        with open(output_csv, 'w', encoding='CP932') as f:
            # まず、保存していたカテゴリ行を書き込む
            f.write(header_line + '\n')
            # その後、データフレームを書き込む
            df_b.to_csv(f, index=False, encoding='CP932')

        print(f"\n結果を '{output_csv}' に保存しました。")

        return df_b

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None


# 使用例
if __name__ == "__main__":
    # ファイルパスを設定
    system_a_csv = "【近藤編集】Salesforce塾生データ_渋谷校以外.csv"  # システムA(SalesForce)のCSV（更新元）
    system_b_csv = "CSV渋谷校以外インポート用3_20250525220826.csv"  # システムB(Liny)の既存CSV（更新先）
    output_csv = f"liny_csv_updated_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.csv"  # 更新後のCSV

    # キー列名を設定（顧客番号のカラム名）
    key_column_system_a = "顧客番号"  # システムAでの顧客番号カラム名
    key_column_system_b1 = "生徒1_顧客番号"  # システムBでの顧客番号カラム名
    key_column_system_b2 = "生徒2_顧客番号"  # システムBでの顧客番号カラム名
    key_column_system_b3 = "生徒3_顧客番号"  # システムBでの顧客番号カラム名

    # 更新するカラムのマッピングを設定
    columns_to_update = {
        # Linyのカラム名(systemB): SalesForceのカラム名(systemA)
        # '生徒1_氏名': '氏名',
        # '生徒1_ふりがな': 'ふりがな',
        # '生徒1_性別': '性別',
        # '生徒1_生年月日': '生年月日',
        # '生徒1_Entry時の学年': 'Entry時の学年',
        '保護者氏名': '保護者氏名',
        '電話番号': '電話番号',
        'メールアドレス': 'メールアドレス',
        '郵便番号': '郵便番号',
        '都道府県': '都道府県',
        '市町村区': '市町村区',
        '町域': '町域',
        # '生徒1_休会/退会種別': '休会/退会種別',
        # '生徒1_体験レッスン申込日': '体験レッスン申込日',
        # '生徒1_レギュラー_初回レッスン日': 'レギュラー_初回レッスン日',
        # '生徒1_継続月数（既存用）': '継続月数（既存用）',
        # '生徒1_英語学習の目標・目的': '英語学習の目標・目的',
        # '生徒1_他塾名': '他塾名',
        # '生徒1_学校の英語の成績': '学校の英語の成績',
        # '生徒1_取得英検級': '取得英検級',
        # '生徒1_直近の受験英検級': '直近の受験英検級',
        # '生徒1_お子さまの性格・モチベーション': 'お子さまの性格・モチベーション',
        # '生徒1_スタッフと保護者様だけで相談したい話': 'スタッフと保護者様だけで相談したい話',
        # '生徒1_キャタルを知ったきっかけ': 'キャタルを知ったきっかけ',
        # '生徒1_紹介元の氏名': '紹介元の氏名',
        # '生徒1_体験レッスンに申し込んだ決め手': '体験レッスンに申し込んだ決め手',
        # '生徒1_体験レッスン申し込みまでに分かりづらかった点': '体験レッスン申し込みまでに分かりづらかった点',
        # '渋谷校': '渋谷校',
        '塾生紹介': '塾生紹介',
        '社長紹介': '社長紹介',
        'キャタルコミュニケーションズ マークさん': 'キャタルコミュニケーションズ マークさん',
        'President Family プレジデント・ファミリー': 'President Family プレジデント・ファミリー',
        'Bon Voyage ボン・ボヤージュ': 'Bon Voyage ボン・ボヤージュ',
    }
    tags = {
        '渋谷 留学校': '渋谷 留学校',
        'KR館': '慶應NY校',
        '自由が丘校': '自由が丘校',
        '二子玉川校': '二子玉川ライズ校',
        '池袋校': '池袋校',
        '吉祥寺校': '吉祥寺校',
        '横浜校': '横浜校',
        '薬院大通校': '薬院大通校',
        '西新校': '西新校',
        'オンライン校': 'オンライン校',
    }
    # 生徒1のカラム更新をしたい項目はこっちに抜き出す
    columns_to_update_student1 = {
        '生徒1_氏名': '氏名',
        '生徒1_ふりがな': 'ふりがな',
        '生徒1_性別': '性別',
        '生徒1_生年月日': '生年月日',
        '生徒1_Entry時の学年': 'Entry時の学年',
        '生徒1_小学校名': '小学校名',
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
        '生徒1_ステータス': 'ステータス',
        '生徒1_詳細': '詳細',
    }

    # 生徒2のカラム更新をしたい項目はこっちに抜き出す
    columns_to_update_student2 = {
        '生徒2_氏名': '氏名',
        '生徒2_ふりがな': 'ふりがな',
        '生徒2_性別': '性別',
        '生徒2_生年月日': '生年月日',
        '生徒2_Entry時の学年': 'Entry時の学年',
        '生徒2_小学校名': '小学校名', #これほんまにいいんか！！！！！！！！！！！！！！！
        '生徒2_休会/退会種別': '休会/退会種別',
        '生徒2_体験レッスン申込日': '体験レッスン申込日',
        '生徒2_レギュラー_初回レッスン日': 'レギュラー_初回レッスン日',
        '生徒2_継続月数（既存用）': '継続月数（既存用）',
        '生徒2_英語学習の目標・目的': '英語学習の目標・目的',
        '生徒2_他塾名': '他塾名',
        '生徒2_学校の英語の成績': '学校の英語の成績',
        '生徒2_取得英検級': '取得英検級',
        '生徒2_直近の受験英検級': '直近の受験英検級',
        '生徒2_お子さまの性格・モチベーション': 'お子さまの性格・モチベーション',
        '生徒2_スタッフと保護者様だけで相談したい話': 'スタッフと保護者様だけで相談したい話',
        '生徒2_キャタルを知ったきっかけ': 'キャタルを知ったきっかけ',
        # '生徒2_紹介元の氏名': '紹介元の氏名',
        '生徒2_体験レッスンに申し込んだ決め手': '体験レッスンに申し込んだ決め手',
        '生徒2_体験レッスン申し込みまでに分かりづらかった点': '体験レッスン申し込みまでに分かりづらかった点',
        '生徒2_ステータス': 'ステータス',
        '生徒2_詳細': '詳細',
    }

    # 生徒3のカラム更新をしたい項目はこっちに抜き出す
    columns_to_update_student3 = {
        '生徒3_氏名': '氏名',
        '生徒3_ふりがな': 'ふりがな',
        '生徒3_性別': '性別',
        '生徒3_生年月日': '生年月日',
        '生徒3_Entry時の学年': 'Entry時の学年',
        '生徒3_小学校名': '小学校名',
        '生徒3_休会/退会種別': '休会/退会種別',
        '生徒3_体験レッスン申込日': '体験レッスン申込日',
        '生徒3_レギュラー_初回レッスン日': 'レギュラー_初回レッスン日',
        '生徒3_継続月数（既存用）': '継続月数（既存用）',
        '生徒3_英語学習の目標・目的': '英語学習の目標・目的',
        '生徒3_他塾名': '他塾名',
        '生徒3_学校の英語の成績': '学校の英語の成績',
        '生徒3_取得英検級': '取得英検級',
        '生徒3_直近の受験英検級': '直近の受験英検級',
        '生徒3_お子さまの性格・モチベーション': 'お子さまの性格・モチベーション',
        '生徒3_スタッフと保護者様だけで相談したい話': 'スタッフと保護者様だけで相談したい話',
        '生徒3_キャタルを知ったきっかけ': 'キャタルを知ったきっかけ',
        # '生徒3_紹介元の氏名': '紹介元の氏名',
        '生徒3_体験レッスンに申し込んだ決め手': '体験レッスンに申し込んだ決め手',
        '生徒3_体験レッスン申し込みまでに分かりづらかった点': '体験レッスン申し込みまでに分かりづらかった点',
        '生徒3_ステータス': 'ステータス',
        '生徒3_詳細': '詳細',
    }
    # データ更新を実行
    result_df = update_customer_data(
        system_a_csv, # salesforce
        system_b_csv, # liny
        output_csv,
        key_a=key_column_system_a,
        key_b1=key_column_system_b1,
        key_b2=key_column_system_b2,
        key_b3=key_column_system_b3,
        tags=tags,
        columns_to_update=columns_to_update,
        columns_to_update_student1=columns_to_update_student1,
        columns_to_update_student2=columns_to_update_student2,
        columns_to_update_student3=columns_to_update_student3,

    )