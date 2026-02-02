# データソース一覧

## 1. 主要データ: Archaeology Data Service (ADS)

### Butcher & Ponting (2015)

| 項目 | 内容 |
|------|------|
| **タイトル** | The Metallurgy of Roman Silver Coinage: From the Reform of Nero to the Reform of Trajan |
| **著者** | Kevin Butcher, Matthew Ponting |
| **出版社** | Cambridge University Press |
| **出版年** | 2015 |
| **DOI** | https://doi.org/10.5284/1035238 |
| **データ公開元** | Archaeology Data Service (ADS) |
| **ライセンス** | ADS Terms of Use |

### ダウンロードしたファイル

```
data/
├── Denarii_JC_to_Trajans_reform_final.xlsx   # 728件
└── Provincial_JC_to_Trajans_reform_final.xlsx # 349件
```

### データ期間
- BC44年（ユリウス・カエサル）〜 AD98年（ネルウァ帝）

### 主要カラム
- `EMPEROR`: 皇帝名
- `SILVER`: 銀含有率 (%)
- `COPPER`: 銅含有率 (%)
- `LEAD`: 鉛含有率 (%)
- `GOLD`: 金含有率 (%)
- `MINT`: 鋳造地
- `DENOMINATION`: 貨幣種別
- `RIC`: Roman Imperial Coinage 参照番号

---

## 2. 3世紀データ: 二次文献から抽出

### Walker (1976, 1977, 1978)

| 項目 | 内容 |
|------|------|
| **タイトル** | The Metrology of the Roman Silver Coinage |
| **著者** | D.R. Walker |
| **出版社** | BAR Publishing |
| **シリーズ** | BAR Supplementary Series |

**Part I (1976)**: Augustus to Domitian - BAR Supplementary Series 5
**Part II (1977)**: Nerva to Commodus - BAR Supplementary Series 22
**Part III (1978)**: Pertinax to Uranius Antoninus - BAR Supplementary Series 40

**注意**: Walker のデータは表面分析のため、-10%の補正が必要（Gitler & Ponting 2003）

---

### Gitler & Ponting (2003)

| 項目 | 内容 |
|------|------|
| **タイトル** | The Silver Coinage of Septimius Severus and His Family (193-211 AD) |
| **著者** | Haim Gitler, Matthew Ponting |
| **出版** | Glaux 16 |
| **出版年** | 2003 |

---

## 3. 先行研究: モデル参照

### Roman & Palmer (2019)

| 項目 | 内容 |
|------|------|
| **タイトル** | The Growth and Decline of the Western Roman Empire: Quantifying the Dynamics of Army Size, Territory, and Coinage |
| **著者** | Sabin Roman, Erika Palmer |
| **出版年** | 2019 |
| **URL** | https://escholarship.org/uc/item/2cz4q2jq |
| **補足データ** | eScholarship "Supplemental Material" |

**参照データソース（論文内で使用）**:
- 軍隊規模: MacMullen (1980) "How Big was the Roman Imperial Army?" *Klio* 62
- 領土面積: Taagepera (1979) "Size and Duration of Empires" *Social Science History* 3
- 貨幣鋳造量: Hopkins (1980) "Taxes and Trade in the Roman Empire" *JRS* 70

---

## 4. 追加データベース（参考）

### OCRE - Online Coins of the Roman Empire
- URL: https://numismatics.org/ocre/
- ライセンス: Open Database License
- 内容: 43,000以上のコインタイプ

### RPC - Roman Provincial Coinage
- URL: https://rpc.ashmus.ox.ac.uk/
- Vol.X: AD253-295/6をカバー

### Visual Capitalist
- URL: https://money.visualcapitalist.com/deaths-roman-emperors-vs-silver-coin-content/
- 内容: 皇帝死亡と銀含有率の相関データ

### Seshat: Global History Databank
- URL: http://seshatdatabank.info/
- 内容: クリオダイナミクス研究の標準データベース

### OXREP - Oxford Roman Economy Project
- URL: http://oxrep.classics.ox.ac.jp/
- 内容: ローマ経済データ（難破船、鉱山など）

---

## 5. 作成したデータファイル

### third_century_silver.csv

**作成日**: 2026-02-02
**データ件数**: 36件
**期間**: BC27年 〜 AD295年

**カラム**:
| カラム名 | 型 | 説明 |
|---------|-----|------|
| YEAR | int | 年代（負値はBC） |
| EMPEROR | str | 皇帝名 |
| SILVER | float | 銀含有率 (%) |
| COIN_TYPE | str | 貨幣種別（Denarius, Antoninianus等） |
| SOURCE | str | データ出典 |
| NOTES | str | 備考 |

**データの流れ**:
```
BC27 Augustus     98.5%  ← Butcher & Ponting平均値
  ↓
AD64 Nero改変     93.5%  ← ネロの貨幣改変
  ↓
AD215 Caracalla   51.5%  ← アントニニアヌス導入
  ↓
AD268 Gallienus    4.5%  ← 3世紀の危機最悪期
  ↓
AD295 Diocletian  95.0%  ← アルゲンテウス導入で回復
```

---

## 6. 因果連鎖検証用データソース

### 仮説: 気候変動 → 農業 → 人口 → 財政 → 社会不安

---

### 6.1 気候変動データ

#### データベース
| 名称 | URL | 内容 | アクセス |
|------|-----|------|---------|
| **NOAA Paleoclimatology** | https://www.ncei.noaa.gov/products/paleoclimatology | 古気候アーカイブ | オープン |
| **European Summer Temperature** | DOI: 10.25921/b43b-1v41 | 138BCE-2003CE | オープン |

