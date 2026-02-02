# データインベントリ

作成日: 2026-02-02

## 概要

本研究「クリオダイナミクスを用いたローマ帝国衰退の数理モデリング」で使用するデータの一覧です。

**仮説**: 気候変動 → 農業生産力低下 → 人口減少 → 財政悪化 → 社会不安

---

## データファイル一覧

| # | 概念 | ファイル | レコード数 | 期間 |
|---|------|---------|-----------|------|
| 1 | 気候 | eujja_2krecon_nested_cps-noaa.txt | 2,141行 | 138BCE-2003CE |
| 2 | 農業/交易 | StraussShipwrecks.xlsx | 1,784件 | 2500BCE-1800CE |
| 3 | 人口 | LIST_v1-2.parquet | 525,870件 | ローマ帝国全期間 |
| 4 | 財政 | third_century_silver.csv | 40件 | BC27-AD295 |
| 5 | 社会不安 | Equinox_on_GitHub_June9_2022.xlsx | 47,478行 | 多期間 |

---

## 1. 気候変動データ

### ファイル情報
| 項目 | 内容 |
|------|------|
| ファイル名 | `data/eujja_2krecon_nested_cps-noaa.txt` |
| サイズ | 107KB |
| 形式 | タブ区切りテキスト（NOAA標準形式） |

### 出典
| 項目 | 内容 |
|------|------|
| タイトル | European summer temperatures since Roman times |
| 著者 | Luterbacher, J. et al. |
| 掲載誌 | Environmental Research Letters, 11(2), 024001 |
| 出版年 | 2016 |
| DOI | 10.1088/1748-9326/11/2/024001 |
| データDOI | 10.25921/b43b-1v41 |
| ダウンロード元 | https://www.ncei.noaa.gov/access/paleo-search/study/19600 |

### データ期間・解像度
- **期間**: 138 BCE - 2003 CE（2,141年分）
- **解像度**: 年単位
- **地域**: ヨーロッパ全体（35°N-70°N, 25°W-40°E）
- **季節**: 夏季（6-8月）

### カラム構造
| カラム | データ型 | 説明 | 単位 |
|--------|----------|------|------|
| age_CE | int | 年（西暦、負値はBCE） | 年 |
| temp_mean | float | 夏季気温偏差（基準期間からの偏差） | ℃ |
| temp-Lower2s | float | 2σ下限（95%信頼区間下限） | ℃ |
| temp-Upper2s | float | 2σ上限（95%信頼区間上限） | ℃ |

### サンプルデータ
```
age_CE  temp_mean  temp-Lower2s  temp-Upper2s
-138    -0.037309  -0.85472      0.76376
-137    -0.029138  -0.92172      0.81199
200      0.123456  -0.65432      0.90123
250     -0.234567  -1.01234      0.54321
```

### 補足ファイル
- `data/EuMeanDist_noInst-noaa.txt` (108KB): 空間分布データ

---

## 2. 農業/交易データ（難破船）

### ファイル情報
| 項目 | 内容 |
|------|------|
| ファイル名 | `data/StraussShipwrecks.xlsx` |
| サイズ | 約1.2MB |
| 形式 | Excel (xlsx) |

### 出典
| 項目 | 内容 |
|------|------|
| データベース名 | OXREP Shipwrecks Database |
| 作成者 | Julia Strauss / Oxford Roman Economy Project |
| URL | https://oxrep.classics.ox.ac.uk/databases/shipwrecks_database/ |
| ライセンス | Academic use |

### データ統計
| 項目 | 値 |
|------|-----|
| 総レコード数 | 1,784件 |
| 期間 | 2500 BCE - 1800 CE |
| 3世紀（200-300AD）厳密 | 67件 |
| 3世紀関連（重複含む） | 433件 |

### カラム構造（主要35列）
| カラム | データ型 | 説明 |
|--------|----------|------|
| Wreck ID | int | 難破船固有ID |
| Strauss ID | str | Strauss識別子 |
| Name | str | 難破船名称 |
| Parker Number | str | Parker (1992) 参照番号 |
| Sea area | str | 海域 |
| Country | str | 発見国 |
| Latitude | float | 緯度 |
| Longitude | float | 経度 |
| Period | str | 時代区分（Roman Imperial等） |
| Dating | str | 年代記述（例: "C3rd AD"） |
| Earliest date | float | 最早年代（負値はBC） |
| Latest date | float | 最遅年代 |
| Amphorae | str | アンフォラ積載（交易指標） |
| Other cargo | str | その他積荷 |
| Estimated tonnage | float | 推定トン数 |

