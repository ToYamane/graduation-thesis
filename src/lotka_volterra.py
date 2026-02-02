"""
ロトカ・ヴォルテラモデル
Roman & Palmer (2019) を参考にしたローマ帝国の成長・衰退モデル

参考文献:
Roman, Sabin, and Erika Palmer. "The Growth and Decline of the Western Roman Empire:
Quantifying the Dynamics of Army Size, Territory, and Coinage." (2019)
"""
import numpy as np
from scipy.integrate import odeint
from scipy.interpolate import interp1d
import pandas as pd
from typing import Tuple, Callable, Optional
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config import LOTKA_VOLTERRA_PARAMS, INITIAL_CONDITIONS


class RomanEmpireModel:
    """
    ローマ帝国の成長・衰退をモデル化するロトカ・ヴォルテラ型方程式

    変数:
        x: 軍隊規模
        y: 領土面積
        z: 貨幣品位（銀含有率）

    Roman & Palmer (2019) の簡略化版
    """

    def __init__(self, params: dict = None):
        """
        パラメータ:
            alpha: 軍隊の基本成長率
            beta: 領土による軍隊成長の抑制
            gamma: 軍隊による領土拡大率
            delta: 領土の自然減少率
            epsilon: 経済ストレスによる影響
            zeta: 貨幣品位の低下率
        """
        self.params = params or LOTKA_VOLTERRA_PARAMS.copy()
        self.silver_interp: Optional[Callable] = None

    def set_silver_data(self, years: np.ndarray, silver_content: np.ndarray):
        """
        歴史的な銀含有率データから補間関数を作成

        Parameters:
            years: 年代の配列
            silver_content: 銀含有率（%）の配列
        """
        self.silver_interp = interp1d(
            years, silver_content,
            kind='linear',
            fill_value='extrapolate',
            bounds_error=False
        )

    def equations(self, state: np.ndarray, t: float) -> list:
        """
        微分方程式系

        dx/dt = α*x - β*x*y/K - ε*(100-z)/100 * x
        dy/dt = γ*x*y/K - δ*y
        dz/dt = -ζ*x/K  (軍事費による品位低下)

        ここで:
            x = 軍隊規模
            y = 領土面積
            z = 銀含有率
            K = 環境収容力（正規化係数）
        """
        x, y, z = state
        p = self.params

        # 正規化係数
        K = 1000000

        # 経済ストレス（銀含有率が低いほどストレス大）
        economic_stress = p['epsilon'] * (100 - z) / 100

        # 軍隊変化: 成長 - 維持コスト - 経済ストレス
        dx_dt = p['alpha'] * x - p['beta'] * x * y / K - economic_stress * x

        # 領土変化: 軍事拡張 - 自然減少
        dy_dt = p['gamma'] * x * y / K - p['delta'] * y

        # 貨幣品位変化: 軍事費による低下（最低値は0）
        dz_dt = -p['zeta'] * x / K
        if z <= 0:
            dz_dt = max(0, dz_dt)

        return [dx_dt, dy_dt, dz_dt]

    def equations_with_historical_silver(self, state: np.ndarray, t: float) -> list:
        """
        歴史的な銀含有率データを使用した微分方程式

        銀含有率は歴史データから補間し、軍隊と領土のみを計算
        """
        x, y = state
        p = self.params
        K = 1000000

        # 歴史的な銀含有率を取得
        if self.silver_interp is not None:
            z = self.silver_interp(t)
        else:
            z = 98.5  # デフォルト（アウグストゥス期）

        # 経済ストレス
        economic_stress = p['epsilon'] * (100 - z) / 100

        dx_dt = p['alpha'] * x - p['beta'] * x * y / K - economic_stress * x
        dy_dt = p['gamma'] * x * y / K - p['delta'] * y

        return [dx_dt, dy_dt]

    def solve(
        self,
        t_span: np.ndarray,
        initial_state: Tuple[float, float, float] = None,
        use_historical_silver: bool = False
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        数値解を求める

        Parameters:
            t_span: 時間配列（年）
            initial_state: 初期状態 (軍隊, 領土, 銀含有率) または (軍隊, 領土)
            use_historical_silver: Trueの場合、歴史的銀含有率データを使用

        Returns:
            t_span: 時間配列
            solution: 解の配列
        """
        if use_historical_silver:
            if initial_state is None:
                initial_state = (
                    INITIAL_CONDITIONS['army_size'],
                    INITIAL_CONDITIONS['territory']
                )
            solution = odeint(
                self.equations_with_historical_silver,
                initial_state[:2],
                t_span
            )
        else:
            if initial_state is None:
                initial_state = (
                    INITIAL_CONDITIONS['army_size'],
                    INITIAL_CONDITIONS['territory'],
                    INITIAL_CONDITIONS['coin_fineness']
                )
            solution = odeint(self.equations, initial_state, t_span)

        return t_span, solution

    def run_simulation(
        self,
        start_year: int = -27,
        end_year: int = 300,
        silver_data: pd.DataFrame = None
    ) -> pd.DataFrame:
        """
        シミュレーションを実行し、結果をDataFrameで返す

        Parameters:
            start_year: 開始年（BC27年 = -27）
            end_year: 終了年
            silver_data: 銀含有率データ（year, silver列を持つDataFrame）

        Returns:
            DataFrame with columns: year, army, territory, silver
        """
        t_span = np.arange(start_year, end_year + 1, 1)

        if silver_data is not None:
            # 歴史データを使用
            self.set_silver_data(
                silver_data['year'].values,
                silver_data['silver'].values
            )
            _, solution = self.solve(t_span, use_historical_silver=True)

            # 銀含有率は補間値を使用
            silver_values = self.silver_interp(t_span)

            result = pd.DataFrame({
                'year': t_span,
                'army': solution[:, 0],
                'territory': solution[:, 1],
                'silver': silver_values
            })
        else:
            # 内生的に計算
            _, solution = self.solve(t_span, use_historical_silver=False)

            result = pd.DataFrame({
                'year': t_span,
                'army': solution[:, 0],
                'territory': solution[:, 1],
                'silver': solution[:, 2]
            })

        return result


def plot_simulation_results(results: pd.DataFrame, save_path: str = None):
    """
    シミュレーション結果をプロット

    Parameters:
        results: run_simulation()の出力
        save_path: 保存先パス
    """
    import matplotlib.pyplot as plt

    plt.rcParams['font.family'] = ['MS Gothic', 'Yu Gothic', 'Meiryo', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False

    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    # 軍隊規模
    axes[0].plot(results['year'], results['army'], 'b-', linewidth=2)
    axes[0].set_ylabel('軍隊規模', fontsize=12)
    axes[0].set_title('ローマ帝国シミュレーション結果', fontsize=14)
    axes[0].grid(True, alpha=0.3)
    axes[0].axvline(x=235, color='red', linestyle='--', alpha=0.5, label='3世紀の危機開始')
    axes[0].legend()

    # 領土面積
    axes[1].plot(results['year'], results['territory'], 'g-', linewidth=2)
    axes[1].set_ylabel('領土面積', fontsize=12)
    axes[1].grid(True, alpha=0.3)
    axes[1].axvline(x=235, color='red', linestyle='--', alpha=0.5)

    # 銀含有率
    axes[2].plot(results['year'], results['silver'], 'orange', linewidth=2)
    axes[2].set_ylabel('銀含有率 (%)', fontsize=12)
    axes[2].set_xlabel('年 (AD)', fontsize=12)
    axes[2].grid(True, alpha=0.3)
    axes[2].axvline(x=235, color='red', linestyle='--', alpha=0.5)
    axes[2].set_ylim(0, 105)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"図を保存しました: {save_path}")

    return fig, axes


def main():
    """動作確認用"""
    from data_loader import RomanCoinDataLoader

    print("=== ロトカ・ヴォルテラモデル テスト ===\n")

    # データ読み込み
    loader = RomanCoinDataLoader()
    silver_ts = loader.get_full_time_series()
    print("銀含有率データ:")
    print(silver_ts[['year', 'emperor', 'silver']].head(10))

    # モデル初期化
    model = RomanEmpireModel()

    # シミュレーション実行（歴史データ使用）
    print("\n=== シミュレーション実行（BC27〜AD300）===")
    results = model.run_simulation(
        start_year=-27,
        end_year=300,
        silver_data=silver_ts
    )

    print("\n結果サンプル:")
    print(results[results['year'].isin([-27, 0, 100, 200, 235, 268, 284, 300])])

    # プロット
    from config import FIGURES_DIR
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plot_simulation_results(results, save_path=FIGURES_DIR / "lotka_volterra_simulation.png")

    print("\n=== 完了 ===")


if __name__ == "__main__":
    main()
