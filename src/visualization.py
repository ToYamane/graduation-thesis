"""
可視化モジュール
ローマ銀貨データの可視化関数群
"""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Optional, Tuple
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config import (
    FIGURES_DIR, HISTORICAL_EVENTS, COMPOSITION_COLUMNS,
    FIGURE_DPI, FIGURE_FORMAT
)

# 日本語フォント設定
plt.rcParams['font.family'] = ['MS Gothic', 'Yu Gothic', 'Meiryo', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# Seabornスタイル設定
sns.set_style("whitegrid")
sns.set_palette("deep")


class SilverContentVisualizer:
    """銀含有率可視化クラス"""

    def __init__(self, figsize: Tuple[int, int] = (12, 6)):
        self.figsize = figsize
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    def plot_emperor_timeline(
        self,
        ts: pd.DataFrame,
        title: str = "ローマ帝国デナリウス貨の銀含有率推移",
        save_path: Optional[str] = None
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        皇帝別銀含有率の時系列プロット

        Parameters:
            ts: get_time_series()の出力DataFrame
            title: グラフタイトル
            save_path: 保存先パス（Noneの場合は保存しない）
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        # エラーバー付きプロット
        ax.errorbar(
            ts['year'], ts['silver_mean'],
            yerr=ts['silver_std'],
            fmt='o-', capsize=5, capthick=2,
            markersize=8, linewidth=2,
            color='#2E86AB', ecolor='#A23B72',
            label='銀含有率（平均±標準偏差）'
        )

        # 皇帝名のアノテーション
        for _, row in ts.iterrows():
            ax.annotate(
                row['emperor'],
                (row['year'], row['silver_mean']),
                textcoords="offset points",
                xytext=(0, 12),
                ha='center', fontsize=7, rotation=45
            )

        # 歴史的イベントの垂直線
        for year, event in HISTORICAL_EVENTS.items():
            if ts['year'].min() <= year <= ts['year'].max():
                ax.axvline(x=year, color='red', linestyle='--', alpha=0.7)
                ax.text(year, ax.get_ylim()[1], event,
                       rotation=90, va='top', ha='right', fontsize=8, color='red')

        ax.set_xlabel('年 (AD)', fontsize=12)
        ax.set_ylabel('銀含有率 (%)', fontsize=12)
        ax.set_title(title, fontsize=14)
        ax.legend(loc='lower left')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(max(0, ts['silver_mean'].min() - 15), 105)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
            print(f"図を保存しました: {save_path}")

        return fig, ax

    def plot_emperor_boxplot(
        self,
        df: pd.DataFrame,
        title: str = "皇帝別の銀含有率分布",
        save_path: Optional[str] = None
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        皇帝別の銀含有率ボックスプロット
        """
        fig, ax = plt.subplots(figsize=(14, 6))

        # 年代順にソート
        if 'YEAR_MIDPOINT' in df.columns:
            emperor_order = df.groupby('EMPEROR')['YEAR_MIDPOINT'].first().sort_values().index
        else:
            emperor_order = df['EMPEROR'].unique()

        sns.boxplot(
            data=df, x='EMPEROR', y='SILVER',
            order=emperor_order, ax=ax, palette='coolwarm'
        )

        ax.set_xlabel('皇帝', fontsize=12)
        ax.set_ylabel('銀含有率 (%)', fontsize=12)
        ax.set_title(title, fontsize=14)
        plt.xticks(rotation=45, ha='right')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
            print(f"図を保存しました: {save_path}")

        return fig, ax

    def plot_scatter_by_mint(
        self,
        df: pd.DataFrame,
        top_n: int = 5,
        title: str = "鋳造地別の銀含有率分布",
        save_path: Optional[str] = None
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        鋳造地別の銀含有率散布図
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        if 'MINT' not in df.columns:
            print("Warning: MINT column not found")
            return fig, ax

        # 上位N鋳造地を抽出
        top_mints = df['MINT'].value_counts().head(top_n).index
        colors = plt.cm.Set2(np.linspace(0, 1, len(top_mints)))

        for mint, color in zip(top_mints, colors):
            subset = df[df['MINT'] == mint]
            ax.scatter(
                subset['YEAR_MIDPOINT'], subset['SILVER'],
                alpha=0.6, label=mint, c=[color], s=50
            )

        ax.set_xlabel('年 (AD)', fontsize=12)
        ax.set_ylabel('銀含有率 (%)', fontsize=12)
        ax.set_title(title, fontsize=14)
        ax.legend(title='鋳造地', loc='lower left')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
            print(f"図を保存しました: {save_path}")

        return fig, ax

    def plot_correlation_heatmap(
        self,
        df: pd.DataFrame,
        title: str = "成分間の相関行列",
        save_path: Optional[str] = None
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        成分間の相関ヒートマップ
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        # 存在するカラムのみ選択
        cols = [c for c in COMPOSITION_COLUMNS if c in df.columns]
        corr_matrix = df[cols].corr()

        sns.heatmap(
            corr_matrix,
            annot=True, fmt='.2f',
            cmap='RdBu_r', center=0,
            vmin=-1, vmax=1,
            square=True, ax=ax
        )

        ax.set_title(title, fontsize=14)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
            print(f"図を保存しました: {save_path}")

        return fig, ax

    def plot_silver_distribution(
        self,
        df: pd.DataFrame,
        title: str = "銀含有率の分布",
        save_path: Optional[str] = None
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        銀含有率のヒストグラムとKDE
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        sns.histplot(
            data=df, x='SILVER',
            kde=True, bins=30,
            color='steelblue', ax=ax
        )

        ax.axvline(df['SILVER'].mean(), color='red', linestyle='--',
                  label=f'平均: {df["SILVER"].mean():.1f}%')
        ax.axvline(df['SILVER'].median(), color='green', linestyle=':',
                  label=f'中央値: {df["SILVER"].median():.1f}%')

        ax.set_xlabel('銀含有率 (%)', fontsize=12)
        ax.set_ylabel('頻度', fontsize=12)
        ax.set_title(title, fontsize=14)
        ax.legend()

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
            print(f"図を保存しました: {save_path}")

        return fig, ax


def create_all_figures(df: pd.DataFrame, ts: pd.DataFrame, output_dir: Path = FIGURES_DIR):
    """
    全ての図を一括生成

    Parameters:
        df: 前処理済みのDataFrame
        ts: 時系列データ
        output_dir: 出力先ディレクトリ
    """
    viz = SilverContentVisualizer()

    print("=== 図の生成を開始 ===")

    # 1. 時系列グラフ
    viz.plot_emperor_timeline(
        ts,
        save_path=output_dir / "01_silver_timeline.png"
    )

    # 2. ボックスプロット
    viz.plot_emperor_boxplot(
        df,
        save_path=output_dir / "02_emperor_boxplot.png"
    )

    # 3. 鋳造地別散布図
    viz.plot_scatter_by_mint(
        df,
        save_path=output_dir / "03_mint_scatter.png"
    )

    # 4. 相関ヒートマップ
    viz.plot_correlation_heatmap(
        df,
        save_path=output_dir / "04_correlation_heatmap.png"
    )

    # 5. 銀含有率分布
    viz.plot_silver_distribution(
        df,
        save_path=output_dir / "05_silver_distribution.png"
    )

    print("=== 全ての図を生成しました ===")


def main():
    """動作確認用"""
    from data_loader import RomanCoinDataLoader

    loader = RomanCoinDataLoader()
    denarii = loader.load_denarii()
    denarii = loader.preprocess(denarii)
    ts = loader.get_time_series(denarii)

    create_all_figures(denarii, ts)


if __name__ == "__main__":
    main()
