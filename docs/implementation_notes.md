# 実装記録

作成日: 2026-02-02
更新日: 2026-02-02

## プロジェクト概要

**研究テーマ**: クリオダイナミクスを用いたローマ帝国衰退の数理モデリング
- 構造的デモグラフィ理論（SDT）による3世紀の危機の検証

**研究問い（RQ）**:
> 気候変動に起因する農業生産力の低下は、人口と国家能力を通じて、3世紀の危機（235-284年）の政治的不安定をどの程度説明できるか？

**2つのアプローチを併用**:
1. **気候→農業→人口モデル**（主軸）
   - 因果連鎖: 気候 → 収穫 → 生活水準/死亡率 → 人口 → 徴税・兵站 → 政治不安定
2. **ロトカ・ヴォルテラ型モデル**（補助）
   - 軍隊規模・領土・貨幣（銀含有率）の連立方程式

---

## ディレクトリ構成

```
卒論/
├── data/                           # データファイル
│   ├── Denarii_JC_to_Trajans_reform_final.xlsx
│   ├── Provincial_JC_to_Trajans_reform_final.xlsx
│   └── third_century_silver.csv    # 新規作成
├── docs/                           # ドキュメント
│   └── implementation_notes.md     # 本ファイル
├── src/                            # ソースコード
│   ├── config.py                   # 設定ファイル
│   ├── data_loader.py              # データ読み込み
│   ├── visualization.py            # 可視化
│   └── lotka_volterra.py           # 数理モデル
├── notebooks/
│   └── analysis.ipynb              # 分析ノートブック
├── outputs/
│   └── figures/                    # 出力図表
├── image/                          # スライド用画像
├── requirements.txt                # 依存ライブラリ
├── slide.md                        # 中間発表スライド（Marp形式）
└── slides.tex                      # 中間発表スライド（Beamer/XeLaTeX形式）
```

---

## データソース

### 1. Butcher & Ponting (2015) - 主要データ

**ファイル名**:
- `Denarii_JC_to_Trajans_reform_final.xlsx` (728件)
- `Provincial_JC_to_Trajans_reform_final.xlsx` (349件)

**ダウンロード元**:
- Archaeology Data Service (ADS)
- URL: https://doi.org/10.5284/1035238
- 正式名称: "The Metallurgy of Roman Silver Coinage"
- 著者: Kevin Butcher & Matthew Ponting
- 出版年: 2015

**データ内容**:
- 期間: BC44年 〜 AD98年（トラヤヌス改革まで）
- カラム: 皇帝名(EMPEROR)、銀含有率(SILVER)、銅(COPPER)、鉛(LEAD)、鋳造地(MINT)など33列

**引用形式**:
```
Butcher, K. and Ponting, M. (2015) The Metallurgy of Roman Silver Coinage:
From the Reform of Nero to the Reform of Trajan. Cambridge University Press.
https://doi.org/10.5284/1035238
```

---

### 2. 3世紀データ - 二次文献から抽出

**ファイル名**: `third_century_silver.csv` (36件)

**データ期間**: BC27年 〜 AD295年

**データソース（出典）**:

| 期間 | 出典 | 備考 |
|------|------|------|
| BC27〜AD98 | Butcher & Ponting (2015) | 上記データの平均値 |
| AD98〜AD193 | Walker (1976, 1977) | D.R. Walker, *The Metrology of the Roman Silver Coinage* Part I & II |
| AD193〜AD211 | Gitler & Ponting (2003) | セウェルス朝のデータ |
| AD211〜AD284 | Walker (1978) | *The Metrology of the Roman Silver Coinage* Part III |
| AD284〜AD295 | 二次文献 | ディオクレティアヌス期のアルゲンテウス |

**Walker (1978) データの注意事項**:
- 表面分析のため、実際の含有率より高く出る傾向
- Gitler & Ponting (2003) により **-10%の補正** が推奨されている
- 本データセットでは補正済みの値を使用

**出典文献**:
```
Walker, D.R. (1976) The Metrology of the Roman Silver Coinage, Part I:
From Augustus to Domitian. BAR Supplementary Series 5.

Walker, D.R. (1977) The Metrology of the Roman Silver Coinage, Part II:
From Nerva to Commodus. BAR Supplementary Series 22.

Walker, D.R. (1978) The Metrology of the Roman Silver Coinage, Part III:
From Pertinax to Uranius Antoninus. BAR Supplementary Series 40.

Gitler, H. and Ponting, M. (2003) The Silver Coinage of Septimius Severus
and His Family (193-211 AD). Glaux 16.
```

---

### 3. 先行研究 - モデル参照

**Roman & Palmer (2019)**

- 論文: "The Growth and Decline of the Western Roman Empire: Quantifying the Dynamics of Army Size, Territory, and Coinage"
- URL: https://escholarship.org/uc/item/2cz4q2jq
- ロトカ・ヴォルテラモデルのパラメータ設計に参照

