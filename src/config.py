"""
プロジェクト設定ファイル
ローマ銀貨分析のための定数とマッピング
"""
from pathlib import Path

# ===== パス設定 =====
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUT_DIR / "figures"

# データファイル - 銀貨分析
DENARII_FILE = DATA_DIR / "Denarii_JC_to_Trajans_reform_final.xlsx"
PROVINCIAL_FILE = DATA_DIR / "Provincial_JC_to_Trajans_reform_final.xlsx"
THIRD_CENTURY_FILE = DATA_DIR / "third_century_silver.csv"  # 3世紀データ

# データファイル - 因果連鎖分析
CLIMATE_FILE = DATA_DIR / "eujja_2krecon_nested_cps-noaa.txt"  # 気候データ
SHIPWRECK_FILE = DATA_DIR / "StraussShipwrecks.xlsx"  # 難破船データ
INSCRIPTION_FILE = DATA_DIR / "LIST_v1-2.parquet"  # 碑文データ
SESHAT_FILE = DATA_DIR / "Equinox_on_GitHub_June9_2022.xlsx"  # 政治不安定データ

# ===== 皇帝の在位期間マッピング =====
# 時系列分析用: start=在位開始年, end=在位終了年, midpoint=中間年
EMPEROR_DATES = {
    # ユリウス・クラウディウス朝
    'Augustus': {'start': -27, 'end': 14, 'midpoint': -6},
    'Tiberius': {'start': 14, 'end': 37, 'midpoint': 26},
    'Caligula': {'start': 37, 'end': 41, 'midpoint': 39},
    'Claudius': {'start': 41, 'end': 54, 'midpoint': 48},
    'Nero': {'start': 54, 'end': 68, 'midpoint': 61},

    # 四皇帝の年 (AD69)
    'Galba': {'start': 68, 'end': 69, 'midpoint': 68},
    'Otho': {'start': 69, 'end': 69, 'midpoint': 69},
    'Vitellius': {'start': 69, 'end': 69, 'midpoint': 69},

    # フラウィウス朝
    'Vespasian': {'start': 69, 'end': 79, 'midpoint': 74},
    'Titus': {'start': 79, 'end': 81, 'midpoint': 80},
    'Domitian': {'start': 81, 'end': 96, 'midpoint': 89},

    # ネルウァ＝アントニヌス朝
    'Nerva': {'start': 96, 'end': 98, 'midpoint': 97},
    'Trajan': {'start': 98, 'end': 117, 'midpoint': 108},
    'Hadrian': {'start': 117, 'end': 138, 'midpoint': 128},
    'Antoninus Pius': {'start': 138, 'end': 161, 'midpoint': 150},
    'Marcus Aurelius': {'start': 161, 'end': 180, 'midpoint': 171},
    'Commodus': {'start': 180, 'end': 192, 'midpoint': 186},

    # 3世紀の危機（追加データ用）
    'Septimius Severus': {'start': 193, 'end': 211, 'midpoint': 202},
    'Caracalla': {'start': 211, 'end': 217, 'midpoint': 214},
    'Elagabalus': {'start': 218, 'end': 222, 'midpoint': 220},
    'Severus Alexander': {'start': 222, 'end': 235, 'midpoint': 229},
    'Maximinus Thrax': {'start': 235, 'end': 238, 'midpoint': 237},
    'Gordian III': {'start': 238, 'end': 244, 'midpoint': 241},
    'Philip I': {'start': 244, 'end': 249, 'midpoint': 247},
    'Decius': {'start': 249, 'end': 251, 'midpoint': 250},
    'Trebonianus Gallus': {'start': 251, 'end': 253, 'midpoint': 252},
    'Valerian': {'start': 253, 'end': 260, 'midpoint': 257},
    'Gallienus': {'start': 253, 'end': 268, 'midpoint': 261},
    'Claudius II': {'start': 268, 'end': 270, 'midpoint': 269},
    'Aurelian': {'start': 270, 'end': 275, 'midpoint': 273},
    'Probus': {'start': 276, 'end': 282, 'midpoint': 279},
    'Diocletian': {'start': 284, 'end': 305, 'midpoint': 295},
}

# ===== 重要な歴史的イベント =====
HISTORICAL_EVENTS = {
    64: 'ネロの貨幣改変',
    69: '四皇帝の年',
    193: '五皇帝の年',
    235: '3世紀の危機開始',
    249: 'キプリアヌスの疫病開始',
    260: 'ヴァレリアヌス捕囚',
    262: 'キプリアヌスの疫病終息',
    284: 'ディオクレティアヌス即位（危機終結）',
}

# ===== 分析期間設定 =====
ANALYSIS_PERIOD = {
    'start': 1,      # 分析開始年（AD）
    'end': 300,      # 分析終了年（AD）
    'crisis_start': 235,  # 3世紀の危機開始
    'crisis_end': 284,    # 3世紀の危機終了
}

# ===== 因果連鎖分析設定 =====
CAUSAL_ANALYSIS_CONFIG = {
    'aggregation_period': 10,  # 集計期間（年）
    'smoothing_window': 10,    # 平滑化ウィンドウ
    'max_lag': 3,              # グレンジャー検定の最大ラグ（観測数31に対応）
}

# ===== 成分分析カラム名 =====
COMPOSITION_COLUMNS = [
    'SILVER', 'COPPER', 'LEAD', 'GOLD',
    'ARSENIC', 'IRON', 'NICKEL', 'ANTIMONY', 'TIN', 'ZINC'
]

# ===== 可視化設定 =====
FIGURE_DPI = 300
FIGURE_FORMAT = 'png'

# ===== ロトカ・ヴォルテラモデル パラメータ =====
# Roman & Palmer (2019) を参考にした初期パラメータ
LOTKA_VOLTERRA_PARAMS = {
    # 軍隊成長率
    'alpha': 0.02,      # 基本成長率
    'beta': 0.0001,     # 領土による成長抑制
    # 領土変化率
    'gamma': 0.015,     # 軍隊による領土拡大
    'delta': 0.001,     # 自然減少率
    # 貨幣・経済
    'epsilon': 0.01,    # 銀準備の減少率
    'zeta': 0.005,      # 品位低下率
}

# 初期条件 (AD27年頃)
INITIAL_CONDITIONS = {
    'army_size': 250000,        # 軍隊規模（人）
    'territory': 2500000,       # 領土面積（km²）
    'silver_reserve': 100,      # 銀準備（相対値）
    'coin_fineness': 98.5,      # 銀含有率（%）
}
