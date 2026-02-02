# 分析方針

作成日: 2026-02-02

## 研究問い

> 気候変動に起因する農業生産力の低下は、人口と国家能力を通じて、3世紀の危機（235-284年）の政治的不安定をどの程度説明できるか？

---

## 仮説

**因果連鎖モデル**:
```
気候変動(C) → 農業生産力(A) → 人口(N) → 財政(F) → 社会不安(I)
```

各矢印（因果関係）を時系列分析により検証する。

---

## 変数の操作化

| 概念 | 変数名 | 操作化 | データソース | 単位 |
|------|--------|--------|-------------|------|
| 気候変動 | C | 夏季気温偏差 | Luterbacher et al. (2016) | ℃ |
| 農業生産力 | A | 難破船数（10年集計） | OXREP Shipwrecks | 件/10年 |
| 人口 | N | 碑文数（10年集計） | LIST Dataset | 件/10年 |
| 財政能力 | F | 銀含有率 | Butcher & Ponting等 | % |
| 社会不安 | I | 不安定指標合計 | Seshat Equinox | 0-3 |

### 不安定指標の構成
```python
I = InternalW + MilRevolt + PopUprising
```
- InternalW: 内戦（0/1）
- MilRevolt: 軍事反乱（0/1）
- PopUprising: 民衆蜂起（0/1）

---

## 分析期間

| 期間 | 説明 |
|------|------|
| 全体 | AD 1 - 300（300年間） |
| 焦点 | AD 235 - 284（3世紀の危機） |
| 比較期間1 | AD 1 - 150（パクス・ロマーナ） |
| 比較期間2 | AD 151 - 234（衰退前期） |
| 比較期間3 | AD 285 - 300（回復期） |

---

## 分析フロー

```
┌─────────────────────────────────────────────────────────────────┐
│  Phase 1: データ準備                                            │
│  ├─ 1.1 各データソースの読み込み                                │
│  ├─ 1.2 時間軸の統一（年単位、AD1-300）                        │
│  ├─ 1.3 欠損値補間（線形補間）                                 │
│  └─ 1.4 10年移動平均による平滑化                               │
└─────────────────────────────────┬───────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│  Phase 2: 探索的データ分析（EDA）                               │
│  ├─ 2.1 各変数の記述統計                                       │
│  ├─ 2.2 時系列プロット（5変数重ね合わせ）                      │
│  ├─ 2.3 期間別比較（箱ひげ図）                                 │
│  └─ 2.4 3世紀の危機期間（235-284）のハイライト                 │
└─────────────────────────────────┬───────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│  Phase 3: 相関分析                                              │
│  ├─ 3.1 ピアソン相関係数（同時点）                             │
│  ├─ 3.2 相関行列のヒートマップ                                 │
│  └─ 3.3 クロス相関分析（タイムラグ検出）                       │
└─────────────────────────────────┬───────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│  Phase 4: 因果性検定                                            │
│  ├─ 4.1 定常性検定（ADF検定）                                  │
│  ├─ 4.2 グレンジャー因果性検定（各ペア）                       │
│  ├─ 4.3 最適ラグの決定（AIC/BIC）                              │
│  └─ 4.4 VARモデルの推定                                        │
└─────────────────────────────────┬───────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│  Phase 5: 結果の解釈                                            │
│  ├─ 5.1 因果連鎖の支持/棄却判定                                │
│  ├─ 5.2 インパルス応答関数の分析                               │
│  ├─ 5.3 分散分解分析                                           │
│  └─ 5.4 考察と限界                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 統計手法の詳細

### 1. クロス相関分析

**目的**: 変数間の最適なタイムラグを特定

**手法**:
```python
from scipy.signal import correlate, correlation_lags

def cross_correlation(x, y, max_lag=50):
    """
    クロス相関を計算
    正のラグ: xがyに先行
    負のラグ: yがxに先行
    """
    correlation = correlate(x - x.mean(), y - y.mean(), mode='full')
    correlation /= (len(x) * x.std() * y.std())
    lags = correlation_lags(len(x), len(y), mode='full')
    return lags, correlation
```

**解釈**:
- 最大相関が得られるラグ = 因果的影響の遅延時間
- 例: 気候→農業で最大相関がラグ5年なら、気候変動の影響が5年後に農業に現れる

### 2. グレンジャー因果性検定

**目的**: 変数Xが変数Yを「グレンジャー原因する」かを検定

**帰無仮説**: XはYをグレンジャー原因しない（Xの過去値はYの予測に寄与しない）

**手法**:
```python
from statsmodels.tsa.stattools import grangercausalitytests

def test_granger_causality(data, cause_var, effect_var, max_lag=10):
    """
    グレンジャー因果性検定
    p < 0.05 で帰無仮説を棄却 → 因果関係あり
    """
    test_data = data[[effect_var, cause_var]].dropna()
    results = grangercausalitytests(test_data, maxlag=max_lag, verbose=False)

    # 各ラグのp値を取得
    p_values = {lag: results[lag][0]['ssr_ftest'][1] for lag in range(1, max_lag+1)}
    return p_values
```

**検定する因果関係**:
| 原因 (X) | 結果 (Y) | 期待される結果 |
|----------|----------|---------------|
| 気候(C) | 農業(A) | 有意 (p < 0.05) |
| 農業(A) | 人口(N) | 有意 (p < 0.05) |
| 人口(N) | 財政(F) | 有意 (p < 0.05) |
| 財政(F) | 不安定(I) | 有意 (p < 0.05) |

### 3. 定常性検定（ADF検定）

**目的**: 時系列が定常かどうかを検定（グレンジャー検定の前提条件）

**手法**:
```python
from statsmodels.tsa.stattools import adfuller

