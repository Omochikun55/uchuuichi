#!/usr/bin/env python3
"""
生成したカードを既存のアプリデータに統合
"""

import json
from pathlib import Path

def merge_cards():
    # ファイルパス
    app_data_path = Path('/home/mochi/uchuichi-app/public/learning-data.json')
    new_cards_path = Path('/home/mochi/uchuichi-app/pdf-extractor/output/extracted_cards.json')
    
    # 既存データ読み込み
    with open(app_data_path, 'r', encoding='utf-8') as f:
        app_data = json.load(f)
    
    # 新規カード読み込み
    with open(new_cards_path, 'r', encoding='utf-8') as f:
        new_data = json.load(f)
    
    # カードの統合（重複チェック付き）
    existing_ids = {card['id'] for card in app_data['cards']}
    new_cards_added = 0
    
    for new_card in new_data['cards']:
        # IDを調整（衝突回避）
        if new_card['id'] in existing_ids:
            new_card['id'] = f"pdf_{new_card['id']}"
        
        # フィールドの調整（アプリ形式に合わせる）
        formatted_card = {
            'id': new_card['id'],
            'question': new_card['question'],
            'answer': new_card['answer'],
            'type': new_card.get('type', 'definition'),
            'difficulty': new_card.get('difficulty', 2),
            'subject': new_card.get('subject', 'chemistry'),
            'chapter': new_card.get('chapter', '酸と塩基'),
            'page': new_card.get('page', 1),
            'reviewCount': new_card.get('reviewCount', 0),
            'correctCount': new_card.get('correctCount', 0),
            'confidence': new_card.get('confidence', 0),
            'tags': new_card.get('tags', [])
        }
        
        # misconceptionsがある場合は追加
        if 'misconceptions' in new_card:
            formatted_card['misconceptions'] = new_card['misconceptions']
        
        app_data['cards'].append(formatted_card)
        new_cards_added += 1
    
    # メタデータ更新
    app_data['metadata']['totalCards'] = len(app_data['cards'])
    app_data['metadata']['chemistryCards'] = len([c for c in app_data['cards'] if c.get('subject') == 'chemistry'])
    app_data['metadata']['physicsCards'] = len([c for c in app_data['cards'] if c.get('subject') == 'physics'])
    
    # 保存
    with open(app_data_path, 'w', encoding='utf-8') as f:
        json.dump(app_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {new_cards_added}枚の新規カードを追加しました")
    print(f"総カード数: {app_data['metadata']['totalCards']}")
    
    return new_cards_added

if __name__ == "__main__":
    merge_cards()