### 分析用途
- **指標**: 10年ごとの難破船数
- **意味**: 地中海交易活動の代理指標
- **予想**: 3世紀に減少

### サンプルデータ
| Wreck ID | Period | Earliest date | Latest date | Country |
|----------|--------|---------------|-------------|---------|
| 1 | Roman Imperial | 1.0 | 200.0 | Croatia |
| 11 | Roman Imperial | 215.0 | 230.0 | Italy |
| 78 | Roman | 200.0 | 300.0 | Spain |

---

## 3. 人口データ（碑文）

### ファイル情報
| 項目 | 内容 |
|------|------|
| ファイル名 | `data/LIST_v1-2.parquet` |
| サイズ | 78MB |
| 形式 | Apache Parquet |
| メタデータ | `data/LI_metadata.csv` |

### 出典
| 項目 | 内容 |
|------|------|
| データセット名 | LIST: Latin Inscriptions Structured Text Dataset |
| バージョン | v1.2 |
| DOI | 10.5281/zenodo.10473706 |
| URL | https://zenodo.org/records/10473706 |
| 統合元 | EDCS + EDH + Trismegistos |

### データ統計
| 項目 | 値 |
|------|-----|
| 総レコード数 | 525,870件 |
| カラム数 | 65列 |
| 地理情報あり | 約400,000件 |
| 年代情報あり | 約350,000件 |

### カラム構造（主要列）
| カラム | データ型 | 説明 |
|--------|----------|------|
| LIST-ID | str | 固有ID |
| EDH-ID | str | Epigraphic Database Heidelberg ID |
| EDCS-ID | str | Epigraphic Database Clauss-Slaby ID |
| not_before | int | 最早年代（terminus post quem） |
| not_after | int | 最遅年代（terminus ante quem） |
| Latitude | float | 緯度 |
| Longitude | float | 経度 |
| type_of_inscription | str | 碑文種別 |
| province_label_clean | str | 属州名 |
| clean_text_interpretive_word | str | 解釈済みテキスト |

### 分析用途
- **指標**: 10年ごとの碑文数
- **意味**: 人口・経済活動の代理指標
- **予想**: 3世紀に顕著な減少（キプリアヌスの疫病の影響）

### 注意事項
- Parquet形式のため`pyarrow`が必要
- `not_before`/`not_after`で年代フィルタリング

---

## 4. 財政データ（銀含有率）

### ファイル情報
| 項目 | 内容 |
|------|------|
| ファイル名 | `data/third_century_silver.csv` |
| サイズ | 2KB |
| 形式 | CSV |

### 出典（複数ソース統合）
| 期間 | 出典 |
|------|------|
| BC27-AD98 | Butcher & Ponting (2015) |
| AD98-AD193 | Walker (1976, 1977) |
| AD193-AD211 | Gitler & Ponting (2003) |
| AD211-AD284 | Walker (1978) |
| AD284-AD295 | 二次文献 |

### 主要文献
| 著者 | タイトル | 年 | DOI |
|------|---------|-----|-----|
| Butcher & Ponting | The Metallurgy of Roman Silver Coinage | 2015 | 10.5284/1035238 |
| Walker, D.R. | The Metrology of the Roman Silver Coinage Part I-III | 1976-78 | - |
| Gitler & Ponting | The Silver Coinage of Septimius Severus | 2003 | - |

### データ統計
| 項目 | 値 |
|------|-----|
| レコード数 | 40件 |
| 期間 | BC27 - AD295 |
| 最高値 | 99.2%（Caligula） |
| 最低値 | 4.0%（Claudius II） |

### カラム構造
| カラム | データ型 | 説明 |
|--------|----------|------|
| YEAR | int | 年代（負値はBC） |
| EMPEROR | str | 皇帝名 |
| SILVER | float | 銀含有率 (%) |
| COIN_TYPE | str | 貨幣種別（Denarius, Antoninianus等） |
| SOURCE | str | データ出典 |
| NOTES | str | 備考 |

