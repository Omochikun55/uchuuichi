#!/usr/bin/env python3
"""
宇宙一PDFから抽出したカードをアプリに統合
品質フィルタリング付き
"""

import json
from pathlib import Path
import re

def clean_card(card):
    """カードのクリーンアップ"""
    # 質問と回答のクリーニング
    card['question'] = clean_text(card['question'])
    card['answer'] = clean_text(card['answer'])
    
    # 無効なカードをフィルタ
    if len(card['question']) < 10 or len(card['answer']) < 5:
        return None
    
    # 改行や不要な文字の削除
    if 'Chapter' in card['question'] or 'じめに' in card['answer']:
        return None
    
    return card

def clean_text(text):
    """テキストのクリーニング"""
    # 不要な改行を削除
    text = re.sub(r'\n+', ' ', text)
    # 連続スペースを単一スペースに
    text = re.sub(r'\s+', ' ', text)
    # 前後の空白を削除
    text = text.strip()
    # 長すぎる場合はトリム
    if len(text) > 200:
        text = text[:197] + '...'
    return text

def merge_cards():
    # ファイルパス
    app_data_path = Path('/home/mochi/uchuichi-app/public/learning-data.json')
    uchuichi_cards_path = Path('/home/mochi/uchuichi-app/pdf-extractor/output_uchuichi/【理論・化学】宇宙一わかりやすい化学_cards.json')
    
    # 既存データ読み込み
    with open(app_data_path, 'r', encoding='utf-8') as f:
        app_data = json.load(f)
    
    # 抽出カード読み込み
    with open(uchuichi_cards_path, 'r', encoding='utf-8') as f:
        uchuichi_data = json.load(f)
    
    # 品質の高いカードのみを選別
    good_cards = []
    for card in uchuichi_data['cards']:
        # クリーニング
        cleaned = clean_card(card)
        if cleaned:
            # 重複チェック（簡易版）
            is_duplicate = False
            for existing in app_data['cards']:
                if cleaned['question'][:30] == existing.get('question', '')[:30]:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                # アプリ形式に変換
                formatted_card = {
                    'id': f"uch_{cleaned['id']}",
                    'question': cleaned['question'],
                    'answer': cleaned['answer'],
                    'type': cleaned.get('type', 'definition'),
                    'difficulty': cleaned.get('difficulty', 2),
                    'subject': 'chemistry',
                    'chapter': cleaned.get('chapter', '理論化学'),
                    'page': cleaned.get('page', 1),
                    'reviewCount': 0,
                    'correctCount': 0,
                    'confidence': 0,
                    'tags': cleaned.get('tags', [])
                }
                
                # 画像がある場合
                if 'image_path' in cleaned:
                    formatted_card['image_path'] = cleaned['image_path']
                
                good_cards.append(formatted_card)
    
    # 特に品質の高いカード（definition, formulaタイプ）を優先
    priority_cards = [c for c in good_cards if c['type'] in ['definition', 'formula']]
    other_cards = [c for c in good_cards if c['type'] not in ['definition', 'formula']]
    
    # 最大50枚まで追加（品質重視）
    cards_to_add = (priority_cards[:30] + other_cards[:20])[:50]
    
    # 既存データに追加
    print(f"追加前のカード数: {len(app_data['cards'])}")
    app_data['cards'].extend(cards_to_add)
    
    # メタデータ更新
    app_data['metadata']['totalCards'] = len(app_data['cards'])
    app_data['metadata']['chemistryCards'] = len([c for c in app_data['cards'] if c.get('subject') == 'chemistry'])
    app_data['metadata']['physicsCards'] = len([c for c in app_data['cards'] if c.get('subject') == 'physics'])
    
    # 保存
    with open(app_data_path, 'w', encoding='utf-8') as f:
        json.dump(app_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(cards_to_add)}枚の高品質カードを追加しました")
    print(f"追加後の総カード数: {app_data['metadata']['totalCards']}")
    
    # 追加したカードのサンプル表示
    print("\n追加したカードの例:")
    for card in cards_to_add[:3]:
        print(f"- Q: {card['question'][:50]}...")
        print(f"  A: {card['answer'][:50]}...")
    
    return len(cards_to_add)

if __name__ == "__main__":
    merge_cards()