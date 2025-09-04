#!/usr/bin/env python3
"""
テキストファイルからフラッシュカード生成（テスト用）
"""

import json
import re
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextToCards:
    """テキストからフラッシュカード生成"""
    
    def __init__(self, text_path: Path, output_dir: Path):
        self.text_path = text_path
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cards = []
        
        # パターン定義
        self.patterns = {
            'definition': r'([^：:。]+?)とは([^。]+?)(?:である|です)',
            'formula': r'(?:式|公式|関係式)[：:]\s*(.+)',
            'important': r'(?:重要|ポイント|覚える)[：:！]\s*(.+)',
            'caution': r'(?:注意|気をつけ|間違い|典型的な間違い)[：:！]\s*(.+)',
            'example': r'(?:例題|例|問題)\s*\d*[：:]\s*(.+)',
            'procedure': r'(?:手順|ステップ)[：:]\s*(.+)',
        }
    
    def process_text(self):
        """テキストファイルを処理"""
        with open(self.text_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # セクションごとに分割
        sections = self.extract_sections(text)
        
        for section in sections:
            cards = self.create_cards_from_section(section)
            self.cards.extend(cards)
        
        logger.info(f"生成されたカード数: {len(self.cards)}")
        return self.cards
    
    def extract_sections(self, text: str) -> List[Dict]:
        """テキストをセクションに分割"""
        sections = []
        
        # 章・節で分割
        chapter_pattern = r'(第[0-9一二三四五六七八九十]+[章節]|\n\d+\.)'
        parts = re.split(f'({chapter_pattern})', text)
        
        current_title = ""
        for i in range(1, len(parts), 2):
            if i < len(parts) - 1:
                title = parts[i].strip()
                content = parts[i + 1].strip()
                
                sections.append({
                    'title': title,
                    'content': content
                })
        
        return sections
    
    def create_cards_from_section(self, section: Dict) -> List[Dict]:
        """セクションからカードを生成"""
        cards = []
        content = section['content']
        card_id_base = len(self.cards)
        
        # 定義の抽出
        for match in re.finditer(self.patterns['definition'], content):
            term = match.group(1).strip()
            definition = match.group(2).strip()
            
            cards.append({
                'id': f'text_{card_id_base + len(cards):04d}',
                'subject': '化学',
                'chapter': section['title'],
                'type': 'quick',
                'question': f'{term}とは何ですか？',
                'answer': definition,
                'original_text': match.group(0),
                'tags': ['定義', term],
                'difficulty': 1,
                'reviewCount': 0,
                'correctCount': 0,
                'confidence': 0
            })
            logger.info(f"定義カード作成: {term}")
        
        # 公式の抽出
        for match in re.finditer(self.patterns['formula'], content):
            formula = match.group(1).strip()
            
            # 化学式の整形
            formula = self.format_formula(formula)
            
            cards.append({
                'id': f'text_{card_id_base + len(cards):04d}',
                'subject': '化学',
                'chapter': section['title'],
                'type': 'formula',
                'question': 'この式の意味を説明してください',
                'answer': formula,
                'original_text': match.group(0),
                'tags': ['公式'],
                'difficulty': 2,
                'reviewCount': 0,
                'correctCount': 0,
                'confidence': 0
            })
        
        # 重要ポイントの抽出
        for match in re.finditer(self.patterns['important'], content):
            point = match.group(1).strip()
            
            cards.append({
                'id': f'text_{card_id_base + len(cards):04d}',
                'subject': '化学',
                'chapter': section['title'],
                'type': 'quick',
                'question': 'このポイントについて説明してください',
                'answer': point,
                'tags': ['重要', 'ポイント'],
                'difficulty': 2,
                'reviewCount': 0,
                'correctCount': 0,
                'confidence': 0
            })
        
        # 注意事項（典型ミス）の抽出
        for match in re.finditer(self.patterns['caution'], content):
            caution = match.group(1).strip()
            
            cards.append({
                'id': f'text_{card_id_base + len(cards):04d}',
                'subject': '化学',
                'chapter': section['title'],
                'type': 'quick',
                'question': 'この内容で注意すべき点は？',
                'answer': caution,
                'misconceptions': [caution],
                'tags': ['注意', '典型ミス'],
                'difficulty': 3,
                'reviewCount': 0,
                'correctCount': 0,
                'confidence': 0
            })
        
        # 例題の抽出
        example_matches = re.finditer(self.patterns['example'], content)
        for match in example_matches:
            example = match.group(1).strip()
            
            # 例題の後の解答部分を探す
            start = match.end()
            end = start + 500  # 次の500文字を確認
            answer_text = content[start:min(end, len(content))]
            
            cards.append({
                'id': f'text_{card_id_base + len(cards):04d}',
                'subject': '化学',
                'chapter': section['title'],
                'type': 'application',
                'question': example,
                'answer': answer_text[:200] if answer_text else '解答を確認してください',
                'tags': ['例題', '応用'],
                'difficulty': 3,
                'reviewCount': 0,
                'correctCount': 0,
                'confidence': 0
            })
        
        # pH計算などの手順がある場合
        if '手順' in content or 'ステップ' in content:
            # 手順を番号付きリストとして抽出
            step_pattern = r'(\d+)\.\s*(.+?)(?=\d+\.|$)'
            steps = re.findall(step_pattern, content, re.DOTALL)
            
            if steps:
                step_list = [f"{num}. {text.strip()}" for num, text in steps]
                cards.append({
                    'id': f'text_{card_id_base + len(cards):04d}',
                    'subject': '化学',
                    'chapter': section['title'],
                    'type': 'process',
                    'question': 'この計算の手順を説明してください',
                    'answer': '\n'.join(step_list),
                    'tags': ['手順', 'プロセス'],
                    'difficulty': 3,
                    'reviewCount': 0,
                    'correctCount': 0,
                    'confidence': 0
                })
        
        return cards
    
    def format_formula(self, formula: str) -> str:
        """化学式を整形"""
        # 簡単な下付き文字変換
        replacements = {
            'H2O': 'H₂O',
            'H3O': 'H₃O',
            'CO2': 'CO₂',
            'H2': 'H₂',
            'O2': 'O₂',
            'N2': 'N₂',
            'H+': 'H⁺',
            'OH-': 'OH⁻',
            'Cl-': 'Cl⁻',
            'A-': 'A⁻',
            '->': '→',
            '=>': '→',
            '<=': '⇄',
            '<->': '⇄',
        }
        
        for old, new in replacements.items():
            formula = formula.replace(old, new)
        
        return formula
    
    def save_cards(self):
        """カードをJSON形式で保存"""
        output_path = self.output_dir / 'extracted_cards.json'
        
        data = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'source': str(self.text_path),
                'totalCards': len(self.cards),
                'chemistryCards': len([c for c in self.cards if c['subject'] == '化学']),
                'physicsCards': 0,
                'version': '1.0'
            },
            'cards': self.cards
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"カードを保存しました: {output_path}")
        return output_path
    
    def create_summary(self):
        """抽出結果のサマリーを作成"""
        summary = []
        summary.append("=== カード抽出結果 ===")
        summary.append(f"総カード数: {len(self.cards)}")
        
        # タイプ別集計
        from collections import Counter
        types = Counter(card['type'] for card in self.cards)
        summary.append("\nタイプ別:")
        for card_type, count in types.items():
            summary.append(f"  {card_type}: {count}枚")
        
        # 章別集計
        chapters = Counter(card['chapter'] for card in self.cards)
        summary.append("\n章別:")
        for chapter, count in chapters.items():
            summary.append(f"  {chapter}: {count}枚")
        
        # 難易度別集計
        difficulties = Counter(card['difficulty'] for card in self.cards)
        summary.append("\n難易度別:")
        for diff, count in sorted(difficulties.items()):
            summary.append(f"  レベル{diff}: {count}枚")
        
        return "\n".join(summary)

def main():
    """メイン処理"""
    text_path = Path('/home/mochi/uchuichi-app/pdf-extractor/sample_text.txt')
    output_dir = Path('/home/mochi/uchuichi-app/pdf-extractor/output')
    
    # 抽出実行
    extractor = TextToCards(text_path, output_dir)
    cards = extractor.process_text()
    
    # 保存
    output_path = extractor.save_cards()
    
    # サマリー表示
    summary = extractor.create_summary()
    print(summary)
    
    # 最初の3枚を表示
    print("\n=== サンプルカード ===")
    for card in cards[:3]:
        print(f"\nID: {card['id']}")
        print(f"Q: {card['question']}")
        print(f"A: {card['answer'][:100]}...")

if __name__ == "__main__":
    main()