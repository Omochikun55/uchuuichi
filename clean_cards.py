#!/usr/bin/env python3
"""
カードデータのクレンジング・正規化
OCRノイズ修正、型変換、LaTeX化、条件・ミス情報追加
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any

class CardCleaner:
    def __init__(self):
        # OCRノイズの置換表
        self.ocr_replacements = {
            # 化学式の誤認識
            'H20': 'H₂O', 'H2O': 'H₂O',
            '02': 'O₂', 'O2': 'O₂',
            'C02': 'CO₂', 'CO2': 'CO₂',
            'N2': 'N₂',
            'NH3': 'NH₃',
            'H2SO4': 'H₂SO₄',
            'NaCi': 'NaCl',
            'NaOH': 'NaOH',
            'HCl': 'HCl',
            'HNO3': 'HNO₃',
            'Ca(OH)2': 'Ca(OH)₂',
            'Al2O3': 'Al₂O₃',
            'Fe2O3': 'Fe₂O₃',
            'CaCO3': 'CaCO₃',
            'CH4': 'CH₄',
            'C2H4': 'C₂H₄',
            'C6H6': 'C₆H₆',
            
            # イオン
            'H+': 'H⁺',
            'OH-': 'OH⁻',
            'Na+': 'Na⁺',
            'Cl-': 'Cl⁻',
            'SO42-': 'SO₄²⁻',
            'NO3-': 'NO₃⁻',
            
            # 記号の正規化
            '′': '',
            '，': '、',
            '｡': '。',
            '→': '→',
            '⇄': '⇄',
            '℃': '°C',
        }
        
        # 章別の典型的な条件・ミスコンセプション
        self.chapter_conditions = {
            '理論化学': {
                'conditions': ['温度一定', '圧力一定', '理想気体として扱う'],
                'misconceptions': ['実在気体と理想気体の混同', '単位換算ミス', '有効数字の扱い']
            },
            '無機化学': {
                'conditions': ['標準状態', '水溶液中', '常温常圧'],
                'misconceptions': ['イオン化傾向の誤解', '沈殿の色の混同', '錯イオンの構造誤り']
            },
            '有機化学': {
                'conditions': ['触媒存在下', '加熱条件', '無水条件'],
                'misconceptions': ['構造異性体の見落とし', '反応機構の誤解', '官能基の反応性誤認']
            },
            '酸と塩基': {
                'conditions': ['希薄溶液', '25°C', '水溶液中'],
                'misconceptions': ['pHとpOHの関係誤解', '緩衝液の原理誤解', '電離度の計算ミス']
            },
            '酸化還元': {
                'conditions': ['標準電極電位', '酸性条件', '塩基性条件'],
                'misconceptions': ['酸化数の計算ミス', '半反応式の電子数不一致', 'イオン反応式の電荷不均衡']
            }
        }
        
        # カードタイプのマッピング
        self.type_mapping = {
            'definition': 'quick',
            'formula': 'quick',
            'application': 'process',
            'separation': 'decision',
            'quick': 'quick',
            'graph': 'graph',
        }
        
    def clean_text(self, text: str) -> str:
        """テキストのクリーニング"""
        if not text:
            return text
            
        # OCRノイズの修正
        for old, new in self.ocr_replacements.items():
            text = text.replace(old, new)
        
        # 不要な「とは何ですか？」パターンの除去
        text = re.sub(r'とは何ですか[？?]', 'は？', text)
        
        # 連続する空白を単一スペースに
        text = re.sub(r'\s+', ' ', text)
        
        # 前後の空白を削除
        text = text.strip()
        
        return text
    
    def to_latex(self, text: str) -> str:
        """数式をLaTeX形式に変換"""
        # pH式
        text = re.sub(r'pH\s*=\s*-?\s*log\s*\[?H\+?\]?', r'pH = -\\log[\\mathrm{H^+}]', text)
        
        # 平衡定数
        text = re.sub(r'K([awbc])', r'K_{\\1}', text)
        
        # 化学式の下付き文字（すでに変換済みのものはスキップ）
        # 例: H2O → H₂O（すでに処理済み）
        
        # 指数表記
        text = re.sub(r'10\^(-?\d+)', r'10^{\\1}', text)
        text = re.sub(r'(\d+)\s*×\s*10\^(-?\d+)', r'\\1 \\times 10^{\\2}', text)
        
        return text
    
    def determine_type(self, card: Dict) -> str:
        """カードタイプを決定"""
        question = card.get('question', '').lower()
        answer = card.get('answer', '')
        current_type = card.get('type', 'quick')
        
        # キーワードベースの判定
        if any(word in question for word in ['手順', 'ステップ', '方法', 'やり方']):
            return 'process'
        elif any(word in question for word in ['選べ', '選択', 'どちら', 'どれ']):
            return 'decision'
        elif 'グラフ' in question or 'graph' in current_type:
            return 'graph'
        elif any(word in question for word in ['単位', '次元']):
            return 'unit-dim'
        elif any(word in question for word in ['概算', '見積', 'オーダー']):
            return 'estimation'
        else:
            return self.type_mapping.get(current_type, 'quick')
    
    def add_metadata(self, card: Dict) -> Dict:
        """条件やミスコンセプションを追加"""
        chapter = card.get('chapter', '一般')
        
        # 章に応じた条件とミスコンセプションを追加
        if chapter in self.chapter_conditions:
            meta = self.chapter_conditions[chapter]
        else:
            # デフォルトの条件
            meta = {
                'conditions': ['標準状態'],
                'misconceptions': ['単位の取り違え', '有効数字の扱い']
            }
        
        # 既存の情報があれば保持
        if 'conditions' not in card:
            card['conditions'] = meta['conditions'][:2]  # 最大2つ
        if 'misconceptions' not in card:
            card['misconceptions'] = meta['misconceptions'][:2]  # 最大2つ
            
        return card
    
    def clean_card(self, card: Dict) -> Dict:
        """カード1枚をクリーニング"""
        # テキストフィールドのクリーニング
        if 'question' in card:
            card['question'] = self.clean_text(card['question'])
            card['question'] = self.to_latex(card['question'])
        
        if 'answer' in card:
            card['answer'] = self.clean_text(card['answer'])
            card['answer'] = self.to_latex(card['answer'])
        
        # タイプの正規化
        card['type'] = self.determine_type(card)
        
        # タグのクリーニングと正規化
        if 'tags' in card:
            card['tags'] = [self.clean_text(tag) for tag in card['tags'] if tag]
            # 最大5つに制限
            card['tags'] = card['tags'][:5]
        
        # 条件・ミスコンセプションの追加
        card = self.add_metadata(card)
        
        # ヒントフィールドの追加（短い要約）
        if 'hint' not in card and 'answer' in card:
            answer = card['answer']
            if len(answer) > 30:
                card['hint'] = answer[:30] + '...'
            else:
                card['hint'] = answer
        
        return card
    
    def remove_duplicates(self, cards: List[Dict]) -> List[Dict]:
        """重複カードの除去"""
        seen_questions = {}
        unique_cards = []
        
        for card in cards:
            q = card.get('question', '')
            # 質問文の最初の30文字で重複判定
            key = q[:30] if len(q) > 30 else q
            
            if key not in seen_questions:
                seen_questions[key] = True
                unique_cards.append(card)
            else:
                # 重複の場合、より完全な方を採用
                existing_idx = None
                for i, uc in enumerate(unique_cards):
                    if uc.get('question', '')[:30] == key:
                        existing_idx = i
                        break
                
                if existing_idx is not None:
                    # より多くの情報を持つ方を採用
                    existing_card = unique_cards[existing_idx]
                    if len(card.get('answer', '')) > len(existing_card.get('answer', '')):
                        unique_cards[existing_idx] = card
        
        return unique_cards
    
    def clean_dataset(self, input_path: Path, output_path: Path):
        """データセット全体をクリーニング"""
        print(f"読み込み中: {input_path}")
        
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        original_count = len(data['cards'])
        print(f"元のカード数: {original_count}")
        
        # 各カードをクリーニング
        cleaned_cards = []
        for i, card in enumerate(data['cards']):
            cleaned = self.clean_card(card)
            cleaned_cards.append(cleaned)
            
            if (i + 1) % 20 == 0:
                print(f"  処理中... {i+1}/{original_count}")
        
        # 重複除去
        cleaned_cards = self.remove_duplicates(cleaned_cards)
        
        # データ更新
        data['cards'] = cleaned_cards
        data['metadata']['totalCards'] = len(cleaned_cards)
        data['metadata']['version'] = '2.0'
        from datetime import datetime
        data['metadata']['cleanedAt'] = datetime.now().isoformat()
        
        # 保存
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ クリーニング完了")
        print(f"  元のカード数: {original_count}")
        print(f"  クリーニング後: {len(cleaned_cards)}")
        print(f"  削除された重複: {original_count - len(cleaned_cards)}")
        print(f"  出力: {output_path}")
        
        # サンプル表示
        print("\n📝 クリーニング例（最初の3枚）:")
        for card in cleaned_cards[:3]:
            print(f"\n[{card.get('type', 'unknown')}] {card.get('chapter', '')}") 
            print(f"  Q: {card.get('question', '')[:60]}...")
            print(f"  A: {card.get('answer', '')[:60]}...")
            if 'conditions' in card:
                print(f"  条件: {', '.join(card['conditions'])}")
            if 'misconceptions' in card:
                print(f"  典型ミス: {', '.join(card['misconceptions'][:1])}")

def main():
    cleaner = CardCleaner()
    
    input_path = Path('/home/mochi/uchuichi-app/public/learning-data.json')
    output_path = Path('/home/mochi/uchuichi-app/public/learning-data-v2.json')
    
    cleaner.clean_dataset(input_path, output_path)

if __name__ == "__main__":
    main()