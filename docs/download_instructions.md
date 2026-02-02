# データダウンロード手順

## 概要

因果連鎖（気候→農業→人口→財政→社会不安）を検証するために必要なデータのダウンロード手順です。

---

## 1. OXREP Shipwrecks（難破船データ）- 農業/交易指標

**用途**: 交易活動の代理指標として使用

### 手順
1. https://oxrep.classics.ox.ac.uk/databases/shipwrecks_database/ にアクセス
2. ページ下部の「Download」セクションを探す
3. 「Download the database (ZIP format)」をクリック
4. ZIPファイルを `data/` フォルダに展開

### 保存先
```
data/oxrep_shipwrecks/
```

---

## 2. Seshat Equinox Dataset（政治不安定データ）

**用途**: 社会不安の指標（統治者暗殺、内戦など）

### 手順
1. https://zenodo.org/records/6642229 にアクセス
2. 「Files」セクションから必要なファイルをダウンロード
   - `seshat-equinox-2022-08.csv`（主要データ）
3. `data/` フォルダに保存

### 保存先
```
data/seshat_equinox.csv
```

---

## 3. LIST Dataset（碑文データ）- 人口指標

**用途**: 碑文頻度を人口の代理指標として使用

### 手順
1. https://zenodo.org/records/10473706 にアクセス
2. 「Files」セクションからCSVファイルをダウンロード
3. `data/` フォルダに保存

### 保存先
```
data/list_inscriptions.csv
```

**注意**: ファイルサイズが大きい（525,870件）

---

## 4. McCormick et al. (2012) 気候データ

**用途**: 古気候復元データ

### 手順
1. https://direct.mit.edu/jinh/article/43/2/169/48835 にアクセス
2. 「Supplementary Materials」または「Supporting Information」を探す
3. 補足データファイルをダウンロード
4. `data/` フォルダに保存

### 代替: NOAA Paleoclimatology
1. https://www.ncei.noaa.gov/products/paleoclimatology にアクセス
2. 「Data Search」で以下を検索:
   - 地域: Europe, Mediterranean
   - 期間: 0-500 CE
3. 関連データセットをダウンロード

### 保存先
```
data/climate/
```

---

## 5. Coin Hoards of the Roman Empire（コインホード）

**用途**: 社会不安・経済危機の指標

### 手順
1. https://chre.ashmus.ox.ac.uk/ にアクセス
2. 「Search」機能で期間を指定（AD 200-300）
3. 結果をエクスポート（可能な場合）

**注意**: Web閲覧のみでダウンロード機能がない場合は、検索結果を手動で記録

---

## 6. European Summer Temperature Reconstruction

**用途**: 気候変動データ

### 手順
1. https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=noaa-recon-19600 にアクセス
2. 「Download」セクションからデータファイルを取得
3. フォーマット: NetCDF または TXT

### 保存先
```
data/climate/european_temperature.txt
```

---

## ダウンロード後の確認

すべてのデータをダウンロードしたら、以下のフォルダ構成になっているか確認してください：

```
data/
├── Denarii_JC_to_Trajans_reform_final.xlsx    # 既存
├── Provincial_JC_to_Trajans_reform_final.xlsx # 既存
├── third_century_silver.csv                   # 既存
├── oxrep_shipwrecks/                          # 新規
├── seshat_equinox.csv                         # 新規
├── list_inscriptions.csv                      # 新規
└── climate/                                   # 新規
    └── european_temperature.txt
```

---

## 優先順位

時間がない場合、以下の順序でダウンロードを推奨：

1. **Seshat Equinox** - 政治不安定の直接指標（最重要）
2. **OXREP Shipwrecks** - 交易活動/農業の代理指標
3. **気候データ** - 因果連鎖の起点
4. **LIST Dataset** - 人口の代理指標（ファイルが大きい）

---

## ダウンロード完了後

データをダウンロードしたら、私に教えてください。データの読み込みと前処理のコードを作成します。
