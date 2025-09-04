#!/usr/bin/env python3
"""
物理カードを削除して化学のみにする
"""

import json
from pathlib import Path

def remove_physics_cards():
    # ファイルパス
    data_path = Path('/home/mochi/uchuichi-app/public/learning-data.json')
    
    # データ読み込み
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 物理カードを除外
    original_count = len(data['cards'])
    chemistry_cards = [card for card in data['cards'] if card.get('subject') == 'chemistry']
    physics_cards = [card for card in data['cards'] if card.get('subject') == 'physics']
    
    print(f"元のカード数: {original_count}")
    print(f"化学カード: {len(chemistry_cards)}")
    print(f"物理カード: {len(physics_cards)}")
    
    # 化学カードのみにする
    data['cards'] = chemistry_cards
    
    # メタデータ更新
    data['metadata']['totalCards'] = len(chemistry_cards)
    data['metadata']['chemistryCards'] = len(chemistry_cards)
    data['metadata']['physicsCards'] = 0
    
    # 保存
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 物理カードを削除しました")
    print(f"新しい総カード数: {len(chemistry_cards)}")
    
    return len(chemistry_cards)

if __name__ == "__main__":
    remove_physics_cards()