**参照データ（論文内）**:
- 軍隊規模: MacMullen (1980)
- 領土面積: Taagepera (1979)
- 貨幣鋳造量: Hopkins (1980)

---

## 実装内容

### 1. src/config.py

**機能**:
- パス定義（データ、出力先）
- 皇帝の在位期間マッピング（BC27〜AD305）
- 歴史的イベント定義
- ロトカ・ヴォルテラモデルのパラメータ

**主要定数**:
```python
EMPEROR_DATES = {...}        # 皇帝30名の在位期間
HISTORICAL_EVENTS = {...}    # ネロ改変、3世紀の危機など
LOTKA_VOLTERRA_PARAMS = {...} # モデルパラメータ
INITIAL_CONDITIONS = {...}   # 初期条件（AD27年頃）
```

---

### 2. src/data_loader.py

**機能**:
- Excel/CSVデータの読み込み
- 前処理（異常値処理、年代情報付与）
- 時系列データ生成
- 3世紀データとの統合

**主要メソッド**:
```python
class RomanCoinDataLoader:
    def load_denarii()           # デナリウス貨データ読み込み
    def load_provincial()        # 属州貨幣データ読み込み
    def load_third_century()     # 3世紀データ読み込み
    def preprocess()             # 前処理
    def get_time_series()        # 皇帝別時系列
    def get_full_time_series()   # BC44〜AD295完全時系列
```

---

### 3. src/visualization.py

**機能**:
- 銀含有率の時系列グラフ
- 皇帝別ボックスプロット
- 鋳造地別散布図
- 成分相関ヒートマップ
- 銀含有率の分布ヒストグラム

**主要メソッド**:
```python
class SilverContentVisualizer:
    def plot_emperor_timeline()      # 時系列グラフ
    def plot_emperor_boxplot()       # ボックスプロット
    def plot_scatter_by_mint()       # 散布図
    def plot_correlation_heatmap()   # 相関ヒートマップ
    def plot_silver_distribution()   # 分布ヒストグラム
```

---

### 4. src/lotka_volterra.py

**機能**:
- ロトカ・ヴォルテラ型微分方程式の実装
- 歴史的銀含有率データを使用したシミュレーション
- 結果のプロット

**数理モデル**:
```
dx/dt = α*x - β*x*y/K - ε*(100-z)/100 * x  (軍隊規模)
dy/dt = γ*x*y/K - δ*y                       (領土面積)
dz/dt = -ζ*x/K                              (銀含有率)
```

**主要メソッド**:
```python
class RomanEmpireModel:
    def set_silver_data()        # 銀含有率データ設定
    def equations()              # 微分方程式
    def solve()                  # 数値解法（odeint）
    def run_simulation()         # シミュレーション実行
```

---

### 5. notebooks/analysis.ipynb

**内容**:
1. データの読み込み
2. 探索的データ分析（EDA）
3. 銀含有率の時系列分析
4. 統計検定（ANOVA、t検定）
5. 可視化
6. 図の一括保存
7. 3世紀データの分析
8. ロトカ・ヴォルテラモデルのシミュレーション
9. まとめと考察

---

## 依存ライブラリ

```
pandas>=2.0.0
numpy>=1.24.0
openpyxl>=3.1.0
matplotlib>=3.7.0
seaborn>=0.12.0
scipy>=1.10.0
jupyter>=1.0.0
```

インストール: `pip install -r requirements.txt`

---

## 使い方

### 1. データ読み込み確認
```bash
python src/data_loader.py
```

### 2. 分析ノートブック実行
```bash
cd notebooks
jupyter notebook analysis.ipynb
```

### 3. シミュレーション実行
```bash
python src/lotka_volterra.py
```

---

## 出力ファイル

`outputs/figures/` に以下の図が保存される:

| ファイル名 | 内容 |
|-----------|------|
| 01_silver_timeline.png | 銀含有率の時系列グラフ |
| 02_emperor_boxplot.png | 皇帝別ボックスプロット |
| 03_mint_scatter.png | 鋳造地別散布図 |
| 04_correlation_heatmap.png | 成分相関ヒートマップ |
| 05_silver_distribution.png | 銀含有率の分布 |
| full_silver_timeline.png | BC27〜AD295完全時系列 |
| lotka_volterra_simulation.png | モデルシミュレーション結果 |

---

## 今後の課題

### 主軸モデル（気候→農業→人口）
1. **気候データの取得**: 古気候復元データ（降水・気温）
2. **農業プロキシの取得**: 穀物価格、難破船データ（OXREP）
3. **人口データの取得**: Seshatからの人口推計
4. **不安定度指標の構築**: 皇帝交代頻度のデータ化

### 補助モデル（ロトカ・ヴォルテラ）
1. **パラメータ最適化**: 歴史データへのフィッティング
2. **感度分析**: パラメータ変更による影響評価

### 共通
1. **モデル比較**: 気候主導 vs 疫病主導 vs 貨幣崩壊主導
2. **論文執筆**: 図表の最終調整、考察の深化
