#!/usr/bin/env python3
"""
全化学PDFから抽出したカードをアプリに統合
高品質フィルタリング付き
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

def get_chapter_tag(card, source):
    """章タグを取得"""
    if source == 'theory':
        return '理論化学'
    elif source == 'inorganic':
        return '無機化学'
    elif source == 'organic':
        return '有機化学'
    return '一般'

def merge_all_cards():
    # ファイルパス
    app_data_path = Path('/home/mochi/uchuichi-app/public/learning-data.json')
    
    # 抽出済みカードのパス
    card_files = [
        Path('/home/mochi/uchuichi-app/pdf-extractor/output_uchuichi/【理論・化学】宇宙一わかりやすい化学_cards.json'),
        Path('/home/mochi/uchuichi-app/pdf-extractor/output_muki/【無機・化学】宇宙一わかりやすい化学_cards.json'),
        Path('/home/mochi/uchuichi-app/pdf-extractor/output_yuki/【有機・化学】宇宙一わかりやすい化学_cards.json')
    ]
    
    # 既存データ読み込み
    with open(app_data_path, 'r', encoding='utf-8') as f:
        app_data = json.load(f)
    
    # 既存のPDF由来カードを削除（クリーンスタート）
    original_cards = [c for c in app_data['cards'] if not c['id'].startswith('uch_')]
    print(f"既存の非PDFカード数: {len(original_cards)}")
    
    all_new_cards = []
    
    # 各PDFからカードを収集
    for card_file in card_files:
        if not card_file.exists():
            print(f"⚠️ ファイルが見つかりません: {card_file}")
            continue
            
        with open(card_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        source = 'theory'
        if '無機' in str(card_file):
            source = 'inorganic'
        elif '有機' in str(card_file):
            source = 'organic'
            
        print(f"\n📚 {card_file.name} から {len(data['cards'])}枚のカード")
        
        # カードを処理
        for card in data['cards']:
            cleaned = clean_card(card)
            if cleaned:
                # IDを更新
                cleaned['id'] = f"uch_{source[:3]}_{cleaned['id'][-7:]}"
                
                # 章タグを追加
                chapter_tag = get_chapter_tag(cleaned, source)
                
                # アプリ形式に変換
                formatted_card = {
                    'id': cleaned['id'],
                    'question': cleaned['question'],
                    'answer': cleaned['answer'],
                    'type': cleaned.get('type', 'definition'),
                    'difficulty': cleaned.get('difficulty', 2),
                    'subject': 'chemistry',
                    'chapter': chapter_tag,
                    'page': cleaned.get('page', 1),
                    'reviewCount': 0,
                    'correctCount': 0,
                    'confidence': 0,
                    'tags': [chapter_tag] + cleaned.get('tags', [])
                }
                
                # 画像がある場合
                if 'image_path' in cleaned:
                    formatted_card['image_path'] = cleaned['image_path']
                
                all_new_cards.append(formatted_card)
    
    # 品質フィルタリング
    print(f"\n収集したカード総数: {len(all_new_cards)}")
    
    # タイプ別に分類
    definitions = [c for c in all_new_cards if c['type'] == 'definition']
    formulas = [c for c in all_new_cards if c['type'] == 'formula']
    quicks = [c for c in all_new_cards if c['type'] == 'quick']
    graphs = [c for c in all_new_cards if c['type'] == 'graph']
    
    # バランスよく選択（最大150枚）
    selected_cards = []
    
    # 理論・無機・有機から均等に選択
    theory_cards = [c for c in definitions if '理論' in c['chapter']][:20]
    inorganic_cards = [c for c in definitions if '無機' in c['chapter']][:20]
    organic_cards = [c for c in definitions if '有機' in c['chapter']][:20]
    
    selected_cards.extend(theory_cards)
    selected_cards.extend(inorganic_cards)
    selected_cards.extend(organic_cards)
    
    # 公式カードを追加
    selected_cards.extend(formulas[:15])
    
    # 重要ポイントカードを追加
    selected_cards.extend(quicks[:15])
    
    # 図解カードを少し追加（画像付き）
    selected_cards.extend(graphs[:10])
    
    print(f"\n選択したカード数: {len(selected_cards)}")
    print(f"  理論化学: {len([c for c in selected_cards if '理論' in c['chapter']])}枚")
    print(f"  無機化学: {len([c for c in selected_cards if '無機' in c['chapter']])}枚")
    print(f"  有機化学: {len([c for c in selected_cards if '有機' in c['chapter']])}枚")
    
    # 既存カードと統合
    app_data['cards'] = original_cards + selected_cards
    
    # メタデータ更新
    app_data['metadata']['totalCards'] = len(app_data['cards'])
    app_data['metadata']['chemistryCards'] = len([c for c in app_data['cards'] if c.get('subject') == 'chemistry'])
    app_data['metadata']['physicsCards'] = len([c for c in app_data['cards'] if c.get('subject') == 'physics'])
    
    # 保存
    with open(app_data_path, 'w', encoding='utf-8') as f:
        json.dump(app_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ {len(selected_cards)}枚の高品質カードを追加しました")
    print(f"総カード数: {app_data['metadata']['totalCards']}")
    
    # 追加したカードのサンプル表示
    print("\n追加したカードの例:")
    for i, card in enumerate(selected_cards[:5]):
        print(f"\n{i+1}. [{card['chapter']}] {card['type']}")
        print(f"   Q: {card['question'][:50]}...")
        print(f"   A: {card['answer'][:50]}...")
    
    return len(selected_cards)

if __name__ == "__main__":
    merge_all_cards()