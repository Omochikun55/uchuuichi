#!/usr/bin/env python3
"""
Claude APIを使った高品質カード生成
原文活用＋図表対応版
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
import anthropic
from dotenv import load_dotenv
import logging
from extract_cards import ChemistryPDFExtractor, FlashCard

# 環境変数読み込み
load_dotenv()

logger = logging.getLogger(__name__)

class EnhancedExtractor(ChemistryPDFExtractor):
    """Claude APIを使った拡張版抽出器"""
    
    def __init__(self, pdf_path: Path, output_dir: Path):
        super().__init__(pdf_path, output_dir)
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    
    def process_with_claude(self, section_text: str, page_num: int, images: List[str] = None) -> List[FlashCard]:
        """Claude APIでセクションを高品質カードに変換"""
        
        prompt = f"""
あなたは「宇宙一わかりやすい化学」の内容を学習カードに変換する専門家です。

【重要な方針】
1. 原文の優れた説明はそのまま活用してOK
2. 化学式・反応式は正確性重視で原文を使用
3. 図表がある場合は積極的に参照
4. 「宇宙一」の特徴的な説明や例えは保持

【入力テキスト】
{section_text}

【ページ番号】
{page_num}

【画像】
{f"画像ファイル: {', '.join(images)}" if images else "なし"}

【出力形式】
以下のJSON配列形式でカードを生成してください：

[
  {{
    "type": "quick",
    "question": "質問文（120文字以内）",
    "answer": "回答文（原文活用OK）",
    "hint": "ヒント（任意）",
    "misconceptions": ["よくある間違い"],
    "tags": ["タグ1", "タグ2"],
    "level": 1
  }},
  {{
    "type": "decision",
    "prompt": "問題提起",
    "choices": ["選択肢1", "選択肢2", "選択肢3"],
    "answer_index": 0,
    "why": "理由の説明"
  }}
]

【カード生成のポイント】
- 定義や重要な説明は原文をそのまま使用可
- 化学式は正確に記述（H₂O, CO₂など）
- 1セクションから3-5枚のカードを生成
- 図表参照がある場合は "image_ref": true を追加

