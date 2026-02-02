"""
統計的に有意な因果関係のグラフ作成
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

# 日本語フォント設定
plt.rcParams['font.family'] = 'MS Gothic'
plt.rcParams['axes.unicode_minus'] = False

from src.data_loader import CausalChainDataLoader
from src.causal_analysis import CausalChainAnalyzer
from src.config import FIGURES_DIR, ANALYSIS_PERIOD

def main():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    print(f'出力先: {FIGURES_DIR}')

    # データ読み込み
    print('データ読み込み中...')
    loader = CausalChainDataLoader()
    data = loader.create_unified_dataset()
    analyzer = CausalChainAnalyzer(data)

    crisis_start = ANALYSIS_PERIOD['crisis_start']
    crisis_end = ANALYSIS_PERIOD['crisis_end']

    # ======================================
    # 図1: 気候 → 交易 の因果関係
    # ======================================
    print('図1: 気候→交易 作成中...')
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1-1: 時系列（二軸）
    ax1 = axes[0, 0]
    ax1_twin = ax1.twinx()

    line1, = ax1.plot(data['year'], data['climate'], 'b-', linewidth=2, marker='o', markersize=4, label='気候（気温偏差）')
    line2, = ax1_twin.plot(data['year'], data['trade'], 'g-', linewidth=2, marker='s', markersize=4, label='交易（難破船数）')

    ax1.axvspan(crisis_start, crisis_end, alpha=0.2, color='red')
    ax1.set_xlabel('年 (CE)', fontsize=11)
    ax1.set_ylabel('気温偏差 (℃)', color='blue', fontsize=11)
    ax1_twin.set_ylabel('難破船数', color='green', fontsize=11)
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1_twin.tick_params(axis='y', labelcolor='green')
    ax1.set_title('気候と交易の時系列比較', fontsize=12, fontweight='bold')
    ax1.legend([line1, line2], ['気候（気温偏差）', '交易（難破船数）'], loc='upper right')
    ax1.grid(True, alpha=0.3)

    # 1-2: 散布図（同時点）
    ax2 = axes[0, 1]
    sc = ax2.scatter(data['climate'], data['trade'], c=data['year'], cmap='viridis', s=80, edgecolors='black', linewidth=0.5)
    cbar = plt.colorbar(sc, ax=ax2)
    cbar.set_label('年 (CE)')

    mask = ~(data['climate'].isna() | data['trade'].isna())
    if mask.sum() > 2:
        z = np.polyfit(data.loc[mask, 'climate'], data.loc[mask, 'trade'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(data['climate'].min(), data['climate'].max(), 100)
        ax2.plot(x_line, p(x_line), 'r--', linewidth=2, label='回帰直線')

        r = data.loc[mask, 'climate'].corr(data.loc[mask, 'trade'])
        ax2.text(0.05, 0.95, f'r = {r:.3f}', transform=ax2.transAxes, fontsize=12,
                 verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax2.set_xlabel('気温偏差 (℃)', fontsize=11)
    ax2.set_ylabel('難破船数', fontsize=11)
    ax2.set_title('気候 vs 交易（同時点）', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    # 1-3: ラグ付き散布図（気候が1期先行）
    ax3 = axes[1, 0]
    climate_lagged = data['climate'].shift(1)
    merged = pd.DataFrame({'climate_lag': climate_lagged, 'trade': data['trade'], 'year': data['year']}).dropna()

    sc = ax3.scatter(merged['climate_lag'], merged['trade'], c=merged['year'], cmap='viridis', s=80, edgecolors='black', linewidth=0.5)
    cbar = plt.colorbar(sc, ax=ax3)
    cbar.set_label('年 (CE)')

    if len(merged) > 2:
        z = np.polyfit(merged['climate_lag'], merged['trade'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(merged['climate_lag'].min(), merged['climate_lag'].max(), 100)
        ax3.plot(x_line, p(x_line), 'r--', linewidth=2)

        r = merged['climate_lag'].corr(merged['trade'])
        ax3.text(0.05, 0.95, f'r = {r:.3f}', transform=ax3.transAxes, fontsize=12,
                 verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax3.set_xlabel('気温偏差 (t-1期)', fontsize=11)
    ax3.set_ylabel('難破船数 (t期)', fontsize=11)
    ax3.set_title('気候(t-1) → 交易(t)：1期ラグ', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)

    # 1-4: クロス相関
    ax4 = axes[1, 1]
    lags, corr = analyzer.compute_cross_correlation('climate', 'trade', max_lag=5)
    colors = ['green' if l == 1 else 'steelblue' for l in lags]
    ax4.bar(lags, corr, color=colors, alpha=0.7, edgecolor='black')
    ax4.axhline(y=0, color='k', linewidth=0.5)
    ax4.axvline(x=1, color='red', linestyle='--', linewidth=2, label='最適ラグ=1')
    ax4.set_xlabel('ラグ（10年単位）', fontsize=11)
    ax4.set_ylabel('相関係数', fontsize=11)
    ax4.set_title('クロス相関（気候 → 交易）', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    fig.suptitle('因果関係1: 気候変動 → 交易活動（グレンジャー因果性 p=0.003）', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / 'significant_climate_trade.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('  保存: significant_climate_trade.png')

    # ======================================
    # 図2: 財政 → 不安定 の因果関係
    # ======================================
    print('図2: 財政→不安定 作成中...')
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    data_valid = data.dropna(subset=['instability'])

    # 2-1: 時系列（二軸）
    ax1 = axes[0, 0]
    ax1_twin = ax1.twinx()

    line1, = ax1.plot(data['year'], data['fiscal'], 'r-', linewidth=2, marker='o', markersize=4, label='財政（銀含有率）')
    line2, = ax1_twin.plot(data_valid['year'], data_valid['instability'], 'purple', linewidth=2, marker='s', markersize=6, label='不安定指標')

    ax1.axvspan(crisis_start, crisis_end, alpha=0.2, color='red')
    ax1.set_xlabel('年 (CE)', fontsize=11)
    ax1.set_ylabel('銀含有率 (%)', color='red', fontsize=11)
    ax1_twin.set_ylabel('不安定指標', color='purple', fontsize=11)
    ax1.tick_params(axis='y', labelcolor='red')
    ax1_twin.tick_params(axis='y', labelcolor='purple')
    ax1.set_title('財政能力と政治不安定の時系列比較', fontsize=12, fontweight='bold')
    ax1.legend([line1, line2], ['財政（銀含有率）', '不安定指標'], loc='upper right')
    ax1.grid(True, alpha=0.3)

    # 2-2: 散布図（同時点）
    ax2 = axes[0, 1]
    sc = ax2.scatter(data_valid['fiscal'], data_valid['instability'], c=data_valid['year'], cmap='plasma', s=100, edgecolors='black', linewidth=0.5)
    cbar = plt.colorbar(sc, ax=ax2)
    cbar.set_label('年 (CE)')

    mask = ~(data_valid['fiscal'].isna() | data_valid['instability'].isna())
    if mask.sum() > 2:
        z = np.polyfit(data_valid.loc[mask, 'fiscal'], data_valid.loc[mask, 'instability'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(data_valid['fiscal'].min(), data_valid['fiscal'].max(), 100)
        ax2.plot(x_line, p(x_line), 'r--', linewidth=2)

        r = data_valid['fiscal'].corr(data_valid['instability'])
        ax2.text(0.05, 0.95, f'r = {r:.3f}', transform=ax2.transAxes, fontsize=12,
                 verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax2.set_xlabel('銀含有率 (%)', fontsize=11)
    ax2.set_ylabel('不安定指標', fontsize=11)
    ax2.set_title('財政 vs 不安定（同時点）', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    # 2-3: ラグ付き散布図（財政が1期先行）
    ax3 = axes[1, 0]
    fiscal_lagged = data['fiscal'].shift(1)
    merged = pd.DataFrame({'fiscal_lag': fiscal_lagged, 'instability': data['instability'], 'year': data['year']}).dropna()

    sc = ax3.scatter(merged['fiscal_lag'], merged['instability'], c=merged['year'], cmap='plasma', s=100, edgecolors='black', linewidth=0.5)
    cbar = plt.colorbar(sc, ax=ax3)
    cbar.set_label('年 (CE)')

    if len(merged) > 2:
        z = np.polyfit(merged['fiscal_lag'], merged['instability'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(merged['fiscal_lag'].min(), merged['fiscal_lag'].max(), 100)
        ax3.plot(x_line, p(x_line), 'r--', linewidth=2)

        r = merged['fiscal_lag'].corr(merged['instability'])
        ax3.text(0.05, 0.95, f'r = {r:.3f}', transform=ax3.transAxes, fontsize=12,
                 verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax3.set_xlabel('銀含有率 (t-1期)', fontsize=11)
    ax3.set_ylabel('不安定指標 (t期)', fontsize=11)
    ax3.set_title('財政(t-1) → 不安定(t)：1期ラグ', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)

    # 2-4: クロス相関
    ax4 = axes[1, 1]
    lags, corr = analyzer.compute_cross_correlation('fiscal', 'instability', max_lag=5)
    colors = ['green' if l == 1 else 'steelblue' for l in lags]
    ax4.bar(lags, corr, color=colors, alpha=0.7, edgecolor='black')
    ax4.axhline(y=0, color='k', linewidth=0.5)
    ax4.axvline(x=1, color='red', linestyle='--', linewidth=2, label='最適ラグ=1')
    ax4.set_xlabel('ラグ（10年単位）', fontsize=11)
    ax4.set_ylabel('相関係数', fontsize=11)
    ax4.set_title('クロス相関（財政 → 不安定）', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    fig.suptitle('因果関係2: 財政悪化 → 政治不安定（グレンジャー因果性 p=0.020）', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / 'significant_fiscal_instability.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('  保存: significant_fiscal_instability.png')

    # ======================================
    # 図3: 因果連鎖の全体像
    # ======================================
    print('図3: 因果連鎖全体像 作成中...')
    fig, ax = plt.subplots(figsize=(16, 8))

    vars_to_plot = ['climate', 'trade', 'population', 'fiscal', 'instability']
    labels = ['気候', '交易', '人口', '財政', '不安定']
    colors_plot = ['blue', 'green', 'orange', 'red', 'purple']

    # 正規化
    data_norm = data.copy()
    for var in vars_to_plot:
        valid_mask = ~data_norm[var].isna()
        if valid_mask.sum() > 0:
            mean = data_norm.loc[valid_mask, var].mean()
            std = data_norm.loc[valid_mask, var].std()
            if std > 0:
                data_norm[var] = (data_norm[var] - mean) / std

    for var, label, color in zip(vars_to_plot, labels, colors_plot):
        ax.plot(data_norm['year'], data_norm[var], color=color, linewidth=2,
                marker='o', markersize=4, label=label, alpha=0.8)

    ax.axvspan(crisis_start, crisis_end, alpha=0.15, color='red', label='3世紀の危機')
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.5)

    ax.set_xlabel('年 (CE)', fontsize=12)
    ax.set_ylabel('標準化値', fontsize=12)
    ax.set_title('因果連鎖変数の時系列（標準化）\n気候 → 交易 → 人口 → 財政 → 不安定', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 310)

    # 有意な因果関係を注釈
    ax.annotate('', xy=(50, 2.5), xytext=(100, 2.5),
                arrowprops=dict(arrowstyle='->', color='green', lw=3))
    ax.text(75, 2.7, '気候→交易\n(p=0.003)', ha='center', fontsize=10, color='green', fontweight='bold')

    ax.annotate('', xy=(200, -2.5), xytext=(250, -2.5),
                arrowprops=dict(arrowstyle='->', color='purple', lw=3))
    ax.text(225, -2.3, '財政→不安定\n(p=0.020)', ha='center', fontsize=10, color='purple', fontweight='bold')

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / 'causal_chain_overview.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('  保存: causal_chain_overview.png')

    print()
    print('=== 全ての図を保存しました ===')


if __name__ == "__main__":
    main()
