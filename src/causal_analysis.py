"""
因果連鎖分析モジュール

気候 → 農業 → 人口 → 財政 → 社会不安 の因果連鎖を
時系列分析により検証する
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import warnings

# 統計ライブラリ
from scipy import stats
from scipy.signal import correlate, correlation_lags

# statsmodels（インポートエラー時の対処）
try:
    from statsmodels.tsa.stattools import adfuller, grangercausalitytests
    from statsmodels.tsa.api import VAR
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    warnings.warn("statsmodels is not installed. Some functions will not work.")

# matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config import (
    ANALYSIS_PERIOD, CAUSAL_ANALYSIS_CONFIG,
    FIGURES_DIR, FIGURE_DPI, FIGURE_FORMAT
)
from src.data_loader import CausalChainDataLoader


class CausalChainAnalyzer:
    """
    因果連鎖分析クラス

    Methods:
        compute_correlation_matrix: 相関行列の計算
        compute_cross_correlation: クロス相関の計算
        test_stationarity: 定常性検定（ADF検定）
        test_granger_causality: グレンジャー因果性検定
        fit_var_model: VARモデルの推定
        plot_time_series: 時系列プロット
        plot_correlation_heatmap: 相関行列ヒートマップ
        plot_cross_correlation: クロス相関プロット
        generate_report: 分析レポートの生成
    """

    def __init__(self, data: pd.DataFrame = None):
        """
        初期化

        Args:
            data: 統合データセット（columns: year, climate, trade, population, fiscal, instability）
        """
        self.data = data
        self.variables = ['climate', 'trade', 'population', 'fiscal', 'instability']
        self.var_labels = {
            'climate': '気候（気温偏差）',
            'trade': '交易（難破船数）',
            'population': '人口（碑文数）',
            'fiscal': '財政（銀含有率）',
            'instability': '不安定指標'
        }
        self.results = {}

    def load_data(self):
        """データローダーからデータを読み込み"""
        loader = CausalChainDataLoader()
        self.data = loader.create_unified_dataset()
        return self.data

    def compute_correlation_matrix(self) -> pd.DataFrame:
        """
        ピアソン相関係数行列を計算

        Returns:
            相関行列 (DataFrame)
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        corr = self.data[self.variables].corr()
        self.results['correlation_matrix'] = corr
        return corr

    def compute_cross_correlation(
        self,
        var1: str,
        var2: str,
        max_lag: int = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        クロス相関を計算

        Args:
            var1: 変数1（原因候補）
            var2: 変数2（結果候補）
            max_lag: 最大ラグ

        Returns:
            (lags, correlation): ラグと相関係数の配列
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        if max_lag is None:
            max_lag = CAUSAL_ANALYSIS_CONFIG['max_lag']

        x = self.data[var1].dropna().values
        y = self.data[var2].dropna().values

        # 長さを揃える
        min_len = min(len(x), len(y))
        x = x[:min_len]
        y = y[:min_len]

        # 標準化
        x = (x - x.mean()) / x.std()
        y = (y - y.mean()) / y.std()

        # クロス相関
        correlation = correlate(x, y, mode='full')
        correlation = correlation / min_len  # 正規化
        lags = correlation_lags(len(x), len(y), mode='full')

        # max_lagでフィルタリング
        mask = (lags >= -max_lag) & (lags <= max_lag)
        lags = lags[mask]
        correlation = correlation[mask]

        return lags, correlation

    def find_optimal_lag(self, var1: str, var2: str, max_lag: int = None) -> Dict:
        """
        最適なラグ（最大相関を与えるラグ）を特定

        Args:
            var1: 原因変数
            var2: 結果変数
            max_lag: 最大ラグ

        Returns:
            {'optimal_lag': int, 'max_correlation': float, 'direction': str}
        """
        lags, corr = self.compute_cross_correlation(var1, var2, max_lag)

        # 絶対値で最大の相関を探す
        abs_corr = np.abs(corr)
        max_idx = np.argmax(abs_corr)
        optimal_lag = lags[max_idx]
        max_correlation = corr[max_idx]

        # 方向の解釈
        if optimal_lag > 0:
            direction = f"{var1} が {var2} に先行"
        elif optimal_lag < 0:
            direction = f"{var2} が {var1} に先行"
        else:
            direction = "同時"

        return {
            'var1': var1,
            'var2': var2,
            'optimal_lag': optimal_lag,
            'max_correlation': max_correlation,
            'direction': direction
        }

    def test_stationarity(self, variable: str, significance: float = 0.05) -> Dict:
        """
        ADF検定による定常性検定

        Args:
            variable: 検定する変数名
            significance: 有意水準

        Returns:
            検定結果の辞書
        """
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels is required for this function.")

        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        series = self.data[variable].dropna()
        result = adfuller(series)

        return {
            'variable': variable,
            'test_statistic': result[0],
            'p_value': result[1],
            'critical_values': result[4],
            'is_stationary': result[1] < significance,
            'n_lags_used': result[2],
            'n_obs': result[3]
        }

    def test_all_stationarity(self) -> pd.DataFrame:
        """全変数の定常性を検定"""
        results = []
        for var in self.variables:
            try:
                res = self.test_stationarity(var)
                results.append({
                    '変数': self.var_labels.get(var, var),
                    'ADF統計量': f"{res['test_statistic']:.4f}",
                    'p値': f"{res['p_value']:.4f}",
                    '定常': '○' if res['is_stationary'] else '×'
                })
            except Exception as e:
                results.append({
                    '変数': self.var_labels.get(var, var),
                    'ADF統計量': 'エラー',
                    'p値': str(e),
                    '定常': '-'
                })

        df = pd.DataFrame(results)
        self.results['stationarity'] = df
        return df

    def test_granger_causality(
        self,
        cause_var: str,
        effect_var: str,
        max_lag: int = None
    ) -> Dict:
        """
        グレンジャー因果性検定

        Args:
            cause_var: 原因変数
            effect_var: 結果変数
            max_lag: 最大ラグ

        Returns:
            各ラグでの検定結果
        """
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels is required for this function.")

        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        if max_lag is None:
            max_lag = CAUSAL_ANALYSIS_CONFIG['max_lag']

        # データ準備（結果変数を最初に）
        test_data = self.data[[effect_var, cause_var]].dropna()

        # 検定実行
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            results = grangercausalitytests(test_data, maxlag=max_lag, verbose=False)

        # 結果を整理
        p_values = {}
        f_stats = {}
        for lag in range(1, max_lag + 1):
            p_values[lag] = results[lag][0]['ssr_ftest'][1]
            f_stats[lag] = results[lag][0]['ssr_ftest'][0]

        # 最小p値とそのラグ
        min_p_lag = min(p_values, key=p_values.get)
        min_p_value = p_values[min_p_lag]

        return {
            'cause': cause_var,
            'effect': effect_var,
            'p_values': p_values,
            'f_stats': f_stats,
            'min_p_lag': min_p_lag,
            'min_p_value': min_p_value,
            'is_significant': min_p_value < 0.05
        }

    def test_causal_chain(self) -> pd.DataFrame:
        """
        因果連鎖の全ステップを検定

        気候 → 交易 → 人口 → 財政 → 不安定
        """
        chain = [
            ('climate', 'trade'),
            ('trade', 'population'),
            ('population', 'fiscal'),
            ('fiscal', 'instability')
        ]

        results = []
        for cause, effect in chain:
            try:
                res = self.test_granger_causality(cause, effect)
                results.append({
                    '原因': self.var_labels.get(cause, cause),
                    '結果': self.var_labels.get(effect, effect),
                    '最小p値': f"{res['min_p_value']:.4f}",
                    '最適ラグ': res['min_p_lag'],
                    '有意': '○' if res['is_significant'] else '×'
                })
            except Exception as e:
                results.append({
                    '原因': self.var_labels.get(cause, cause),
                    '結果': self.var_labels.get(effect, effect),
                    '最小p値': 'エラー',
                    '最適ラグ': '-',
                    '有意': str(e)[:20]
                })

        df = pd.DataFrame(results)
        self.results['causal_chain'] = df
        return df

    def fit_var_model(self, max_lag: int = None) -> Optional[object]:
        """
        VARモデルを推定

        Args:
            max_lag: 最大ラグ（AICで最適化）

        Returns:
            fitted VAR model
        """
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels is required for this function.")

        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        if max_lag is None:
            max_lag = CAUSAL_ANALYSIS_CONFIG['max_lag']

        # データ準備
        model_data = self.data[self.variables].dropna()

        if len(model_data) < max_lag + 5:
            warnings.warn(f"Insufficient data for VAR model. Need at least {max_lag + 5} observations.")
            return None

        # モデル構築
        model = VAR(model_data)

        # 最適ラグの選択
        lag_order = model.select_order(maxlags=min(max_lag, len(model_data) // 3))

        # AICで最適ラグを決定
        optimal_lag = max(1, lag_order.aic)

        # モデル推定
        fitted = model.fit(optimal_lag)

        self.results['var_model'] = fitted
        self.results['var_optimal_lag'] = optimal_lag

        return fitted

    def plot_time_series(self, save_path: str = None, figsize: Tuple = (14, 10)) -> plt.Figure:
        """
        5変数の時系列プロット

        Args:
            save_path: 保存先パス
            figsize: 図のサイズ
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        fig, axes = plt.subplots(5, 1, figsize=figsize, sharex=True)

        crisis_start = ANALYSIS_PERIOD['crisis_start']
        crisis_end = ANALYSIS_PERIOD['crisis_end']

        for i, (var, ax) in enumerate(zip(self.variables, axes)):
            # データプロット
            ax.plot(self.data['year'], self.data[var], 'b-', linewidth=1.5, label=var)
            ax.fill_between(self.data['year'], self.data[var], alpha=0.3)

            # 3世紀の危機をハイライト
            ax.axvspan(crisis_start, crisis_end, alpha=0.2, color='red', label='3世紀の危機')

            # ラベル
            ax.set_ylabel(self.var_labels.get(var, var), fontsize=10)
            ax.grid(True, alpha=0.3)

            # 左側に変数名
            ax.text(-0.12, 0.5, self.var_labels.get(var, var),
                   transform=ax.transAxes, fontsize=10,
                   verticalalignment='center', rotation=90)

        axes[-1].set_xlabel('年 (CE)', fontsize=12)
        axes[0].set_title('因果連鎖変数の時系列（AD 1-300年）', fontsize=14)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')

        return fig

    def plot_correlation_heatmap(self, save_path: str = None, figsize: Tuple = (8, 6)) -> plt.Figure:
        """相関行列のヒートマップ"""
        if 'correlation_matrix' not in self.results:
            self.compute_correlation_matrix()

        corr = self.results['correlation_matrix']

        fig, ax = plt.subplots(figsize=figsize)

        # ヒートマップ
        im = ax.imshow(corr.values, cmap='RdBu_r', vmin=-1, vmax=1)

        # カラーバー
        plt.colorbar(im, ax=ax, label='相関係数')

        # ラベル
        labels = [self.var_labels.get(v, v) for v in self.variables]
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_yticklabels(labels)

        # 値を表示
        for i in range(len(labels)):
            for j in range(len(labels)):
                val = corr.iloc[i, j]
                color = 'white' if abs(val) > 0.5 else 'black'
                ax.text(j, i, f'{val:.2f}', ha='center', va='center', color=color)

        ax.set_title('変数間の相関行列', fontsize=14)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')

        return fig

    def plot_cross_correlation(self, save_path: str = None, figsize: Tuple = (12, 8)) -> plt.Figure:
        """因果連鎖の各ステップのクロス相関プロット"""
        chain = [
            ('climate', 'trade'),
            ('trade', 'population'),
            ('population', 'fiscal'),
            ('fiscal', 'instability')
        ]

        fig, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()

        for i, (cause, effect) in enumerate(chain):
            ax = axes[i]
            lags, corr = self.compute_cross_correlation(cause, effect)

            ax.bar(lags, corr, color='steelblue', alpha=0.7)
            ax.axhline(y=0, color='k', linewidth=0.5)

            # 最適ラグをマーク
            opt = self.find_optimal_lag(cause, effect)
            ax.axvline(x=opt['optimal_lag'], color='red', linestyle='--',
                      label=f"最適ラグ: {opt['optimal_lag']}")

            ax.set_xlabel('ラグ（10年単位）')
            ax.set_ylabel('相関係数')
            ax.set_title(f"{self.var_labels.get(cause, cause)} → {self.var_labels.get(effect, effect)}")
            ax.legend(loc='upper right', fontsize=8)
            ax.grid(True, alpha=0.3)

        plt.suptitle('因果連鎖のクロス相関分析', fontsize=14)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')

        return fig

    def generate_report(self) -> str:
        """分析レポートを生成"""
        report = []
        report.append("=" * 60)
        report.append("因果連鎖分析レポート")
        report.append("=" * 60)
        report.append("")

        # データ概要
        report.append("【データ概要】")
        if self.data is not None:
            report.append(f"  期間: AD {self.data['year'].min()} - {self.data['year'].max()}")
            report.append(f"  観測数: {len(self.data)}")
        report.append("")

        # 相関行列
        report.append("【相関行列】")
        if 'correlation_matrix' in self.results:
            report.append(self.results['correlation_matrix'].round(3).to_string())
        report.append("")

        # 定常性検定
        report.append("【定常性検定（ADF検定）】")
        if 'stationarity' in self.results:
            report.append(self.results['stationarity'].to_string(index=False))
        report.append("")

        # グレンジャー因果性検定
        report.append("【グレンジャー因果性検定】")
        if 'causal_chain' in self.results:
            report.append(self.results['causal_chain'].to_string(index=False))
        report.append("")

        # VARモデル
        report.append("【VARモデル】")
        if 'var_optimal_lag' in self.results:
            report.append(f"  最適ラグ（AIC）: {self.results['var_optimal_lag']}")
        report.append("")

        return "\n".join(report)


def main():
    """動作確認用"""
    print("=" * 60)
    print("因果連鎖分析モジュールのテスト")
    print("=" * 60)

    # データロード
    analyzer = CausalChainAnalyzer()
    print("\nデータを読み込み中...")

    try:
        data = analyzer.load_data()
        print(f"読み込み完了: {len(data)} 観測")
        print("\nデータプレビュー:")
        print(data.head(10).to_string())
    except Exception as e:
        print(f"データ読み込みエラー: {e}")
        return

    # 相関分析
    print("\n--- 相関分析 ---")
    try:
        corr = analyzer.compute_correlation_matrix()
        print(corr.round(3).to_string())
    except Exception as e:
        print(f"エラー: {e}")

    # 定常性検定
    print("\n--- 定常性検定 ---")
    try:
        stationarity = analyzer.test_all_stationarity()
        print(stationarity.to_string(index=False))
    except Exception as e:
        print(f"エラー: {e}")

    # グレンジャー因果性検定
    print("\n--- グレンジャー因果性検定 ---")
    try:
        causal = analyzer.test_causal_chain()
        print(causal.to_string(index=False))
    except Exception as e:
        print(f"エラー: {e}")

    # レポート生成
    print("\n--- 分析レポート ---")
    report = analyzer.generate_report()
    print(report)


if __name__ == "__main__":
    main()