JSON配列のみを出力してください。
"""
        
        try:
            message = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # レスポンスからJSON部分を抽出
            response_text = message.content[0].text
            
            # JSON部分を見つける
            import re
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            if json_match:
                cards_data = json.loads(json_match.group())
                
                # FlashCardオブジェクトに変換
                cards = []
                for i, card_data in enumerate(cards_data):
                    # 共通フィールド
                    base_fields = {
                        'id': f"chem_{page_num:03d}_{i:03d}_claude",
                        'subject': "化学",
                        'chapter': "",
                        'source_page': page_num
                    }
                    
                    if card_data['type'] == 'quick':
                        card = FlashCard(
                            **base_fields,
                            type="quick",
                            topic=card_data.get('topic', '一般'),
                            question=card_data['question'],
                            answer=card_data['answer'],
                            hint=card_data.get('hint'),
                            misconceptions=card_data.get('misconceptions'),
                            tags=card_data.get('tags', []),
                            level=card_data.get('level', 1),
                            image_path=images[0] if images and card_data.get('image_ref') else None
                        )
                        cards.append(card)
                    
                    elif card_data['type'] == 'decision':
                        # decisionタイプの処理
                        choices_str = json.dumps(card_data.get('choices', []), ensure_ascii=False)
                        card = FlashCard(
                            **base_fields,
                            type="decision",
                            topic="原理選択",
                            question=card_data['prompt'],
                            answer=f"正解: {card_data['choices'][card_data['answer_index']]} - {card_data.get('why', '')}",
                            tags=card_data.get('tags', ['decision']),
                            level=card_data.get('level', 2)
                        )
                        cards.append(card)
                
                logger.info(f"Claude APIで{len(cards)}枚のカードを生成")
                return cards
            else:
                logger.warning("JSONを抽出できませんでした")
                return []
                
        except Exception as e:
            logger.error(f"Claude API エラー: {e}")
            return []
    
    def process_pdf_with_claude(self) -> List[FlashCard]:
        """PDF全体をClaudeで処理（ハイブリッド方式）"""
        pages_data = self.extract_text_and_images()
        
        for page_data in pages_data[:10]:  # 最初の10ページをテスト
            page_num = page_data['page']
            text = page_data['text']
            images = page_data['images']
            
            # まずルールベースで基本カードを抽出
            sections = self.extract_sections(text)
            for section in sections:
                # 基本カード（ルールベース）
                basic_cards = self.create_cards_from_section(section, page_num, images)
                self.cards.extend(basic_cards)
                
                # セクションが十分な内容を持つ場合、Claudeで高品質カードを生成
                section_text = '\n'.join(section['content'])
                if len(section_text) > 200:  # 200文字以上の場合
                    claude_cards = self.process_with_claude(section_text, page_num, images)
                    self.cards.extend(claude_cards)
        
        # 重複除去
        self.remove_duplicates()
        
        logger.info(f"総カード数（重複除去後）: {len(self.cards)}")
        return self.cards
    
    def remove_duplicates(self):
        """重複カードを除去"""
        seen_questions = set()
        unique_cards = []
        
        for card in self.cards:
            if card.question not in seen_questions:
                seen_questions.add(card.question)
                unique_cards.append(card)
            else:
                logger.debug(f"重複カードを除去: {card.question[:30]}...")
        
        self.cards = unique_cards
    
    def validate_cards(self) -> Dict[str, Any]:
        """カードの品質を検証"""
        stats = {
            'total': len(self.cards),
            'by_type': {},
            'warnings': [],
            'quality_score': 0
        }
        
        from collections import Counter
        type_counts = Counter(card.type for card in self.cards)
        stats['by_type'] = dict(type_counts)
        
        # 品質チェック
        for card in self.cards:
            # 質問文の長さチェック
            if len(card.question) > 120:
                stats['warnings'].append(f"質問文が長すぎる: {card.id}")
            
            # 回答文の長さチェック
            if len(card.answer) > 200:
                stats['warnings'].append(f"回答文が長すぎる: {card.id}")
            
            # misconceptionsの存在チェック（加点）
            if card.misconceptions:
                stats['quality_score'] += 1
            
            # 画像参照の適切性
            if card.image_path and card.type != 'graph':
                stats['warnings'].append(f"画像参照が不適切: {card.id}")
        
        # 品質スコア計算（0-100）
        if stats['total'] > 0:
            stats['quality_score'] = int(
                (stats['quality_score'] / stats['total']) * 100
            )
        
        return stats

def main():
    """メイン処理"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PDFからフラッシュカードを生成')
    parser.add_argument('pdf_path', help='入力PDFファイルのパス')
    parser.add_argument('--output', default='output', help='出力ディレクトリ')
    parser.add_argument('--use-claude', action='store_true', help='Claude APIを使用')
    parser.add_argument('--max-pages', type=int, help='処理する最大ページ数')
    
    args = parser.parse_args()
    
    pdf_path = Path(args.pdf_path)
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    
    if args.use_claude:
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("エラー: ANTHROPIC_API_KEYが設定されていません")
            return
        
        print("Claude APIを使用した高品質抽出を開始...")
        extractor = EnhancedExtractor(pdf_path, output_dir)
        cards = extractor.process_pdf_with_claude()
        
        # 品質検証
        stats = extractor.validate_cards()
        print(f"\n=== 品質レポート ===")
        print(f"総カード数: {stats['total']}")
        print(f"タイプ別: {stats['by_type']}")
        print(f"品質スコア: {stats['quality_score']}/100")
        if stats['warnings']:
            print(f"警告: {len(stats['warnings'])}件")
            for warning in stats['warnings'][:5]:
                print(f"  - {warning}")
    else:
        print("ルールベース抽出を開始...")
        extractor = ChemistryPDFExtractor(pdf_path, output_dir)
        cards = extractor.process_pdf()
    
    # 保存
    extractor.save_cards()
    extractor.create_review_html()
    
    print(f"\n✅ 完了！")
    print(f"カード: {output_dir}/cards.json")
    print(f"レビュー: {output_dir}/review.html")

if __name__ == "__main__":
    main()