def test_stationarity(series, significance=0.05):
    """
    Augmented Dickey-Fuller検定
    p < 0.05 で定常
    """
    result = adfuller(series.dropna())
    return {
        'test_statistic': result[0],
        'p_value': result[1],
        'is_stationary': result[1] < significance
    }
```

**非定常の場合の対処**:
1. 1次差分を取る: `y_diff = y.diff()`
2. 対数変換: `y_log = np.log(y)`
3. トレンド除去: `y_detrended = y - y.rolling(window).mean()`

### 4. VARモデル（ベクトル自己回帰）

**目的**: 5変数の同時方程式モデルを推定

**モデル**:
```
Y_t = c + A_1 * Y_{t-1} + A_2 * Y_{t-2} + ... + A_p * Y_{t-p} + ε_t

Y_t = [C_t, A_t, N_t, F_t, I_t]'
```

**手法**:
```python
from statsmodels.tsa.api import VAR

def fit_var_model(data, variables, max_lag=10):
    """
    VARモデルの推定
    """
    model_data = data[variables].dropna()
    model = VAR(model_data)

    # 最適ラグの選択（AIC基準）
    lag_order = model.select_order(maxlags=max_lag)
    optimal_lag = lag_order.aic

    # モデル推定
    fitted = model.fit(optimal_lag)
    return fitted
```

### 5. インパルス応答関数

**目的**: 1変数へのショックが他変数にどう波及するかを可視化

**手法**:
```python
def plot_impulse_response(fitted_model, impulse, response, periods=20):
    """
    インパルス応答関数のプロット
    例: 気候ショックが不安定度にどう影響するか
    """
    irf = fitted_model.irf(periods)
    irf.plot(impulse=[impulse], response=[response])
```

---

## 予想される結果

### 時系列パターン

```
時間軸: AD1 ──────────────────────────────────────→ AD300
        ├─パクス・ロマーナ─┼─衰退前期─┼─3世紀危機─┼─回復─┤

気候:   ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▃▃▃▂▂▁▁▁▁▂▂▃▃▄▄
        Roman Climate Optimum    ↓寒冷化(245-275)

農業:   ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▃▃▃▂▂▁▁▁▁▁▂▃▃▄▄
        交易活発              ↓減少（ラグ5-10年）

人口:   ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▃▃▃▂▂▁▁▁▁▁▂▂▂▃▃
        人口増加              ↓疫病・減少（ラグ10-20年）

財政:   ▄▄▄▄▄▄▄▄▄▄▄▄▃▃▃▃▂▂▂▁▁▁▁▁▁▁▁▂▂▄▄
        高銀含有率            ↓貨幣改悪（ラグ5-10年）

不安定: ▁▁▁▁▁▁▁▁▁▂▂▂▂▃▃▄▄▄▄▄▄▄▄▄▃▃▂▂▁▁
        安定期                ↑3世紀の危機（ラグ5-10年）
```

### 相関係数（予想）

| ペア | 予想相関 | 予想ラグ |
|------|---------|---------|
| C → A | r = -0.4〜-0.6 | 5-10年 |
| A → N | r = +0.5〜+0.7 | 10-20年 |
| N → F | r = +0.4〜+0.6 | 5-10年 |
| F → I | r = -0.5〜-0.7 | 5-10年 |

### グレンジャー因果性（予想）

| 検定 | 予想p値 | 判定 |
|------|--------|------|
| C → A | p < 0.05 | 有意 |
| A → N | p < 0.05 | 有意 |
| N → F | p < 0.05 | 有意 |
| F → I | p < 0.05 | 有意 |

---

## 分析の限界と注意点

### 1. データの限界
- **難破船データ**: 発見バイアス（考古学的調査の地理的偏り）
- **碑文データ**: 保存バイアス（耐久性のある素材が残りやすい）
- **銀含有率**: 皇帝ごとの不連続データ（補間が必要）
- **Seshatデータ**: 100年単位の粗い解像度（200年, 300年のみ）

### 2. 方法論的限界
- **グレンジャー因果性**: 真の因果関係ではなく「予測的因果」
- **欠測値**: 補間による人工的パターンの可能性
- **外生変数**: 疫病（キプリアヌスの疫病）の独立した効果
- **非線形性**: 線形モデルでは捉えられない閾値効果

### 3. 解釈上の注意
- 相関≠因果（第三変数の影響の可能性）
- 代理指標の限界（難破船数≠農業生産力）
- 時代による社会構造の変化

---

## 出力物

### 図表
| 番号 | 内容 | ファイル名 |
|------|------|-----------|
| Fig.1 | 5変数の時系列プロット | causal_chain_timeseries.png |
| Fig.2 | 相関行列ヒートマップ | correlation_heatmap.png |
| Fig.3 | クロス相関プロット | cross_correlation.png |
| Fig.4 | グレンジャー因果性結果 | granger_causality.png |
| Fig.5 | インパルス応答関数 | impulse_response.png |

### 統計表
| 番号 | 内容 |
|------|------|
| Table 1 | 記述統計（期間別） |
| Table 2 | 相関係数行列 |
| Table 3 | グレンジャー因果性検定結果 |
| Table 4 | VARモデル推定結果 |
| Table 5 | 分散分解結果 |

---

## 参考文献（方法論）

```bibtex
@book{turchin2003historical,
  title={Historical Dynamics: Why States Rise and Fall},
  author={Turchin, Peter},
  year={2003},
  publisher={Princeton University Press}
}

@article{granger1969investigating,
  title={Investigating causal relations by econometric models and cross-spectral methods},
  author={Granger, Clive WJ},
  journal={Econometrica},
  pages={424--438},
  year={1969}
}

@book{hamilton1994time,
  title={Time Series Analysis},
  author={Hamilton, James D},
  year={1994},
  publisher={Princeton University Press}
}
```
