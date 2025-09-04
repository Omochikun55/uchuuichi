#!/usr/bin/env python3
"""
宇宙一わかりやすい化学PDFから高品質カード抽出
実際のPDF対応版
"""

import json
import re
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UchuichiExtractor:
    """宇宙一わかりやすいシリーズ専用抽出器"""
    
    def __init__(self, pdf_path: Path, output_dir: Path, max_pages: int = None):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.max_pages = max_pages
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cards = []
        
        # 画像保存用ディレクトリ
        self.image_dir = self.output_dir / "images"
        self.image_dir.mkdir(exist_ok=True)
        
    def extract_pages(self, start_page: int = 0, num_pages: int = 10):
        """指定ページ範囲を抽出（メモリ効率化）"""
        logger.info(f"PDFを開いています: {self.pdf_path}")
        
        try:
            doc = fitz.open(self.pdf_path)
            total_pages = len(doc)
            end_page = min(start_page + num_pages, total_pages)
            
            if self.max_pages:
                end_page = min(end_page, self.max_pages)
            
            logger.info(f"ページ {start_page+1} から {end_page} まで処理")
            
            pages_data = []
            for page_num in range(start_page, end_page):
                page = doc[page_num]
                
                # テキスト抽出
                text = page.get_text()
                
                # 画像抽出（重要な図のみ）
                images = []
                if self._has_important_diagram(text):
                    image_list = page.get_images()
                    for img_index, img in enumerate(image_list[:2]):  # 最初の2画像のみ
                        try:
                            xref = img[0]
                            pix = fitz.Pixmap(doc, xref)
                            if pix.n - pix.alpha < 4:
                                img_path = self.image_dir / f"p{page_num+1}_img{img_index}.png"
                                pix.save(str(img_path))
                                images.append(str(img_path.relative_to(self.output_dir)))
                                logger.debug(f"画像保存: {img_path}")
                            pix = None
                        except Exception as e:
                            logger.warning(f"画像抽出エラー: {e}")
                
                pages_data.append({
                    'page': page_num + 1,
                    'text': text,
                    'images': images
                })
            
            doc.close()
            return pages_data
            
        except Exception as e:
            logger.error(f"PDF処理エラー: {e}")
            return []
    
    def _has_important_diagram(self, text: str) -> bool:
        """重要な図があるかチェック"""
        keywords = ['図', '表', 'グラフ', '反応式', '構造式']
        return any(keyword in text for keyword in keywords)
    
    def extract_cards_from_text(self, text: str, page_num: int) -> List[Dict]:
        """テキストからカード抽出"""
        cards = []
        
        # パターンマッチング
        patterns = {
            # 定義パターン
            'definition': [
                r'([^。]+?)とは、?([^。]+?)(?:のこと)?(?:です|である|。)',
                r'([^。]+?)は、?([^。]+?)(?:です|である|。)',
                r'■\s*([^■\n]+)\n([^■]+?)(?=■|\n\n|$)',
            ],
            # 公式・式
            'formula': [
                r'(?:公式|式|関係式)[：:]\s*([^\n]+)',
                r'([A-Z][a-z]?\d*[^\n]*=[^\n]+)',
                r'(\[[^\]]+\]\s*=\s*[^\n]+)',
            ],
            # ポイント・重要
            'important': [
                r'(?:ポイント|重要|覚える|注意)[：:！]\s*([^。\n]+)',
                r'★\s*([^★\n]+)',
                r'！\s*([^！\n]+)',
            ],
            # 例題
            'example': [
                r'(?:例題|問題|演習)\s*\d*[：:]\s*([^。\n]+)',
                r'Q\.\s*([^A\n]+)',
            ]
        }
        
        # 定義カード生成
        for pattern in patterns['definition']:
            for match in re.finditer(pattern, text, re.MULTILINE | re.DOTALL):
                groups = match.groups()
                if len(groups) >= 2:
                    term = groups[0].strip()
                    definition = groups[1].strip()[:200]  # 長さ制限
                    
                    # 質の低いマッチを除外
                    if len(term) < 50 and len(definition) > 10:
                        cards.append({
                            'id': f'uch_{page_num:04d}_{len(cards):03d}',
                            'question': f'{term}とは何ですか？',
                            'answer': definition,
                            'type': 'definition',
                            'subject': 'chemistry',
                            'chapter': self._extract_chapter(text),
                            'page': page_num,
                            'difficulty': 1,
                            'tags': ['定義', term[:20]],
                            'reviewCount': 0,
                            'correctCount': 0,
                            'confidence': 0
                        })
        
        # 公式カード生成
        for pattern in patterns['formula']:
            for match in re.finditer(pattern, text):
                formula = match.group(1).strip()
                if 10 < len(formula) < 100:  # 適切な長さ
                    cards.append({
                        'id': f'uch_{page_num:04d}_{len(cards):03d}',
                        'question': 'この式の意味を説明してください',
                        'answer': self._format_formula(formula),
                        'type': 'formula',
                        'subject': 'chemistry',
                        'chapter': self._extract_chapter(text),
                        'page': page_num,
                        'difficulty': 2,
                        'tags': ['公式'],
                        'reviewCount': 0,
                        'correctCount': 0,
                        'confidence': 0
                    })
        
        # 重要ポイントカード
        for pattern in patterns['important']:
            for match in re.finditer(pattern, text):
                point = match.group(1).strip()
                if 20 < len(point) < 200:
                    cards.append({
                        'id': f'uch_{page_num:04d}_{len(cards):03d}',
                        'question': 'このポイントを説明してください',
                        'answer': point,
                        'type': 'quick',
                        'subject': 'chemistry',
                        'chapter': self._extract_chapter(text),
                        'page': page_num,
                        'difficulty': 2,
                        'tags': ['重要', 'ポイント'],
                        'reviewCount': 0,
                        'correctCount': 0,
                        'confidence': 0
                    })
        
        return cards
    
    def _extract_chapter(self, text: str) -> str:
        """章タイトルを抽出"""
        chapter_match = re.search(r'第(\d+)章[：:]\s*([^\n]+)', text)
        if chapter_match:
            return f"第{chapter_match.group(1)}章 {chapter_match.group(2).strip()}"
        
        # 見出しパターン
        heading_match = re.search(r'■\s*([^■\n]+)', text)
        if heading_match:
            return heading_match.group(1).strip()[:30]
        
        return "一般"
    
    def _format_formula(self, formula: str) -> str:
        """化学式・数式の整形"""
        # 基本的な置換
        replacements = {
            '->': '→',
            '=>': '→',
            '<=': '⇄',
            '<->': '⇄',
            'H2O': 'H₂O',
            'CO2': 'CO₂',
            'O2': 'O₂',
            'H2': 'H₂',
            'N2': 'N₂',
            'NH3': 'NH₃',
            'H2SO4': 'H₂SO₄',
            'HCl': 'HCl',
            'NaOH': 'NaOH',
            'H+': 'H⁺',
            'OH-': 'OH⁻',
            'e-': 'e⁻',
        }
        
        for old, new in replacements.items():
            formula = formula.replace(old, new)
        
        return formula
    
    def process_pdf(self, batch_size: int = 50):
        """PDF全体をバッチ処理"""
        logger.info(f"PDF処理開始: {self.pdf_path.name}")
        
        # PDFの総ページ数を取得
        with fitz.open(self.pdf_path) as doc:
            total_pages = len(doc)
            if self.max_pages:
                total_pages = min(total_pages, self.max_pages)
        
        logger.info(f"総ページ数: {total_pages}")
        
        # バッチ処理
        all_cards = []
        for start_page in range(0, total_pages, batch_size):
            pages_data = self.extract_pages(start_page, batch_size)
            
            for page_data in pages_data:
                text = page_data['text']
                page_num = page_data['page']
                
                # カード抽出
                cards = self.extract_cards_from_text(text, page_num)
                all_cards.extend(cards)
                
                # 画像付きカード
                if page_data['images']:
                    for img_path in page_data['images'][:1]:
                        all_cards.append({
                            'id': f'uch_{page_num:04d}_img',
                            'question': 'この図が示している内容を説明してください',
                            'answer': '図を参照して理解してください',
                            'type': 'graph',
                            'image_path': img_path,
                            'subject': 'chemistry',
                            'page': page_num,
                            'difficulty': 2,
                            'tags': ['図解'],
                            'reviewCount': 0,
                            'correctCount': 0,
                            'confidence': 0
                        })
            
            logger.info(f"ページ {start_page+1}-{min(start_page+batch_size, total_pages)} 処理完了: {len(all_cards)}枚のカード")
        
        self.cards = all_cards
        return all_cards
    
    def save_results(self):
        """結果を保存"""
        output_file = self.output_dir / f"{self.pdf_path.stem}_cards.json"
        
        data = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'source_pdf': self.pdf_path.name,
                'totalCards': len(self.cards),
                'version': '2.0'
            },
            'cards': self.cards
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"結果を保存: {output_file}")
        logger.info(f"総カード数: {len(self.cards)}")
        
        # サマリー作成
        self.create_summary()
        
        return output_file
    
    def create_summary(self):
        """処理サマリーを作成"""
        from collections import Counter
        
        summary_lines = [
            f"=== 抽出結果サマリー ===",
            f"PDF: {self.pdf_path.name}",
            f"総カード数: {len(self.cards)}",
            ""
        ]
        
        # タイプ別集計
        types = Counter(card['type'] for card in self.cards)
        summary_lines.append("タイプ別:")
        for card_type, count in types.most_common():
            summary_lines.append(f"  {card_type}: {count}枚")
        
        # ページ範囲
        if self.cards:
            pages = [card['page'] for card in self.cards]
            summary_lines.append(f"\nページ範囲: {min(pages)} - {max(pages)}")
        
        summary = '\n'.join(summary_lines)
        print(summary)
        
        # ファイルにも保存
        summary_file = self.output_dir / "summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)

def main():
    """メイン処理"""
    # 理論化学PDFを処理
    pdf_path = Path("/home/mochi/uchuichi-app/PDF/宇宙一わかりやすい化学（理論）/【理論・化学】宇宙一わかりやすい化学.pdf")
    output_dir = Path("/home/mochi/uchuichi-app/pdf-extractor/output_uchuichi")
    
    # 抽出実行（最初の50ページのみテスト）
    extractor = UchuichiExtractor(pdf_path, output_dir, max_pages=50)
    cards = extractor.process_pdf(batch_size=10)
    
    # 結果保存
    output_file = extractor.save_results()
    
    print(f"\n✅ 処理完了！")
    print(f"出力: {output_file}")

if __name__ == "__main__":
    main()