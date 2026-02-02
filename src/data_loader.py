"""
データローダーモジュール
ローマ銀貨データおよび因果連鎖分析用データの読み込みと前処理
"""
import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config import (
    DENARII_FILE, PROVINCIAL_FILE, THIRD_CENTURY_FILE,
    CLIMATE_FILE, SHIPWRECK_FILE, INSCRIPTION_FILE, SESHAT_FILE,
    EMPEROR_DATES, COMPOSITION_COLUMNS, ANALYSIS_PERIOD, CAUSAL_ANALYSIS_CONFIG
)


class RomanCoinDataLoader:
    """ローマ貨幣データの読み込みと前処理クラス"""

    def __init__(self):
        self.denarii: Optional[pd.DataFrame] = None
        self.provincial: Optional[pd.DataFrame] = None
        self.third_century: Optional[pd.DataFrame] = None

    def load_denarii(self) -> pd.DataFrame:
        """デナリウス貨データを読み込み"""
        self.denarii = pd.read_excel(DENARII_FILE)
        return self.denarii

    def load_provincial(self) -> pd.DataFrame:
        """属州貨幣データを読み込み"""
        self.provincial = pd.read_excel(PROVINCIAL_FILE)
        return self.provincial

    def load_third_century(self) -> pd.DataFrame:
        """3世紀の銀含有率データを読み込み"""
        self.third_century = pd.read_csv(THIRD_CENTURY_FILE)
        return self.third_century

    def load_all(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """両データセットを読み込み"""
        return self.load_denarii(), self.load_provincial()

    def get_full_time_series(self) -> pd.DataFrame:
        """
        BC44年〜AD295年の完全な銀含有率時系列データを取得

        既存のデナリウス貨データと3世紀データを統合

        Returns:
            DataFrame with columns: year, emperor, silver, coin_type, source
        """
        # 3世紀データを読み込み
        if self.third_century is None:
            self.load_third_century()

        # 必要なカラムのみ選択して統一フォーマットに
        ts = self.third_century[['YEAR', 'EMPEROR', 'SILVER', 'COIN_TYPE', 'SOURCE']].copy()
        ts.columns = ['year', 'emperor', 'silver', 'coin_type', 'source']
        ts = ts.sort_values('year')

        return ts

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        データ前処理パイプライン

        1. 不要なUnnamed列を削除
        2. 成分データを数値型に変換
        3. 異常値を処理
        4. 年代情報を付与
        """
        df = df.copy()

        # 1. 不要列の削除（Unnamed列）
        unnamed_cols = [c for c in df.columns if str(c).startswith('Unnamed')]
        df = df.drop(columns=unnamed_cols, errors='ignore')

        # 2. 数値型への変換
        for col in COMPOSITION_COLUMNS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 3. 異常値の処理（銀含有率が0未満または100超）
        if 'SILVER' in df.columns:
            df.loc[df['SILVER'] < 0, 'SILVER'] = np.nan
            df.loc[df['SILVER'] > 100, 'SILVER'] = 100.0

        # 4. 皇帝名の正規化（大文字小文字の統一）
        if 'EMPEROR' in df.columns:
            df['EMPEROR'] = df['EMPEROR'].str.strip()

        # 5. 年代情報の付与
        if 'EMPEROR' in df.columns:
            df['YEAR_START'] = df['EMPEROR'].map(
                lambda x: EMPEROR_DATES.get(x, {}).get('start', np.nan)
            )
            df['YEAR_END'] = df['EMPEROR'].map(
                lambda x: EMPEROR_DATES.get(x, {}).get('end', np.nan)
            )
            df['YEAR_MIDPOINT'] = df['EMPEROR'].map(
                lambda x: EMPEROR_DATES.get(x, {}).get('midpoint', np.nan)
            )

        return df

    def get_time_series(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        皇帝別の銀含有率時系列データを生成

        Returns:
            DataFrame with columns: emperor, silver_mean, silver_std, count, year
        """
        if 'SILVER' not in df.columns or 'EMPEROR' not in df.columns:
            raise ValueError("DataFrame must have SILVER and EMPEROR columns")

        # 前処理がまだなら実行
        if 'YEAR_MIDPOINT' not in df.columns:
            df = self.preprocess(df)

        ts = df.groupby('EMPEROR').agg({
            'SILVER': ['mean', 'std', 'count'],
            'YEAR_MIDPOINT': 'first'
        }).reset_index()

        ts.columns = ['emperor', 'silver_mean', 'silver_std', 'count', 'year']
        ts = ts.dropna(subset=['year'])
        ts = ts.sort_values('year')

        return ts

    def get_summary_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        成分データの記述統計を取得

        Returns:
            DataFrame with descriptive statistics
        """
        cols = [c for c in COMPOSITION_COLUMNS if c in df.columns]
        return df[cols].describe()

    def get_emperor_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        皇帝別の銀含有率統計を取得

        Returns:
            DataFrame with emperor-level statistics
        """
        if 'YEAR_MIDPOINT' not in df.columns:
            df = self.preprocess(df)

        stats = df.groupby('EMPEROR').agg({
            'SILVER': ['mean', 'std', 'min', 'max', 'count'],
            'YEAR_MIDPOINT': 'first'
        }).round(2)

        stats.columns = ['銀含有率_平均', '銀含有率_標準偏差',
                        '銀含有率_最小', '銀含有率_最大', '件数', '年代']
        stats = stats.sort_values('年代')

        return stats


class CausalChainDataLoader:
    """
    因果連鎖分析用データローダー

    気候 → 農業 → 人口 → 財政 → 社会不安 の因果連鎖検証に必要な
    5種類のデータを読み込み、統合する
    """

    def __init__(self):
        self.climate: Optional[pd.DataFrame] = None
        self.shipwrecks: Optional[pd.DataFrame] = None
        self.inscriptions: Optional[pd.DataFrame] = None
        self.silver: Optional[pd.DataFrame] = None
        self.seshat: Optional[pd.DataFrame] = None
        self.unified: Optional[pd.DataFrame] = None

    def load_climate_data(self) -> pd.DataFrame:
        """
        気候データ（夏季気温偏差）を読み込み

        Source: Luterbacher et al. (2016)
        Period: 138 BCE - 2003 CE
        """
        # NOAAフォーマットのテキストファイルを読み込み
        # ヘッダー行をスキップ
        with open(CLIMATE_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # データ行を探す（#で始まらない行）
        data_start = 0
        for i, line in enumerate(lines):
            if not line.startswith('#') and 'age_CE' in line:
                data_start = i
                break

        # pandasで読み込み
        self.climate = pd.read_csv(
            CLIMATE_FILE,
            sep='\t',
            skiprows=data_start,
            na_values=['', 'NA', 'NaN']
        )

        # カラム名を正規化
        self.climate.columns = ['year', 'temp_mean', 'temp_lower', 'temp_upper']

        # 分析期間にフィルタリング
        self.climate = self.climate[
            (self.climate['year'] >= ANALYSIS_PERIOD['start']) &
            (self.climate['year'] <= ANALYSIS_PERIOD['end'])
        ].copy()

        return self.climate

    def load_shipwreck_data(self) -> pd.DataFrame:
        """
        難破船データを読み込み（農業/交易の代理指標）

        Source: OXREP Shipwrecks Database (Strauss)
        """
        self.shipwrecks = pd.read_excel(SHIPWRECK_FILE)

        # 必要なカラムのみ選択
        cols = ['Wreck ID', 'Earliest date', 'Latest date', 'Period']
        self.shipwrecks = self.shipwrecks[cols].copy()
        self.shipwrecks.columns = ['wreck_id', 'earliest_date', 'latest_date', 'period']

        # 分析期間にフィルタリング（部分的に重複するものも含む）
        self.shipwrecks = self.shipwrecks[
            (self.shipwrecks['earliest_date'] <= ANALYSIS_PERIOD['end']) &
            (self.shipwrecks['latest_date'] >= ANALYSIS_PERIOD['start'])
        ].dropna(subset=['earliest_date', 'latest_date']).copy()

        return self.shipwrecks

    def load_inscription_data(self) -> pd.DataFrame:
        """
        碑文データを読み込み（人口の代理指標）

        Source: LIST Dataset (Latin Inscriptions Structured Text)
        Note: Requires pyarrow for Parquet format
        """
        try:
            self.inscriptions = pd.read_parquet(INSCRIPTION_FILE)
        except ImportError:
            raise ImportError("pyarrow is required to read Parquet files. Install with: pip install pyarrow")

        # 必要なカラムのみ選択
        cols_needed = ['LIST-ID', 'not_before', 'not_after', 'Latitude', 'Longitude']
        cols_available = [c for c in cols_needed if c in self.inscriptions.columns]
        self.inscriptions = self.inscriptions[cols_available].copy()

        # 年代情報のある行のみ
        self.inscriptions = self.inscriptions.dropna(subset=['not_before'])

        # 分析期間にフィルタリング
        self.inscriptions = self.inscriptions[
            (self.inscriptions['not_before'] <= ANALYSIS_PERIOD['end']) &
            (self.inscriptions['not_before'] >= ANALYSIS_PERIOD['start'] - 100)  # 余裕を持たせる
        ].copy()

        return self.inscriptions

    def load_silver_data(self) -> pd.DataFrame:
        """
        銀含有率データを読み込み（財政能力の指標）

        Source: Butcher & Ponting (2015), Walker (1976-78), etc.
        """
        self.silver = pd.read_csv(THIRD_CENTURY_FILE)

        # カラム名を小文字に統一
        self.silver.columns = [c.lower() for c in self.silver.columns]

        # 分析期間にフィルタリング
        self.silver = self.silver[
            (self.silver['year'] >= ANALYSIS_PERIOD['start']) &
            (self.silver['year'] <= ANALYSIS_PERIOD['end'])
        ].copy()

        return self.silver

    def load_seshat_data(self) -> pd.DataFrame:
        """
        Seshat政治不安定データを読み込み

        Source: Seshat Equinox Dataset
        Sheet: TSDat123 (時系列データ)
        """
        # TSDat123シートを読み込み
        df = pd.read_excel(SESHAT_FILE, sheet_name='TSDat123')

        # ローマ帝国のデータを抽出
        roman_polities = ['ItRomPr', 'TrRomDm', 'ItRomLR', 'ItRomMR', 'ItRomER']
        self.seshat = df[df['PolID'].isin(roman_polities)].copy()

        # 必要なカラムを選択
        instability_cols = ['PolID', 'Time', 'ExternalW', 'InternalW', 'IntraElitW',
                           'PopUprising', 'MilRevolt', 'SepRebellion', 'PolPop', 'PolTerr']
        available_cols = [c for c in instability_cols if c in self.seshat.columns]
        self.seshat = self.seshat[available_cols].copy()

        # 年を数値に
        self.seshat['year'] = pd.to_numeric(self.seshat['Time'], errors='coerce')

        # 分析期間にフィルタリング
        self.seshat = self.seshat[
            (self.seshat['year'] >= ANALYSIS_PERIOD['start']) &
            (self.seshat['year'] <= ANALYSIS_PERIOD['end'])
        ].copy()

        return self.seshat

    def aggregate_shipwrecks_by_decade(self) -> pd.DataFrame:
        """難破船データを10年ごとに集計"""
        if self.shipwrecks is None:
            self.load_shipwreck_data()

        # 中央年を計算
        self.shipwrecks['mid_year'] = (
            self.shipwrecks['earliest_date'] + self.shipwrecks['latest_date']
        ) / 2

        # 10年区切りに丸める
        period = CAUSAL_ANALYSIS_CONFIG['aggregation_period']
        self.shipwrecks['decade'] = (self.shipwrecks['mid_year'] // period) * period

        # 集計
        agg = self.shipwrecks.groupby('decade').size().reset_index(name='shipwreck_count')
        agg.columns = ['year', 'shipwreck_count']

        return agg

    def aggregate_inscriptions_by_decade(self) -> pd.DataFrame:
        """碑文データを10年ごとに集計"""
        if self.inscriptions is None:
            self.load_inscription_data()

        # 10年区切りに丸める
        period = CAUSAL_ANALYSIS_CONFIG['aggregation_period']
        self.inscriptions['decade'] = (self.inscriptions['not_before'] // period) * period

        # 集計
        agg = self.inscriptions.groupby('decade').size().reset_index(name='inscription_count')
        agg.columns = ['year', 'inscription_count']

        # 分析期間にフィルタリング（10年単位に合わせる）
        start_decade = (ANALYSIS_PERIOD['start'] // period) * period
        end_decade = (ANALYSIS_PERIOD['end'] // period) * period
        agg = agg[
            (agg['year'] >= start_decade) &
            (agg['year'] <= end_decade)
        ]

        return agg

    def compute_instability_index(self) -> pd.DataFrame:
        """不安定指標を計算（InternalW + MilRevolt + PopUprising）"""
        if self.seshat is None:
            self.load_seshat_data()

        # 不安定指標を計算
        instability_cols = ['InternalW', 'MilRevolt', 'PopUprising']
        available = [c for c in instability_cols if c in self.seshat.columns]

        if available:
            self.seshat['instability_index'] = self.seshat[available].sum(axis=1)
        else:
            self.seshat['instability_index'] = np.nan

        return self.seshat[['year', 'instability_index', 'PolPop', 'PolTerr']].copy()

    def create_unified_dataset(self) -> pd.DataFrame:
        """
        全データを統合した分析用データセットを作成

        Returns:
            DataFrame with columns:
            - year: 年（10年単位）
            - climate: 夏季気温偏差（10年平均）
            - trade: 難破船数（10年集計）
            - population: 碑文数（10年集計）
            - fiscal: 銀含有率（補間済み）
            - instability: 不安定指標
        """
        # 基準となる年の列を作成（0, 10, 20, ... で10年単位）
        period = CAUSAL_ANALYSIS_CONFIG['aggregation_period']
        # 開始年を10で割り切れる値に丸める
        start_decade = (ANALYSIS_PERIOD['start'] // period) * period
        end_decade = (ANALYSIS_PERIOD['end'] // period) * period
        years = list(range(start_decade, end_decade + 1, period))
        self.unified = pd.DataFrame({'year': years})

        # 1. 気候データ（10年平均）
        if self.climate is None:
            self.load_climate_data()
        climate_decade = self.climate.copy()
        climate_decade['decade'] = (climate_decade['year'] // period) * period
        climate_agg = climate_decade.groupby('decade')['temp_mean'].mean().reset_index()
        climate_agg.columns = ['year', 'climate']
        self.unified = self.unified.merge(climate_agg, on='year', how='left')

        # 2. 交易データ（難破船数）
        trade_agg = self.aggregate_shipwrecks_by_decade()
        trade_agg.columns = ['year', 'trade']
        self.unified = self.unified.merge(trade_agg, on='year', how='left')

        # 3. 人口データ（碑文数）
        pop_agg = self.aggregate_inscriptions_by_decade()
        pop_agg.columns = ['year', 'population']
        self.unified = self.unified.merge(pop_agg, on='year', how='left')

        # 4. 財政データ（銀含有率、補間）
        if self.silver is None:
            self.load_silver_data()
        silver_decade = self.silver.copy()
        silver_decade['decade'] = (silver_decade['year'] // period) * period
        silver_agg = silver_decade.groupby('decade')['silver'].mean().reset_index()
        silver_agg.columns = ['year', 'fiscal']
        self.unified = self.unified.merge(silver_agg, on='year', how='left')
        # 線形補間
        self.unified['fiscal'] = self.unified['fiscal'].interpolate(method='linear')

        # 5. 不安定データ
        instability = self.compute_instability_index()
        instability_decade = instability.copy()
        instability_decade['decade'] = (instability_decade['year'] // period) * period
        instability_agg = instability_decade.groupby('decade')['instability_index'].mean().reset_index()
        instability_agg.columns = ['year', 'instability']
        self.unified = self.unified.merge(instability_agg, on='year', how='left')

        # 欠損値を補間
        for col in ['climate', 'trade', 'population', 'fiscal', 'instability']:
            self.unified[col] = self.unified[col].interpolate(method='linear')

        return self.unified

    def get_summary(self) -> Dict:
        """データロード状況のサマリーを取得"""
        return {
            'climate': {
                'loaded': self.climate is not None,
                'rows': len(self.climate) if self.climate is not None else 0
            },
            'shipwrecks': {
                'loaded': self.shipwrecks is not None,
                'rows': len(self.shipwrecks) if self.shipwrecks is not None else 0
            },
            'inscriptions': {
                'loaded': self.inscriptions is not None,
                'rows': len(self.inscriptions) if self.inscriptions is not None else 0
            },
            'silver': {
                'loaded': self.silver is not None,
                'rows': len(self.silver) if self.silver is not None else 0
            },
            'seshat': {
                'loaded': self.seshat is not None,
                'rows': len(self.seshat) if self.seshat is not None else 0
            },
            'unified': {
                'loaded': self.unified is not None,
                'rows': len(self.unified) if self.unified is not None else 0
            }
        }


def main():
    """動作確認用"""
    loader = RomanCoinDataLoader()

    print("=== デナリウス貨データの読み込み ===")
    denarii = loader.load_denarii()
    print(f"読み込み件数: {len(denarii)}")
    print(f"カラム数: {len(denarii.columns)}")

    print("\n=== 前処理 ===")
    denarii = loader.preprocess(denarii)
    print(f"前処理後カラム: {list(denarii.columns)}")

    print("\n=== 皇帝別統計 ===")
    emperor_stats = loader.get_emperor_stats(denarii)
    print(emperor_stats)

    print("\n=== 時系列データ（Butcher & Ponting）===")
    ts = loader.get_time_series(denarii)
    print(ts)

    print("\n=== 3世紀データの読み込み ===")
    third_century = loader.load_third_century()
    print(f"3世紀データ件数: {len(third_century)}")

    print("\n=== 完全な時系列データ（BC44〜AD295）===")
    full_ts = loader.get_full_time_series()
    print(full_ts.to_string())


def test_causal_chain_loader():
    """因果連鎖データローダーの動作確認"""
    print("\n" + "=" * 60)
    print("=== 因果連鎖データローダーのテスト ===")
    print("=" * 60)

    loader = CausalChainDataLoader()

    # 1. 気候データ
    print("\n--- 気候データ ---")
    try:
        climate = loader.load_climate_data()
        print(f"読み込み件数: {len(climate)}")
        print(f"期間: {climate['year'].min()} - {climate['year'].max()}")
        print(f"気温偏差範囲: {climate['temp_mean'].min():.2f} - {climate['temp_mean'].max():.2f}")
    except Exception as e:
        print(f"エラー: {e}")

    # 2. 難破船データ
    print("\n--- 難破船データ ---")
    try:
        shipwrecks = loader.load_shipwreck_data()
        print(f"読み込み件数: {len(shipwrecks)}")
        agg = loader.aggregate_shipwrecks_by_decade()
        print(f"10年集計後: {len(agg)} 期間")
    except Exception as e:
        print(f"エラー: {e}")

    # 3. 碑文データ
    print("\n--- 碑文データ ---")
    try:
        inscriptions = loader.load_inscription_data()
        print(f"読み込み件数: {len(inscriptions)}")
        agg = loader.aggregate_inscriptions_by_decade()
        print(f"10年集計後: {len(agg)} 期間")
    except Exception as e:
        print(f"エラー: {e}")

    # 4. 銀含有率データ
    print("\n--- 銀含有率データ ---")
    try:
        silver = loader.load_silver_data()
        print(f"読み込み件数: {len(silver)}")
        print(f"期間: {silver['year'].min()} - {silver['year'].max()}")
    except Exception as e:
        print(f"エラー: {e}")

    # 5. Seshatデータ
    print("\n--- Seshat不安定データ ---")
    try:
        seshat = loader.load_seshat_data()
        print(f"読み込み件数: {len(seshat)}")
        instability = loader.compute_instability_index()
        print(f"不安定指標計算済み")
    except Exception as e:
        print(f"エラー: {e}")

    # 6. 統合データセット
    print("\n--- 統合データセット ---")
    try:
        unified = loader.create_unified_dataset()
        print(f"統合データ件数: {len(unified)}")
        print("\nプレビュー:")
        print(unified.head(10).to_string())
        print("\n記述統計:")
        print(unified.describe().round(2).to_string())
    except Exception as e:
        print(f"エラー: {e}")

    # サマリー
    print("\n--- データロード状況 ---")
    summary = loader.get_summary()
    for key, val in summary.items():
        status = "OK" if val['loaded'] else "未読み込み"
        print(f"  {key}: {status} ({val['rows']} rows)")


if __name__ == "__main__":
    main()
    test_causal_chain_loader()
