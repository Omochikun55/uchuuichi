#!/usr/bin/env python3
"""
化学カードデータのクレンジングスクリプト
OCRノイズ除去、表記正規化、重複検出、タイプ正規化を行う
"""

import json
import re
from typing import Dict, List, Any
from collections import defaultdict
import unicodedata

class ChemistryCardCleaner:
    """化学カードのクレンジング処理"""
    
    def __init__(self):
        # OCRノイズ修正テーブル
        self.ocr_replacements = {
            # 化学式の一般的なOCRエラー
            'H20': 'H₂O', 'H2O': 'H₂O',
            '02': 'O₂', 'O2': 'O₂',
            'C02': 'CO₂', 'CO2': 'CO₂',
            'S02': 'SO₂', 'SO2': 'SO₂',
            'N02': 'NO₂', 'NO2': 'NO₂',
            'NH3': 'NH₃',
            'H2S04': 'H₂SO₄', 'H2SO4': 'H₂SO₄',
            'HN03': 'HNO₃', 'HNO3': 'HNO₃',
            'NaCi': 'NaCl', 'NaCI': 'NaCl',
            'HCi': 'HCl', 'HCI': 'HCl',
            'CaC03': 'CaCO₃', 'CaCO3': 'CaCO₃',
            'Ag+': 'Ag⁺',
            'Na+': 'Na⁺',
            'H+': 'H⁺',
            'OH-': 'OH⁻',
            'Cl-': 'Cl⁻',
            
            # よくある文字化け
            '′': "'",
            '，': ',',
            '．': '.',
            '：': ':',
            '；': ';',
            '％': '%',
            '℃': '°C',
            
            # ローマ数字のIとlの混同
            'HCl': 'HCl',  # 塩酸
            'NaCl': 'NaCl', # 塩化ナトリウム
            
            # rnとmの混同（OCRでよくある）
            'rnol': 'mol',
            'rnL': 'mL',
            
            # 全角を半角に
            '０': '0', '１': '1', '２': '2', '３': '3', '４': '4',
            '５': '5', '６': '6', '７': '7', '８': '8', '９': '9',
        }
        
        # 数式・LaTeX変換パターン
        self.math_patterns = [
            (r'pH\s*=\s*-?\s*log\s*\[?H\+\]?', r'pH = -\\log[\\mathrm{H^+}]'),
            (r'pOH\s*=\s*-?\s*log\s*\[?OH-\]?', r'pOH = -\\log[\\mathrm{OH^-}]'),
            (r'Ka\s*=\s*', r'K_a = '),
            (r'Kb\s*=\s*', r'K_b = '),
            (r'Kw\s*=\s*', r'K_w = '),
            (r'Ksp\s*=\s*', r'K_{sp} = '),
            (r'PV\s*=\s*nRT', r'PV = nRT'),
            (r'ΔH', r'\\Delta H'),
            (r'ΔG', r'\\Delta G'),
            (r'ΔS', r'\\Delta S'),
        ]
        
        # タイプマッピング（既存type → 新type）
        self.type_mapping = {
            'definition': 'quick',
            'formula': 'quick',
            'application': 'decision',
            'separation': 'process',
            'calculation': 'process',
            'theory': 'quick',
            'law': 'quick',
            'structure': 'quick',
        }
        
        # 章別の条件・典型ミステンプレート
        self.chapter_templates = {
            '酸と塩基': {
                'conditions': ['希薄水溶液', '25°C', '活量係数≈1'],
                'misconceptions': ['pH + pOH = 14を忘れる', '対数計算のミス', '近似条件の適用ミス']
            },
            '酸化還元': {
                'conditions': ['標準状態', '電子の出入りを明確に'],
                'misconceptions': ['酸化数の計算ミス', '半反応式の電子数不一致', '係数の調整ミス']
            },
            '気体の性質': {
                'conditions': ['理想気体近似', '温度・圧力一定'],
                'misconceptions': ['単位変換ミス', 'R値の選択ミス', '絶対温度への変換忘れ']
            },
            '化学平衡': {
                'conditions': ['平衡状態', '温度一定'],
                'misconceptions': ['平衡定数の定義ミス', 'ルシャトリエの原理の誤適用', '濃度と分圧の混同']
            },
            '熱化学': {
                'conditions': ['標準状態（25°C, 1atm）', '定圧条件'],
                'misconceptions': ['発熱・吸熱の符号ミス', 'ヘスの法則の適用ミス', '単位換算ミス']
            },
            '有機化学': {
                'conditions': ['常温常圧', '水溶液中'],
                'misconceptions': ['異性体の見落とし', '反応機構の理解不足', '官能基の特定ミス']
            },
            '無機化学': {
                'conditions': ['標準状態', '水溶液中'],
                'misconceptions': ['沈殿の色の暗記ミス', 'イオン反応式のミス', '錯イオンの構造ミス']
            }
        }
    
    def clean_text(self, text: str) -> str:
        """テキストのクレンジング"""
        if not text:
            return text
            
        # OCRノイズの修正
        for old, new in self.ocr_replacements.items():
            text = text.replace(old, new)
        
        # 余分な空白の正規化
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # 変な記号の除去
        text = re.sub(r'[′′`]', "'", text)
        text = re.sub(r'["""]', '"', text)
        
        # 全角英数字を半角に変換（化学式以外）
        text = unicodedata.normalize('NFKC', text)
        
        return text
    
    def apply_math_formatting(self, text: str) -> str:
        """数式のLaTeX形式への変換"""
        for pattern, replacement in self.math_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text
    
    def normalize_card_type(self, card: Dict) -> str:
        """カードタイプの正規化"""
        current_type = card.get('type', 'quick')
        
        # 既存のタイプマッピング
        if current_type in self.type_mapping:
            return self.type_mapping[current_type]
        
        # 質問文からタイプを推定
        question = card.get('question', '').lower()
        
        if any(word in question for word in ['手順', 'ステップ', '方法', '作り方']):
            return 'process'
        elif any(word in question for word in ['選べ', '選択', 'どれ', 'どちら']):
            return 'decision'
        elif any(word in question for word in ['計算', '求めよ', '算出']):
            return 'process'
        else:
            return 'quick'
    
    def add_chapter_metadata(self, card: Dict) -> Dict:
        """章に応じた条件・典型ミスを追加"""
        chapter = card.get('chapter', '')
        
        # デフォルト値
        if 'conditions' not in card:
            card['conditions'] = []
        if 'misconceptions' not in card:
            card['misconceptions'] = []
        
        # 章別テンプレートから追加
        for template_chapter, metadata in self.chapter_templates.items():
            if template_chapter in chapter or chapter in template_chapter:
                if not card['conditions']:
                    card['conditions'] = metadata['conditions']
                if not card['misconceptions']:
                    card['misconceptions'] = metadata['misconceptions']
                break
        
        return card
    
    def detect_duplicates(self, cards: List[Dict]) -> List[Dict]:
        """重複カードの検出と統合"""
        seen_questions = defaultdict(list)
        
        for card in cards:
            # 正規化した質問文でグルーピング
            normalized_q = self.clean_text(card.get('question', '')).lower()
            normalized_q = re.sub(r'[、。？！\s]+', '', normalized_q)
            seen_questions[normalized_q].append(card)
        
        # 重複を統合
        unique_cards = []
        for normalized_q, card_group in seen_questions.items():
            if len(card_group) == 1:
                unique_cards.append(card_group[0])
            else:
                # 最も完全な情報を持つカードを選択
                best_card = max(card_group, key=lambda c: len(c.get('answer', '')))
                best_card['duplicate_count'] = len(card_group)
                unique_cards.append(best_card)
        
        return unique_cards
    
    def clean_card(self, card: Dict) -> Dict:
        """個別カードのクレンジング"""
        # テキストフィールドのクレンジング
        if 'question' in card:
            card['question'] = self.clean_text(card['question'])
            card['question'] = self.apply_math_formatting(card['question'])
        
        if 'answer' in card:
            card['answer'] = self.clean_text(card['answer'])
            card['answer'] = self.apply_math_formatting(card['answer'])
        
        # タイプの正規化
        card['type'] = self.normalize_card_type(card)
        
        # 章別メタデータの追加
        card = self.add_chapter_metadata(card)
        
        # タグのクレンジング
        if 'tags' in card and isinstance(card['tags'], list):
            card['tags'] = [self.clean_text(tag) for tag in card['tags']]
            # 重複タグの除去
            card['tags'] = list(dict.fromkeys(card['tags']))
        
        return card
    
    def process_file(self, input_file: str, output_file: str):
        """ファイル全体の処理"""
        print(f"Loading {input_file}...")
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cards = data.get('cards', [])
        print(f"Found {len(cards)} cards")
        
        # 各カードをクレンジング
        print("Cleaning cards...")
        cleaned_cards = [self.clean_card(card) for card in cards]
        
        # 重複検出と統合
        print("Detecting duplicates...")
        unique_cards = self.detect_duplicates(cleaned_cards)
        print(f"Reduced to {len(unique_cards)} unique cards")
        
        # 統計情報
        type_counts = defaultdict(int)
        chapter_counts = defaultdict(int)
        
        for card in unique_cards:
            type_counts[card.get('type', 'unknown')] += 1
            chapter_counts[card.get('chapter', 'unknown')] += 1
        
        print("\n=== Statistics ===")
        print("Card Types:")
        for card_type, count in sorted(type_counts.items()):
            print(f"  {card_type}: {count}")
        
        print("\nChapters:")
        for chapter, count in sorted(chapter_counts.items()):
            print(f"  {chapter}: {count}")
        
        # 保存
        output_data = {
            'version': '2.0',
            'total_cards': len(unique_cards),
            'cards': unique_cards,
            'metadata': {
                'cleaned': True,
                'type_distribution': dict(type_counts),
                'chapter_distribution': dict(chapter_counts)
            }
        }
        
        print(f"\nSaving to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print("Done!")
        
        # サンプル出力
        print("\n=== Sample Cleaned Cards (first 3) ===")
        for i, card in enumerate(unique_cards[:3]):
            print(f"\nCard {i+1}:")
            print(f"  Q: {card.get('question', 'N/A')}")
            print(f"  A: {card.get('answer', 'N/A')[:100]}...")
            print(f"  Type: {card.get('type', 'N/A')}")
            if card.get('conditions'):
                print(f"  Conditions: {card['conditions']}")
            if card.get('misconceptions'):
                print(f"  Misconceptions: {card['misconceptions']}")

if __name__ == '__main__':
    cleaner = ChemistryCardCleaner()
    cleaner.process_file(
        'public/learning-data.json',
        'public/learning-data-v2.json'
    )