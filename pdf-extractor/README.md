# 宇宙一わかりやすい化学 PDF → フラッシュカード変換システム

## 特徴（ユーザー要望対応版）

### ✅ 原文活用方針
- **定義・重要概念**：原文の分かりやすい説明をそのまま採用
- **化学式・反応式**：正確性重視で原文を優先使用
- **「宇宙一」の特徴**：独特の説明や例えは保持

### ✅ 図表の積極活用
- 図表を画像として抽出・保存
- カードに画像パスを紐付け
- 視覚的理解を促進

### ✅ ハイブリッドアプローチ
- **シンプルな内容**：ルールベース抽出（高速）
- **複雑な内容**：Claude API活用（高品質）
- **品質チェック**：自動検証＋人手レビュー

## セットアップ

```bash
# 仮想環境作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージインストール
pip install -r requirements.txt

# 環境変数設定（Claude API使用時）
cp .env.example .env
# .envファイルにANTHROPIC_API_KEYを設定
```

## 使い方

### 1. 基本的な抽出（ルールベース）

```python
from pathlib import Path
from extract_cards import ChemistryPDFExtractor

# PDFからカード抽出
pdf_path = Path("宇宙一わかりやすい化学.pdf")
output_dir = Path("output")

extractor = ChemistryPDFExtractor(pdf_path, output_dir)
cards = extractor.process_pdf()

# JSON保存
extractor.save_cards()

# レビュー用HTML生成
extractor.create_review_html()
```

### 2. Claude APIを使った高品質抽出

```python
from extract_with_claude import EnhancedExtractor

# APIキーを環境変数に設定後
extractor = EnhancedExtractor(pdf_path, output_dir)
cards = extractor.process_with_claude()
```

### 3. バッチ処理（章ごと）

```bash
python batch_process.py --input-dir pdfs/ --output-dir output/
```

## カードタイプ

### quick（クイック問答）
```json
{
  "type": "quick",
  "question": "ブレンステッド酸の定義は？",
  "answer": "プロトン（H⁺）を与える物質"
}
```

### decision（原理選択）
```json
{
  "type": "decision",
  "prompt": "弱酸のpH計算で使う近似は？",
  "choices": ["完全電離", "Henderson式", "弱電離近似"],
  "answer_index": 2
}
```

### process（手順分解）
```json
{
  "type": "process",
  "steps": [
    {"prompt": "立式", "expected": "Ka = [H+][A-]/[HA]"},
    {"prompt": "近似", "expected": "[HA] ≈ C0"},
    {"prompt": "解", "expected": "[H+] = √(Ka×C0)"}
  ]
}
```

### graph（図表理解）
```json
{
  "type": "graph",
  "image_path": "images/titration_curve.png",
  "question": "この滴定曲線の当量点は？",
  "answer": "pH 8.7付近（弱酸-強塩基）"
}
```

## 出力ファイル

```
output/
├── cards.json          # フラッシュカードデータ
├── review.html         # レビュー用HTML
├── images/             # 抽出した図表
│   ├── page_001_img_0.png
│   └── ...
└── logs/               # 処理ログ
    └── extraction.log
```

## 品質管理

### 自動チェック項目
- ✓ 質問文の長さ（120文字以内推奨）
- ✓ 回答文の長さ（160文字以内推奨）
- ✓ 化学式の形式チェック
- ✓ 重複カードの検出
- ✓ 必須フィールドの確認

### レビューワークフロー
1. `review.html`を開く
2. 各カードを確認
3. 承認/編集/削除をクリック
4. 編集が必要なカードはCSVエクスポート
5. 一括修正後、再インポート

## トラブルシューティング

### PDFからテキストが抽出できない
- OCR機能を有効化：`pytesseract`インストール確認
- 日本語OCR：`tesseract-ocr-jpn`パッケージ追加

### 画像が表示されない
- 画像パスが相対パスになっているか確認
- `review.html`と`images/`フォルダの位置関係確認

### メモリ不足
- PDFを章ごとに分割して処理
- `--max-pages`オプションで処理ページ数制限

## 注意事項

- **著作権**：生成したカードは個人学習用途に限定
- **配布禁止**：PDFコンテンツの再配布は行わない
- **品質確認**：自動生成カードは必ずレビュー後に使用

## ライセンス

個人学習用途限定。商用利用不可。