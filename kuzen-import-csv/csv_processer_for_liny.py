import pandas as pd
import chardet
import re
from pyasn1.type import tag


def update_customer_data(system_a_csv, system_b_csv, output_csv,
                         matching_key_a='ユーザーID', matching_key_b='LINE UserID',
                         tags=None,
                         columns_to_update=None):
    """
    システムAのデータを使ってシステムBのデータを上書き更新する関数
    システムAのデータを基準にループ処理を行う
    共通情報のみを更新する

    Parameters:
    - system_a_csv: システムAのCSVファイルパス（更新元）
    - system_b_csv: システムBのCSVファイルパス（更新先）
    - output_csv: 出力CSVファイルパス
    - matching_key_a: システムAでの顧客番号カラム名
    - matching_key_b: システムBでの生徒1の顧客番号カラム名
    - tags: タグのマッピング辞書。今は使っていないので使う時は修正して下さい。
    - columns_to_update: 共通情報の更新するカラムのマッピング辞書 {'システムBのカラム名': 'システムAのカラム名'}
    """
    print(f"processing...")
    try:
        # データ部分を読み込む
        df_a = pd.read_csv(system_a_csv, encoding="CP932", dtype=str)
        print(f"システムAのデータ: {len(df_a)}行, {len(df_a.columns)}列")
        print(df_a[[matching_key_a]].head())  # 顧客番号のカラムを表示

        # システムBのCSVファイルを読み込む
        print(f"\nシステムBのCSVファイル '{system_b_csv}' を読み込んでいます...")
        with open(system_b_csv, 'r', encoding='CP932') as f:
            header_line = f.readline().strip()

        # 検出されたエンコーディングを使用
        df_b = pd.read_csv(system_b_csv, header=1, encoding="CP932", dtype=str)

        # キー列の存在チェック
        if matching_key_a not in df_a.columns:
            raise ValueError(f"システムAのCSVに '{matching_key_a}' という列が見つかりません。")
        if matching_key_b not in df_b.columns:
            raise ValueError(f"システムBのCSVに '{matching_key_b}' という列が見つかりません。")

        # 更新対象カラムの設定
        if tags is None or columns_to_update is None:
            raise ValueError(f"関数への入力が正しくありません。")

        nan_rows = df_a[df_a[matching_key_a].isna()]
        if not nan_rows.empty:
            print(f"\n警告: LinyのデータにNaNのマッチングキーが{len(nan_rows)}件あります")
            print("--- NaNを含む行のデータ ---")
            print(nan_rows[[matching_key_a, "ID"]].to_string())  # NaNを含む行の顧客番号を表示
            print("以上の行は除外されます")

        # kuzenのcsvからマッチングキーがNaNを除外してから処理
        df_a_clean = df_a.dropna(subset=[matching_key_a])
        print(f"\n有効なデータ行数: {len(df_a_clean)}行（除外された行数: {len(df_a) - len(df_a_clean)}行）")

        # 更新前の状態をバックアップ
        # df_b_original = df_b.copy()

        # システムBの顧客番号をキーにして辞書を作成（高速なルックアップのため）
        system_b_lookup_dict = {str(customer_id): idx for idx, customer_id in enumerate(df_b[matching_key_b])}

        # 更新カウンタ
        updated_rows = 0
        updated_cells = 0
        missing_customers = 0

        # Kuzenの各行を処理 (変更部分: Kuzenをベースにループ)
        for idx, row in df_a_clean.iterrows():
            matching_id = row[matching_key_a]

            # システムBにこのマッチングキーが存在するか確認
            if str(matching_id) in system_b_lookup_dict:
                b_idx = system_b_lookup_dict[str(matching_id)]
                row_updated = False

                for system_a_col_name, system_b_col_name in columns_to_update.items():
                    if system_a_col_name in df_a_clean.columns:
                        # 元の値と新しい値を取得
                        original_value = df_b.at[b_idx, system_b_col_name]
                        new_value = row[system_a_col_name]

                        # Kuzenに値が存在していて、値が異なる場合のみ更新
                        if original_value != new_value and not pd.isna(new_value):
                            # 日付形式の変換 (YYYY-MM-DD -> YYYY/MM/DD)
                            date_columns = [
                                '生年月日',
                                '挙式日',
                                '最終利用日',
                                '利用開始日'
                            ]

                            # 日付形式の文字列かどうかを正規表現で確認してから変換
                            if system_a_col_name in date_columns and new_value and isinstance(new_value, str):
                                # YYYY-MM-DD形式の日付を検出する正規表現
                                date_pattern = r'(\d{4})-(\d{1,2})-(\d{1,2})'
                                if re.search(date_pattern, new_value):
                                    # 日付形式のハイフンのみを置換
                                    new_value = re.sub(date_pattern, r'\1/\2/\3', new_value)

                            df_b.at[b_idx, system_b_col_name] = new_value
                            updated_cells += 1
                            row_updated = True
                # for tag_a_value, tag_b_column in tags.items():
                #     df_a_tag_name = row['校舎=校舎名のタグで1']
                #     if tag_a_value == df_a_tag_name:
                #         original_value = df_b.at[b_idx, tag_b_column]
                #         new_value = 1
                #         if original_value != 1:
                #             # タグが一致する場合のみ更新
                #             df_b.at[b_idx, tag_b_column] = new_value

                if row_updated:
                    updated_rows += 1

            else:
                # システムBにマッチングキーが存在しない場合
                missing_customers += 1
                # print(f"Kuzenのマッチングキー '{matching_id}'、名前　'{row['ユーザー名']}' はLinyのシステムに存在しません。")

        # 更新統計
        print(f"\n更新統計:")
        print(f"Kuzenの有効顧客データ: {len(df_a_clean)}件")
        print(f"システムBに存在しない顧客: {missing_customers}件")
        print(f"更新された顧客: {updated_rows}件")
        print(f"更新されたセル: {updated_cells}件")

        # 結果を出力CSVに保存
        # df_b.to_csv(output_csv, index=False, encoding="shift_jis")
        # todo: output_csvをいい感じにできるなら
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
    system_a_csv = "kuzen-user-list-1 (1)_cp932.csv"  # KuzenのCSV（更新元）
    system_b_csv = "member_202509021516_20250902151617.csv"  # Liny(Liny)の既存CSV（更新先）
    output_csv = f"BP_for_import_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.csv"  # 更新後のCSV

    # キー列名を設定（マッチングキーのカラム名）
    matching_key_a = "ユーザーID"  # Kuzenでのマッチングキーカラム名
    matching_key_b = "LINE UserID"  # Linyでの生徒1のマッチングキーカラム名

    # 更新するカラムのマッピングを設定
    # fixme: ここを修正する
    columns_to_update = {
        'お名前': 'フリガナ',
        '生年月日': '生年月日（年月日）',
        '流入経路': '流入経路',
        '式前式後': '式前式後',
        '挙式日': '挙式日（年月日）',
        '会場': '会場',
        '式前後_会場': '式前後_会場',
        '都道府県': 'お住まい',
        'セミナー日程': 'セミナー日程',
        '保険セミナー申込みフラグ': '保険セミナー申込みフラグ',
        '住宅相談セミナー申込みフラグ': '住宅相談セミナー申込みフラグ',
        '住宅_成約済み': '住宅_成約済み',
        '住宅セミナー開催日': '住宅セミナー開催日',
        '家族構成': '家族構成',
        '最終利用日': '最終利用日（年月日）',
        '利用開始日': '利用開始日（年月日）',
        '最終アンフォロー日時': '最終アンフォロー日時',
        '住宅相談セミナーアンケート完了フラグ': '住宅セミナー予約',
        'メールアドレス': 'メールアドレス',
        '保険セミナーアンケート完了フラグ': '保険セミナーアンケート完了フラグ',
        '流入経路_保存用': '流入経路_保存用',
        '流入経路_Webページ': '流入経路_Webページ',
        '保険セミナー開催日': '保険セミナー開催日'
    }

    tags = {
        # '渋谷 留学校': '渋谷 留学校',
        # 'KR館': '慶應NY校',
        # '自由が丘校': '自由が丘校',
        # '二子玉川校': '二子玉川ライズ校',
        # '池袋校': '池袋校',
        # '吉祥寺校': '吉祥寺校',
        # '横浜校': '横浜校',
        # '薬院大通校': '薬院大通校',
        # '西新校': '西新校',
        # 'オンライン校': 'オンライン校',
    }

    # データ更新を実行
    result_df = update_customer_data(
        system_a_csv,  # kuzen
        system_b_csv,  # liny
        output_csv,
        matching_key_a=matching_key_a,
        matching_key_b=matching_key_b,
        tags=tags,
        columns_to_update=columns_to_update
    )