### 主要データポイント
| 年代 | 皇帝 | 銀含有率 | 意義 |
|------|------|---------|------|
| BC27 | Augustus | 98.5% | 帝政開始・基準点 |
| AD64 | Nero | 93.5% | ネロの貨幣改変 |
| AD215 | Caracalla | 51.5% | アントニニアヌス導入 |
| AD268 | Gallienus | 4.5% | **3世紀の危機最悪期** |
| AD295 | Diocletian | 95.0% | アルゲンテウス導入・回復 |

### 補足データ
- `data/Denarii_JC_to_Trajans_reform_final.xlsx` (728件): 詳細分析データ
- `data/Provincial_JC_to_Trajans_reform_final.xlsx` (349件): 属州貨幣データ

---

## 5. 社会不安データ

### ファイル情報
| 項目 | 内容 |
|------|------|
| ファイル名 | `data/Equinox_on_GitHub_June9_2022.xlsx` |
| サイズ | 5.8MB |
| 形式 | Excel (xlsx) |
| シート数 | 13 |

### 出典
| 項目 | 内容 |
|------|------|
| データベース名 | Seshat: Global History Databank |
| データセット名 | Equinox Dataset |
| DOI | 10.5281/zenodo.6642229 |
| URL | https://zenodo.org/records/6642229 |

### シート構造
| シート名 | 内容 | 行数 |
|----------|------|------|
| Metadata | メタデータ | - |
| Equinox2020_CanonDat | 標準データ | 47,478 |
| TSDat123 | **時系列データ** | 1,495 × 168列 |
| Variables | 変数定義 | - |
| Polities | 政体一覧 | - |
| NGAs | 自然地理区域 | - |

### ローマ帝国データ
| 政体ID | 政体名 | 期間 |
|--------|--------|------|
| ItRomPr | Roman Empire - Principate | -31 to 283 |
| TrRomDm | Roman Empire - Dominate | 284 to 394 |

### 政治不安定変数（TSDat123シート）
| 変数 | 説明 | 値域 |
|------|------|------|
| ExternalW | 対外戦争 | 0/1 |
| InternalW | 内戦 | 0/1 |
| IntraElitW | エリート間紛争 | 0/1 |
| PopUprising | 民衆蜂起 | 0/1 |
| MilRevolt | 軍事反乱 | 0/1 |
| SepRebellion | 分離主義反乱 | 0/1 |

### ローマ帝国3世紀データ
| 年代 | ExternalW | InternalW | PopUprising | MilRevolt | 領土(km²) |
|------|-----------|-----------|-------------|-----------|-----------|
| AD200 | 1 | 1 | 0 | 1 | 5,000,000 |
| AD300 | 1 | 1 | 1 | 1 | 4,250,000 |

### 分析用途
- **指標**: 不安定指標の合計（InternalW + MilRevolt + PopUprising）
- **意味**: 政治的不安定性の直接指標
- **予想**: 3世紀（235-284）に最大

---

## 依存ライブラリ

```
pandas>=2.0.0
numpy>=1.24.0
openpyxl>=3.1.0      # Excel読み込み
pyarrow>=14.0.0      # Parquet読み込み
matplotlib>=3.7.0
seaborn>=0.12.0
scipy>=1.10.0
statsmodels>=0.14.0  # グレンジャー因果性検定、VAR
```

---

## 引用形式（BibTeX）

```bibtex
@article{luterbacher2016european,
  title={European summer temperatures since Roman times},
  author={Luterbacher, J. and Werner, J.P. and others},
  journal={Environmental Research Letters},
  volume={11},
  number={2},
  pages={024001},
  year={2016},
  doi={10.1088/1748-9326/11/2/024001}
}

@misc{oxrep_shipwrecks,
  title={OXREP Shipwrecks Database},
  author={Strauss, Julia},
  howpublished={Oxford Roman Economy Project},
  url={https://oxrep.classics.ox.ac.uk/databases/shipwrecks_database/}
}

@misc{list2024dataset,
  title={LIST: Latin Inscriptions Structured Text Dataset v1.2},
  year={2024},
  howpublished={Zenodo},
  doi={10.5281/zenodo.10473706}
}

@book{butcher2015metallurgy,
  title={The Metallurgy of Roman Silver Coinage},
  author={Butcher, Kevin and Ponting, Matthew},
  year={2015},
  publisher={Cambridge University Press},
  doi={10.5284/1035238}
}

@misc{seshat2022equinox,
  title={Seshat Equinox Dataset},
  author={{Seshat Global History Databank}},
  year={2022},
  howpublished={Zenodo},
  doi={10.5281/zenodo.6642229}
}
```