#### 主要論文
| 著者 | タイトル | 年 | 備考 |
|------|---------|-----|------|
| **McCormick et al.** | Climate Change during and after the Roman Empire | 2012 | **最重要**、補足データあり |
| **Zonneveld, Harper et al.** | Climate change, society, and pandemic disease in Roman Italy | 2024 | Science Advances |
| **Harper, Kyle** | The Fate of Rome | 2017 | Princeton University Press |

#### 重要イベント
- Roman Climate Optimum: 250BCE-400CE
- **3世紀の寒冷化: 245-275CE**

---

### 6.2 農業生産力データ

#### データベース
| 名称 | URL | 内容 | アクセス |
|------|-----|------|---------|
| **OXREP Shipwrecks** | https://oxrep.classics.ox.ac.uk/databases/shipwrecks_database/ | 難破船1,784件 | オープン（ZIP） |
| **OXREP Mines** | https://oxrep.classics.ox.ac.uk/databases/mines_database/ | 鉱山データ | オープン |

#### 主要論文
| 著者 | タイトル | 年 |
|------|---------|-----|
| **Erdkamp, Paul** | The Grain Market in the Roman Empire | 2005 |
| **Garnsey, Peter** | Famine and Food Supply in the Graeco-Roman World | 1988 |

---

### 6.3 人口データ

#### データベース
| 名称 | URL | 内容 | アクセス |
|------|-----|------|---------|
| **Coin Hoards of the Roman Empire** | https://chre.ashmus.ox.ac.uk/ | 15,000件のホード | オープン |
| **Epigraphic Database Heidelberg** | https://edh.ub.uni-heidelberg.de/ | 71,000件の碑文 | オープン |
| **LIST Dataset** | Zenodo DOI: 10.5281/zenodo.10473706 | 525,870件の碑文 | オープン |

#### 主要論文
| 著者 | タイトル | 年 |
|------|---------|-----|
| **Bagnall & Frier** | The Demography of Roman Egypt | 1994 |
| **Scheidel, Walter** | Roman Population Size: The Logic of the Debate | 2007 |
| **Harper, Kyle** | Pandemics and Passages to Late Antiquity | 2015 |

#### キプリアヌスの疫病（AD249-262）
- 人口減少率: 10-30%
- 碑文頻度: 3世紀に顕著な減少
- コインホード: 3世紀が全体の47.5%

---

### 6.4 社会不安データ

#### データベース
| 名称 | URL | 内容 | アクセス |
|------|-----|------|---------|
| **Seshat Databank** | https://seshat-db.com/ | 862政体、政治不安定変数 | オープン |
| **Seshat Equinox** | Zenodo DOI: 10.5281/zenodo.6642229 | 機械可読形式 | オープン |

#### Seshatの政治不安定変数
- Ruler Assassination（統治者暗殺）
- Civil War（内戦）
- Uprising / Revolution（蜂起・革命）
- Population Decline（人口減少）

#### 3世紀の危機の統計
- 皇帝数: 26人以上（50年間）
- 平均在位: 約2年未満
- 暗殺率: 54%（26人中14人）

---

## 引用形式

### BibTeX

```bibtex
@book{butcher2015metallurgy,
  title={The Metallurgy of Roman Silver Coinage: From the Reform of Nero to the Reform of Trajan},
  author={Butcher, Kevin and Ponting, Matthew},
  year={2015},
  publisher={Cambridge University Press},
  doi={10.5284/1035238}
}

@article{roman2019growth,
  title={The Growth and Decline of the Western Roman Empire: Quantifying the Dynamics of Army Size, Territory, and Coinage},
  author={Roman, Sabin and Palmer, Erika},
  year={2019},
  url={https://escholarship.org/uc/item/2cz4q2jq}
}

@book{walker1978metrology,
  title={The Metrology of the Roman Silver Coinage, Part III: From Pertinax to Uranius Antoninus},
  author={Walker, D.R.},
  year={1978},
  series={BAR Supplementary Series 40},
  publisher={BAR Publishing}
}

@article{mccormick2012climate,
  title={Climate Change during and after the Roman Empire: Reconstructing the Past from Scientific and Historical Evidence},
  author={McCormick, Michael and B{\"u}ntgen, Ulf and Cane, Mark A and Cook, Edward R and Harper, Kyle and Huybers, Peter and Litt, Thomas and Manning, Sturt W and Mayewski, Paul A and More, Alexander FM and others},
  journal={Journal of Interdisciplinary History},
  volume={43},
  number={2},
  pages={169--220},
  year={2012},
  doi={10.1162/JINH_a_00379}
}

@book{harper2017fate,
  title={The Fate of Rome: Climate, Disease, and the End of an Empire},
  author={Harper, Kyle},
  year={2017},
  publisher={Princeton University Press},
  isbn={9780691166834}
}

@article{zonneveld2024climate,
  title={Climate change, society, and pandemic disease in Roman Italy between 200 BCE and 600 CE},
  author={Zonneveld, Karin AF and Harper, Kyle and others},
  journal={Science Advances},
  year={2024},
  doi={10.1126/sciadv.adk1033}
}

@misc{seshat2022equinox,
  title={Seshat Equinox Dataset},
  author={{Seshat Global History Databank}},
  year={2022},
  howpublished={Zenodo},
  doi={10.5281/zenodo.6642229}
}

@misc{list2024dataset,
  title={LIST: Latin Inscriptions Structured Text Dataset},
  year={2024},
  howpublished={Zenodo},
  doi={10.5281/zenodo.10473706}
}
```
