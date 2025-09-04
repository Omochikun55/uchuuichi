#!/usr/bin/env python3
"""
宇宙一わかりやすい化学 PDF → フラッシュカード変換プログラム
ユーザー要望版：原文活用OK、図表積極活用
"""

import json
import re
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass, asdict
from datetime import datetime

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class FlashCard:
    """フラッシュカードのデータ構造"""
    id: str
    subject: str
    chapter: str
    topic: str
    type: str  # quick, decision, process, graph
    question: str
    answer: str
    hint: Optional[str] = None
    image_path: Optional[str] = None
    image_caption: Optional[str] = None
    tags: List[str] = None
    level: int = 1
    misconceptions: List[str] = None
    source_page: Optional[int] = None
    original_text: Optional[str] = None  # 原文保存用
    
    def to_dict(self) -> Dict:
        """辞書形式に変換（None値を除外）"""
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}

class ChemistryPDFExtractor:
    """化学PDFからフラッシュカードを抽出"""
    
    def __init__(self, pdf_path: Path, output_dir: Path):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.cards: List[FlashCard] = []
        self.image_dir = output_dir / "images"
        self.image_dir.mkdir(parents=True, exist_ok=True)
        
        # パターン定義
        self.patterns = {
            'definition': r'([^。]+?)とは([^。]+)。',
            'formula': r'(?:式|公式|関係式)[：:]\s*(.+)',
            'important': r'(?:重要|ポイント|覚える)[：:！]\s*(.+)',
            'caution': r'(?:注意|気をつけ|間違えやすい)[：:！]\s*(.+)',
            'example': r'(?:例題|例|問題)\s*\d*[：:]\s*(.+)',
        }
        
    def extract_text_and_images(self) -> List[Dict]:
        """PDFからテキストと画像を抽出"""
        logger.info(f"PDFを開いています: {self.pdf_path}")
        doc = fitz.open(self.pdf_path)
        pages_data = []
        
        for page_num, page in enumerate(doc, 1):
            # テキスト抽出
            text = page.get_text()
            
            # 画像抽出（図表があるページ）
            images = []
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                # 画像を保存
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                
                if pix.n - pix.alpha < 4:  # GRAY or RGB
                    img_path = self.image_dir / f"page_{page_num}_img_{img_index}.png"
                    pix.save(str(img_path))
                    images.append(str(img_path.relative_to(self.output_dir)))
                    logger.info(f"画像を保存: {img_path}")
                
                pix = None
            
            pages_data.append({
                'page': page_num,
                'text': text,
                'images': images
            })
            
        doc.close()
        logger.info(f"抽出完了: {len(pages_data)}ページ")
        return pages_data
    
    def extract_sections(self, text: str) -> List[Dict]:
        """テキストからセクションを抽出"""
        sections = []
        
        # 見出しパターンで分割
        chapter_pattern = r'(第[0-9一二三四五六七八九十]+[章節]|^\d+[\.．])'
        lines = text.split('\n')
        
        current_section = {
            'title': '',
            'content': [],
            'type': 'general'
        }
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 見出し検出
            if re.match(chapter_pattern, line):
                if current_section['content']:
                    sections.append(current_section)
                current_section = {
                    'title': line,
                    'content': [],
                    'type': 'chapter'
                }
            else:
                current_section['content'].append(line)
        
        if current_section['content']:
            sections.append(current_section)
            
        return sections
    
    def create_cards_from_section(self, section: Dict, page_num: int, images: List[str]) -> List[FlashCard]:
        """セクションからカードを生成"""
        cards = []
        content = '\n'.join(section['content'])
        
        # 定義カード
        for match in re.finditer(self.patterns['definition'], content):
            term = match.group(1).strip()
            definition = match.group(2).strip()
            
            card = FlashCard(
                id=f"chem_{page_num:03d}_{len(cards):03d}",
                subject="化学",
                chapter=section.get('title', ''),
                topic="定義",
                type="quick",
                question=f"{term}とは何ですか？",
                answer=definition,  # 原文をそのまま使用
                original_text=match.group(0),  # 原文保存
                tags=[term, "定義"],
                level=1,
                source_page=page_num
            )
            cards.append(card)
            logger.debug(f"定義カード作成: {term}")
        
        # 公式カード
        for match in re.finditer(self.patterns['formula'], content):
            formula = match.group(1).strip()
            
            # 化学式の整形（簡易版）
            formula = self._format_chemical_formula(formula)
            
            card = FlashCard(
                id=f"chem_{page_num:03d}_{len(cards):03d}",
                subject="化学",
                chapter=section.get('title', ''),
                topic="公式",
                type="quick",
                question="次の公式は何を表していますか？",
                answer=formula,
                original_text=match.group(0),
                tags=["公式"],
                level=2,
                source_page=page_num
            )
            cards.append(card)
        
        # 注意事項カード（典型ミス）
        for match in re.finditer(self.patterns['caution'], content):
            caution = match.group(1).strip()
            
            card = FlashCard(
                id=f"chem_{page_num:03d}_{len(cards):03d}",
                subject="化学",
                chapter=section.get('title', ''),
                topic="注意点",
                type="quick",
                question="この内容で気をつけるべきことは？",
                answer=caution,
                misconceptions=[caution],
                tags=["注意", "典型ミス"],
                level=2,
                source_page=page_num
            )
            cards.append(card)
        
        # 画像付きカード（画像がある場合）
        if images:
            for img_path in images[:1]:  # 最初の画像を使用
                card = FlashCard(
                    id=f"chem_{page_num:03d}_{len(cards):03d}",
                    subject="化学",
                    chapter=section.get('title', ''),
                    topic="図解",
                    type="graph",
                    question="この図が示している内容は？",
                    answer="図を参照して理解してください",
                    image_path=img_path,
                    image_caption=f"ページ{page_num}の図",
                    tags=["図解"],
                    level=2,
                    source_page=page_num
                )
                cards.append(card)
        
        return cards
    
    def _format_chemical_formula(self, formula: str) -> str:
        """化学式の簡易整形"""
        # 数字を下付きに（簡易版）
        formula = re.sub(r'([A-Z][a-z]?)(\d+)', r'\1₂', formula)
        # 矢印の統一
        formula = formula.replace('->', '→').replace('=>', '→')
        return formula
    
    def process_pdf(self) -> List[FlashCard]:
        """PDF全体を処理"""
        pages_data = self.extract_text_and_images()
        
        for page_data in pages_data:
            page_num = page_data['page']
            text = page_data['text']
            images = page_data['images']
            
            # セクション抽出
            sections = self.extract_sections(text)
            
            # カード生成
            for section in sections:
                cards = self.create_cards_from_section(section, page_num, images)
                self.cards.extend(cards)
        
        logger.info(f"総カード数: {len(self.cards)}")
        return self.cards
    
    def save_cards(self, output_path: Optional[Path] = None):
        """カードをJSON形式で保存"""
        if output_path is None:
            output_path = self.output_dir / "cards.json"
        
        cards_data = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'source_pdf': str(self.pdf_path),
                'total_cards': len(self.cards),
                'version': '2.0'
            },
            'cards': [card.to_dict() for card in self.cards]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(cards_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"カードを保存しました: {output_path}")
        
    def create_review_html(self):
        """レビュー用HTMLを生成"""
        html_path = self.output_dir / "review.html"
        
        html_content = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>フラッシュカード レビュー</title>
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .card { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 8px; }
        .card-header { font-weight: bold; color: #333; margin-bottom: 10px; }
        .question { background: #f0f8ff; padding: 10px; margin: 5px 0; border-radius: 4px; }
        .answer { background: #f0fff0; padding: 10px; margin: 5px 0; border-radius: 4px; }
        .meta { color: #666; font-size: 0.9em; margin-top: 10px; }
        .image { max-width: 100%; margin: 10px 0; }
        .actions { margin-top: 10px; }
        button { padding: 5px 15px; margin-right: 10px; cursor: pointer; }
        .approve { background: #4CAF50; color: white; border: none; border-radius: 4px; }
        .reject { background: #f44336; color: white; border: none; border-radius: 4px; }
        .edit { background: #FF9800; color: white; border: none; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>フラッシュカード レビュー</h1>
    <p>総カード数: """ + str(len(self.cards)) + """</p>
    <div id="cards">
"""
        
        for i, card in enumerate(self.cards):
            html_content += f"""
        <div class="card" data-id="{card.id}">
            <div class="card-header">カード {i+1} / {len(self.cards)} - {card.type} - {card.topic}</div>
            <div class="question"><strong>Q:</strong> {card.question}</div>
            <div class="answer"><strong>A:</strong> {card.answer}</div>
            """
            
            if card.image_path:
                html_content += f'<img class="image" src="{card.image_path}" alt="図">'
            
            if card.hint:
                html_content += f'<div class="hint"><strong>ヒント:</strong> {card.hint}</div>'
            
            if card.misconceptions:
                html_content += f'<div class="misconception"><strong>典型ミス:</strong> {", ".join(card.misconceptions)}</div>'
            
            html_content += f"""
            <div class="meta">
                ページ: {card.source_page or "不明"} | 
                レベル: {card.level} | 
                タグ: {", ".join(card.tags or [])}
            </div>
            <div class="actions">
                <button class="approve" onclick="approve('{card.id}')">承認</button>
                <button class="edit" onclick="edit('{card.id}')">編集</button>
                <button class="reject" onclick="reject('{card.id}')">削除</button>
            </div>
        </div>
"""
        
        html_content += """
    </div>
    <script>
        function approve(id) {
            document.querySelector(`[data-id="${id}"]`).style.background = '#e8f5e9';
            console.log('Approved:', id);
        }
        function edit(id) {
            document.querySelector(`[data-id="${id}"]`).style.background = '#fff3e0';
            console.log('Edit:', id);
        }
        function reject(id) {
            document.querySelector(`[data-id="${id}"]`).style.background = '#ffebee';
            console.log('Rejected:', id);
        }
    </script>
</body>
</html>
"""
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"レビューHTMLを作成: {html_path}")

def main():
    """メイン処理"""
    # 設定
    pdf_path = Path("sample.pdf")  # PDFパスを指定
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # 抽出実行
    extractor = ChemistryPDFExtractor(pdf_path, output_dir)
    cards = extractor.process_pdf()
    
    # 保存
    extractor.save_cards()
    extractor.create_review_html()
    
    # 統計表示
    print(f"\n=== 抽出結果 ===")
    print(f"総カード数: {len(cards)}")
    
    # タイプ別集計
    from collections import Counter
    types = Counter(card.type for card in cards)
    for card_type, count in types.items():
        print(f"  {card_type}: {count}枚")
    
    print(f"\n出力先: {output_dir}")

if __name__ == "__main__":
    main()